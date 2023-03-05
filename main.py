import time
from time import sleep
from bs4 import BeautifulSoup
import requests
# from functions import *
import json
import os.path

"""
Max page = 50
Cookies in congif files must be with ';' separator, juste copy paste google chrome cookies for best use
"""


class EbayKleineanzeigenApi:
    def __init__(self, filename: str = "default.json",
                 url_prefix: str = "", type: str = "html", log=True):
        # Test for custom configs
        self.login = True
        self.filename = filename
        self.ebay_url = "https://www.ebay-kleinanzeigen.de/"
        # user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) Gecko/20100101 Firefox/108.0"
        self.headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept': '*/*'}
        self.cookie_domain = "http://localhost:4200/"
        self.cookie_domain = "ebay-kleinanzeigen-zakir"
        self.googleChromeCookie: list[dict] = []
        self.load_cookies(log=log)
        self.refresh_cookies(log=log)
        self.cookies = {}
        for cook in self.googleChromeCookie:
            self.cookies[cook['name']] = cook['value']
        if not self.check_cookies():
            self.cookies = {}
            self.googleChromeCookie = {}
            self.save_cookies()
            self.login = False

        if type == "html":
            url = self.ebay_url + url_prefix
            result = self.request_url(url, log=log)
            self.html_text = result.text
            self.soup = BeautifulSoup(self.html_text, 'lxml')
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
        with open(self.filename, 'r') as f:
            self.googleChromeCookie = json.load(f)
            if log:
                print("Loading default config")

    def save_cookies(self):
        f = open(self.filename, "w")
        f.write(json.dumps(self.googleChromeCookie))
        f.close()

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
             'domain': self.cookie_domain, 'path': c.path}
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

        html_item = "ad-listitem lazyload-item"
        self.print_item_number(html_item, "Search")
        jobs = self.soup.find_all('li', class_=html_item)
        add_list = []
        for job in jobs:
            add = dict()
            try:
                html_price = "aditem-main--middle--price-shipping--price"  # "aditem-main--middle--price"
                html_url_link = "ellipsis"
                html_image = "imagebox"
                html_description = "aditem-main--middle--description"
                html_location = "aditem-main--top--left"
                if job.find("p", html_price):
                    add['price'] = " ".join(job.find("p", html_price).text.strip().split(" "))
                else:
                    add['price'] = ""
                add['title'] = " ".join(job.find("a", class_=html_url_link).text.strip().split(" "))
                add['url_link'] = self.ebay_url + " ".join(job.find("a", class_=html_url_link)['href'].split(" "))
                add['description'] = " ".join(job.find("p", class_=html_description).text.strip().split(" "))
                add['location'] = " ".join(job.find("div", class_=html_location).text.strip().split(" "))
                add['image_url'] = " ".join(job.find("div", class_=html_image)['data-imgsrc'].split(" "))
            except KeyError as k:
                add['image_url'] = ""

            add_list.append(add)
        # sleep(60 * 5)
        return add_list

    def get_cities(self):
        list = []
        for code, name in self.json_obj.items():
            city = dict(code=code[1:], name=name)
            list.append(city)

        return list

    def get_main(self):
        html_item = "itemtile-fullpic"
        self.print_item_number(html_item, "main window")
        items = self.soup.find_all('li', class_=html_item)
        add_list = []
        for item in items:
            add = dict()
            try:
                html_price = "itemtile-price"
                # html_link = "ellipsis"
                html_image = "itemtile-header"
                html_title = "itemtile-title"
                html_location = "itemtile-location"
                add['url_link'] = self.ebay_url + item.find("a")['href']
                add['title'] = str(item.find("h3", class_=html_title).text).strip()
                add['location'] = item.find("div", class_=html_location).text.strip()
                price = item.find("span", html_price)
                if price:
                    add['price'] = price.text
                else:
                    add['price'] = ""
                add['image_link'] = item.find("div", class_=html_image).find("img")['src']

            except KeyError as k:
                add['image_link'] = ""

            add_list.append(add)
        # sleep(60 * 5)
        return add_list

    def get_categories(self):

        html_item = "text-link-secondary treelist-headline"
        self.print_item_number(html_item, "Categories")
        items = self.soup.find_all('a', class_=html_item)

        add_list = []
        for item in items:
            add = dict()

            add['url_link'] = self.ebay_url + item['href'][1:]
            add['code'] = item['href'][item['href'].index("/", 1) + 1:]
            add['name'] = item.text.strip()
            add['children'] = []

            for childItem in item.parent.findAll("li"):
                if childItem.find("a").get('href'):
                    child = dict()
                    child['url_link'] = self.ebay_url + childItem.find("a").get('href')[1:]
                    child['code'] = childItem.find("a")['href'][childItem.find("a")['href'].index("/", 1) + 1:]
                    child['name'] = childItem.find("a").text.strip()
                    add['children'].append(child)

            add_list.append(add)
        # sleep(60 * 5)
        return add_list

    def get_galerie(self):
        html_item = "itemtile-condensed"
        self.print_item_number(html_item, "Galerie")
        items = self.soup.find_all('li', class_=html_item)
        add_list = []
        for item in items:
            add = dict()
            try:
                html_price = "itemtile-price"
                # html_link = "ellipsis"
                html_image = "itemtile-header"
                html_title = "itemtile-title"
                html_location = "itemtile-location"

                add['url_link'] = self.ebay_url + item.find("a")['href']
                add['title'] = str(item.find("h3", class_=html_title).text).strip()
                add['location'] = item.find("div", class_=html_location).text.strip()
                price = item.find("span", html_price)
                if price:
                    add['price'] = price.text
                else:
                    add['price'] = ""
                add['image_link'] = item.find("div", class_=html_image).find("img")['src']

            except KeyError as k:
                add['image_link'] = ""

            add_list.append(add)
        # sleep(60 * 5)
        return add_list

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
    api = None
    try:
        api = EbayKleineanzeigenApi("")

        # ads = api.get_ads(min_price="100")
    except Exception as e:
        print("Error exception caut")
