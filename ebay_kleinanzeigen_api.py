import json
import re
import traceback
from ssl import SSLError
from lxml.html import fromstring
from bs4 import BeautifulSoup, Tag
import requests
from flask import jsonify
from requests import Response
from requests.exceptions import ProxyError, ConnectTimeout

from Cookies.cookies import Cookies
from Extractor.extractor import EbayKleinanzeigenExtractor
from print_dict import pd


class EbayKleinanzeigenApi:

    def __init__(self, filename: str = "default.json", log: bool = True,
                 cookies: dict = None, save=False, mode: str = "client",
                 keep_old_cookies=True, rotate_ip: bool = False, webshare_rotate=False):
        # Test for custom configs
        self.rotate_ip = rotate_ip
        self._csrf = None
        self.authorization = None
        self.ebay_url = "https://www.kleinanzeigen.de/"
        self.cookies = Cookies(filename, log, cookies, save, mode, keep_old=keep_old_cookies)
        self.log = log
        self.login = True
        self.request_error = False
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) Gecko/20100101 Firefox/108.0"
        self.headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept': '*/*'}
        self.html_text = ""
        self.json_obj: dict | None = None
        self.soup: Tag | None = None
        self.extractor: EbayKleinanzeigenExtractor | None = None
        self.response: Response | None = None
        self.active_proxy = None
        self.webshare_proxies = None
        if webshare_rotate:
            self.webshare_proxies = {
                "http": "http://oeaariao-rotate:yoeq67r30rhb@p.webshare.io:80/",
                "https": "http://oeaariao-rotate:yoeq67r30rhb@p.webshare.io:80/"
            }

        if rotate_ip:
            self.countries = json.loads(open('Countries.json', "r").read())[:8]
            self.proxies = self.fetch_proxies()
            print(self.proxies)
            self.try_hard(self.is_user_logged_in, lambda res: res)
        else:
            self.is_user_logged_in()

        if not self.login and log:
            print("leider koennte nciht einlogen", )

        # self.login = self.is_user_logged_in()

    def try_hard(self, func1, func2):
        for x in range(len(self.proxies)):
            self.active_proxy = self.proxies[x]
            if self.log:
                print("trying with :", self.active_proxy['country'], self.active_proxy['proxy'])
            res = func1()
            if func2(res):
                if self.log:
                    print("operation done successfully")
                return res
        return None

    def fetch_proxies(self):
        src = 'https://api64.ipify.org'
        response = requests.get('https://free-proxy-list.net/')
        parser = fromstring(response.text)
        proxies = []
        for i in parser.xpath('//tbody/tr'):
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                if i.xpath('.//td[4]/text()')[0] in self.countries or True:
                    proxy = ":".join([i.xpath('.//td[1]/text()')[0],
                                      i.xpath('.//td[2]/text()')[0]])
                    country = i.xpath('.//td[4]/text()')[0]
                    proxy = dict(proxy=proxy, country=country)
                    proxies.append(proxy)
        return proxies

    def make_request(self, type, method, url, body=None, files=None):
        # self.cookies.print_request_cookies()
        # if self.proxies:
        #     self.active_proxy = random.choice(self.proxies)
        #     if  self.log:
        #         print("active proxy")
        #         pd(self.active_proxy)

        try:
            if method == "post":
                self.request_url_post(url, body=body, type=type, files=files)
            elif method == "get":
                self.request_url(url)
            else:
                print("method should be either post or get")
            self.request_error = False
        except (SSLError, ProxyError, ConnectTimeout, Exception):
            traceback.print_exc()
            print("max retries exceed with url - printend from server")

            self.request_error = True
        else:
            if "html" in type:
                self.html_text = self.response.text
            if "soup" in type:
                html_text = self.response.text
                self.soup = BeautifulSoup(html_text, "html.parser")
            if "ext" in type:
                html_text = self.response.text
                soup = BeautifulSoup(html_text, "html.parser")
                print("starting extractor")
                self.extractor = EbayKleinanzeigenExtractor(soup)
            if "json" in type:
                try:
                    self.json_obj = self.response.json()
                except Exception as e:
                    self.json_obj = None
                    # traceback.print_exc()
                    print("json parsing error")
                    # print(e)
                    pass

    def request_url(self, url):
        # print("x-csrf-token befor :", self.cookies.request_cookies.get('CSRF-TOKEN'))

        session = requests.Session()
        if self.active_proxy and self.rotate_ip:
            result = session.get(url, proxies={"http": self.active_proxy['proxy'],
                                               "https": self.active_proxy['proxy']},
                                 headers=self.headers,
                                 cookies=self.cookies.request_cookies)

        else:

            print("get request using proxies webshare")
            result = session.get(url, proxies=self.webshare_proxies,
                                 headers=self.headers,
                                 cookies=self.cookies.request_cookies)
        self.response = result
        if result.status_code < 400:
            self.cookies.set_cookies(session)
        if self.log:
            print("URL = " + url)
            print("StatusCode = " + str(result.status_code))
            print("x-csrf-token after:", self.cookies.request_cookies.get('CSRF-TOKEN'))
        return result

    def request_url_post(self, url, body, type, files):
        print("x-csrf-token befor:", self.cookies.request_cookies.get('CSRF-TOKEN'))

        session = requests.Session()
        if self.rotate_ip and self.active_proxy:
            result = self.request_url_post_with_proxy(url, body, type, session)
        else:
            result = self.request_url_post_without_proxy(url, body, type, session, files)
        self.response = result
        if result.status_code > 301:
            self.cookies.set_cookies(session)
        if self.log:
            print("URL = " + url)
            print("StatusCode = " + str(result.status_code))
            print("x-csrf-token after:", self.cookies.request_cookies.get('CSRF-TOKEN'))

        return result

    def request_url_post_with_proxy(self, url, body, type, session):
        if "jsondata" in type:
            result = session.post(url, proxies={"http": self.active_proxy['proxy'],
                                                "https": self.active_proxy['proxy']},
                                  headers=self.headers,
                                  cookies=self.cookies.request_cookies, json=body)
        else:
            result = session.post(url, proxies={"http": self.active_proxy['proxy'],
                                                "https": self.active_proxy['proxy']},
                                  headers=self.headers,
                                  cookies=self.cookies.request_cookies, data=body)
        return result

    def request_url_post_without_proxy(self, url, body, type, session, files):

        if "jsondata" in type:
            result = session.post(url, headers=self.headers, proxies=self.webshare_proxies,
                                  cookies=self.cookies.request_cookies, json=body)
        elif "image" in type:
            result = session.post(url, headers=self.headers, proxies=self.webshare_proxies,
                                  cookies=self.cookies.request_cookies, data=body, files=files)
        else:
            result = session.post(url, headers=self.headers, allow_redirects=True, proxies=self.webshare_proxies,
                                  cookies=self.cookies.request_cookies, data=body, )
        return result

    def is_user_logged_in(self):
        url = self.ebay_url
        self.make_request(url=url, method="get", type="html")

        if self.request_error:
            self.login = False
            return False
        html_item = "itemtile-fullpic"
        item_number = self.html_text.count(html_item)
        if item_number < 400:
            self.login = False
            self.cookies.reset_cookies()
            return False
        else:
            self.login = True
            return True

    def attach_cookies_to_response(self, ads: dict):
        res = jsonify(ads)
        for cook in self.cookies.googleChromeCookie:
            if cook.get('expirationDate'):
                res.set_cookie(key=cook['name'], value=cook['value'],
                               expires=cook['expirationDate'], path=cook['path'],
                               domain=self.cookies.cookie_domain)
            # print(cook['name']+"   "+cook['domain'])
        res.headers.add('Access-Control-Allow-Credentials', 'true')
        return res

    def set_header_for_bearer_token(self):
        accept = "application/json, text/plain, */*"
        self.headers['Accept'] = accept
        accept_encoding = "gzip, deflate, br"
        self.headers['Accept-Encoding'] = accept_encoding
        accept_language = "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6"
        self.headers['Accept-Language'] = accept_language

        dnt = "1"
        self.headers['Dnt'] = dnt
        referer = "https://www.kleinanzeigen.de/p-anzeige-aufgeben-schritt2.html"
        self.headers['Referer'] = referer
        sec_ch_ua = '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"'
        self.headers["Sec-Ch-Ua"] = sec_ch_ua
        sec_ch_ua_mobile = "?0"
        self.headers["Sec-Ch-Ua-Mobile"] = sec_ch_ua_mobile
        sec_ch_ua_platform = '"Windows"'
        self.headers["Sec-Ch-Ua-Platform"] = sec_ch_ua_platform
        sec_fetch_dest = "empty"
        self.headers['Sec-Fetch-Dest'] = sec_fetch_dest
        sec_fetch_mode = "cors"
        self.headers['Sec-Fetch-Mode'] = sec_fetch_mode

        sec_fetch_site = "same-origin"
        self.headers['Sec-Fetch-Site'] = sec_fetch_site
        # sec_fetch_user = "?1"
        upgrade_insecure_requests = "1"
        self.headers['Upgrade-Insecure-Requests'] = upgrade_insecure_requests
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/110.0.0.0 Safari/537.36 "
        self.headers['User-Agent'] = user_agent
        self.headers['X-Csrf-Token'] = self.cookies.request_cookies.get('CSRF-TOKEN')
        pass

    def set_bearer_token(self):
        print("""*************************** setting bearer Token *********************************""")
        url1 = "https://www.ebay-kleinanzeigen.de/m-access-token.json"
        self.headers = dict()
        self.set_header_for_bearer_token()
        self.make_request(url=url1, type="html", method="get")

        auth = self.response.headers.get("Authorization")
        self.headers['Authorization'] = auth
        self.authorization = auth
        if self.log:
            print("printin bearer Token")
            print("html_text (empty?) :", self.html_text)
            print("authorization :", auth)
            print("\n\n\n")

    def set_xsrf_token(self, mode=1):

        action = ""
        if mode == 1:
            action = "POST_MESSAGE"
        elif mode == 2:
            action = "POST_AD"

        # self.set_bearer_token()
        print("""*************************** settting xsrf token *********************************""")
        url2 = "https://gateway.ebay-kleinanzeigen.de/user-trust/users/current/verifications/phone/required?action" \
               "=" + action + "&source=DESKTOP "
        self.make_request(url=url2, type="html", method="get")
        # self.headers['x-csrf-token'] = self.cookies.request_cookies.get('CSRF-TOKEN')
        self._csrf = self.cookies.request_cookies.get('CSRF-TOKEN')
        if self.log:
            print("printing csrf token")
            print("x-csrf-token :", self.headers.get('X-Csrf-Token'))
            print(self.html_text)
            print("\n\n\n")

    def get_user_name(self):
        url = self.ebay_url
        self.make_request("soup", "get", url)
        if self.request_error:
            return None
        soup = self.soup
        user_elm = soup.find("span", id="user-email", class_='text-body-regular')
        if user_elm:
            user_text = user_elm.text.strip()
            user_email = user_text.replace("angemeldet", "").replace("als", "").replace(":", "").strip()
            user_name = user_email[:user_email.index("@")]
            if self.log:
                print("user_email :", user_email)
                print("user_name :", user_name)
            return user_email, user_name

        return None

    def get_user_id(self):
        url = "https://www.ebay-kleinanzeigen.de/m-nachrichten.html"
        self.make_request(type="soup", method="get", url=url)
        scripts = self.soup.find_all("script", type="text/javascript")
        main_script = None
        for script in scripts:
            if "userId" in script.text:
                main_script = script
        text = main_script.text
        user_id_regex = re.compile(r'userId: (\d+)')
        match = user_id_regex.search(text)
        if self.log:
            print("user id =  ", match.groups()[0])
        return match.groups()[0]
        pass

    def get_cities(self, url):
        self.make_request(url=url, type="json", method="get")
        cities_list = []
        for code, name in self.json_obj.items():
            city = dict(code=code[1:], name=name)
            cities_list.append(city)

        return cities_list


if __name__ == "__main__":
    api = EbayKleinanzeigenApi(mode="server", keep_old_cookies=False)
    # login = api.is_user_logged_in()
    print("login ", api.login)
    # user_email, user_name = api.get_user_name()
    api.try_hard(api.get_user_name, lambda res: res)
    pass
