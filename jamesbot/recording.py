from user import User
from message import Message
from smalltalk import handle_smalltalk
from helpers import have_common_words
import re

def can_record_message(message, chat):
    if message.text and message.text.startswith("/"):
        return False

    config = chat.config['Recording']
    if config.get('enabled', 'False') != 'True':
        return False

    if have_common_words(
            re.split('\W+', message.text or ""),
            config.get("skip_words", "").split(" ")
        ):
        return False

    return True

def record_message(bot, update, job_queue, ctx):
    message = update.message

    chat = ctx.get_chat(message.chat_id)
    ctx.add_user(User.from_telegram(message.from_user))

    if message.text and message.text.startswith("/"):
        #Don't log or respond to failed commands
        return

    #Smalltalk before recording to avoid repeating users
    handle_smalltalk(bot, message, chat, job_queue, ctx)

    if can_record_message(message, chat):
        chat.add_message(Message.from_telegram(message))

def recording_control(bot, update, args, ctx):
    chat = ctx.get_chat(update.message.chat_id)
    if len(args) == 0:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="What about it?"
        )
        return

    command = args[0]

    config = chat.config['Recording']

    if command == 'start':
        config['enabled'] = "True"

    elif command == 'stop':
        config['enabled'] = "False"

    elif command == 'skipwords':
        config['skip_words'] = ' '.join(args[1:])
    
    else:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="I'm sorry, I don't know of such a preference."
        )

    chat.save_config()
