import json
import os

import requests
import tqdm as tqdm
from pexels_api import API
from pexels_api.tools import Photo

API_Key = "V6Jf2PHBA1T8VuoqbVQIYzj5L8klpclR8PK8WQGp4PdPnJrCEve8mz49"
api = API(API_Key)

photos = []
for i in range(1):
    api.search('Coding Monitor',page=(i+1),results_per_page=80)
    photos.extend(api.get_entries())
output = dict()
for photo in photos:
    photo : Photo = photo
    output[photo.id.__str__()] = vars(photo)['_Photo__photo']

open("coding_fotos.json","w").write(json.dumps(output))

RESOLUTION = "small"
for val in tqdm.tqdm(output.values()):
    url = val['src'][RESOLUTION]
    fname = os.path.basename(val['src']['original'])
    image_path = os.path.join("pexels", fname)
    if not os.path.isfile(image_path):
        response = requests.get(url, stream=True)
        with open(image_path, 'wb') as outfile:
            outfile.write(response.content)
    else:
        # ignore if already downloaded
        print(f"File {image_path} exists")