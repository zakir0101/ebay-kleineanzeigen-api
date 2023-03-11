import sys

import requests

from main import EbayKleinanzeigenApi


class AnzeigeAbschicken:
    def __init__(self, cookies):
        self.cookies = cookies
        self.url = "https://www.ebay-kleinanzeig1en.de/p-anzeige-abschicken.html"
        self.form_data = self.get_form_data()
        self.headers = self.get_headers(self.form_data)


    def get_form_data(self):
        NachbarschaftHilfe = "401"
        zuVerschenken = "192"
        location_id1="3343"
        location_id2="1124"

        csrf = "f670377f-1257-465a-92db-a9f600d22f5c"

        for cook in self.cookies.keys():
            if cook == "CSRF-TOKEN":
                csrf = self.cookies[cook]
        form_data = dict(adType="OFFER",
                         title="Nachhilfe java",
                         categoryId=zuVerschenken ,
                         previousCategoryId=zuVerschenken,
                         userSelectedAttributeMap="{}",
                         suggestedCategoryId=zuVerschenken,
                         trackingId="fa99601b-34dd-4432-b026-ad8082545711",
                         priceAmount="",
                         description="sldfjlsfd ldsjflsj löj lsd jlösk jöflkj",
                         buyNow="false",
                         zipCode="10627",
                         locationId=location_id1,
                         latitude="52.520008",
                         longitude="13.404954",
                         _addressVisibility="on",
                         posterType="PRIVATE",
                         contactName="Abood",
                         _phoneNumberVisibility="on",
                         imprint="",
                         adid="",
                         flow="true",
                         postAdWenkseSessionId="d1393bef-90be-47fc-86ff-4d7a8077a636",
                         _csrf=csrf)

        form_data['attributeMap[notebooks.versand_s]'] = "nein"
        print("csrf :" + csrf)
        return form_data

        pass

    def get_headers(self,form_data):
        authority = "www.ebay-kleinanzeigen.de"
        method = "POST"
        path = "/p-anzeige-abschicken.html"
        shema = "https"
        accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        accept_encoding = "gzip, deflate, br"
        accept_language = "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6"
        cache_control = "max-age=0"
        content_length = sys.getsizeof(form_data).__str__()
        content_type = "application/x-www-form-urlencoded"
        dnt = "1"
        origin = "https://www.ebay-kleinanzeigen.de"
        referer = "https://www.ebay-kleinanzeigen.de/p-anzeige-aufgeben-schritt2.html"
        sec_ch_ua = '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"'
        sec_ch_ua_mobile = "?0"
        sec_ch_ua_platform = "Windows"
        sec_fetch_dest = "document"
        sec_fetch_mode = "navigate"
        sec_fetch_site = "cross-origin"
        sec_fetch_user = "?1"
        upgrade_insecure_requests = "1"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/110.0.0.0 Safari/537.36 "
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) Gecko/20100101 Firefox/108.0"
        headers = {"authority": authority, "method": method, "path": path, "shema": shema,
                   "accept": accept, "accept-encoding": accept_encoding, "accept-language": accept_language,
                   "cache-control": cache_control, "content-length": content_length, "content-type": content_type,
                   "dnt": dnt, "origin": origin, "referer": referer, "sec-ch-ua": sec_ch_ua,
                   "sec-ch-ua-mo    bile": sec_ch_ua_mobile, "sec-ch-ua-platform": sec_ch_ua_platform,
                   "sec-fetch-dest": sec_fetch_dest, "sec-fetch-mode": sec_fetch_mode,
                   "sec-fetch-site": sec_fetch_site,
                   "sec-fetch-user": sec_fetch_user, "upgrade-insecure-requests": upgrade_insecure_requests,
                   "user-agent": user_agent

                   }

        return headers

    def anzeige_abschicken(self):
        session = requests.Session()
        result = session.post(self.url, headers=self.headers, cookies=self.cookies, data=self.form_data)

        print("URL = " + self.url + "\n\n")
        print("StatusCode = " + str(result.status_code))
        print("encoding  = " + result.encoding)

        html_text = result.text

        f = open("result.html", "w", encoding='utf-8')
        f.write(html_text)
        f.close()

        pass


if __name__ == "__main__":
    api = None
    schicken = None
    try:
        api = EbayKleinanzeigenApi(mode="server", log=False)
        schicken = AnzeigeAbschicken(api.cookies)
        print("configeration done")
    except Exception as e:
        print("Exception :")
        print(e)
    else:
        if api.check_cookies():
            schicken.anzeige_abschicken()
