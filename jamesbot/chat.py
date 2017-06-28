from message import Message

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
        for message in self.history:
            if message.user_id == user_id:
                yield message.text

    def all_messages(self):
        for message in self.history:
            yield message.text


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

