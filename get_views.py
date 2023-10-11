import time

from main import Main

def get_header():
    headers = dict()
    accept = "application/json, text/plain, */*"
    headers['Accept'] = accept
    accept_encoding = "gzip, deflate, br"
    headers['Accept-Encoding'] = accept_encoding
    accept_language = "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6"
    headers['Accept-Language'] = accept_language

    dnt = "1"
    headers['Dnt'] = dnt
    referer = "https://www.kleinanzeigen.de/s-anzeige/python-java-sql-help-and-support-from-computer-engineer/2557207555-268-6443"
    headers['Referer'] = referer
    sec_ch_ua = '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"'
    headers["Sec-Ch-Ua"] = sec_ch_ua
    sec_ch_ua_mobile = "?0"
    headers["Sec-Ch-Ua-Mobile"] = sec_ch_ua_mobile
    sec_ch_ua_platform = '"Windows"'
    headers["Sec-Ch-Ua-Platform"] = sec_ch_ua_platform
    sec_fetch_dest = "empty"
    headers['Sec-Fetch-Dest'] = sec_fetch_dest
    sec_fetch_mode = "cors"
    headers['Sec-Fetch-Mode'] = sec_fetch_mode

    sec_fetch_site = "same-origin"
    headers['Sec-Fetch-Site'] = sec_fetch_site
    # sec_fetch_user = "?1"
    upgrade_insecure_requests = "1"
    headers['Upgrade-Insecure-Requests'] = upgrade_insecure_requests
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                 "Chrome/110.0.0.0 Safari/537.36 "
    headers['User-Agent'] = user_agent
    headers['X-Requested-With'] = "XMLHttpRequest"
    return headers

    pass

def getCookies():
    return {
        "CSRF-TOKEN" : "lsdfjdls"
    }



add_id = "2557207555"
counter = 0
for i in range(1):
    print(f"******************* {i} *********************")
    api = Main(log=True,filename="default2.json",save=True,mode="server",webshare_rotate=False)
    # api.cookies.remove_specific_cookies()
    api.headers = get_header()
    add_detail = api.get_add_views(add_id, True)
    if add_detail is not  None:
        counter += 1
    # try:
    #     add_detail = api.try_hard_get_add_views(add_id,True)
    # except Exception:
    #     add_detail = api.html_text
    print(add_detail)
    print(api.html_text)
    api.cookies.request_cookies = dict()
    api.cookies.googleChromeCookie = []
    api.cookies.save_cookies()
    time.sleep(2)


print("numb of views =",counter)