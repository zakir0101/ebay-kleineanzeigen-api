import traceback
from time import sleep
import uuid
from print_dict import pd
from urllib import parse
from uuid import uuid4
from ebay_kleinanzeigen_api import EbayKleinanzeigenApi


class AnzeigeAbschickenApi(EbayKleinanzeigenApi):
    def __init__(self, filename: str = "default.json", log: bool = True, cookies: dict = None, save=False,
                 mode: str = "client",rotate_ip: bool = False):
        super().__init__(filename, log, cookies, save, mode,rotate_ip)
        self.adwen_id = None
        self.form_data = None
        self.NachbarschaftHilfe = "401"
        self.zuVerschenken = "192"
        self.NACHHILFE = "268"
        self.WEITERE_DIENSTLEISTUN = "298"
        self.tracking_id = "ma99601b-34dd-4432-b026-ad8082545711"

    def set_headers(self):
        # authority = "www.ebay-kleinanzeigen.de"
        # method = "POST"
        # path = "/p-anzeige-abschicken.html"
        # shema = "https"
        accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8," \
                 "application/signed-exchange;v=b3;q=0.7 "
        self.headers['accept'] = accept
        accept_encoding = "gzip, deflate, br"
        self.headers['accept-encoding'] = accept
        accept_language = "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6"
        self.headers['accept-language'] = accept_language
        cache_control = "max-age=0"
        self.headers['cache-control'] = cache_control
        content_type = "application/x-www-form-urlencoded"
        self.headers['content-type'] = content_type
        dnt = "1"
        self.headers['dnt'] = dnt
        # origin = "https://www.ebay-kleinanzeigen.de"
        # referer = "https://www.ebay-kleinanzeigen.de/p-anzeige-aufgeben-schritt2.html"
        # sec_ch_ua = '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"'
        # sec_ch_ua_mobile = "?0"
        # sec_ch_ua_platform = "Windows"
        # sec_fetch_dest = "document"
        # sec_fetch_mode = "navigate"
        # sec_fetch_site = "cross-origin"
        # sec_fetch_user = "?1"
        upgrade_insecure_requests = "1"
        self.headers['upgrade-insecure-requests'] = upgrade_insecure_requests
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/110.0.0.0 Safari/537.36 "

        return

    def get_category_id(self, title):
        if "nachhilfe" in title.lower():
            return self.NACHHILFE
        elif "webseite" in title.lower():
            return self.WEITERE_DIENSTLEISTUN
        else:
            return self.zuVerschenken

    def set_form_data(self, title, price, zip_code, city_code, description, contact_name):
        category_id = self.get_category_id(title)
        sug_category_id = self.get_suggested_category(title)
        # location = self.get_location_by_zip(zip_code)
        if category_id == self.zuVerschenken:
            price = ""
        form_data = dict(adType="OFFER",
                         title=title,
                         categoryId=category_id,
                         previousCategoryId="",
                         userSelectedAttributeMap="{}",
                         suggestedCategoryId=sug_category_id,
                         trackingId=self.tracking_id,
                         priceAmount=price,
                         description=description,
                         buyNow="false",
                         zipCode=zip_code,
                         locationId=city_code,
                         latitude="",
                         longitude="",
                         posterType="PRIVATE",
                         contactName=contact_name,
                         _addressVisibility="on",
                         _phoneNumberVisibility="on",
                         imprint="",
                         adid="",
                         flow="true",
                         postAdWenkseSessionId=self.adwen_id,
                         _csrf=self._csrf)

        # form_data['attributeMap[notebooks.versand_s]'] = "nein"
        if category_id == self.zuVerschenken:
            form_data['attributeMap[zu_verschenken.versand_s]'] = "nein"
        self.form_data = form_data
        return form_data

        pass

    def get_location_by_id(self, location_id):
        url = self.ebay_url + "p-orte-der-plz.jason?locationId=" + location_id
        self.make_request("json", "get", url)
        res = self.json_obj[0]
        return res
        pass

    def get_location_by_zip(self, zip):
        url = self.ebay_url + "p-orte-der-plz.json?zipCode=" + zip
        self.make_request("json", "get", url)
        # if self.json_obj.__len__() == 0:
        #     return None
        # self.json_obj = self.json_obj[0]
        # self.json_obj['zip'] = zip
        if self.log:
            pd(self.json_obj)
        return self.json_obj
        pass

    def get_suggested_category(self, title):
        url = self.ebay_url + "p-category-suggestion.json?title=" + title
        self.make_request("json", "get", url)
        if self.log:
            print("suggested category is")
            pd(self.json_obj)
        return self.json_obj.get("category_id")

    def get_price_suggestion(self, title, category_id):
        url = self.ebay_url + "p-price-suggestion.json?title=" + title + "&categoryId=" + str(category_id)
        self.make_request("html", "get", url)
        if self.log:
            print("suggested price is :")
            print(self.html_text)
        return self.json_obj

    def get_attributes_suggestion(self, title, category_id):
        url = self.ebay_url + "p-attribute-suggestion.json"
        self.set_xsrf_token(mode=2)
        data = dict(title=title, categoryId=category_id,
                    previousCategoryId=category_id, attributes="{}")
        self.headers['content-type'] = "application/json"
        self.headers['x-requested-with'] = "XMLHttpRequest"
        self.make_request("jsondata_json", "post", url, data)
        if self.log:
            print("suggested attributes are")
            pd(self.json_obj)
        return self.json_obj

    def check_add_state(self, adid):
        url = self.ebay_url + "p-mein-anzeige-status.json?id=" + adid
        self.make_request("json", "get", url)
        if self.log:
            pd(self.json_obj)
        return self.json_obj

    def anzeige_abschicken(self, title, price, zip_code, city_code, description, contact_name):
        url = self.ebay_url + "p-anzeige-abschicken.html"

        self.adwen_id = str(uuid4())
        self.tracking_id = str(uuid4())

        # setting header
        self.set_headers()
        self.set_bearer_token()
        sleep(1)
        self.set_xsrf_token()
        sleep(1)

        # setting form data
        self.set_form_data(title, price, zip_code, city_code, description, contact_name)

        # making request
        self.make_request(type="html", method="post", url=url, body=self.form_data)
        sleep(1)
        f = open("result.html", "w", encoding="utf-8")
        f.write(self.html_text)
        if self.log:
            print(self.response.url)
        adId = parse.parse_qs(parse.urlparse(self.response.url).query).get('adId')

        # trackingId = parse.parse_qs(parse.urlparse(self.response.url).query)['trackingId'][0]
        # uuid = parse.parse_qs(parse.urlparse(self.response.url).query)['uuid'][0]
        return adId


