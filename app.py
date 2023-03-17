import traceback
from flask_cors import CORS
from flask import Flask, request, jsonify, render_template
from print_dict import pd

from anzeige_abschicken import AnzeigeAbschickenApi
from main import Main
import json

app = Flask(__name__)
CORS(app)

log = False
cookie_domain = 'ebay-kleinanzeigen-zakir.onrender.com'
app.config['SERVER_NAME'] = 'ebay-kleinanzeigen-zakir.onrender.com'


@app.route('/')
@app.route('/search')
@app.route('/add')
@app.route('/user')
@app.route('/messages')
@app.route('/myadd')
@app.route('/publish')
@app.route('/static/')
@app.route('/static/search')
@app.route('/static/add')
@app.route('/static/user')
@app.route('/static/messages')
@app.route('/static/myadd')
@app.route('/static/publish')
def get_index():
    return render_template("index.html")


@app.route('/islogged')
def is_user_logged():  # put application's code here
    try:

        api = Main(log=log, cookies=request.cookies)
        is_logged = api.login
        user_id = ""
        api.set_xsrf_token()
        api.set_xsrf_token()
        is_logged  = api.is_user_logged_in()
        if is_logged:
            user_id = api.get_user_id()

        res = dict(isLogged=is_logged, user_id=user_id)
        res = api.attach_cookies_to_response(res)
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


@app.route('/main')
def get_main():  # put application's code here
    try:
        print_cookies(request.cookies)
        api = Main(log=log, cookies=request.cookies)
        ads = api.get_main(api.ebay_url)
        res = api.attach_cookies_to_response(ads)
        return res
    except Exception as e:
        return get_error_msg(e, log)


@app.route('/search/<search>/<token>/api')
def search_for(search, token):  # put application's code here
    try:
        path = request.args.get("path")
        api = Main(log=log, cookies=request.cookies)
        prefix = api.set_up_url_for_search(search, token, path)
        url = api.ebay_url + prefix
        add_list = api.search_for(url)
        res = api.attach_cookies_to_response(add_list)
        return res
    except Exception as e:
        return get_error_msg(e, True)


@app.route('/cities/<search>')
def get_cities(search):  # put application's code here
    try:
        url = "https://www.ebay-kleinanzeigen.de/s-ort-empfehlungen.json?query=" + search
        api = Main(log=log, cookies=request.cookies)
        ads = api.get_cities(url)
        if log:
            print("city number found = " + len(ads).__str__())
        return api.attach_cookies_to_response(ads)

    except Exception as e:
        return get_error_msg(e, log)


@app.route('/categories')
def get_categories():  # put application's code here
    try:
        api = Main(log=log, cookies=request.cookies)
        url = api.ebay_url
        ads = api.get_categories(url)
        return api.attach_cookies_to_response(ads)
    except Exception as e:
        return get_error_msg(e, log)


@app.route('/add/api')
def get_add_page():  # put application's code here
    try:
        add_link = request.args.get("link")[1:]
        api = Main(log=log, cookies=request.cookies)
        url = api.ebay_url + add_link
        add_detail = api.get_add_detail(url)
        res = api.attach_cookies_to_response(add_detail)
        return res
    except Exception as e:
        return get_error_msg(e, log)


@app.route('/user/api')
def get_user_page():  # put application's code here
    try:
        user_link = request.args.get("link")[1:]
        api = Main(log=log, cookies=request.cookies)
        url = api.ebay_url + user_link
        user_detail = api.get_user_detail(url)
        res = api.attach_cookies_to_response(user_detail)
        return res
    except Exception as e:
        return get_error_msg(e, log)


@app.route('/send/addpage')
def send_message():  # put application's code here
    try:
        api = Main(log=False, cookies=request.cookies)
        args = request.args
        api.send_message_from_add_page(args.get("message"), args.get("add_id"),
                                       args.get('add_type'), args.get("contact_name"))
        res: dict | None
        if json.loads(api.html_text):
            res = api.json_obj
        else:
            res = dict(msg=api.html_text, type="Error")
        res = api.attach_cookies_to_response(res)
        return res
    except Exception as e:
        return get_error_msg(e, log)


@app.route('/send/messagebox')
def send_message2():  # put application's code here
    try:
        api = Main(log=False, cookies=request.cookies)
        args = request.args
        api.send_message_from_message_box(args.get("message"), args.get("user_id"),
                                          args.get('conversation_id'))

        res = dict(msg=api.html_text, status="OK")
        res = api.attach_cookies_to_response(res)
        return res
    except Exception as e:
        return get_error_msg(e, log)


@app.route('/conversations')
def get_conversation():  # put application's code here
    try:
        args = request.args
        api = Main(log=log, cookies=request.cookies)
        conversation_page = api.get_conversations(args.get("user_id"), args.get("page"), args.get("size"), )
        res = api.attach_cookies_to_response(conversation_page)
        return res
    except Exception as e:
        return get_error_msg(e, log)


@app.route('/messages/api')
def get_messages():  # put application's code here
    try:
        args = request.args
        api = Main(log=log, cookies=request.cookies)
        messages_list = api.get_messages(args.get("user_id"), args.get("conversation_id"))
        res = api.attach_cookies_to_response(messages_list)
        return res
    except Exception as e:
        return get_error_msg(e, log)


@app.route('/publish/api')
def publish_add():  # put application's code here
    try:
        args = request.args
        print("argument :")
        pd(args.to_dict())
        api = AnzeigeAbschickenApi(log=log, cookies=request.cookies)

        adid = api.anzeige_abschicken(args.get('title'), args.get('price'),
                                      args.get('zip'), args.get('city_code'),
                                      args.get('description'), args.get('contact_name'))

        res = dict()
        if adid:
            res = dict(state="OK", add_id=adid)
            print("Add-id is :", adid)
        else:
            res = dict(state="ERROR", html=api.html_text)
            f = open("result.html", "w", encoding="utf-8")
            f.write(api.html_text)
        res = api.attach_cookies_to_response(res)
        return res
    except Exception as e:
        return get_error_msg(e, log)


@app.route('/check/add')
def check_add():  # put application's code here
    try:
        args = request.args
        api = AnzeigeAbschickenApi(log=log, cookies=request.cookies)
        check = api.check_add_state(args.get("add_id"))
        res = api.attach_cookies_to_response(check)

        return res
    except Exception as e:
        return get_error_msg(e, log)


@app.route('/cities/zip')
def get_cities_by_zip():  # put application's code here
    try:
        args = request.args
        api = AnzeigeAbschickenApi(log=log, cookies=request.cookies)
        cities = api.get_location_by_zip(args.get("zip"))
        res = api.attach_cookies_to_response(cities)
        return res
    except Exception as e:
        return get_error_msg(e, log)


# @app.route('/<path:any_path1>')
# @app.route('/static/<path:any_path2>')

def get_error_msg(e, log=False):
    traceback.print_exc()
    res = dict()
    res['type'] = "Error"
    res['msg'] = e.__str__()
    if log:
        print("error" + e.__str__())
    res = jsonify(res)
    res.headers.add('Access-Control-Allow-Credentials', 'true')
    return res
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


def print_cookies(cookies):
    print("recieved cookies")
    for name, value in cookies.items():
        print(name + " : " + value[:10])


if __name__ == '__main__':
    app.run()
