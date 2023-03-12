
import traceback

from bs4 import BeautifulSoup, Tag
import requests
from flask import jsonify
from requests import Response

from Cookies.cookies import Cookies
from Extractor.extractor import EbayKleinanzeigenExtractor
from print_dict import pd


class EbayKleinanzeigenApi:
    def __init__(self, filename: str = "default.json", log: bool = True,
                 cookies: dict = None, save=False, mode: str = "client"):
        # Test for custom configs

        self.cookies = Cookies(filename, log, cookies, save, mode, keep_old=True)
        self.login = self.is_user_logged_in()
        self.log = log
        self.login = True
        self.ebay_url = "https://www.ebay-kleinanzeigen.de/"
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) Gecko/20100101 Firefox/108.0"
        self.headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept': '*/*'}
        self.html_text = ""
        self.json_obj: dict | None = None
        self.soup: Tag | None = None
        self.extractor: EbayKleinanzeigenExtractor | None = None
        self.response: Response | None = None

    def make_request(self, type, method, url, body=None):

        if method == "post":
            self.request_url_post(url,  body=body)
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

    def search_for(self, url):
        self.make_request(type="extractor", method="get", url=url)
        return self.extractor.parse(path="Extractor/", filename="SearchWindow.json")

    def set_up_url_for_search(self, search, token, path) -> str:
        prefix = ""
        if path == "None":
            if search == "None" and token == "None":
                prefix += "s-suchen.html"
            elif search == "None" and token != "None":
                prefix += token
            else:
                prefix += search + "/" + token
        else:
            if search == "None" and token == "None":
                prefix += path
            elif search == "None" and token != "None":
                prefix += path + token
            else:
                prefix += path + search + "/" + token

        return prefix

    def get_cities(self, url):
        self.make_request(url=url, type="json", method="get")
        cities_list = []
        for code, name in self.json_obj.items():
            city = dict(code=code[1:], name=name)
            cities_list.append(city)

        return cities_list

    def get_main(self, url):
        self.make_request(url=url, method="get", type="extractor")
        main_page = self.extractor.parse("Extractor/", "MainWindow.json")
        return main_page

    def get_categories(self, url):
        self.make_request(url=url, method="get", type="extractor")
        cat_lst = self.extractor.parse("Extractor/", "Categories.json")
        return cat_lst

    def get_add_detail(self, url):
        self.make_request(url=url, type="extractor", method="get")
        add_page = self.extractor.parse(path="Extractor/", filename="AddWindow.json")
        add_page['views'] = self.get_add_views(add_page['add_id'], log=self.log)
        return add_page

    def get_user_detail(self, url):
        self.make_request(url=url, type="extractor", method="get")
        user_page = self.extractor.parse(path="Extractor/", filename="UserWindow.json")
        return user_page

    def get_add_views(self, add_id, log):
        url = self.ebay_url + "s-vac-inc-get.json?adId=" + add_id
        self.make_request(url=url, method="get", type="json")
        return self.json_obj.get('numVisits')

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

    def send_message(self, message, add_id, add_type, contact_name):
        self.set_xsrf_token()
        body = dict(message=message,
                    adId=add_id,
                    adType=add_type,
                    contactName=contact_name)
        url = "https://www.ebay-kleinanzeigen.de/s-anbieter-kontaktieren.json"
        self.make_request(type="json_html", method="post", url=url, body=body)
        if self.log:
            print("printing send message result")
            print(self.html_text)
            print("\n\n\n")

    pass


if __name__ == "__main__":
    pass
