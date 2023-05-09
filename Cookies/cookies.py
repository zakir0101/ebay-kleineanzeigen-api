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
        deploy_mode = "offline"
        if deploy_mode == "online":
            self.cookie_domain = ".ebay-kleinanzeigen-zakir-new.onrender.com"
        elif deploy_mode == "offline":
            self.cookie_domain = ".ebay-kleinanzeigen-zakir.de"
        elif deploy_mode == "mobile":
            self.cookie_domain = ".192.168.151.149"

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
                self.refresh_google_chrome_cookies()
            for cook in self.googleChromeCookie:
                self.request_cookies[cook['name']] = cook['value']

    ###############################################
    #   load google chrome cookies
    ###############################################
    def load_google_chrome_cookies_from_file(self, log=True):
        with open(self.filename, 'r') as f:
            self.googleChromeCookie = json.load(f)
            if log:
                print("Loading default config")

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
            cook['domain'] = self.cookie_domain
            index = 0
            if cook.get('expirationDate'):
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
        self.cookies_temp = [
            {'name': c.name, 'secure': c.secure, 'hostOnly': True,
             'httpOnly': False, 'value': c.value, "sameSite": "unspecified",
             'expirationDate': c.expires, "session": False, "storeId": 0,
             'domain': self.cookie_domain, 'path': "/"}
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

        self.save_cookies()

    ###############################################
    #   resetting cookies
    ###############################################
    def reset_cookies(self):
        return
        self.request_cookies = {}
        self.googleChromeCookie = []
        self.save_cookies()
