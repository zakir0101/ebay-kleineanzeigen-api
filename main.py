import time
from bs4 import BeautifulSoup
import requests
from Extractor.extractor import EbayKleinanzeigenExtractor
import json
from print_dict import pd

"""
Max page = 50
Cookies in congif files must be with ';' separator, juste copy paste google chrome cookies for best use
"""


class EbayKleineanzeigenApi:
    def __init__(self, filename: str = "default.json",
                 url_prefix: str = "", type: str = "html", log: bool = True,
                 cookies: dict = None, save=False, mode: str = "client"):
        # Test for custom configs
        self.log=log
        self.mode = mode
        self.save = save
        self.login = True
        self.filename = filename
        self.ebay_url = "https://www.ebay-kleinanzeigen.de/"
        # user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) Gecko/20100101 Firefox/108.0"
        self.headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept': '*/*'}
        self.cookie_domain = "ebay-kleinanzeigen-zakir.de"
        self.googleChromeCookie = []
        self.cookies = dict()

        # self.refresh_cookies(log=log)
        if mode == "client":
            if cookies:
                self.cookies = cookies.copy()
                self.load_cookies(log=log)
        elif mode == "server":
            self.load_cookies(log=log)
            for cook in self.googleChromeCookie:
                self.cookies[cook['name']] = cook['value']
        if not self.check_cookies():
            self.cookies = {}
            self.googleChromeCookie = []
            self.save_cookies()
            self.login = False

        if type == "html":
            url = self.ebay_url + url_prefix
            result = self.request_url(url, log=log)
            self.html_text = result.text
            self.soup = BeautifulSoup(self.html_text, 'lxml')
            self.extractor = EbayKleinanzeigenExtractor(self.soup)
        elif type == "json":
            url = "https://www.ebay-kleinanzeigen.de/s-ort-empfehlungen.json?query=" + url_prefix
            result = self.request_url(url, log=log)
            self.json_obj = result.json()

    def request_url(self, url, log=True):
        session = requests.Session()
        result = session.get(url, headers=self.headers, cookies=self.cookies)
        self.set_cookies(session)
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

    def load_cookies(self, log=True):
        if self.mode == "server":
            with open(self.filename, 'r') as f:
                self.googleChromeCookie = json.load(f)
                if log:
                    print("Loading default config")

        elif self.mode == "client":
            for name, value in self.cookies.items():
                cook = dict(name=name, value=value, path="/",
                            domain=self.cookie_domain,
                            expirationDate="")
                self.googleChromeCookie.append(cook)

    def save_cookies(self):
        f = open(self.filename, "w")
        f.write(json.dumps(self.googleChromeCookie))
        f.close()

    ###############################################
    #   removing expired cookies
    ###############################################
    def refresh_cookies(self, log=True):
        for cook in self.googleChromeCookie:
            cook['domain'] = self.cookie_domain
            index = 0
            if cook.get('expirationDate'):
                rem = int(cook.get('expirationDate')) - time.time()
                if rem <= 0:
                    self.googleChromeCookie.remove(cook)
                    if log:
                        print(cook['name'] + " was removed from cookies")
            else:
                self.googleChromeCookie.remove(cook)
                if log:
                    print(cook['name'] + " was removed from cookies")

            pass
        pass

    def set_cookies(self, session):
        self.cookies_temp = [
            {'name': c.name, 'secure': c.secure, 'hostOnly': True,
             'httpOnly': False, 'value': c.value, "sameSite": "unspecified",
             'expirationDate': c.expires, "session": False, "storeId": 0,
             'domain': self.cookie_domain, 'path': "/"}
            for c in session.cookies]
        for cook in self.cookies_temp:
            self.cookies[cook['name']] = cook['value']
        found = False
        for cook in self.cookies_temp:
            for cook2 in self.googleChromeCookie:
                if cook['name'] == cook2['name']:
                    found = True
                    self.googleChromeCookie.remove(cook2)
                    self.googleChromeCookie.append(cook)

            if not found:
                if cook['expirationDate']:
                    self.googleChromeCookie.append(cook)
            found = False

        self.save_cookies()

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
        api = EbayKleineanzeigenApi(url_prefix=prefix, log=True, mode="server", filename="default.json")
        ext = EbayKleinanzeigenExtractor(api.soup)
        res = ext.parse(path="Extractor/", filename="SearchWindow.json")
        pd(res)
    if test == 2:
        api2 = EbayKleineanzeigenApi(cookies=None, mode='server')
        add = api2.get_galerie()
        pd(add)
    if test == 3:
        api3 = EbayKleineanzeigenApi(mode='server')
        add = EbayKleinanzeigenExtractor(api3.soup).parse(path="Extractor/", filename="Categories.json")
        pd(add)
    if test == 4:
        prefix = "s-anzeige/top-delonghi-primadonna-s-de-luxe-kaffeevollautomat/2378252152-176-6832"
        api = EbayKleineanzeigenApi(url_prefix=prefix, log=True, mode="server", filename="default.json")
        ext = EbayKleinanzeigenExtractor(api.soup)
        res = ext.parse(path="Extractor/", filename="AddWindow.json")
        res['views'] = api.get_add_views(res['add_id'], log=True)
        pd(res)
    if test == 5:
        prefix = "s-bestandsliste.html?userId=85361371"
        api = EbayKleineanzeigenApi(url_prefix=prefix, log=True, mode="server", filename="default.json")
        ext = EbayKleinanzeigenExtractor(api.soup)
        res = ext.parse(path="Extractor/", filename="UserWindow.json")

        pd(res)
