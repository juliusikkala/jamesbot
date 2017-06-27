#! /usr/bin/env python3

#Copyright 2017 Julius Ikkala
#
#This file is part of JamesBot.
#
#JamesBot is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#JamesBot is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with JamesBot.  If not, see <http://www.gnu.org/licenses/>.

import sys
import configparser
import os.path
import logging
import json
from telegram.ext import Updater, MessageHandler, Filters

config_paths = [
    "./jamesbot.cfg",
    "~/.config/jamesbot.cfg",
    "/etc/jamesbot.cfg"
]

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

class Chat:
    def __init__(self, history_file):
        self.history = []
        self.history_file = open(history_file, 'a+')

        for line in self.history_file:
            self.history.append(Message.from_json(line));

    def add_message(self, message):
        self.history.append(message)
        self.history_file.write(message.to_json()+"\n")
        self.history_file.flush()

class Context:
    def __init__(self, history_dir):
        self.chats = {}
        self.history_dir = history_dir

    def get_chat(self, chat_id):
        if chat_id not in self.chats:
            self.chats[chat_id] = Chat(
                os.path.join(self.history_dir, str(chat_id))
            )
        return self.chats[chat_id]

def record_message(bot, update, ctx):
    print(str(update.message.chat_id) + ": " + update.message.text)

    chat = ctx.get_chat(update.message.chat_id);
    chat.add_message(Message.from_telegram(update.message));

    if update.message.chat_id == 250295888:
        bot.send_message(update.message.chat_id, "I heard: " + update.message.text)

def main(argv):
    global history_dir

    if len(argv) > 2:
        print("Usage: " + argv[0] + " [cfgpath]")
        return
    elif len(argv) == 2:
        config_paths.insert(0, argv[1])
    
    #Read first found config file
    config = configparser.ConfigParser()
    for path in config_paths:
        if os.path.isfile(path):
            config.read(path)
            break

    #Read necessary variables from config
    token = config['General']['token']
    history_dir = config['General']['historydir']

    #Initialize bot
    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    logging.basicConfig(
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level = logging.INFO
    )

    ctx = Context(history_dir)

    #JamesBot never misses a thing.
    recorder = MessageHandler(
        Filters.all,
        lambda bot, update: record_message(bot, update, ctx)
    )
    dispatcher.add_handler(recorder)

    updater.start_polling()

if __name__ == "__main__":
    main(sys.argv)
