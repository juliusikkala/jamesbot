import json

class Message:
    def __init__(self, user_id, text):
        self.user_id = user_id
        self.text = text

    def from_telegram(tg_message):
        return Message(tg_message.from_user.id, tg_message.text);

    def from_json(json_message):
        message_dict = json.loads(json_message)
        return Message(message_dict["user_id"], message_dict["text"]);

    def to_json(self):
        return json.dumps({"user_id": self.user_id, "text": self.text});
