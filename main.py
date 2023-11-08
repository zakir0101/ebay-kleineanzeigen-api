import json
import time
from datetime import datetime
from print_dict import pd, print_dict
from ebay_kleinanzeigen_api import EbayKleinanzeigenApi


class Main(EbayKleinanzeigenApi):
    def __init__(self, filename: str = "default.json", log: bool = True, cookies: dict = None, save=False,
                 mode: str = "client",rotate_ip : bool = False,keep_old_cookies=True,webshare_rotate=False):
        # Test for custom configs
        super().__init__(filename, log, cookies, save, mode,keep_old_cookies,rotate_ip,webshare_rotate)

        self.days_of_week = ['Mon', 'Die', 'Mit', 'Don', 'Fri', 'Sam', 'Son']
    def search_for(self, url):
        self.make_request(type="extractor", method="get", url=url)
        return self.extractor.parse(path="Extractor/", filename="SearchWindow.json")

    def set_up_url_for_search(self, search, token, path) -> str:
        prefix = ""
        if path == "None":
            if search == "None" and token == "None":
                prefix += "s-suchen.html"
            elif search == "None" and token != "None":
                prefix += token
            else:
                prefix += search + "/" + token
        else:
            if search == "None" and token == "None":
                prefix += path
            elif search == "None" and token != "None":
                prefix += path + token
            else:
                prefix += path + search + "/" + token

        return prefix

    def get_main(self, url):
        self.make_request(url=url, method="get", type="extractor")
        main_page = self.extractor.parse("Extractor/", "MainWindow.json")
        return main_page

    def get_categories(self, url):
        self.make_request(url=url, method="get", type="extractor")
        cat_lst = self.extractor.parse("Extractor/", "Categories.json")
        return cat_lst

    def get_categories2(self):
        url = self.ebay_url+"api/categories/v1"
        self.set_bearer_token()
        self.set_xsrf_token()
        self.make_request(url=url, method="get", type="html")
        categories = self.html_text
        return categories

    def get_add_detail(self, url):
        self.make_request(url=url, type="extractor", method="get")
        add_page = self.extractor.parse(path="Extractor/", filename="AddWindow.json")
        # add_page['views'] = self.get_add_views(add_page['add_id'], log=self.log)
        add_page['views'] = None
        return add_page

    def get_user_detail(self, url):
        self.make_request(url=url, type="extractor", method="get")
        user_page = self.extractor.parse(path="Extractor/", filename="UserWindow.json")
        return user_page

    def get_setting_page(self):
        url = self.ebay_url + "m-einstellungen.html"
        self.make_request(url=url, type="extractor", method="get")
        user_page = self.extractor.parse(path="Extractor/", filename="Setting.json")
        user_page['add_num_online'] = user_page['add_num_online'].replace('Mein',"").replace("Konto","")
        return user_page

    def get_add_views(self, add_id, log):
        url = self.ebay_url + "s-vac-inc-get.json?adId=" + add_id
        self.make_request(url=url, method="get", type="html-json")
        if self.json_obj:
            return self.json_obj.get('numVisits')
        else:
            return None

    def try_hard_get_add_views(self,add_id,log):
        views = 0
        if self.log:
            print("trying to get views")
        for x in range(len(self.proxies)):
            error = False
            self.active_proxy = self.proxies[x]
            if self.log:
                print("trying with :", self.active_proxy['country'], self.active_proxy['proxy'])

            views = self.get_add_views(add_id,log)
            if views is not None:
                if self.log:
                    print("operation done successfully")
                return views
        return None


    def get_conversations(self, user_id, page:str, size:str="10"):
        if not user_id:
            user_id = self.get_user_id()
        url = "https://gateway.ebay-kleinanzeigen.de/messagebox/api/users/" + \
              user_id.__str__() + "/conversations?page=" + page.__str__() + "&size=" + size
        self.set_bearer_token()
        self.make_request(type="json", method="get", url=url)
        json_object = self.json_obj
        if json_object is None:
            return None
        json_object["lastModified"] = self.get_time_readable(json_object['lastModified'])
        for conv in json_object.get("conversations"):
            conv["receivedDate"] = self.get_time_readable(conv["receivedDate"])
        return self.json_obj

    def send_message_from_add_page(self, message, add_id, add_type, contact_name):
        self.set_xsrf_token()
        body = dict(message=message,
                    adId=add_id,
                    adType=add_type,
                    contactName=contact_name)
        # self.headers["content-type"] = "application/json"
        url = "https://www.ebay-kleinanzeigen.de/s-anbieter-kontaktieren.json"
        self.make_request(type="html_json", method="post", url=url, body=body)
        if self.log:
            print("printing send message result")
            print(self.html_text.encode("utf-8"))
            print("\n\n\n")


    def send_message_from_message_box(self, message, user_id, conversation_id):
        if not user_id:
            user_id = self.get_user_id()
        self.set_bearer_token()
        self.set_xsrf_token()
        self.headers["x-ecg-user-agent"] = "messagebox-1"
        self.headers["content-type"] = "application/json"
        self.headers["accept-language"] = "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6"

        body = dict(message=message)
        print( " message is = ",message )
        print("pody is")
        pd( body )
        url = "https://gateway.ebay-kleinanzeigen.de/messagebox/api/users/"+user_id\
              +"/conversations/"+conversation_id+"?warnPhoneNumber=false&warnEmail=false&warnBankDetails=false"
        self.make_request(type="jsondata_json_html", method="post", url=url, body=body)
        if self.log:
            print("printing send message from message Box")
            print(self.html_text)
            print("\n\n\n")

    def get_messages(self, user_id, conversation_id):
        if not user_id:
            user_id = self.get_user_id()
        url = "https://gateway.ebay-kleinanzeigen.de/messagebox/api/users/" + \
              user_id + "/conversations/" + conversation_id + "?contentWarnings=true"
        self.set_bearer_token()
        self.make_request(type="json", method="get", url=url)
        for msg in self.json_obj.get('messages'):
            msg['readableDate'] = self.get_time_readable(msg.get('receivedDate'))
        return self.json_obj



    def get_time_readable(self,time_str):
        try:
            time_obj = time.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f+0100")
        except Exception as e:
            time_obj = time.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f+0200")
        my_datetime = datetime(time_obj.tm_year, time_obj.tm_mon,
                               time_obj.tm_mday, time_obj.tm_hour,
                               time_obj.tm_min, time_obj.tm_sec)

        epoch = my_datetime.timestamp()
        now = time.time()
        a_day = 24 * 60 * 60
        day_morning = datetime(time_obj.tm_year, time_obj.tm_mon,
                               time_obj.tm_mday, 0,
                               0, 0).timestamp()

        if (now - day_morning) < a_day:
            return "Heute"+my_datetime.strftime(' %H:%M')
        elif (now - day_morning) < 2 * a_day:
            return "Gersten" + my_datetime.strftime(' %H:%M')
        elif (now - day_morning) < a_day * 7:
            return 'letzte ' + self.days_of_week[time_obj.tm_wday]+my_datetime.strftime(' %H:%M')
        else:
            return my_datetime.strftime('%d-%b-%y %H:%M')

        pass


if __name__ == '__main__':
    id = 1
    api = Main(log=True, mode="server", filename="Cookies/adnan.json", keep_old_cookies=False,                               save=True, webshare_rotate=False)
    if api.login:
        user_id = api.get_user_id()
        conversation_id = "dq1r:2pc1q4v:2knzkfc9x"
        api.send_message_from_message_box("hey, gerne helfe ich dir",user_id,conversation_id)

        # conver = api.get_conversations(user_id,"0","10")
        # messages = api.get_messages(user_id,conve_id)
        #
        #
        # open("testing/conversations.json","w",encoding="utf-8").write(json.dumps(conver,ensure_ascii=False))
        # open("testing/messages.json", "w", encoding="utf-8").write(json.dumps(messages, ensure_ascii=False))