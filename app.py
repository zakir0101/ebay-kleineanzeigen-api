from flask_cors import CORS
from flask import Flask, request, jsonify

from main import EbayKleineanzeigenApi
import json

app = Flask(__name__)
CORS(app)

log = False
app.config['SERVER_NAME'] = 'ebay-kleinanzeigen-zakir.de:5000'

@app.route('/galerie')
def get_galerie():  # put application's code here
    try:
        api = EbayKleineanzeigenApi(log=log)
        ads = api.get_galerie()
        return json.dumps(ads)
    except Exception as e:
        res = dict()
        res['type'] = "Error"
        res['msg'] = e
        return json.dumps(res)


@app.route('/main')
def get_main():  # put application's code here
    try:
        api = EbayKleineanzeigenApi(log=True)
        ads = api.get_main()
        res = create_responce_from_dict(ads,api)
        res.headers.add('Access-Control-Allow-Credentials', 'true')

        return res
    except Exception as e:
        res = dict()
        res['type'] = "Error"
        res['msg'] = e
        return json.dumps(res)


@app.route('/islogged')
def is_user_logged():  # put application's code here
    try:
        api = EbayKleineanzeigenApi(log=log)
        is_logged = api.check_cookies()
        res = dict(isLogged=is_logged)
        return json.dumps(res)
    except Exception as e:
        res = dict()
        res['type'] = "Error"
        res['msg'] = e
        return json.dumps(res)


@app.route('/login')
def login():  # put application's code here
    try:
        api = EbayKleineanzeigenApi(log=log)
        is_logged = api.check_cookies()
        res = dict(isLogged=is_logged)
        return json.dumps(res)
    except Exception as e:
        res = dict()
        res['type'] = "Error"
        res['msg'] = e
        return json.dumps(res)


@app.route('/search/<search>/<token>')
def search_for(search, token):  # put application's code here
    try:
        path = request.args.get("path")
        prefix = set_up_url_for_search(search, token, path)
        api = EbayKleineanzeigenApi(url_prefix=prefix, log=log)
        add_list = api.search_for()
        return json.dumps(add_list)
    except Exception as e:
        res = dict(type="Error", msg=e.__str__())
        return json.dumps(res)


def set_up_url_for_search(search, token, path) -> str:
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


@app.route('/cities/<search>')
def get_cities(search):  # put application's code here
    try:
        api = EbayKleineanzeigenApi(url_prefix= search,type= "json", log=log)
        ads = api.get_cities()
        return json.dumps(ads)
    except Exception as e:
        res = dict()
        res['type'] = "Error"
        res['msg'] = e
        return json.dumps(res)


@app.route('/categories')
def get_categories():  # put application's code here
    try:
        api = EbayKleineanzeigenApi(log=log)
        ads = api.get_categories()
        return json.dumps(ads)
    except Exception as e:
        res = dict()
        res['type'] = "Error"
        res['msg'] = e
        return json.dumps(res)



def create_responce_from_dict(ads:dict ,api:EbayKleineanzeigenApi):
    res = jsonify(ads)
    for cook in api.googleChromeCookie:
        if cook.get('expirationDate'):
            expires = cook['expirationDate']
        elif cook.get['expires']:
            expires = cook['expires']
        print(cook['name']+" : "+cook['value'][:30])
        res.set_cookie(key= cook['name'],value= cook['value'][:30],
                       expires=expires,path=cook['path'],domain=cook['domain'])

    return res

if __name__ == '__main__':
    app.run()
