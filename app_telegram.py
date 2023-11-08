import glob
import json
import os
from threading import Thread

import requests
from flask import Flask, request
from flask_cors import CORS

from main import Main
from telegram.base import Base
from telegram.image_files import ImageFiles
from telegram.messages import Messages
from telegram.my_ad_files import AdFiles
from telegram.publish_add import PublishAd

app = Flask(__name__)
CORS(app)

# Replace with your actual Telegram bot token
TELEGRAM_TOKEN = '6819822176:AAHnYg7TVpRXaDE4Yt0F6du_WwfDmbDryX8'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}'

# Stores the state for each user session
user_states = dict()


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook endpoint to receive updates from Telegram.
    """

    data = request.get_json()
    chat_id = ""
    if "message" in data:
        chat_id = data['message']['chat']['id']

    else:
        chat_id = data['callback_query']['message']['chat']['id']

    if not user_states.get(chat_id):
        user_states[chat_id] = dict()
        user_states[chat_id]["webshare_rotate"] = False
    user_state = user_states.get(chat_id)
    base = Base(TELEGRAM_API_URL, TELEGRAM_TOKEN, user_state, chat_id)
    publish = PublishAd(TELEGRAM_API_URL, TELEGRAM_TOKEN, user_state, chat_id)
    ad_file = AdFiles(TELEGRAM_API_URL, TELEGRAM_TOKEN, user_state, chat_id)
    image_files = ImageFiles(TELEGRAM_API_URL, TELEGRAM_TOKEN, user_state, chat_id)
    messages = Messages(TELEGRAM_API_URL, TELEGRAM_TOKEN, user_state, chat_id)

    if 'message' in data:

        if 'text' in data['message']:
            text = data['message']['text']

            handle_text_messages(text, user_state, base, publish, ad_file, image_files, messages, None)
        elif "photo" in data['message']:
            image_info = data.get('message', {}).get('photo', [])

            handle_file_message(data["message"], user_state, base, publish, ad_file, image_files, image_info)
    elif 'callback_query' in data:
        callback_query = data['callback_query']
        message = callback_query['message']
        data = callback_query['data']
        id = callback_query['id']
        handle_callback_query(data, message, id, user_state, base, publish, ad_file, image_files, messages)

    return '', 200


def handle_text_messages(text: str, user_state: dict, base: Base, publish: PublishAd, ad_file: AdFiles,
                         image_files: ImageFiles, messages: Messages, image_info=None):
    """
    Handles text messages received from users.
    """

    mode = user_state.get("mode")

    if text.startswith("/"):
        base.reset_user_state()
        if text == '/start':
            base.send_welcome_message()
        elif text == '/my_ad_files':
            ad_file.handle_my_adds()
        elif text == '/publish_ad':
            publish.send_token_file_selection()
        elif text == '/manage_images':
            image_files.handle_image_files_menu()
        elif text == '/enable_webshare':
            user_state["webshare_rotate"] = True
            base.send_message("webshare has been enabled")
            base.send_welcome_message()
        elif text == '/disable_webshare':
            user_state["webshare_rotate"] = False
            base.send_message("webshare has been disabled")
            base.send_welcome_message()
        elif text == '/messages':
            messages.handle_messages_menu()
    elif mode == base.MODE_MESSAGES:
        sending = user_state.get("sending")

        if sending:
            messages.send_user_message(text)
        elif text in os.listdir('Cookies'):
            messages.display_conversation(text)
        else:
            messages.send_message("text input is not expected here")

    elif mode == base.MODE_AD_FILE:

        if user_state.get('waiting_for_field_value'):
            ad_file.handle_field_value_input(text, user_state)
        elif user_state.get("edit_mode"):
            ad_file.handle_edit_field(text)
        elif user_state.get("add_mode"):
            ad_file.handle_new_ad_file_name(text)
        else:
            ad_file.handle_ad_file_selection(text)
            # view_or_edit_ad(chat_id, text)
    elif mode == base.MODE_PUBLISH:
        if text in os.listdir('Cookies'):
            publish.handle_token_selection(text)
        elif text in os.listdir('adds'):
            publish.handle_ad_selection(text)
    elif mode == base.MODE_IMAGE_FILE:
        subdirectory = user_state.get("subdirectory")
        add_image: bool = user_state.get("add_image")
        add_subdirectory: bool = user_state.get('add_subdirectory')
        if add_image:
            image_files.handle_new_image_name(text)
        elif add_subdirectory:
            image_files.handle_new_subdirectory_name(text)
        elif subdirectory:
            image_files.handle_image_file_selection(subdirectory, text)
        else:
            image_files.handle_image_files_selection(text)
    else:

        base.send_message("I didn't understand that command.")


def handle_file_message(text, user_state, base, publish, ad_file, image_files, image_info):
    mode = user_state.get("mode")
    if mode == base.MODE_IMAGE_FILE:
        subdirectory = user_state.get("subdirectory")
        add_image: bool = user_state.get("add_image")
        image_name: str = user_state.get("image_name")
        add_subdirectory: bool = user_state.get('add_subdirectory')
        if add_image and image_name and image_info:
            best_image = image_info[-1]  # Assuming the last item is the largest image
            file_id = best_image['file_id']
            print("file_id", file_id)
            image_files.handle_new_image(file_id, image_name, subdirectory)

        else:
            print("image_name", image_name)
            print("image_info", image_info)
            image_files.send_message("image could not be received")
            user_state.pop("add_image")
            user_state.pop("subdirectory")
            image_files.handle_image_files_selection(subdirectory)

    pass


def handle_callback_query(data: str, message, id, user_state: dict, base: Base, publish: PublishAd, ad_file: AdFiles,
                          image_files: ImageFiles, messages: Messages):
    """
    Handles callback queries from inline keyboards.
    """
    mode = user_state.get("mode")

    if data.startswith("notify"):
        notify, action, conversation_id, *token = data.split('_')
        cookie_file = '_'.join(token)
        api = Main(log=True, mode="server", filename=f"Cookies/{cookie_file}", keep_old_cookies=False, save=True,
                   webshare_rotate=False)
        if api.login:
            user_state["api"] = api
            user_state["mode"] = base.MODE_MESSAGES
            user_state['cookie_file'] = cookie_file
            user_state['user_id'] = api.get_user_id()
            user_state['current_conversation_id'] = conversation_id
            if action == "show":
                messages.display_messages(api, conversation_id)
                pass
            elif action == "reply":
                user_state['sending'] = True
                messages.handle_send_button()
                pass
            elif action == "read":
                messages.send_user_message("hallo")
                pass


    elif mode == base.MODE_PUBLISH:
        if data == 'confirm_publish':
            if user_state and 'token_file' in user_state and 'ad_file' in user_state:
                answer_callback_query(id)
                if user_state.get("publishing") is None:
                    user_state["publishing"] = False
                if not user_state.get('publishing'):
                    publish.publish_ad(user_state['token_file'], user_state['ad_file'])
                user_state["publishing"] = False
                base.send_welcome_message()

        elif data == 'cancel_publish':
            base.send_message("Publishing cancelled.")
            base.send_welcome_message()
    elif mode == base.MODE_AD_FILE:
        if data.startswith('edit_'):
            ad_file_name = data.split('edit_')[1]
            ad_file.start_editing_ad(ad_file_name)
        elif data == 'back_to_list':
            ad_file.handle_my_adds()

    elif mode == base.MODE_IMAGE_FILE:
        action, *params = data.split('_')
        param2 = '_'.join(params)
        if action == 'delete':
            image_name = param2
            subdirectory = user_state.get("subdirectory")
            image_files.delete_image(subdirectory, image_name)
            # user_state.pop("image_name")
            # image_files.handle_image_files_selection(subdirectory)
        elif action == 'back':
            subdirectory = param2
            image_files.handle_image_files_selection(subdirectory)

    elif mode == base.MODE_MESSAGES:
        if data.startswith('conv_'):
            conversation_id = data.split('conv_')[1]
            api = user_state['api']
            messages.display_messages(api, conversation_id)  # Pass the correct API instance here
        elif data == "back_to_main":
            messages.send_welcome_message()
        elif data == 'send_message':
            messages.handle_send_button()
        elif data == 'back_to_conversations':
            messages.handle_back_button()  # Pass the correct API instance here
        pass

    answer_callback_query(id)


def answer_callback_query(callback_query_id):
    """
    Sends a request to Telegram API to answer a callback query.
    """
    url = TELEGRAM_API_URL + '/answerCallbackQuery'
    params = {'callback_query_id': callback_query_id}
    requests.post(url, params)


CHAT_ID = "5351556147"


def notify_user(text, reply_markup=None):
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'reply_markup': reply_markup,
    }
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", data=payload)


def notify_messages_async_task():
    for index, cookie_file in enumerate(glob.glob("Cookies/*.json")):
        index = index + 1
        print(f"{index}: logged in as {cookie_file}")
        api = Main(log=True, mode="server", filename=f"Cookies/{cookie_file}", keep_old_cookies=False, save=True,
                   webshare_rotate=True)
        if api.login:

            api.cookies.remove_specific_cookies()
            user_id = api.get_user_id()
            api.cookies.remove_specific_cookies()
            user_name = api.get_user_name()
            conversations = api.get_conversations(user_id, "0", "10")
            notify_user(f"{index}. Conversations for {user_name}")
            if conversations["numUnreadMessages"] > 0:
                for conversation in conversations.get("conversations", []):
                    if conversation['unreadMessagesCount'] > 0:
                        messages = api.get_messages(user_id, conversation["id"])
                        num_unread = messages["numUnread"]
                        unread_messages = messages["messages"][-num_unread:]  # Get last 'x' unread messages
                        contact_name = messages['buyerName'] if messages['role'] == "Seller" else messages['sellerName']
                        message_text = f"New messages from {contact_name}:\n"
                        message_text += "\n".join([msg["textShort"] for msg in unread_messages])
                        # Construct reply_markup for Telegram API
                        reply_markup = {
                            "inline_keyboard": [
                                [{"text": "Show all messages",
                                  "callback_data": f"notify_show_{conversation['id']}_{cookie_file}"}],
                                [{"text": "Reply",
                                  "callback_data": f"notify_reply_{conversation['id']}_{cookie_file}"}],
                                [{"text": "Mark as read",
                                  "callback_data": f"notify_read_{conversation['id']}_{cookie_file}"}],
                            ]
                        }

                        notify_user(text=message_text, reply_markup=json.dumps(reply_markup))
            else:
                notify_user("no new Messages")

        else:
            notify_user(f"{index}. can't login to account : {cookie_file}")
    return "OK", 200


@app.route('/notify')
def notify_new_messages_cron_job():
    thread = Thread(target=notify_messages_async_task)
    thread.start()
    return "OK", 200


if __name__ == '__main__':
    app.run(debug=True)
