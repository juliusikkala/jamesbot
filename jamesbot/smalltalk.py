from datetime import datetime, timedelta
from markovchain import MarkovChain
from impersonation import send_impersonated_message
import random
import re

def parse_time(time):
    return datetime.strptime(time, "%H:%M:%S").time()

def parse_time_range(time_range):
    times = time_range.split('-')
    if len(times) != 2:
        raise ValueError()
    
    return (parse_time(times[0]), parse_time(times[1]))

def format_time(time):
    return time.strftime("%H:%M:%S")

def format_time_range(time_range):
    return format_time(time_range[0])+"-"+format_time(time_range[1])

def time_in_range(time_range, time):
    start = time_range[0]
    end = time_range[1]
    if start <= end:
        return start <= time <= end
    else:
        return start <= time or time <= end

def smalltalk_control(bot, update, args, ctx):
    chat = ctx.get_chat(update.message.chat_id)
    if len(args) == 0:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="What about it?"
        )
        return

    command = args[0]

    config = chat.config['Smalltalk']

    if command == 'start':
        config['enabled'] = "True"

    elif command == 'stop':
        config['enabled'] = "False"

    elif command == 'icebreakerwait':
        if len(args) != 2:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="How long should I wait until I break the ice?"
            )
            return

        try:
            time = parse_time(args[1])
        except ValueError:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="I only understand the time if it is written as HH:MM:SS."
            )
            return
        
        config['ice_breaker_wait'] = format_time(time)

    elif command == 'responselikelihood':
        if len(args) != 2:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="What should the probability of me answering to messages be?"
            )
            return

        try:
            probability = float(args[1])
            if probability < 0.0 or probability > 1.0:
                raise ValueError
        except ValueError:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="The probability should be a number between 0.0 and 1.0."
            )
            return
        
        config['response_likelihood'] = str(probability)

    elif command == 'triggerwords':
        config['trigger_words'] = ' '.join(args[1:])
    
    elif command == 'silenttimes':
        timeranges = []
        for timerange in args[1:]:
            try:
                timeranges.append(parse_time_range(timerange))
            except ValueError:
                bot.send_message(
                    chat_id=update.message.chat_id,
                    text="The time range should be written as HH:MM:SS-HH:MM:SS."
                )
                return

        config['silent_times'] = ' '.join(map(format_time_range, timeranges))

    
    else:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="I'm sorry, I don't know of such a preference."
        )

    chat.save_config()

def try_smalltalk(bot, chat, ctx):
    current = datetime.now().time()
    silent_times = map(
        parse_time_range,
        filter(
            lambda t: len(t)>0,
            chat.config["Smalltalk"].get("silent_times", "").split(" ")
        )
    )

    for time_range in silent_times:
        if time_in_range(time_range, current):
            return
        
    chain = MarkovChain.from_texts(chat.all_messages())
    send_impersonated_message(bot, chat.chat_id, chain)

def icebreaker(bot, job):
    chat = job.context[0]
    ctx = job.context[1]
    job_queue = job.context[2]

    try_smalltalk(bot, chat, ctx)
    update_icebreaker_timer(chat, job_queue, ctx)

def update_icebreaker_timer(chat, job_queue, ctx):
    talkconfig = chat.config["Smalltalk"]

    #Update ice breaker timer
    if chat.idle_timer:
        chat.idle_timer.schedule_removal()

    wait = parse_time(talkconfig.get("ice_breaker_wait", "00:00:00"))

    due = timedelta(
        hours = wait.hour,
        minutes = wait.minute,
        seconds = wait.second
    ).total_seconds()

    #Don't accidentally flood the chat
    if due > 10:
        chat.idle_timer = job_queue.run_once(
            icebreaker,
            due,
            context=(chat, ctx, job_queue)
        )

def handle_smalltalk(bot, message, chat, job_queue, ctx):
    #Check if we should handle smalltalk
    talkconfig = chat.config["Smalltalk"]
    if talkconfig.get("enabled", "False") == "False":
        return

    update_icebreaker_timer(chat, job_queue, ctx)

    #Handle responding
    triggers = map(
        lambda w: w.lower(),
        talkconfig.get("trigger_words", "").split(" ")
    )
    words = map(
        lambda w: w.lower(),
        re.split('\W+', message.text)
    )

    if len([word for word in words if word in triggers]) > 0:
        try_smalltalk(bot, chat, ctx)
    else:
        probability = float(talkconfig.get("response_likelihood", 0))
        if random.random() < probability:
            try_smalltalk(bot, chat, ctx)
