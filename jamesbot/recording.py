from user import User
from message import Message
from smalltalk import handle_smalltalk

def record_message(bot, update, job_queue, ctx):
    message = update.message

    chat = ctx.get_chat(message.chat_id)
    ctx.add_user(User.from_telegram(message.from_user))

    if message.text and message.text.startswith("/"):
        #Don't log or respond to failed commands
        return
    chat.add_message(Message.from_telegram(message))

    handle_smalltalk(bot, message, chat, job_queue, ctx)

