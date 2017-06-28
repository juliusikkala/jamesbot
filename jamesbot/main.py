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
from message import Message
from markovchain import MarkovChain
from context import Context
from user import User
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def record_message(bot, update, ctx):
    chat = ctx.get_chat(update.message.chat_id)
    ctx.add_user(User.from_telegram(update.message.from_user))
    chat.add_message(Message.from_telegram(update.message))

def impersonate_user(bot, update, args, ctx):
    chat = ctx.get_chat(update.message.chat_id)

    messages = []
    if len(args) > 2:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="I'm sorry, I didn't quite catch your drift."
        )
        return
    elif len(args) == 0:
        messages = chat.all_messages()
    else: 
        user = chat.find_user(ctx, " ".join(args))
        
        if user == None:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="I apologise, I have no recollection of that person."
            )
            return
        messages = chat.messages_from_user(user.user_id)
    

    chain = MarkovChain.from_texts(messages)
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

    local_config_path = None

    if len(argv) > 2:
        print("Usage: " + argv[0] + " [cfgpath]")
        return
    elif len(argv) == 2:
        local_config_path = argv[1]
    
    #Initialize bot
    ctx = Context(local_config_path)
    updater = Updater(token=ctx.config['General']['token'])
    dispatcher = updater.dispatcher

    logging.basicConfig(
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level = logging.INFO
    )

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
