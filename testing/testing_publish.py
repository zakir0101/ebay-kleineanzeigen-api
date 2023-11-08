import glob

import requests

# res = requests.get("http://publish-zakir.onrender.com/publish/saleem/nachhilfe")
# # res = requests.get("http://publish-zakir.onrender.com/main")
# print(res.json())

files = glob.glob("../Cookies/*.json")
print(files)