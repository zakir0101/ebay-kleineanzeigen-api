import random
import sys

import requests

from main import Main


class AnzeigeAbschicken:
    def __init__(self, cookies):
        self.cookies = cookies
        self.url = "https://www.ebay-kleinanzeig1en.de/p-anzeige-abschicken.html"

        self.form_data = self.get_form_data_for_msg()
        self.headers = self.get_headers_for_msg(self.form_data)

    def get_form_data(self):
        NachbarschaftHilfe = "401"
        zuVerschenken = "192"
        location_id1 = "3343"
        location_id2 = "1124"

        csrf = "f670377f-1257-465a-92db-a9f600d22f5c"

        csrf = self.cookies["CSRF-TOKEN"]
        form_data = dict(adType="OFFER",
                         title="Nachhilfe java",
                         categoryId=zuVerschenken,
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

    def get_headers(self, form_data):
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

    def get_headers_for_msg(self, form_data):
        userAgentsList = [
            'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        ];
        authority = "www.ebay-kleinanzeigen.de"
        method = "POST"
        path = "/s-anbieter-kontaktieren.json"
        shema = "https"
        accept = "*/*"
        accept_encoding = "gzip, deflate, br"
        accept_language = "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6"
        # cache_control = "max-age=0"
        content_length = "47"
        # content_length = sys.getsizeof(form_data).__str__()
        content_type = "application/x-www-form-urlencoded; charset=UTF-8"
        dnt = "1"
        origin = "https://www.ebay-kleinanzeigen.de"

        referer = "https://www.ebay-kleinanzeigen.de/s-anzeige/4061-705149-a00-rev-ac-wd-controller-board-my-book/2382158583-225-768"
        sec_ch_ua = '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"'
        sec_ch_ua_mobile = "?0"
        sec_ch_ua_platform = "Windows"
        sec_fetch_dest = "empty"
        sec_fetch_mode = "cors"
        sec_fetch_site = "same-origin"
        # sec_fetch_user = "?1"
        # upgrade_insecure_requests = "1"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        # user_agent = userAgentsList[random.randint(0,2)]
        x_requested_with = "XMLHttpRequest"
        x_csrf_token = "f670377f-1257-465a-92db-a9f600d22f5c"
        # user_agent = "Mo1zilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) Gecko/20100101 Firefox/108.0"
        headers = {"authority": authority, "method": method, "path": path, "shema": shema,
                   "accept": accept, "accept-encoding": accept_encoding, "accept-language": accept_language,
                   "content-type": content_type, "content-length": content_length,
                   "dnt": dnt, "origin": origin, "referer": referer, "sec-ch-ua": sec_ch_ua,
                   "sec-ch-ua-mo    bile": sec_ch_ua_mobile, "sec-ch-ua-platform": sec_ch_ua_platform,
                   "sec-fetch-dest": sec_fetch_dest, "sec-fetch-mode": sec_fetch_mode,
                   "sec-fetch-site": sec_fetch_site,
                   "x-csrf-tokrn": x_csrf_token,
                   "user-agent": user_agent,
                   "x-requested-with": x_requested_with

                   }

        return headers

    def anzeige_abschicken(self):
        session = requests.Session()
        response = session.post(self.url, headers=self.headers,
                                cookies=self.cookies, data=self.form_data)

        print("URL = " + self.url + "\n\n")
        print("StatusCode = " + str(response.status_code))
        print("encoding  = " + response.encoding)
        print("printing response header")
        for key, value in response.headers.items():
            print(key, value)
        print(response.text)
        html_text = response.text

        f = open("result.html", "w", encoding='utf-8')
        f.write(html_text)
        f.close()

        pass


def get_form_data_for_msg():
    add_id = "2382113222"
    msg_body = dict(message="hallo, wie viel kostet es",
                    adId=add_id,
                    adType="private",
                    contactName="Zakir")

    return msg_body


if __name__ == "__main__":
    body = get_form_data_for_msg()

    url1 = "https://www.ebay-kleinanzeigen.de/m-access-token.json"
    url2 = "https://gateway.ebay-kleinanzeigen.de/user-trust/users/current/verifications/phone/required?action=POST_MESSAGE&source=DESKTOP"
    url3 = "https://www.ebay-kleinanzeigen.de/s-anbieter-kontaktieren.json"
    api = Main(mode="server", log=True, )

    api.make_request(url=url1, log=True)
    if api.login:
        print("printing ")
        print(api.html_text)
        print(api.json_obj)
    auth = api.response.headers.get("Authorization")
    print(auth)
    print("\n\n\n")


    api.headers['Authorization'] = auth
    api.make_request(url=url2, log=True)
    if api.login:
        print("printing ")
        print(api.html_text)
        print(api.json_obj)
    print("\n\n\n")

    api.headers['Authorization'] = auth
    api.headers['x-csrf-token'] = api.cookies.request_cookies['CSRF-TOKEN']
    print("x-csrf-token :",api.headers['x-csrf-token'])
    api.make_request(type="json", method="post", url=url3, log=True, body=body)
    if api.login:
        print("printing ")
        print(api.html_text)
        print(api.json_obj)
print("\n\n\n")

