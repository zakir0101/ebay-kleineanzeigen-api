# notify_new_messages.py
import json
import os

import requests

from main import Main

TELEGRAM_TOKEN = '6819822176:AAHnYg7TVpRXaDE4Yt0F6du_WwfDmbDryX8'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}'
CHAT_ID = "5351556147"


def notify_user(text, reply_markup=None):
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'reply_markup': reply_markup,
    }
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)


def main():
    for cookie_file in os.listdir("Cookies"):
        print(f"logged in as {cookie_file}")
        api = Main(log=True, mode="server", filename=f"Cookies/{cookie_file}", keep_old_cookies=False, save=True,
                   webshare_rotate=True)
        if api.login:
            user_id = api.get_user_id()
            user_name = api.get_user_name()
            conversations = api.get_conversations(user_id, "0", "10")
            notify_user(f"Conversations for {user_name}")
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


if __name__ == "__main__":
    main()
