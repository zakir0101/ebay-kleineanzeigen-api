import datetime
import json
import time

from main import Main
import pandas as pd
import os
import pprint as p


class AnzeigeAnmelden(Main):
    def __init__(self, filename: str = "default.json", log: bool = True, cookies: dict = None, save=False,
                 mode: str = "client", rotate_ip: bool = False, keep_old_cookies=True, webshare_rotate = False):
        super().__init__(filename, log, cookies, save, mode, keep_old_cookies, rotate_ip,webshare_rotate)
        self.language = ['java', 'python', 'c++', 'c', 'matlab', 'kotlin', 'javascript', 'sql', 'informatik']
        self.myAdd = ["2548972822","2557207555","2516923750","2557039288"]
        if not os.path.exists("report/reported_adds.csv"):
            df = pd.DataFrame(
                columns=['add_link', 'title', 'add_date', 'views', 'location', 'price', 'add_id', 'user_name',
                         "user_type","reported_1","reported_2","reported_3","deleted", 'java',
                         'python', 'c++', 'c', 'matlab', 'kotlin', 'javascript', 'sql', 'informatik'])
            df.to_csv("reported_adds.csv",index=False)
        pass


    def report_adds_from_csv(self):
        df = pd.read_csv("report/reported_adds2.csv")
        not_deleted = df[(df['deleted'] == False) & (df['reported_1'] == False)]
        for index, row in not_deleted.iterrows():
            add_link = row['add_link']
            add_id = str(row['add_id']).strip()
            if add_id not in self.myAdd :
                if row["user_type"].strip() == "Privater Nutzer":
                    self.report_add(add_id, add_link)
                elif row["user_type"].strip() == "Gewerblicher Nutzer":
                    self.report_add(add_id, add_link ,privat = False)
            # df.at[index, "reported_1"] = self.is_reporting_enabled(add_id,add_link)
        df.to_csv("reported_adds2.csv", index=False)

    def mark_reported_add(self):
        df = pd.read_csv("report/reported_adds2.csv")
        not_deleted = df[(df['deleted'] == False)]
        for index, row in not_deleted.iterrows():
            add_link = row['add_link']
            add_id = row['add_id']
            enabled = self.is_reporting_enabled(str(add_id),add_link)
            df.at[index, "reported_1"] = not enabled
        df.to_csv("reported_adds2.csv", index=False)

    def mark_all_undeleted(self):
        df = pd.read_csv("report/reported_adds2.csv")
        for index, row in df.iterrows():
            df.at[index, "deleted"] = False
        df.to_csv("reported_adds2.csv", index=False)

    def mark_deleted_adds(self):
        string =  "Die gewünschte Anzeige ist nicht mehr"
        df = pd.read_csv("report/reported_adds2.csv")
        not_deleted = df[(df['deleted'] == False)]
        for index, row in not_deleted.iterrows():
            add_link = row['add_link']
            try:
                self.get_add_detail(self.ebay_url + add_link[1:])
            except Exception as e:
                pass

            if "DELETED_AD" in self.response.url:
                df.at[index,"deleted"] = True
        df.to_csv("reported_adds2.csv",index=False)

    def merge_adds_to_csv_file(self,adds:list):
        df = pd.read_csv("report/reported_adds2.csv")
        for add in adds:
            id  = int(add.get("add_id"))
            similar = df[(df['add_id'] == int(id))]
            if similar.empty:
                df.loc[len(df)] = add
                # df2 = df._append(add, ignore_index=True)
            else:
                for index , row in similar.iterrows():
                    df.at[index,"deleted"] = False
        df.to_csv("reported_adds2.csv",index=False)

    def load_adds_from_internet(self, keyword=None):
        all_links = set()
        if keyword is None:
            for keyword in self.language:
                links = self.__get_add_link(keyword)
                for link in links:
                    all_links.add(link)

        else:
            all_links = self.__get_add_link(keyword)

        print("links number :",len(all_links))
        all_links = self.__filter_links(all_links)
        print("filterd links number :",len(all_links))
        all_add = None
        all_add = self.__get_add_details_from_links(all_links)

        return all_add

    def __filter_links(self,links):
        df = pd.read_csv("report/reported_adds2.csv")
        not_deleted = df[(df["deleted"] == False)]["add_link"].tolist()
        for link in not_deleted:
            if link.strip() in links:
                links.remove(link.strip())
        return links

    def __get_add_details_from_links(self, links: set):
        all_add = []
        for link in links:
            res = self.get_add_detail(self.ebay_url + link[1:])
            title = res.get("title").lower()

            price = res.get('price').split(" ")[0]
            try:
                date = datetime.datetime.strptime(res.get("date"), '%d.%m.%Y')
                date = date.strftime('%Y-%m-%d')
            except Exception as e:
                date = res.get("date")
            add = {'add_link': link, 'title': res.get('title'), 'add_date': date, 'views': res['views'],
                   'location': res['location'],
                   'price': price, 'add_id': res.get('add_id'),
                   'user_name': res.get('user').get('user_name'), "user_type": res.get('user').get('user_type')
                      , "reported_1":False, "reported_2":False, "reported_3":False, "deleted":False
                , 'java': 'java' in title, 'python': 'python' in title, 'c++': 'c++' in title, 'c': 'c' in title
                , 'matlab': 'matlab' in title, 'kotlin': 'kotlin' in title, 'javascript': 'javascript' in title,
                   'sql': 'sql' in title, 'informatik': 'informatik' in title}
            all_add.append(add)
        return all_add
        pass

    def __get_add_link(self, keyword):
        prefix = self.set_up_url_for_search("nachhilfe " + keyword, "k0", "None")
        url = self.ebay_url + prefix
        res = self.search_for(url)
        add_links: set = set()
        for result in res.get("result"):
            link: str = result.get("url_link")
            if link != "":
                add_links.add(link)
        return add_links

    def set_headers(self, add_id):
        authority = "www.kleinanzeigen.de"
        method = "POST"
        path = "/flags/ads/" + add_id + ".json"
        shema = "https"
        accept = "application/json, text/plain, */*"
        self.headers['accept'] = accept
        accept_encoding = "gzip, deflate, br"
        self.headers['accept-encoding'] = accept_encoding
        accept_language = "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6"
        self.headers['accept-language'] = accept_language
        # cache_control = "max-age=0"
        # self.headers['cache-control'] = cache_control
        # content_type = "application/x-www-form-urlencoded"
        # self.headers['content-type'] = content_type
        dnt = "1"
        self.headers['dnt'] = dnt
        content_type = "application/json"
        self.headers['Content-Types'] = content_type
        origin = "https://www.kleinanzeigen.de"
        self.headers['Origin'] = origin
        # referer = "https://www.ebay-kleinanzeigen.de/p-anzeige-aufgeben-schritt2.html"
        sec_ch_ua = '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"'
        self.headers["sec-ch-ua"] = '"Chromium"' \
                                    ';v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"'
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
        return

    def read_temp_cookies(self):
        file = open("temp.cookies", "r", encoding="utf-8").read()
        temp = dict()
        for cookLine in file.split(";"):
            split = cookLine.split("=")
            temp[split[0].strip()] = split[1].strip()
        return temp

    def is_reporting_enabled(self,add_id,add_link):
        referer = "https://www.kleinanzeigen.de/s-anzeige" + add_link

        url = "https://www.kleinanzeigen.de/flags/ads/" + add_id + "/enabled.json"
        not_enabled = True
        counter = 0
        while not_enabled:
            if counter == 1:
                break
            self.headers["Referer"] = referer
            self.make_request(type="html-json", method="get", url=url)
            if self.json_obj is  None:
                print(self.html_text)
                raise IOError
            elif self.json_obj == True:
                print("enabled")
                not_enabled = False
            else:
                print("not enabled")
                print(self.html_text)
            counter += 1

        return self.json_obj

    def report_add(self, add_id,add_link,privat = True):
        referer = "https://www.kleinanzeigen.de/s-anzeige" + add_link

        url = "https://www.kleinanzeigen.de/flags/ads/reasons.json"
        self.headers["Referer"] = referer
        self.make_request(type="html-json", method="get", url=url)
        # print(self.json_obj)
        if privat:
            data = dict(reasonId="COMMERCIAL", text="")
        else:
            data = dict(reasonId="OFFENSIVE", text="")
        payload = [data]
        if self.log:
            pass
            # print("payload = " , payload)
        url = "https://www.kleinanzeigen.de/flags/ads/" + add_id + ".json"

        self.headers['x-csrf-token'] = self.cookies.request_cookies.get('CSRF-TOKEN')
        self.headers["Referer"] = referer
        self.set_headers(add_id)
        self.make_request(type="html-jsondata", method="post", url=url, body=payload)
        if self.log:
            if 200 <= self.response.status_code < 300:
                print("die Anzeige'" + add_id + "' würde erfolgreich gemeldet")
            else:
                print("die Anzeige'" + add_id + "' könnte leider nicht gemeldet sein")
                # print(self.html_text)


if __name__ == "__main__":
    # api = AnzeigeAnmelden(log=True, mode="server", keep_old_cookies=False, save=True)
    # print("logged in : ", api.login)
    # api.report_add("2549293655","/s-anzeige/informatik-nachhilfe/2549293655-268-3115")
    api = AnzeigeAnmelden(log=True, mode="server", keep_old_cookies=False, save=True)
    print("logged in : ", api.login)
    adds = api.load_adds_from_internet()
    api.merge_adds_to_csv_file(adds)
    pass
