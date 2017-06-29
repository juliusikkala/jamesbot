from markovchain import MarkovChain

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
    
    MessageGenerator(messages).send(bot, chat.chat_id)
