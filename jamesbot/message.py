import json
import random
from markovchain import MarkovChain

class Message:
    def __init__(self, user_id, text, sticker):
        self.user_id = user_id
        self.text = text
        self.sticker = sticker

    def from_telegram(tg_message):
        return Message(
            tg_message.from_user.id,
            tg_message.text,
            tg_message.sticker and tg_message.sticker.file_id
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

class MessageGenerator:
    def __init__(self, source_messages=[]):
        self.stickers = {}
        self.message_count = 0
        self.chain = MarkovChain()

        for message in source_messages:
            self.add_source_message(message)

    def add_source_message(self, message):
        self.message_count += 1

        if message.sticker:
            if message.sticker in self.stickers:
                self.stickers[message.sticker] += 1
            else:
                self.stickers[message.sticker] = 1
        elif message.text:
            self.chain.add_source(message.text.split(" "))

    def send(self, bot, chat_id):
        #Choose whether to send sticker or generated text
        sticker_chance = len(self.stickers)/self.message_count

        if random.random() < sticker_chance:
            sticker = random.choices(
                list(self.stickers.keys()),
                self.stickers.values()
            )[0]
            bot.send_sticker(
                chat_id=chat_id,
                sticker=sticker
            )
        else:
            words = []
            for word in self.chain.generator():
                words.append(word)
            message = " ".join(words)
            bot.send_message(
                chat_id=chat_id,
                text=message
            )
