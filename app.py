from flask_cors import CORS
from flask import Flask

from main import EbayKleineanzeigenApi
import json

app = Flask(__name__)
CORS(app)


@app.route('/galerie')
def get_galerie():  # put application's code here
    try:
        api = EbayKleineanzeigenApi("")
        # ads = api.get_ads(min_price="100")
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
        api = EbayKleineanzeigenApi("")
        ads = api.get_main()
        return json.dumps(ads)
    except Exception as e:
        res = dict()
        res['type'] = "Error"
        res['msg'] = e
        return json.dumps(res)


@app.route('/search/<search>/<token>')
def search_for(search, token):  # put application's code here
    try:
        api = EbayKleineanzeigenApi("")

    except Exception as e:
        res = dict(type="Error", msg=e.__str__())
        return json.dumps(res)
    else:
        add_list = api.search_for(search, token)
        # api.print_anzeigen(add_list)
        return json.dumps(add_list)

@app.route('/cities/<search>')
def get_cities(search):  # put application's code here
    try:
        api = EbayKleineanzeigenApi("")
        ads = api.get_cities(search=search)
        return json.dumps(ads)
    except Exception as e:
        res = dict()
        res['type'] = "Error"
        res['msg'] = e
        return json.dumps(res)


@app.route('/categories')
def get_categories():  # put application's code here
    try:
        api = EbayKleineanzeigenApi("")
        ads = api.get_categories()
        return json.dumps(ads)
    except Exception as e:
        res = dict()
        res['type'] = "Error"
        res['msg'] = e
        return json.dumps(res)


if __name__ == '__main__':
    app.run()
