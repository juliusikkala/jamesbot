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
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

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

class User:
    def __init__(self, user_id, username, first_name, last_name):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

    def from_telegram(tg_user):
        return User(
            tg_user.id,
            tg_user.username,
            tg_user.first_name,
            tg_user.last_name
        )

    def from_json(json_user):
        user_dict = json.loads(json_user)
        return User(
            user_dict["user_id"],
            user_dict["username"],
            user_dict["first_name"],
            user_dict["last_name"]
        )
    
    def to_json(self):
        return json.dumps({
            "user_id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name
        });

    def matches(self, mention):
        mention = mention.lower()
        if self.username and mention == "@" + self.username.lower():
            return 3
        if self.last_name and (self.first_name+" "+self.last_name).lower() == mention:
            return 2
        if self.first_name.lower() == mention:
            return 1
        return 0

class Chat:
    def __init__(self, history_file):
        self.history = []
        self.history_file = open(history_file, 'a+')
        self.history_file.seek(0)
        self.users = set()

        for line in self.history_file:
            message = Message.from_json(line)
            self.history.append(message)
            self.users.add(message.user_id)


    def add_message(self, message):
        self.history.append(message)
        self.users.add(message.user_id)
        self.history_file.write(message.to_json()+"\n")
        self.history_file.flush()

    def messages_from_user(self, user_id):
        found = []
        for message in self.history:
            if message.user_id == user_id:
                found.append(message.text)

        return found

    def find_user(self, ctx, mention):
        best_match = None
        best_match_level = 0

        for user_id in self.users:
            user = ctx.get_user_by_id(user_id)
            if not user:
                continue

            match_level = user.matches(mention)
            
            if match_level > best_match_level:
                best_match = user
                best_match_level = match_level
            elif match_level == best_match_level:
                best_match = None

        return best_match 

class Context:
    def __init__(self, history_dir):
        self.chats = {}
        self.history_dir = history_dir

        self.users = {}
        self.users_file = open(os.path.join(self.history_dir, 'users'), 'a+')
        self.users_file.seek(0)

        for line in self.users_file:
            user = User.from_json(line)
            self.users[user.user_id] = user

    def get_chat(self, chat_id):
        if chat_id not in self.chats:
            self.chats[chat_id] = Chat(
                os.path.join(self.history_dir, str(chat_id))
            )
        return self.chats[chat_id]

    def add_user(self, user):
        if user.user_id not in self.users:
            self.users[user.user_id] = user
            self.users_file.write(user.to_json()+"\n")
            self.users_file.flush()

    def get_user_by_id(self, user_id):
        if user_id in self.users:
            return self.users[user_id]
        return None

class MarkovChain:
    class Node:
        def __init__(self, word):
            self.word = word
            self.links = {}

        def add_link(self, node):
            if node in self.links:
                self.links[node] += 1
            else:
                self.links[node] = 1

        def next(self):
            return random.choices(list(self.links.keys()), self.links.values())[0]

        def __hash__(self):
            return hash(self.word)

    #source_material should be a list of lists of words.
    def __init__(self, sources):
        self.root_node = self.Node(None)
        self.nodes = {}

        for source in sources:
            prev = self.root_node

            for word in source:
                if word not in self.nodes:
                    self.nodes[word] = self.Node(word)

                cur = self.nodes[word]
                prev.add_link(cur)
                prev = cur

            if prev != self.root_node:
                prev.add_link(None)

    def generator(self):
        node = self.root_node.next()

        while node != None:
            yield node.word
            node = node.next()

    def from_texts(texts):
        sources = []
        for text in texts:
            if not text:
                continue
            words = text.split(' ')
            sources.append(words)
        return MarkovChain(sources)

def record_message(bot, update, ctx):
    chat = ctx.get_chat(update.message.chat_id)
    ctx.add_user(User.from_telegram(update.message.from_user))
    chat.add_message(Message.from_telegram(update.message))

def impersonate_user(bot, update, args, ctx):
    chat = ctx.get_chat(update.message.chat_id)
    if len(args) < 1 or len(args) > 2:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="I'm sorry, I didn't quite catch your drift."
        )
        return
    
    user = chat.find_user(ctx, " ".join(args))
    
    if user == None:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="I apologise, I have no recollection of that person."
        )
        return

    chain = MarkovChain.from_texts(chat.messages_from_user(user.user_id))
    words = []
    for word in chain.generator():
        words.append(word)
    message = " ".join(words)
    bot.send_message(
        chat_id=update.message.chat_id,
        text=message
    )

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

    #JamesBot sometimes responds to commands.
    impersonate = CommandHandler(
        'impersonate',
        lambda bot, update, args: impersonate_user(bot, update, args, ctx),
        pass_args=True
    )

    dispatcher.add_handler(impersonate)
    dispatcher.add_handler(recorder)

    updater.start_polling()

if __name__ == "__main__":
    main(sys.argv)
