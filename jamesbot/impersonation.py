from markovchain import MarkovChain

def send_impersonated_message(bot, chat_id, chain):
    words = []
    for word in chain.generator():
        words.append(word)
    message = " ".join(words)
    bot.send_message(
        chat_id=chat_id,
        text=message
    )


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
    send_impersonated_message(bot, update.message.chat_id, chain)
