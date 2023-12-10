import json
import random
import re
import traceback
from ssl import SSLError
from lxml.html import fromstring
from bs4 import BeautifulSoup, Tag
import requests
from flask import jsonify
from requests import Response
from requests.exceptions import ProxyError, ConnectTimeout

from cookies import Cookies
from Extractor.extractor import EbayKleinanzeigenExtractor


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
        self.webshare_proxies_list = None
        self.webshare_rotate = webshare_rotate
        if webshare_rotate:
            self.zakir_proxies = {
                "http": "http://oeaariao-rotate:yoeq67r30rhb@p.webshare.io:80/",
                "https": "http://oeaariao-rotate:yoeq67r30rhb@p.webshare.io:80/"
            }
            self.abdul_proxies = {
                "htpp" : "http://"
            }
            self.ahmed_tita_proxies = {
                "http": "http://qbdhukkk-rotate:0olcqbjafp1b@p.webshare.io:80/",
                "https": "http://qbdhukkk-rotate:0olcqbjafp1b@p.webshare.io:80/"
            }
            self.webshare_proxies = self.ahmed_tita_proxies
            self.update_webshare_proxies()

        if rotate_ip:
            self.countries = json.loads(open('Countries.json', "r").read())[:8]
            self.proxies = self.fetch_proxies()
            print(self.proxies)
            self.try_hard(self.is_user_logged_in, lambda res: res)
        else:
            self.is_user_logged_in()

        if not self.login and log:
            print("leider koennte nciht einlogen", )


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

    def update_webshare_proxies(self):

        zakir1996_link = "https://proxy.webshare.io/api/v2/proxy/list/download/wwgxjjciahsxutqnrpaodcooxmwivbrgsmbpwbsr/-/any/username/direct/-/"
        zakir_elkheir = "https://proxy.webshare.io/api/v2/proxy/list/download/xeqhkzlgfuzemzoyvizizlvdnrhtoxwemgfgssal/-/any/username/direct/-/"
        adnan_link = "https://proxy.webshare.io/api/v2/proxy/list/download/flgurmocunyqhwsjgfeoojgeirczemcxmrlaglix/-/any/username/direct/-/"
        ahmed_tita_link = "https://proxy.webshare.io/api/v2/proxy/list/download/gwtupjzvgnuqxchyhoqiizmbropovvpniqxewrlu/-/any/username/direct/-/"
        saleem_abd_link = "https://proxy.webshare.io/api/v2/proxy/list/download/wmypmxbysjagflzpkwhgsooyccjqhtpaujclzzsd/-/any/username/direct/-/"
        saleem_omer_link = "https://proxy.webshare.io/api/v2/proxy/list/download/njsxdevopvnjuutgnutwdvztlhfeuqjfifxwxzji/-/any/username/direct/-/"

        all_links = [zakir1996_link, zakir_elkheir, adnan_link, ahmed_tita_link, saleem_abd_link, saleem_omer_link]
        all_links = random.sample(all_links,3)
        proxy_list = []
        for link in all_links:
            if link == "":
                continue
            text = requests.get(link).text
            lines = text.split("\n")
            for line in lines:
                token = line.strip().split(":")
                if len(token) < 4:
                    continue
                ip = token[0].strip()
                if ip == "38.154.227.167":
                    continue
                port = token[1].strip()
                user = token[2].strip()
                password = token[3].strip()
                proxy_link = f"http://{user}:{password}@{ip}:{port}"
                print(proxy_link)
                proxy = {"http": proxy_link, "https": proxy_link}
                proxy_list.append(proxy)
        print("number of proxies added = ", len(proxy_list))
        open("proxies/all_proxies.json", "w").write(json.dumps(proxy_list))
        self.webshare_proxies_list = proxy_list

    def make_request(self, type, method, url, body=None, files=None):
        # self.cookies.print_request_cookies()
        # if self.proxies:
        #     self.active_proxy = random.choice(self.proxies)
        #     if  self.log:
        #         print("active proxy")
        #         pd(self.active_proxy)

        if self.webshare_rotate :
            self.webshare_proxies = random.choice(self.webshare_proxies_list)

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
            if self.log and self.webshare_rotate:
                print("get request using proxies webshare")
                print(self.webshare_proxies.get("http"))
            result = session.get(url, proxies=self.webshare_proxies,
                                 headers=self.headers,
                                 cookies=self.cookies.request_cookies)
        self.response = result
        if result.status_code < 400:
            self.cookies.set_cookies(session)
        if self.log:
            print("URL = " + url)
            print("StatusCode = " + str(result.status_code))
            # print("x-csrf-token after:", self.cookies.request_cookies.get('CSRF-TOKEN'))
        return result

    def request_url_post(self, url, body, type, files):
        # print("x-csrf-token befor:", self.cookies.request_cookies.get('CSRF-TOKEN'))

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
            # print("x-csrf-token after:", self.cookies.request_cookies.get('CSRF-TOKEN'))

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
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "de-DE,de;q=0.9",
            "dnt" : "1",
            "accept-encoding" : "gzip, deflate, br",
            "cache-control": "max-age=0",
            "sec-ch-ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent" : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
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
            return  user_name
        else:
            return self.get_user_name_2()

    def get_user_name_2(self):
        url = self.ebay_url + "m-einstellungen.html#/account-settings"
        url = self.ebay_url
        self.make_request("html-soup","get",url)
        open("result.html","w",encoding="utf-8").write(self.html_text)
        tag = self.soup.find("li", class_="subnav-info")
        if tag is None:
            return None
        tagStrong = tag.find("strong")
        if tagStrong is None:
            return None
        text = tagStrong.text
        return text[:text.index("@")]
    def get_user_id(self):
        url = "https://www.ebay-kleinanzeigen.de/m-nachrichten.html"
        self.make_request(type="soup", method="get", url=url)

        scripts = self.soup.find_all("script", type="text/javascript")
        if  self.soup is None:
            return None
        main_script = None
        for script in scripts:
            if "userId" in script.text:
                main_script = script
        if not main_script:
            return None
        text = main_script.text
        user_id_regex = re.compile(r'userId: (\d+)')
        match = user_id_regex.search(text)
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
    api = EbayKleinanzeigenApi(log=True, mode="server", filename="Cookies/ahmed_tita.json", keep_old_cookies=False,
                               save=True, webshare_rotate=False)
    if api.login:
        user_id = api.get_user_id()
    print("login ", api.login)
    print("user_name",api.get_user_name())
    print("user_id",user_id)

    pass
