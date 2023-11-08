import json
import os
from pathlib import Path
from threading import Thread

from anzeige_abschicken import AnzeigeAbschickenApi
from telegram.base import Base


class PublishAd(Base):

    def __init__(self, telegram_api_url, bot_token, user_state, chat_id):
        super().__init__(telegram_api_url, bot_token, user_state, chat_id)

    def handle_publish_file_menu (self) :
        self.user_state['mode'] = self.MODE_PUBLISH
        self.send_token_file_selection()
    def handle_token_selection(self, token_file_name):
        """
        Handles the event when a user selects a token file.
        """
        self.user_state.update({'token_file': token_file_name})
        self.send_ad_file_selection()

    def send_ad_file_selection(self):
        """
        Sends a list of advertisement files for the user to select from.
        """
        files = os.listdir('./adds')  # Assuming 'adds' directory is where the ad files are stored
        keyboard = self.make_file_selection_keyboard(files)
        self.send_message("Select an ad file:", reply_markup=json.dumps(keyboard))

    def handle_ad_selection(self, ad_file_name):
        """
        Handles the event when a user selects an advertisement file.
        """
        user_state = self.user_state
        if user_state and 'token_file' in user_state:
            user_state['ad_file'] = ad_file_name
            self.send_confirmation_message(user_state['token_file'], ad_file_name)
        else:
            self.send_message("Please select a token file first.")

    def send_confirmation_message(self, token_file, ad_file):
        """
        Sends a confirmation message to the user for publishing the ad.
        """
        confirmation_text = (
            f"You have selected the token file '{token_file}' "
            f"and ad file '{ad_file}'. Do you want to proceed with publishing the ad?"
        )
        confirmation_keyboard = self.make_confirmation_keyboard()
        self.send_message(confirmation_text, reply_markup=json.dumps(confirmation_keyboard))

    def make_confirmation_keyboard(self):
        """
        Creates a confirmation keyboard with "Yes" and "No" options.
        """
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Yes, publish it", "callback_data": "confirm_publish"},
                    {"text": "No, cancel", "callback_data": "cancel_publish"}
                ]
            ]
        }
        return keyboard

    def publish_ad(self, token_file, ad_file):
        """
        Publishes an advertisement using the selected token and ad files.
        """
        thread = Thread(target=self.publish_ad_async,args=(token_file,ad_file))
        thread.start()
    def publish_ad_async(self, token_file, ad_file):
        """
        Publishes an advertisement using the selected token and ad files.
        """
        self.user_state["publishing"] = True

        self.send_message(f"Publishing ad with {token_file} and {ad_file}...")
        try:
            api = AnzeigeAbschickenApi(log=True, mode="server", filename=f"Cookies/{token_file}",
                                       keep_old_cookies=False, save=True,
                                       webshare_rotate=self.user_state["webshare_rotate"],
                                       telegram_api_url=self.TELEGRAM_API_URL, chat_id=self.chat_id)
            if not api.login:
                self.send_message("Couldn't login :(")
                raise Exception()
            self.send_message(f"logged as {api.get_user_name()}")
            res = api.publish_add_from_json_file(Path(f"./adds/{ad_file}"))
            self.send_message(f"Ad published successfully! Response: {res}")
        except Exception as e:
            self.send_message(f"Failed to publish ad. Error: {e}")
