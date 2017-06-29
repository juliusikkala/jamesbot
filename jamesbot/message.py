import json

class Message:
    def __init__(self, user_id, text, sticker):
        self.user_id = user_id
        self.text = text
        self.sticker = sticker

    def from_telegram(tg_message):
        return Message(
            tg_message.from_user.id,
            tg_message.text,
            tg_message.sticker.file_id
        );

    def from_json(json_message):
        message_dict = json.loads(json_message)
        return Message(
            message_dict["user_id"],
            message_dict["text"],
            message_dict.get("sticker", None),
        );

    def to_json(self):
        return json.dumps({
            "user_id": self.user_id,
            "text": self.text,
            "sticker": self.sticker
        });
