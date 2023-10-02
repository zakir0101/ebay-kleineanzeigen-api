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
                    if cook1.get('expirationDate'):
                        print("expirationDate : ",
                              datetime.fromtimestamp(cook1['expirationDate']).strftime('%d-%m-%y-%H:%M'))

                    print("value 2 : " + cook2['value'])
                    if cook2.get('expirationDate'):
                        print("expirationDate : ",
                              datetime.fromtimestamp(cook2.get('expirationDate')).strftime('%d-%m-%y-%H:%M'))
                    print("\n\n\n")


def expirationDate():
    index = 0
    for cook2 in cookies1:

        if cook2.get('expirationDate'):
            rem = int(cook2.get('expirationDate')) - time.time()

            if rem < 2*60*60:
                index += 1
                print("name " + str(index) + " : " + cook2['name'])
                hour = timedelta(seconds=rem)
                print ("remaining time : " +str( hour ))
                print("expirationDate : ", datetime.fromtimestamp(cook2['expirationDate']).strftime('%d-%m-%y-%H:%M'))
                print("now  = " + datetime.now().strftime('%d-%m-%y-%H:%M'))
                print("\n\n\n")

        else:
            index += 1
            print("name " + str(index) + " : " + cook2['name'])

            print("no expiration date avaiolable" )

            print("\n\n\n")


# expirationDate()
def find_csrf_token():
    for cook in cookies2:
        if cook["session"]:
            print(cook['name'])
    pass


compare()