import time
from bs4 import BeautifulSoup
import requests
from requests import Session

from Extractor.extractor import EbayKleinanzeigenExtractor
import json
from print_dict import pd


class Cookies:
    def __init__(self, filename: str = "default.json", log: bool = True,
                 cookies: dict = None, save=False, mode: str = "client", keep_old=False):
        # Test for custom configs
        self.log = log
        self.mode = mode
        self.save = save
        self.filename = filename
        self.googleChromeCookie = []
        self.request_cookies = dict()
        deploy_mode = "server"
        if deploy_mode == "online":
            self.cookie_domain = ".ebay-zakir-1996.onrender.com"
        elif deploy_mode == "offline":
            self.cookie_domain = ".ebay-kleinanzeigen-zakir.de"
        elif deploy_mode == "mobile":
            self.cookie_domain = ".192.168.151.149"
        elif deploy_mode == "server":
            self.cookie_domain = ".kleinanzeigen.de"
        # self.ebay_url = "https://www.ebay-kleinanzeigen.de/"
        # user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) Gecko/20100101 Firefox/108.0"
        # self.headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
        #                 'Accept-Encoding': 'gzip, deflate',
        #                 'Accept': '*/*'}

        if mode == "client":
            if cookies:
                self.request_cookies = cookies.copy()
                self.load_google_chrome_cookies_from_request(log=log)
        elif mode == "server":
            self.load_google_chrome_cookies_from_file(log=log)
            if not keep_old:
                print("refreshing cookies")
                self.refresh_google_chrome_cookies()
            for cook in self.googleChromeCookie:
                # print(cook['name'])
                self.request_cookies[cook['name']] = cook['value']

    ###############################################
    #   load google chrome cookies
    ###############################################
    def load_google_chrome_cookies_from_file(self, log=True):
        with open(self.filename, 'r') as f:
            self.googleChromeCookie = json.load(f)
            # for cook in self.googleChromeCookie:
            #     if "kleinanzeigen.de" not in cook.get("domain"):
            #         self.googleChromeCookie.remove(cook)
            # if log:
            #     print("Loading default config")

    ###############################################
    #   load google chrome cookies
    ###############################################
    def load_google_chrome_cookies_from_request(self, log=True):

        for name, value in self.request_cookies.items():
            cook = dict(name=name, value=value, path="/",
                        domain=self.cookie_domain,
                        expirationDate="")
            self.googleChromeCookie.append(cook)

        self.save_cookies()

    ###############################################
    #   saving cookies to a file
    ###############################################

    def save_cookies(self):
        f = open(self.filename, "w")
        f.write(json.dumps(self.googleChromeCookie))
        f.close()

    ################################################################
    #   removing expired cookies bevor sending request (mode == server
    ################################################################
    def refresh_google_chrome_cookies(self, log=True):
        for cook in self.googleChromeCookie:
            # cook['domain'] = self.cookie_domain
            index = 0
            if cook.get('expirationDate') is not None:
                # print("with expiration ",cook.get("name"))
                rem = int(cook.get('expirationDate')) - time.time()
                if rem <= 0:
                    self.googleChromeCookie.remove(cook)
                    if log:
                        print(cook['name'] + " was removed from cookies")

            else:
                pass
                # self.googleChromeCookie.remove(cook)
                # if log:
                #     print(cook['name'] + " was removed from cookies")

            pass
        pass

    ###############################################
    #   setting
    ###############################################
    def set_cookies(self, session: Session):
        # for co in session.cookies:
        #     for key , value in co.items()
        # c.
        self.cookies_temp = [
            {'name': c.name, 'secure': c.secure, 'hostOnly':  True ,
             'httpOnly': False, 'value': c.value, "sameSite": "unspecified",
             'expirationDate': c.expires, "session": c.expires is None, "storeId": 0,
             'domain': c.domain, 'path': c.path}
            for c in session.cookies]
        for cook in self.cookies_temp:
            self.request_cookies[cook['name']] = cook['value']
        found = False
        for cook in self.cookies_temp:
            for cook2 in self.googleChromeCookie:
                if cook['name'] == cook2['name']:
                    found = True
                    self.googleChromeCookie.remove(cook2)
                    self.googleChromeCookie.append(cook)

            if not found:
                # if cook['expirationDate']:
                self.googleChromeCookie.append(cook)
            found = False
        self.refresh_google_chrome_cookies(self.log)
        for cook in self.googleChromeCookie:
            self.request_cookies[cook['name']] = cook['value']
        self.save_cookies()

    ###############################################
    #   resetting cookies
    ###############################################
    def reset_cookies(self):
        return
        self.request_cookies = {}
        self.googleChromeCookie = []
        self.save_cookies()
    def print_request_cookies(self):
        # for key,value in self.request_cookies.items():
        #     print(key,value)
        for cook in self.googleChromeCookie:
            print(cook['name'],cook['domain'])
    def remove_specific_cookies(self):
        un_wanted_cookies = ["ak_bmsc","_gat","bm_sv"]
        for unw_cook in un_wanted_cookies:
            if self.request_cookies.get(unw_cook):
                print("removing",unw_cook)
                self.request_cookies.pop(unw_cook)
        for cook in self.googleChromeCookie:
            for unw_cook in un_wanted_cookies:
                if cook['name'] == unw_cook:
                    print("removing 2", unw_cook)
                    self.googleChromeCookie.remove(cook)