if __name__ == "__main__":
    id = 10
    api = AnzeigeAbschickenApi(log=True, mode="server")
    title = "Audi 10"
    zip_array = ["01616", "02627",
                 "04617", "06420", "06667", "08209",
                 "09623", "01945", "01990", "18211",
                 "20253", "21107", "10117", "10779", "21244", ]
    title_array = [
        "Nachhilfe Java", "Webseite erstellen", "Nachhilfe Python",
        "Nachhilfe Javascript", "Nachhilfe Informatik" "Logo erstellen",
        "Responsive Webseite Erstellen", "Webdesign Webseite Homepage, web scraping",
        "html css javascript react Angular Vue"]

    if id == 1:
        api.get_location_by_id("3343")
        pd(api.json_obj)
    if id == 2:
        res = api.get_location_by_zip("09126")
        pd(res)
    if id == 3:
        res = api.get_suggested_category(title)
        print("suggested category id = ", res)
        pd(res)
    if id == 4:
        cat = api.get_suggested_category(title_array[0])
        price = api.get_price_suggestion(title_array[0], cat)
        attr = api.get_attributes_suggestion(title_array[0], cat)
    if id == 5:
        published = False
        for zip in zip_array:
            for title in title_array:
                published = api.anzeige_abschicken(title, "15", zip,
                                                   "ich bin informatiker, und ich freu mich auf deine Nachricht",
                                                   "Zakir")
                if published:
                    print("Titel = ", title)
                    print("zip code = ", zip)
                    city = api.get_location_by_zip(zip)['name']
                    print("city name = ", city)
                    break
            if published:
                break
        if published:
            print(" your add was published successfully")
        else:
            print("uninformatively we couldn`t publish your add :( ")

    if id == 10:
        adid = api.anzeige_abschicken(title_array[0], "15","09126" ,"3880",
                                      "ich bin informatiker, und ich freu mich auf deine Nachricht",
                                      "Zakir")

        if adid:
            res = dict(state="OK", add_id=adid)
            print("Add-id is :", adid)
        else:
            res = dict(state="ERROR", html=api.html_text)
            f = open("result.html", "w", encoding="utf-8")
            f.write(api.html_text)
    if id == 6:
        index = 0
        for title in title_array:
            index += 1
            try:
                cat = api.get_suggested_category(title)
                print(index, title, "has the categroy code :", cat)
            except Exception as e:
                print(index, title, "has no categoryis code")

    if id == 7:
        index = 0
        api = AnzeigeAbschickenApi(log=False, mode="server")
        for zip in zip_array:
            index += 1
            try:
                city = api.get_location_by_zip(zip)
                print(index, "  ", zip, "exist :", city['name'])
            except Exception as e:
                traceback.print_exc()
                print(index, "  ", zip, "exist nicht :( ")

    pass
