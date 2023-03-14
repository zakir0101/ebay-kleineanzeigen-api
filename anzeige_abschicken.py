import random
import sys
from ebay_kleinanzeigen_api import EbayKleinanzeigenApi
import requests

from main import Main


class AnzeigeAbschicken(EbayKleinanzeigenApi):
    def __init__(self, filename: str = "default.json", log: bool = True, cookies: dict = None, save=False,
                 mode: str = "client"):
        super().__init__(filename, log, cookies, save, mode)
        self.form_data = None
        self.NachbarschaftHilfe = "401"
        self.zuVerschenken = "192"
        self.NACHHILFE = ""
        self.tracking_id = "fa99601b-34dd-4432-b026-ad8082545711"

    def set_headers(self, form_data):
        self.set_bearer_token()
        self.set_xsrf_token()
        # authority = "www.ebay-kleinanzeigen.de"
        # method = "POST"
        # path = "/p-anzeige-abschicken.html"
        # shema = "https"
        accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
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

    def set_form_data(self, title, category, price, location_id):
        location = get_location(location_id)

        form_data = dict(adType="OFFER",
                         title=title,
                         categoryId=category,
                         previousCategoryId=category,
                         userSelectedAttributeMap="{}",
                         suggestedCategoryId=self.get_suggested_category(title),
                         trackingId=self.tracking_id,
                         priceAmount=price,
                         description="sldfjlsfd ldsjflsj löj lsd jlösk jöflkj",
                         buyNow="false",
                         zipCode=str(location['name']).split("-")[0].strip(),
                         locationId=location['id'],
                         latitude=location['lat'],
                         longitude=location['lng'],
                         _addressVisibility="on",
                         posterType="PRIVATE",
                         contactName="Abood",
                         _phoneNumberVisibility="on",
                         imprint="",
                         adid="",
                         flow="true",
                         postAdWenkseSessionId="d1393bef-90be-47fc-86ff-4d7a8077a636",
                         _csrf=self._csrf)

        form_data['attributeMap[notebooks.versand_s]'] = "nein"
        self.form_data = form_data
        return form_data

        pass

    def get_location_by_id(self,location_id):
        pass
    def get_suggested_category(title):
        pass

    def anzeige_abschicken(self):
        self.set_headers()
        self.set_form_data()
        pass


if __name__ == "__main__":
    pass
