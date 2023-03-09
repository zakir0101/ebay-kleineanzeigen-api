import traceback

from flask_cors import CORS
from flask import Flask, request, jsonify
from main import EbayKleineanzeigenApi
import json




app = Flask(__name__)
CORS(app)

log = False
cookie_domain = 'ebay-kleinanzeigen-zakir.de'
app.config['SERVER_NAME'] = 'ebay-kleinanzeigen-zakir.de:5000'


@app.route('/main')
def get_main():  # put application's code here
    try:
        api = EbayKleineanzeigenApi(log=True, cookies=request.cookies)
        ads = api.get_main()

        res = create_responce_from_dict(ads, api)
        return res
    except Exception as e:
        get_error_msg(e, log)


@app.route('/islogged')
def is_user_logged():  # put application's code here
    try:
        api = EbayKleineanzeigenApi(log=log, cookies=request.cookies)
        is_logged = api.check_cookies()
        res = dict(isLogged=is_logged)
        res = create_responce_from_dict(res, api)
        return res
    except Exception as e:
        return get_error_msg(e, log)


@app.route('/logout')
def logout():  # put application's code here
    try:
        res = dict(isLogged=False)
        res = clear_cookies(res, request.cookies)
        return res
    except Exception as e:
        return get_error_msg(e, log)


def print_cookies(cookies):
    print("recieved cookies")
    for name, value in cookies.items():
        print(name + " : " + value[:10])


@app.route('/search/<search>/<token>')
def search_for(search, token):  # put application's code here
    try:
        path = request.args.get("path")
        prefix = set_up_url_for_search(search, token, path)
        api = EbayKleineanzeigenApi(url_prefix=prefix, log=True, cookies=request.cookies)
        add_list = api.search_for()
        res = create_responce_from_dict(add_list, api)
        return res
    except Exception as e:
        return get_error_msg(e, True)


@app.route('/add')
def get_add_page():  # put application's code here
    try:
        add_link = request.args.get("link")[1:]
        api = EbayKleineanzeigenApi(url_prefix=add_link, log=True, cookies=request.cookies)
        add_detail = api.get_add_detail()
        res = create_responce_from_dict(add_detail, api)
        return res
    except Exception as e:
        return get_error_msg(e, log)


@app.route('/user')
def get_user_page():  # put application's code here
    try:
        user_link = request.args.get("link")[1:]
        api = EbayKleineanzeigenApi(url_prefix=user_link, log=True, cookies=request.cookies)
        user_detail = api.get_user_detail()
        res = create_responce_from_dict(user_detail, api)
        return res
    except Exception as e:
        return get_error_msg(e,log)


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
        api = EbayKleineanzeigenApi(url_prefix=search, type="json", log=log, cookies=request.cookies)
        ads = api.get_cities()
        print("city number found = " + len(ads).__str__())
        return create_responce_from_dict(ads, api)

    except Exception as e:
        return get_error_msg(e, log)


@app.route('/categories')
def get_categories():  # put application's code here
    try:
        api = EbayKleineanzeigenApi(log=log, cookies=request.cookies)
        ads = api.get_categories()
        res = create_responce_from_dict(ads, api)
        return res
    except Exception as e:
        return get_error_msg(e, log)


def get_error_msg(e, log=False):
    traceback.print_exc()
    res = dict()
    res['type'] = "Error"
    res['msg'] = e.__str__()
    if log:
        print("error" + e.__str__())
    return json.dumps(res)
    pass


def clear_cookies(ads: dict, cookies: dict):
    res = jsonify(ads)
    for name, value in cookies.items():
        expires = 850694400
        res.set_cookie(key=name, value=value,
                       expires=expires, path="/",
                       domain=cookie_domain)
        # print(cook['name']+"   "+cook['domain'])
        print(name + " was expired")
    res.headers.add('Access-Control-Allow-Credentials', 'true')
    return res


def create_responce_from_dict(ads: dict, api: EbayKleineanzeigenApi):
    res = jsonify(ads)
    for cook in api.googleChromeCookie:
        if cook.get('expirationDate'):
            expires = cook['expirationDate']
            res.set_cookie(key=cook['name'], value=cook['value'],
                           expires=cook['expirationDate'], path=cook['path'],
                           domain=api.cookie_domain)
        # print(cook['name']+"   "+cook['domain'])
        res.headers.add('Access-Control-Allow-Credentials', 'true')
    return res


if __name__ == '__main__':
    app.run()
