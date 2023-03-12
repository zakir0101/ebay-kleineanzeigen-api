import re
import traceback
from bs4 import BeautifulSoup, Tag
import requests
from flask import jsonify
from requests import Response
import json5
from Cookies.cookies import Cookies
from Extractor.extractor import EbayKleinanzeigenExtractor
from print_dict import pd


class EbayKleinanzeigenApi:
    def __init__(self, filename: str = "default.json", log: bool = True,
                 cookies: dict = None, save=False, mode: str = "client", keep_old_cookies=True):
        # Test for custom configs
        self.ebay_url = "https://www.ebay-kleinanzeigen.de/"
        self.cookies = Cookies(filename, log, cookies, save, mode, keep_old=keep_old_cookies)
        self.log = log
        self.login = True
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) Gecko/20100101 Firefox/108.0"
        self.headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept': '*/*'}
        self.html_text = ""
        self.json_obj: dict | None = None
        self.soup: Tag | None = None
        self.extractor: EbayKleinanzeigenExtractor | None = None
        self.response: Response | None = None
        self.login = self.is_user_logged_in()

    def make_request(self, type, method, url, body=None):

        if method == "post":
            self.request_url_post(url, body=body)
        elif method == "get":
            self.request_url(url)
        else:
            print("method should be either post or get")

        if "html" in type:
            self.html_text = self.response.text
        if "soup" in type:
            html_text = self.response.text
            self.soup = BeautifulSoup(html_text, "html.parser")
        if "ext" in type:
            html_text = self.response.text
            soup = BeautifulSoup(html_text, "html.parser")
            self.extractor = EbayKleinanzeigenExtractor(soup)
        if "json" in type:
            try:
                self.json_obj = self.response.json()
            except Exception as e:
                traceback.print_exc()
                print(e)
                pass

    def request_url(self, url):

        session = requests.Session()
        result = session.get(url, headers=self.headers,
                             cookies=self.cookies.request_cookies)
        self.response = result
        if result.status_code < 301:
            self.cookies.set_cookies(session)
        if self.log:
            print("URL = " + url)
            print("StatusCode = " + str(result.status_code))
        return result

    def request_url_post(self, url, body):
        session = requests.Session()
        result = session.post(url, headers=self.headers,
                              cookies=self.cookies.request_cookies, data=body)
        self.response = result
        if result.status_code > 301:
            self.cookies.set_cookies(session)
        if self.log:
            print("URL = " + url)
            print("StatusCode = " + str(result.status_code))
        return result

    def is_user_logged_in(self):
        url = self.ebay_url
        self.make_request(url=url, method="get", type="html")

        html_item = "itemtile-fullpic"
        item_number = self.html_text.count(html_item)
        if item_number < 400:
            self.cookies.reset_cookies()
            return False
        else:
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

    def set_bearer_token(self):
        url1 = "https://www.ebay-kleinanzeigen.de/m-access-token.json"
        self.make_request(url=url1, type="html", method="get")
        auth = self.response.headers.get("Authorization")
        self.headers['Authorization'] = auth
        if self.log:
            print("printin bearer Token")
            print("Expiration ", self.html_text)
            print(auth)
            print("\n\n\n")

    def set_xsrf_token(self):
        self.set_bearer_token()
        url2 = "https://gateway.ebay-kleinanzeigen.de/user-trust/users/current/verifications/phone/required?action" \
               "=POST_MESSAGE&source=DESKTOP "
        self.make_request(url=url2, type="html", method="get")
        self.headers['x-csrf-token'] = self.cookies.request_cookies['CSRF-TOKEN']
        if self.log:
            print("printing csrf token")
            print("x-csrf-token :", self.headers['x-csrf-token'])
            print(self.html_text)
            print("\n\n\n")

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
            print("user id =  ",match.groups()[0])
        return match.groups()[0]
        pass


if __name__ == "__main__":
    api = EbayKleinanzeigenApi(mode="server", keep_old_cookies=False)
    api.get_user_id()
    pass
