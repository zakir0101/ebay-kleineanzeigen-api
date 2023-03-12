from print_dict import pd
from ebay_kleinanzeigen_api import EbayKleinanzeigenApi


class Main(EbayKleinanzeigenApi):
    def __init__(self, filename: str = "default.json", log: bool = True, cookies: dict = None, save=False,
                 mode: str = "client"):
        # Test for custom configs
        super().__init__(filename, log, cookies, save, mode)

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

    def get_cities(self, url):
        self.make_request(url=url, type="json", method="get")
        cities_list = []
        for code, name in self.json_obj.items():
            city = dict(code=code[1:], name=name)
            cities_list.append(city)

        return cities_list

    def get_main(self, url):
        self.make_request(url=url, method="get", type="extractor")
        main_page = self.extractor.parse("Extractor/", "MainWindow.json")
        return main_page

    def get_categories(self, url):
        self.make_request(url=url, method="get", type="extractor")
        cat_lst = self.extractor.parse("Extractor/", "Categories.json")
        return cat_lst

    def get_add_detail(self, url):
        self.make_request(url=url, type="extractor", method="get")
        add_page = self.extractor.parse(path="Extractor/", filename="AddWindow.json")
        add_page['views'] = self.get_add_views(add_page['add_id'], log=self.log)
        return add_page

    def get_user_detail(self, url):
        self.make_request(url=url, type="extractor", method="get")
        user_page = self.extractor.parse(path="Extractor/", filename="UserWindow.json")
        return user_page

    def get_add_views(self, add_id, log):
        url = self.ebay_url + "s-vac-inc-get.json?adId=" + add_id
        self.make_request(url=url, method="get", type="json")
        return self.json_obj.get('numVisits')

    def get_conversations(self,user_id,  page , size = 10):
        if not user_id:
            user_id = self.get_user_id()
        url = "https://gateway.ebay-kleinanzeigen.de/messagebox/api/users/" + \
              user_id + "/conversations?page=" + page + "&size=" + size
        self.set_bearer_token()
        self.make_request(type="json", method="get", url=url)
        return self.json_obj

    def send_message(self, message, add_id, add_type, contact_name):
        self.set_xsrf_token()
        body = dict(message=message,
                    adId=add_id,
                    adType=add_type,
                    contactName=contact_name)
        url = "https://www.ebay-kleinanzeigen.de/s-anbieter-kontaktieren.json"
        self.make_request(type="json_html", method="post", url=url, body=body)
        if self.log:
            print("printing send message result")
            print(self.html_text)
            print("\n\n\n")

    pass


if __name__ == "__main__":
    api = Main(log=True , mode="server")
    conversation = api.get_conversations("","0","100")
    pd(len(conversation.get('conversations')))
    pass
