# messages.py
from threading import Thread

from telegram.base import Base
import json

from main import Main
from telegram.buttons import InlineKeyboardButton, InlineKeyboardMarkup


class Messages(Base):
    def __init__(self, telegram_api_url, bot_token, user_state, chat_id):
        super().__init__(telegram_api_url, bot_token, user_state, chat_id)

    def handle_messages_menu(self):
        self.user_state["mode"] = self.MODE_MESSAGES
        self.send_token_file_selection()

    def display_conversation(self,cookie_file):
        thread = Thread(target=self.display_conversation_async,args=(cookie_file))
        thread.start()
    def display_conversation_async(self,cookie_file):
        # Code to get conversations list and send it to user
        # You would use the api.get_conversations() here
        # and format it to send to the user with an inline keyboard

        api = Main(log=True, mode="server", filename=f"Cookies/{cookie_file}", keep_old_cookies=False, save=True,
                   webshare_rotate=False)
        self.user_state["cookie_file"] = cookie_file
        self.user_state['api'] = api
        if api.login:
            self.user_state['user_id'] = api.get_user_id()
            user_id = self.user_state['user_id']
            user_name = api.get_user_name()
            conversations = api.get_conversations(user_id, "0", "10")

            if conversations:
                keyboard = []
                for conversation in conversations['conversations']:
                    text = conversation['buyerName']
                    if conversation['unread']:
                        text += f" ({conversation['unreadMessagesCount']} new)"
                    callback_data = f"conv_{conversation['id']}"
                    keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
                keyboard.append([InlineKeyboardButton("Back to Main",callback_data="back_to_main")])
                self.send_message(f"Conversations for {user_name}:")
                reply_markup = InlineKeyboardMarkup(keyboard)
                if len(keyboard) == 1:
                    self.send_message(f"conversation list for user {user_name} is Empty",reply_markup=reply_markup.to_json())
                else:
                    self.send_message("Select a conversation:", reply_markup=reply_markup.to_json())

            else:
                self.send_message(f"could not get conversations for user {user_name}")
                self.leave_message_window()
            pass
        else:
            self.send_message(f"could not Login with token in {cookie_file}")
            self.leave_message_window()

            pass

    def leave_message_window(self):
        self.send_welcome_message()


    def display_messages(self, api, conversation_id):
        thread = Thread(target=self.display_messages_async, args=(api,conversation_id))
        thread.start()
    def display_messages_async(self, api, conversation_id):
        # Code to get messages for the specified conversation
        # You would use the api.get_messages() here
        # Format the messages and send them to the user with "send" and "back" buttons

        user_id = self.user_state['user_id']
        messages = api.get_messages(user_id, conversation_id)
        if messages:
            text = f"Conversation with {messages['buyerName']}:\n"
            self.send_message(text)
            for message in messages['messages']:
                prefix = "You: " if message['boundness'] == "OUTBOUND" else f"{messages['buyerName']}: "
                text = f"{prefix}{message['textShort']} - {message['readableDate']}\n"
                self.send_message(text)
            self.user_state['current_conversation_id'] = conversation_id
            keyboard = [[
                InlineKeyboardButton("Send", callback_data="send_message"),
                InlineKeyboardButton("Back", callback_data="back_to_conversations")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            self.send_message("Choose an option:", reply_markup=reply_markup.to_json())



    def send_user_message(self, text):
        # Code to send the user's message to the conversation
        # You would use the api.send_message_from_message_box() here
        api = self.user_state.get("api")
        conversation_id = self.user_state.get('current_conversation_id')
        user_id = self.user_state['user_id']

        if text.lower() == 'stop':
            if conversation_id:
                self.display_messages(api,conversation_id)
        else:
            if api.login and conversation_id:
                api.send_message_from_message_box(text, user_id, conversation_id)

    def handle_send_button(self):
        # Set the user_state to 'sending' mode and prompt user to type their message
        self.user_state['sending'] = True
        keyboard = self.make_file_selection_keyboard(["stop"])
        self.send_message("Send your message. Type 'stop' to end the sending mode.",reply_markup=json.dumps(keyboard))

    def handle_back_button(self):
        # Display the conversations list again
        self.display_conversation(self.user_state["cookie_file"])
    # def handle_stop_command(self):
        # Exit 'sending' mode and show the conversation again
