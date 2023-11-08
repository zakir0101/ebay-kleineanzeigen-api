import json

class InlineKeyboardButton:
    def __init__(self, text, callback_data=None, url=None):
        self.text = text
        self.callback_data = callback_data
        self.url = url

    def to_dict(self):
        button = {'text': self.text}
        if self.callback_data:
            button['callback_data'] = self.callback_data
        if self.url:
            button['url'] = self.url
        return button

class InlineKeyboardMarkup:
    def __init__(self, keyboard):
        self.keyboard = keyboard

    def to_json(self):
        return json.dumps({'inline_keyboard': [[button.to_dict() for button in row] for row in self.keyboard]})
