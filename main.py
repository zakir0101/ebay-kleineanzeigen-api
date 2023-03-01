
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
    def __init__(self, filename):
        # Test for custom configs

        with open('default.json', 'r') as f:
            self.config = json.load(f)
            print("Loading default config")

        self.googleChromeCookie = self.config['googleChromeCookie']
        self.cookies = {}
        for cook in self.googleChromeCookie:
            self.cookies[cook['name']] = cook['value']
        self.cookies = {}

        self.ebay_url = "https://www.ebay-kleinanzeigen.de/"
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        self.headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept': '*/*'}

    def search_for(self, search, token):
        url = self.ebay_url
        if search == "None" and token == "None":
            url += "s-suchen.html"
        elif search == "None" and token != "None":
            url += token
        else :
            url += search+"/"+token

        result = requests.Session().get(url, headers=self.headers, cookies=self.cookies)
        print("URL = " + url+"\n\n")
        print("StatusCode = " + str(result.status_code))
        print("encoding  = "+result.encoding)

        html_text = result.text

        html_item = "ad-listitem lazyload-item"
        item_number = html_text.count(html_item)
        if item_number == 0:
            sleep(60)
        print("Item Number = " + str(item_number))

        soup = BeautifulSoup(html_text, 'lxml')
        jobs = soup.find_all('li', class_=html_item)
        print("Real Item Number = " + str(len(jobs)))
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


            print(add.get("url_link"))
            add_list.append(add)
        # sleep(60 * 5)
        return add_list



    def get_cities(self, search):
        url = "https://www.ebay-kleinanzeigen.de/s-ort-empfehlungen.json?query=" + search
        result = requests.Session().get(url, headers=self.headers, cookies=self.cookies)
        print("URL = " + url)
        print("StatusCode = " + str(result.status_code))

        json_obj = result.json()
        list = []
        for code, name in json_obj.items():
            city = dict(code=code[1:], name=name)
            list.append(city)

        return list

    def get_main(self):
        url = self.ebay_url
        result = requests.Session().get(url, headers=self.headers, cookies=self.cookies)
        print("URL = " + url)
        print("StatusCode = " + str(result.status_code))

        html_text = result.text

        html_item = "itemtile-fullpic"
        item_number = html_text.count(html_item)
        if item_number == 0:
            sleep(60)
        print("Item Number = " + str(item_number))

        soup = BeautifulSoup(html_text, 'lxml')
        items = soup.find_all('li', class_=html_item)

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
        url = self.ebay_url
        result = requests.Session().get(url, headers=self.headers, cookies=self.cookies)
        print("URL = " + url)
        print("StatusCode = " + str(result.status_code))

        html_text = result.text

        html_item = "text-link-secondary treelist-headline"
        item_number = html_text.count(html_item)
        if item_number == 0:
            sleep(60)
        print("Item Number = " + str(item_number))

        soup = BeautifulSoup(html_text, 'lxml')
        items = soup.find_all('a', class_=html_item)

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
        url = self.ebay_url
        result = requests.Session().get(url, headers=self.headers, cookies=self.cookies)
        print("URL = " + url)
        print("StatusCode = " + str(result.status_code))

        html_text = result.text

        html_item = "itemtile-condensed"
        item_number = html_text.count(html_item)
        if item_number == 0:
            sleep(60)
        print("Item Number = " + str(item_number))

        soup = BeautifulSoup(html_text, 'lxml')
        items = soup.find_all('li', class_=html_item)
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

    # def get_ads(self, city="", min_price="", max_price="", category=""):
    #
    #     page_number = 0
    #
    #     url = self.ebay_url + "s-preis:" + str(min_price) + ":/seite:" + str(
    #         page_number) + "/marklin/k0"
    #     result = requests.Session().get(url, headers=self.headers, cookies=self.cookies)
    #     print("URL = " + url)
    #     print("StatusCode = " + str(result.status_code))
    #
    #     html_text = result.text
    #
    #     html_item = "ad-listitem lazyload-item"
    #     item_number = html_text.count(html_item)
    #     if item_number == 0:
    #         sleep(60)
    #     print("Item Number = " + str(item_number))
    #
    #     soup = BeautifulSoup(html_text, 'lxml')
    #     jobs = soup.find_all('li', class_=html_item)
    #     anzeigen = []
    #     for job in jobs:
    #         anzeige = dict()
    #         try:
    #             html_price = "aditem-main--middle--price-shipping--price"  # "aditem-main--middle--price"
    #             html_ellipsis = "ellipsis"
    #             html_image = "imagebox"
    #             html_description = "aditem-main--middle--description"
    #
    #             anzeige['price'] = job.find("p", html_price).text
    #             anzeige['title'] = job.find("a", class_=html_ellipsis).text
    #             anzeige['url_link'] = self.ebay_url + job.find("a", class_=html_ellipsis)['href']
    #             anzeige['description'] = job.find("p", class_=html_description).text
    #             anzeige['image_link'] = job.find("div", class_=html_image)['data-imgsrc']
    #
    #         except KeyError as k:
    #             anzeige['image_link'] = ""
    #
    #         anzeigen.append(anzeige)
    #     # sleep(60 * 5)
    #     return anzeigen

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
        print("Error exception caught!")
        print(e)
