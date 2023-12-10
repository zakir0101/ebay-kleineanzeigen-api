import json
import os
import traceback
from time import sleep
import random

import requests
from print_dict import pd
from urllib import parse
from uuid import uuid4

from ebay_kleinanzeigen_api import EbayKleinanzeigenApi
from pathlib import Path
import time


class AnzeigeAbschickenApi(EbayKleinanzeigenApi):
    def __init__(self, filename: str = "default.json", log: bool = True, cookies: dict = None, save=False,
                 mode: str = "client", rotate_ip: bool = False, keep_old_cookies=True, webshare_rotate=False,
                 chat_id=None, telegram_api_url=None):
        super().__init__(filename, log, cookies, save, mode, keep_old_cookies, rotate_ip, webshare_rotate)
        self.adwen_id = None
        self.form_data = None
        self.NachbarschaftHilfe = "401"
        self.zuVerschenken = "192"
        self.NACHHILFE = "268"
        self.WEITERE_DIENSTLEISTUN = "298"
        self.tracking_id = "ma99601b-34dd-4432-b026-ad8082545711"
        self.chat_id = chat_id
        self.telegram_api_url = telegram_api_url

    def set_headers_for_posting_add(self):
        accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8," \
                 "application/signed-exchange;v=b3;q=0.7 "
        self.headers['Accept'] = accept
        accept_encoding = "gzip, deflate, br"
        self.headers['Accept-Encoding'] = accept_encoding
        accept_language = "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6"
        self.headers['Accept-Language'] = accept_language
        cache_control = "max-age=0"
        self.headers['Cache-Control'] = cache_control
        # content_type = "application/x-www-form-urlencoded"
        # self.headers['content-type'] = content_type

        content_type = "application/x-www-form-urlencoded"
        self.headers['Content-Type'] = content_type
        dnt = "1"
        self.headers['Dnt'] = dnt
        origin = "https://www.kleinanzeigen.de"
        self.headers['Origin'] = origin
        referer = "https://www.kleinanzeigen.de/p-anzeige-aufgeben-schritt2.html"
        self.headers['Referer'] = referer
        sec_ch_ua = '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"'
        self.headers["Sec-Ch-Ua"] = sec_ch_ua
        sec_ch_ua_mobile = "?0"
        self.headers["Sec-Ch-Ua-Mobile"] = sec_ch_ua_mobile
        sec_ch_ua_platform = '"Windows"'
        self.headers["Sec-Ch-Ua-Platform"] = sec_ch_ua_platform
        sec_fetch_dest = "document"
        self.headers['Sec-Fetch-Dest'] = sec_fetch_dest
        sec_fetch_mode = "navigate"
        self.headers['Sec-Fetch-Mode'] = sec_fetch_mode

        sec_fetch_site = "same-origin"
        self.headers['Sec-Fetch-Site'] = sec_fetch_site
        sec_fetch_user = "?1"
        self.headers['Sec-Fetch-User'] = sec_fetch_user

        # sec_fetch_user = "?1"
        upgrade_insecure_requests = "1"
        self.headers['Upgrade-Insecure-Requests'] = upgrade_insecure_requests
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/110.0.0.0 Safari/537.36 "
        self.headers['User-Agent'] = user_agent
        token = self.cookies.request_cookies.get('CSRF-TOKEN')
        # self.headers['X-Csrf-Token'] = token
        # self.headers['X-Xsrf-Token'] = token

        # authority = "www.ebay-kleinanzeigen.de"
        # method = "POST"
        # path = "/p-anzeige-abschicken.html"
        # shema = "https"

        return

    def get_category_id(self, title):
        if "nachhilfe" in title.lower():
            return self.NACHHILFE
        elif "webseite" in title.lower():
            return self.WEITERE_DIENSTLEISTUN
        else:
            return self.zuVerschenken

    def set_form_data(self, title, price, zip_code, city_code, description, contact_name, image_url_list=None):
        category_id = self.get_category_id(title)
        sug_category_id = self.get_suggested_category(title)
        # location = self.get_location_by_zip(zip_code)
        if category_id == self.zuVerschenken:
            price = ""
        form_data = dict(adType="OFFER",
                         title=title,
                         categoryId=category_id,
                         previousCategoryId=category_id,
                         userSelectedAttributeMap="{}",
                         suggestedCategoryId=sug_category_id,
                         trackingId=self.tracking_id,
                         priceAmount=price,
                         priceType="FIXED",
                         description=description,
                         buyNowEligible='false',
                         buyNow="",
                         zipCode=zip_code,
                         locationId=city_code,
                         latitude="",
                         longitude="",
                         posterType="PRIVATE",
                         contactName=contact_name,
                         _addressVisibility="on",
                         _phoneNumberVisibility="on",
                         imprint="",
                         adId="",
                         _marketingOptIn="on",
                         flow="true",
                         postAdWenkseSessionId=self.adwen_id,
                         _csrf=self._csrf
                         )
        if image_url_list is not None:
            for index, url in enumerate(image_url_list):
                form_data[f"adImages[{index}].url"] = url

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

    def set_headers_for_uploading_image(self):
        # authority = "www.kleinanzeigen.de"
        # self.headers[":authority"] = authority
        # method = "POST"
        # self.headers[":method"] = method
        # path = "/p-bild-hochladen.html"
        # self.headers[":path"] = path
        # scheme = "https"
        # self.headers[":scheme"] = scheme
        accept = "*/*"
        self.headers['accept'] = accept
        accept_encoding = "gzip, deflate, br"
        self.headers['accept-encoding'] = accept_encoding
        accept_language = "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6"
        self.headers['accept-language'] = accept_language
        # cache_control = "max-age=0"
        # self.headers['cache-control'] = cache_control
        # content_type = "application/x-www-form-urlencoded"
        # self.headers['content-type'] = content_type
        #
        obj = time.gmtime(0)
        epoch = time.asctime(obj)

        # print("The epoch is:", epoch)
        curr_time = round(time.time() * 1000)
        # print("Milliseconds since epoch:", curr_time)
        next_time = curr_time + 100000
        # print(next_time)
        content_type = "multipart/form-data; boundary=----moxieboundary" + next_time.__str__().strip()
        self.headers['Content-Types'] = content_type

        dnt = "1"
        self.headers['dnt'] = dnt
        origin = "https://www.kleinanzeigen.de"
        self.headers['Origin'] = origin
        # referer = "https://www.ebay-kleinanzeigen.de/p-anzeige-aufgeben-schritt2.html"
        sec_ch_ua = '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"'
        self.headers["sec-ch-ua"] = sec_ch_ua
        sec_ch_ua_mobile = "?0"
        self.headers["sec-ch-ua-mobile"] = sec_ch_ua_mobile
        sec_ch_ua_platform = '"Windows"'
        self.headers["sec-ch-ua-platform"] = sec_ch_ua_platform
        sec_fetch_dest = "empty"
        self.headers['sec-fetch-dest'] = sec_fetch_dest
        sec_fetch_mode = "cors"
        self.headers['sec-fetch-mode'] = sec_fetch_mode

        sec_fetch_site = "same-origin"
        self.headers['sec-fetch-site'] = sec_fetch_site
        # sec_fetch_user = "?1"
        # upgrade_insecure_requests = "1"
        # self.headers['upgrade-insecure-requests'] = upgrade_insecure_requests
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/110.0.0.0 Safari/537.36 "
        self.headers['User-Agent'] = user_agent
        self.headers['X-Csrf-Token'] = self.cookies.request_cookies.get('CSRF-TOKEN')
        self.headers['X-Xsrf-Token'] = self.cookies.request_cookies.get('CSRF-TOKEN')
        # print(self.cookies.request_cookies.get('CSRF-TOKEN'))
        # print(self._csrf)
        return

    def upload_image(self, image_name, image_path: Path):
        full_path = image_path.joinpath(image_name)
        # print(full_path)
        if not os.path.exists(full_path):
            print("images could not be found")
            return None
        form_data = dict(name=image_name)
        files = {'file': open(full_path, 'rb')}
        if self.log:
            print("uploading images")

        self.set_headers_for_uploading_image()
        url = "https://www.kleinanzeigen.de/p-bild-hochladen.html"
        self.make_request(type="html-json-image", method="post", url=url, body=form_data, files=files)
        if self.log:
            open("result.html", "w", encoding="utf-8").write(self.html_text)
            # pd(self.json_obj)
        if self.json_obj.get("status") == "OK":
            res = self.json_obj['yamsAdImage']
            image_link = res["dynamicRuleThumbnailUrl"]
            if self.log:
                if self.telegram_api_url:
                    self.send_telegram_message(f"image: {image_name} uploaded successfully")
                print(f"image: {image_name} uploaded successfully")
                # print(image_link)
            return image_link
        else:
            if self.log:
                print(f"could not upload image : {image_name}")
            return None

    def get_location_by_zip(self, zip):
        url = self.ebay_url + "p-orte-der-plz.json?zipCode=" + zip
        self.make_request("json", "get", url)
        # if self.json_obj.__len__() == 0:
        #     return None
        # self.json_obj = self.json_obj[0]
        # self.json_obj['zip'] = zip
        if self.log:
            if self.json_obj is not None:
                print("city code found")
                # pd(self.json_obj)
            else:
                print("could NOT find City Code")
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

    def init_request(self):
        url = "https://gateway.kleinanzeigen.de/gdpr/api/frontend-metrics/init"
        json_data = {
            "hostname": "www.kleinanzeigen.de",
            "module": "gdpr-banner",
            "bannerVisible": "False"
        }
        print("********************** validating ***********************")
        self.make_request(method="post", type="jsondata-json", url=url, body=json_data)

    def validate(self):
        url = "https://gateway.kleinanzeigen.de/gdpr/api/consent-v2/validate"
        json_data = {
            "customVersion": 6,
            "consentInterpretationFlags": [
                "googleAdvertisingFeaturesAllowed",
                "googleAnalyticsAllowed",
                "infonlineAllowed",
                "theAdexAllowed",
                "criteoAllowed",
                "facebookAllowed",
                "amazonAdvertisingAllowed",
                "rtbHouseAllowed"
            ]
        }
        print("********************** validating ***********************")
        self.make_request(method="post", type="jsondata-json", url=url, body=json_data)

        pass

    def anzeige_abschicken(self, title, price, zip_code, city_code, description, contact_name, image_link=None):
        url = self.ebay_url + "p-anzeige-abschicken.html"

        self.adwen_id = str(uuid4())
        self.tracking_id = str(uuid4())

        self.cookies.remove_specific_cookies()
        self.set_bearer_token()
        if self.authorization is None:
            if self.telegram_api_url:
                self.send_telegram_message("couldn't get Bearer Token")
                raise Exception()
            return None

        self.cookies.remove_specific_cookies()
        self.set_xsrf_token(mode=2)
        if self.response.status_code >= 400:
            if self.telegram_api_url:
                self.send_telegram_message("couldn't set xsrf token")
        print("""*************************** Header **************************************""")
        self.headers = dict()
        self.set_headers_for_posting_add()
        # pd(self.headers)

        print("""*************************** form data **************************************""")
        webshare_state = self.webshare_rotate
        self.webshare_rotate = False
        self.set_form_data(title, price, zip_code, city_code, description, contact_name, image_link)
        # pd(self.form_data)
        self.webshare_rotate = webshare_state
        # making request
        print("""***************************  posting add 1 **************************************""")

        # self.cookies.remove_specific_cookies()
        self.make_request(type="html-soup", method="post", url=url, body=self.form_data)
        print("\n******************* Response Header 1 **********************************")
        # for key, value in self.response.headers.items():
        #     print(key, value)

        url = self.response.url

        f = open("result.html", "w", encoding="utf-8")
        f.write(self.html_text)
        f.close()
        if self.log:
            print("response url")
            print(url)

        adId = None
        if "adId" in url:
            adId = parse.parse_qs(parse.urlparse(url).query).get('adId')[0].__str__().strip()

        # trackingId = parse.parse_qs(parse.urlparse(self.response.url).query)['trackingId'][0]
        # uuid = parse.parse_qs(parse.urlparse(self.response.url).query)['uuid'][0]
        if self.log:
            if self.telegram_api_url:
                self.send_telegram_message(f"addId : {adId}")
            print("adId", adId)
        return adId

    def anzeige_bestaetigen(self, url):
        self.make_request(method="get", type="html", url=url)

    def choose_rando_images(self, numb=3):
        root_dir = "images/pexels/"
        dir_list = os.listdir(path=root_dir)
        selected = random.sample(dir_list, 3)
        result = selected
        if self.log:
            for item in result:
                print(item, "was selected")

        return result

    def publish_add_from_json_file(self, file_path):

        if not os.path.exists(file_path):
            print("file could not be found :(")
            if self.telegram_api_url:
                self.send_telegram_message("file could not be found :(")
            return False
        add = json.loads(open(file_path, "r", encoding="utf-8").read())
        city_c = self.get_location_by_zip(add['zip'])[0].get('id')
        sleep(0.5)
        if self.log:
            print("city_code", city_c)
        image_folder = add.get("image_folder")
        image_name_list = os.listdir(image_folder)
        image_url_list = []
        for name in image_name_list:
            image_url_list.append(self.upload_image(name, Path(image_folder)))
        # for url in image_url_list:
        #     print("image_url", url)
        if None in image_url_list:
            print("problem uploading some images")
            if self.telegram_api_url:
                self.send_telegram_message("problem uploading some images")
                raise Exception()
            return False
        print("""*************************** Preparing posting add**************************************""")

        add_id = self.anzeige_abschicken(add["title"], add["price"], add["zip"], city_c,
                                         add["description"], add["contact_name"], image_url_list)
        if add_id is None:
            if self.telegram_api_url:
                self.send_telegram_message("could not post add, sorry :(")
                raise Exception()
            print("could not post add, sorry :(")
            return
        print("""*************************** checking add state *********************************""")
        active = False
        for i in range(20):
            response = self.check_add_state(add_id)
            if self.log:
                if self.telegram_api_url:
                    self.send_telegram_message( f"state : {response.get('state') }")
                print(response)
            if response.get("state") == "ACTIVE":
                active = True
                break
            time.sleep(2)
        if self.log:
            if self.telegram_api_url:
                self.send_telegram_message("add was published successfully")
            print("add was published successfully")
        myadds: list = json.loads(open("myAdd.json", "r").read())
        myadds.append(add_id.__str__().strip())
        open("myAdd.json", "w").write(json.dumps(myadds))
        return active

    def send_telegram_message(self, message):

        """
        Sends a message to the specified chat_id on Telegram.
        """
        chat_id = self.chat_id  # Assuming the chat_id is set as an attribute of the instance
        payload = {
            'chat_id': chat_id,
            'text': message
        }
        requests.post(self.telegram_api_url + '/sendMessage', data=payload)


