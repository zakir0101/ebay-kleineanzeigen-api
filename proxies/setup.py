import json

import requests


def prepair_proxies():
    zakir1996_link = "https://proxy.webshare.io/api/v2/proxy/list/download/wwgxjjciahsxutqnrpaodcooxmwivbrgsmbpwbsr/-/any/username/direct/-/"
    zakir_elkheir = "https://proxy.webshare.io/api/v2/proxy/list/download/xeqhkzlgfuzemzoyvizizlvdnrhtoxwemgfgssal/-/any/username/direct/-/"
    adnan_link = "https://proxy.webshare.io/api/v2/proxy/list/download/flgurmocunyqhwsjgfeoojgeirczemcxmrlaglix/-/any/username/direct/-/"
    ahmed_tita_link = "https://proxy.webshare.io/api/v2/proxy/list/download/gwtupjzvgnuqxchyhoqiizmbropovvpniqxewrlu/-/any/username/direct/-/"
    saleem_abd_link = "https://proxy.webshare.io/api/v2/proxy/list/download/wmypmxbysjagflzpkwhgsooyccjqhtpaujclzzsd/-/any/username/direct/-/"
    saleem_omer_link = "https://proxy.webshare.io/api/v2/proxy/list/download/njsxdevopvnjuutgnutwdvztlhfeuqjfifxwxzji/-/any/username/direct/-/"

    all_links = [zakir1996_link, zakir_elkheir, adnan_link, ahmed_tita_link, saleem_abd_link, saleem_omer_link]
    proxy_list = []
    for link in all_links:
        if link == "":
            continue
        text = requests.get(link).text
        lines = text.split("\n")
        for line in lines:
            token = line.strip().split(":")
            if len(token) < 4:
                continue
            ip = token[0].strip()
            port = token[1].strip()
            user = token[2].strip()
            password = token[3].strip()
            proxy_link = f"http://{user}:{password}@{ip}:{port}"
            print(proxy_link)
            proxy = {"http" : proxy_link, "https" : proxy_link}
            proxy_list.append(proxy)
    print("number of proxies added = ",len(proxy_list ))
    open("all_proxies.json","w").write(json.dumps(proxy_list))

if __name__ == '__main__':
    prepair_proxies()