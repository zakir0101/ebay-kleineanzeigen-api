import json
import os
from pathlib import Path

import requests


class Base:
    def __init__(self, telegram_api_url, bot_token, user_state, chat_id):
        self.TELEGRAM_API_URL = telegram_api_url
        self.TELEGRAM_TOKEN = bot_token
        self.user_state: dict = user_state
        self.chat_id = chat_id
        self.MODE_PUBLISH = "publish"
        self.MODE_AD_FILE = "adds"
        self.MODE_IMAGE_FILE = "image_files"
        self.MODE_MESSAGES = "messages"
        self.settings = ["webshare_rotate"]

    def send_message(self, text, reply_markup=None):
        """
        Sends a message to the user on Telegram.
        """
        # print("chat_id",self.chat_id)
        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'reply_markup': reply_markup
        }
        requests.post(self.TELEGRAM_API_URL + '/sendMessage', data=payload)

    def make_file_selection_keyboard(self, files):
        """
        Creates a keyboard with buttons for file selection.
        """
        keyboard = {'keyboard': [[{'text': file}] for file in files],
                    'resize_keyboard': True,
                    'one_time_keyboard': True}
        return keyboard

    def send_welcome_message(self):
        """
        Sends a welcome message to the user with a custom keyboard.
        """
        self.reset_user_state()
        welcome_text = "Welcome! Please select an option to proceed."
        commands = [['/publish_ad'], ['/my_ad_files'],['/messages'],["/manage_images"], ['/my_ads']]
        if self.user_state['webshare_rotate']:
            commands.append(['/disable_webshare'])
        else:
            commands.append(['/enable_webshare'])
        keyboard = {
            'keyboard': commands ,
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        self.send_message(welcome_text, reply_markup=json.dumps(keyboard))

    def send_photo(self, image_file, caption=None):
        url = f"{self.TELEGRAM_API_URL}/sendPhoto"
        files = {'photo': image_file}
        data = {'chat_id': self.chat_id}
        if caption:
            data['caption'] = caption
        res = requests.post(url , files=files,data=data)

    def get_file_path(self, file_id):
        url = f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/getFile"
        response = requests.post(url, data={'file_id': file_id})
        if response.ok:
            file_path = response.json()['result']['file_path']
            return file_path
        else:
            # If the response is not okay, log the error or handle it accordingly.
            print(response.json())
            return None

    def download_image(self, file_path):
        if file_path is not None:
            url = f"https://api.telegram.org/file/bot{self.TELEGRAM_TOKEN}/{file_path}"
            print("download url",url)
            response = requests.get(url, stream=True)
            if response.ok:
                return response
            else:
                # If the response is not okay, log the error or handle it accordingly.
                print(response.json())
                return None
        else:
            # Handle the case where file_path is None (getFile failed).
            return None


    def reset_user_state(self):
        for key in self.user_state.keys():
            if key not in self.settings:
                self.user_state[key] = None
        pass

    def send_token_file_selection(self):
        """
        Sends a list of token files for the user to select from.
        """
        files = os.listdir(Path("Cookies"))  # Assuming 'Cookies' directory is where the token files are stored
        keyboard = self.make_file_selection_keyboard(files)
        self.send_message("Select a token file:", reply_markup=json.dumps(keyboard))