if __name__ == "__main__":
    id = 13

    api = AnzeigeAbschickenApi(log=True, mode="server", filename="Cookies/ahmed_tita.json", keep_old_cookies=False,
                               save=True, webshare_rotate=False)
    # api.is_user_logged_in()
    api.cookies.remove_specific_cookies()
    print("login", api.login)
    print("user name ", api.get_user_name())
    # print(api.html_text)
    if not api.login:

        exit(1)
    # print(api.html_text)
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

    if id == 15:
        adId = ['2559357833']
        print("adId", adId)

    if id == 14:
        api.set_bearer_token()
    if id == 13:
        api.publish_add_from_json_file(Path("./adds/all_ahmed_tita.json"))
    if id == 12:
        api.set_xsrf_token(2)
        print(api.html_text)
    if id == 11:
        res = api.upload_image("python-logo.jpg", Path("./images"))
        # print(res)
    if id == 1:
        api.get_location_by_id("3343")
        pd(api.json_obj)
    if id == 2:
        res = api.get_location_by_zip("10627")
        res = res[0]
        pd(res)
        city_code = res.get('id')
        print("city_code ", city_code)
    if id == 3:
        res = api.get_suggested_category(title_array[0])
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
        title = "Nachhilfe Informatik C++ Python Javascript Java Kotlin Matlab SQL"
        description = """ich biete seit 2 Jahren Nachhilfe in Informatik. 
Egal ob bei der Lösung eine Aufgabe, oder die Implementierung eines Projekt oder um die Grundlagen der Programmierung kennen zu lernen. 
ich helfe euch gerne""";
        zip = "10627"
        res = api.get_location_by_zip(zip)
        res = res[0]
        city_code = res.get('id')
        price = "15"
        image_link = api.upload_image("python-logo.jpg", Path("./images"))
        adid = api.anzeige_abschicken(title, price, zip, city_code,
                                      description, "Zakir", image_link)
        active = False
        while not active:
            res = api.check_add_state(adid)
            print(res)
            if res.get("state") == "ACTIVE":
                active = True
        print("add was published successfully")
        myadds: list = json.loads(open("myAdd.json", "r").read())
        myadds.append(adid.__str__().strip())
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
