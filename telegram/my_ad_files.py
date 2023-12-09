import json
import os
from pathlib import Path

from telegram.base import Base


class AdFiles(Base):

    def __init__(self, telegram_api_url,bot_token, user_state,chat_id):
        super().__init__(telegram_api_url,bot_token, user_state,chat_id)

    def handle_my_adds(self):
        """
        Send a message to the user with a list of their ads allowing them to view, edit, or add a new ad.
        """
        self.user_state['mode'] = "adds"
        ad_files = os.listdir('adds')
        ad_files.append("Add new Ad")
        ad_files.append("Back to start")
        keyboard = self.make_file_selection_keyboard(ad_files)
        self.send_message("Choose an ad to view or edit, or add a new one:", reply_markup=json.dumps(keyboard))

    def handle_ad_file_selection(self, selection):
        """
        Handle user's selection from 'my_adds'.
        """
        if selection == "Back to start":
            self.user_state.pop("mode")
            self.send_welcome_message()
        elif selection == "Add new Ad":
            self.start_adding_ad()
        else:
            # Assuming that the selection is an ad file
            if selection not in os.listdir("adds"):
                selection = self.user_state["ad_file"]
            self.send_ad_content(selection)
            # Ask if user wants to edit or go back to ad list
            keyboard = {
                "inline_keyboard": [
                    [{"text": "Edit this Ad", "callback_data": f"edit_{selection}"}],
                    [{"text": "Back to list", "callback_data": "back_to_list"}]
                ]
            }

            self.send_message("What do you want to do with this ad?", reply_markup=json.dumps(keyboard))

    def send_ad_content(self, ad_file_name):
        """
        Send the ad content to the user.
        """
        try:
            ad_path = Path(f"./adds/{ad_file_name}")
            with ad_path.open('r', encoding='utf-8') as file:
                ad_content = json.load(file)
            pretty_content = json.dumps(ad_content, indent=2, ensure_ascii=False)
            self.send_message(f"Content of {ad_file_name}:\n{pretty_content}")
        except Exception as e:
            self.send_message(f"Failed to load ad content. Error: {e}")

    def start_editing_ad(self, ad_file_name):
        """
        Start the process of editing an ad by asking which field to edit.
        """
        self.user_state .update( {'ad_file': ad_file_name, 'edit_mode': True})
        # This would ideally be dynamic based on the ad structure
        fields = ["title", "description", "zip", "price", "contact_name", "image_folder", "Back to Add Detail"]
        keyboard = self.make_file_selection_keyboard(fields)
        self.send_message("Select a field to edit:", reply_markup=json.dumps(keyboard))
        self.user_state['field_to_edit'] = None

    def handle_edit_field(self, field_name):
        """
        Handle the editing of a specific field in the ad.
        """

        ad_file_name = self.user_state['ad_file']
        ad_path = Path(f"./adds/{ad_file_name}")
        with ad_path.open('r', encoding='utf-8') as file:
            ad_content = json.load(file)

        self.request_new_field_value(ad_content, field_name)

    def request_new_field_value(self, ad_content, field_name):
        """
        Requests a new value for a given field from the user.
        """
        if field_name == "Back to Add Detail":
            self.user_state.pop("edit_mode")
            self.handle_ad_file_selection(self.user_state.get("ad_file"))
        else:
            self.send_message(f"Please send the new value for the '{field_name}':")
            self.user_state['waiting_for_field_value'] = field_name
            self.user_state['ad_content'] = ad_content
            if field_name == "image_folder":
                self.send_image_folder_selection()

    def send_image_folder_selection(self):
        """
        Send a selection of image folders to the user.
        """
        image_folders = [f.name for f in Path('images').iterdir() if f.is_dir()]
        # ... (from previous code)
        keyboard = self.make_file_selection_keyboard(image_folders)
        self.send_message("Please select an image folder:", reply_markup=json.dumps(keyboard))

    def handle_field_value_input(self, text, user_state):
        """
        Handles the user's input for the new field value.
        """
        field_name = self.user_state.get('waiting_for_field_value')

        if field_name:
            ad_content = user_state.get('ad_content', {})
            if field_name == "image_folder":
                ad_content[field_name] = "images/" + text
            else:
                ad_content[field_name] = text
            self.user_state.pop('waiting_for_field_value', None)
            # Save the updated ad content
            self.save_ad_content(ad_content, user_state['ad_file'])
            self.send_message(f"Field '{field_name}' updated successfully with value '{text}'.")
            self.start_editing_ad(user_state.get("ad_file"))

        else:
            self.send_message("No field was waiting for input.")

    def start_adding_ad(self):
        """
        Start the process of adding a new ad by asking for the file name.
        """
        # The bot should send a message asking for the name of the ad file
        self.user_state['add_mode'] = True
        self.send_message("Please send the name for the new ad file.")
        # self.user_state = {'mode': "adds", 'add_mode': True}

    # When the user sends the file name, you save it and ask for the next field
    def handle_new_ad_file_name(self, ad_file_name:str):
        """
        Handle the file name input for a new ad.
        """
        if 'add_mode' in self.user_state:
            # user_state['new_ad_data']['file_name'] = ad_file_name
            # Now you should ask for the next ad field, starting with the title
            if not ad_file_name.endswith(".json"):
                ad_file_name = ad_file_name + ".json"
            muster = open("adds/muster.json", "r", encoding="utf-8").read()
            with open("adds/" + ad_file_name, "w", encoding="utf-8") as f:
                f.write(muster)
                f.close()
            self.send_message("the new add have been created, no you can select the add to edit its fields")
            self.user_state.pop("add_mode")
            self.user_state['ad_file'] = ad_file_name
            self.handle_ad_file_selection(ad_file_name)

    def save_ad_content(self, ad_content, ad_file_name):
        ad_path = Path(f"./adds/{ad_file_name}")
        with ad_path.open('w', encoding='utf-8') as file:
            json.dump(ad_content, file, ensure_ascii=False, indent=4)
        self.send_message("Ad updated successfully!")
1