import time
from bs4 import BeautifulSoup
import requests
from flask import jsonify
from Cookies.cookies import Cookies
from Extractor.extractor import EbayKleinanzeigenExtractor
from print_dict import pd

"""
Max page = 50
Cookies in congif files must be with ';' separator, juste copy paste google chrome cookies for best use
"""


class EbayKleinanzeigenApi:
    def __init__(self, filename: str = "default.json",
                 url_prefix: str = "", type: str = "html", log: bool = True,
                 cookies: dict = None, save=False, mode: str = "client"):
        # Test for custom configs
        self.cookies = Cookies(filename, log, cookies, save, mode)
        self.log = log
        self.login = True
        self.ebay_url = "https://www.ebay-kleinanzeigen.de/"
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) Gecko/20100101 Firefox/108.0"
        self.headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept': '*/*'}

        if not self.check_cookies():
            self.cookies.reset_cookies()
            self.login = False

        if type == "html":
            url = self.ebay_url + url_prefix
            result = self.request_url(url, log=log)
            self.html_text = result.text
            self.soup = BeautifulSoup(self.html_text, "html.parser")
            self.extractor = EbayKleinanzeigenExtractor(self.soup)
        elif type == "json":
            url = "https://www.ebay-kleinanzeigen.de/s-ort-empfehlungen.json?query=" + url_prefix
            result = self.request_url(url, log=log)
            self.json_obj = result.json()

    def request_url(self, url, log=True):
        session = requests.Session()
        result = session.get(url, headers=self.headers, cookies=self.cookies.request_cookies)
        self.cookies.set_cookies(session)
        if log:
            print("URL = " + url)
            print("StatusCode = " + str(result.status_code))
        return result

    def check_cookies(self):
        url = self.ebay_url
        result = self.request_url(url, log=False)
        html_text = result.text
        html_item = "itemtile-fullpic"
        item_number = html_text.count(html_item)
        if item_number < 400:
            return False
        else:
            return True

    def attach_cookies_to_response(self, ads: dict):
        res = jsonify(ads)
        for cook in self.cookies.googleChromeCookie:
            if cook.get('expirationDate'):
                res.set_cookie(key=cook['name'], value=cook['value'],
                               expires=cook['expirationDate'], path=cook['path'],
                               domain=api.cookies.cookie_domain)
            # print(cook['name']+"   "+cook['domain'])
            res.headers.add('Access-Control-Allow-Credentials', 'true')
        return res

    def search_for(self):
        res = self.extractor.parse(path="Extractor/", filename="SearchWindow.json")
        return res

    def get_cities(self):
        list = []
        for code, name in self.json_obj.items():
            city = dict(code=code[1:], name=name)
            list.append(city)

        return list

    def get_main(self):
        main_page = self.extractor.parse("Extractor/", "MainWindow.json")
        return main_page

    def get_categories(self):
        cat_lst = self.extractor.parse("Extractor/", "Categories.json")
        return cat_lst

    def get_add_detail(self):
        add_page = self.extractor.parse(path="Extractor/", filename="AddWindow.json")
        add_page['views'] = self.get_add_views(add_page['add_id'], log=self.log)
        return add_page

    def get_user_detail(self):
        user_page = self.extractor.parse(path="Extractor/", filename="UserWindow.json")
        return user_page

    def get_add_views(self, add_id, log):
        url = self.ebay_url + "s-vac-inc-get.json?adId=" + add_id
        return self.request_url(url, log=log).json().get('numVisits')

    def print_item_number(self, html_item, for_object):
        item_number = self.html_text.count(html_item)
        print(f"Item Number for {for_object} = " + str(item_number))
        print("\n")

    def print_anzeigen(self, anzeigen):
        for anz in anzeigen:
            print("\n")
            for key, value in anz.items():
                try:
                    # print(f'{key} = {value}'.encode('utf8'))
                    print(f'{key} = {value}')
                except UnicodeEncodeError:
                    print(f'{key} = {value}'.encode('utf-8'))
            print("\n")


if __name__ == "__main__":
    test = 1
    if test == 1:
        prefix = "s-direktkaufen:aktiv/book/k0"
        api = EbayKleinanzeigenApi(url_prefix=prefix, log=True, mode="server", filename="default.json")

        res = api.search_for()
        pd(res)
    if test == 2:
        api2 = EbayKleinanzeigenApi(cookies=None, mode='server')
        add = api2.get_main()
        pd(add)
    if test == 3:
        api3 = EbayKleinanzeigenApi(mode='server')
        add = EbayKleinanzeigenExtractor(api3.soup).parse(path="Extractor/", filename="Categories.json")
        pd(add)
    if test == 4:
        prefix = "s-anzeige/top-delonghi-primadonna-s-de-luxe-kaffeevollautomat/2378252152-176-6832"
        api = EbayKleinanzeigenApi(url_prefix=prefix, log=True, mode="server", filename="default.json")
        ext = EbayKleinanzeigenExtractor(api.soup)
        res = ext.parse(path="Extractor/", filename="AddWindow.json")
        res['views'] = api.get_add_views(res['add_id'], log=True)
        pd(res)
    if test == 5:
        prefix = "s-bestandsliste.html?userId=85361371"
        api = EbayKleinanzeigenApi(url_prefix=prefix, log=True, mode="server", filename="default.json")
        ext = EbayKleinanzeigenExtractor(api.soup)
        res = ext.parse(path="Extractor/", filename="UserWindow.json")

        pd(res)
