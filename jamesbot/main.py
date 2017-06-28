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
import logging
from context import Context
from recording import record_message
from impersonation import impersonate_user
from smalltalk import smalltalk_control
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def main(argv):
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


    #JamesBot sometimes responds to commands.
    dispatcher.add_handler(CommandHandler(
        'impersonate',
        lambda bot, update, args: impersonate_user(bot, update, args, ctx),
        pass_args=True
    ))
    dispatcher.add_handler(CommandHandler(
        'smalltalk',
        lambda bot, update, args: smalltalk_control(bot, update, args, ctx),
        pass_args=True
    ))

    #JamesBot never misses a thing.
    dispatcher.add_handler(MessageHandler(
        Filters.all,
        lambda bot, update, job_queue: record_message(
            bot,
            update,
            job_queue,
            ctx
        ),
        pass_job_queue=True
    ))

    updater.start_polling()

if __name__ == "__main__":
    main(sys.argv)
