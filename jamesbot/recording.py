from user import User
from message import Message
from smalltalk import handle_smalltalk

def record_message(bot, update, job_queue, ctx):
    chat = ctx.get_chat(update.message.chat_id)
    ctx.add_user(User.from_telegram(update.message.from_user))
    chat.add_message(Message.from_telegram(update.message))

    handle_smalltalk(bot, update.message, chat, job_queue, ctx)

