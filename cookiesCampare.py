import json
from datetime import datetime
import time

from future.backports.datetime import timedelta

with open('default.json', 'r') as f:
    cookies1 = json.load(f)
    print("Loading default config")

with open('default2.json', 'r') as f:
    cookies2 = json.load(f)
    print("Loading default config")


def compare():
    for cook1 in cookies1:
        for cook2 in cookies2:
            if cook1['name'] == cook2['name']:
                if cook1['value'] != cook2['value']:
                    print(cook1['name'] + " is diffrent")
                    print("value 1 : " + cook1['value'])
                    if cook1['expires']:
                        print("expirationDate : ",
                              datetime.fromtimestamp(cook1['expires']).strftime('%d-%m-%y-%H:%M'))

                    print("value 2 : " + cook2['value'])
                    if cook2['expirationDate']:
                        print("expirationDate : ",
                              datetime.fromtimestamp(cook2['expirationDate']).strftime('%d-%m-%y-%H:%M'))
                    print("\n\n\n")


def expirationDate():
    index = 0
    for cook2 in cookies1:

        if cook2.get('expirationDate'):
            rem = int(cook2.get('expirationDate')) - time.time()

            if rem < 24*60*60:
                index += 1
                print("name " + str(index) + " : " + cook2['name'])
                hour = timedelta(seconds=rem)
                print ("remaining time : " +str( hour ))
                print("expirationDate : ", datetime.fromtimestamp(cook2['expirationDate']).strftime('%d-%m-%y-%H:%M'))
                print("\n\n\n")

        else:
            index += 1
            print("name " + str(index) + " : " + cook2['name'])

            print("no expiration date avaiolable" )

            print("\n\n\n")


expirationDate()










'''

set-cookie: bm_sv=8B5D1182E9AF1B6E637C16BB70C5420B~YAAQjSV+aOI5LYuGAQAAWqI7qBJng5louHZ2L96mEmtt0wy/YaTITkc1q
aGgpHkaai0seQt4GMRjiC02f1o7RVD97bMqhxjTPhgxBw5JSxK+m3XOB60elWXFLeA7vpiaWKBmrOI+h6ni7KZAtMCd+z
BbLKJM/3o1f1bVnYyPrWPoeWi/UAQpcEBCmalVdC6uBA7cIkaxYRw5l9Bro4woS0t71UXGJbsE1JtkARMqYe4UItp8Q4bdK/gHYQx
KXwdLkFxFg0A3dv7Fzys=~1; Domain=.ebay-kleinanzeigen.de; Path=/; Expires=Fri, 03 Mar 2023 17:51:10 GMT;
 Max-Age=6145; Secure



'''
