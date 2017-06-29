from message import Message
import os.path
import configparser

class Chat:
    def __init__(self, persistent_dir, chat_id):
        self.chat_id = chat_id
        self.idle_timer = None
        self.config_path = os.path.join(
            persistent_dir,
            str(chat_id)+"_config.cfg"
        )

        self.messages_path = os.path.join(
            persistent_dir,
            str(chat_id)+"_messages.jsonl"
        )

        self.messages = []
        self.messages_file = open(self.messages_path, 'a+')
        self.messages_file.seek(0)

        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        if not self.config.has_section("Recording"):
            self.config.add_section("Recording")
        if not self.config.has_section("Smalltalk"):
            self.config.add_section("Smalltalk")

        self.users = set()

        for line in self.messages_file:
            message = Message.from_json(line)
            self.messages.append(message)
            self.users.add(message.user_id)


    def save_config(self):
        with open(self.config_path, 'w') as f:
            self.config.write(f)

    def add_message(self, message):
        self.messages.append(message)
        self.users.add(message.user_id)
        self.messages_file.write(message.to_json()+"\n")
        self.messages_file.flush()

    def messages_from_user(self, user_id):
        for message in self.messages:
            if message.user_id == user_id:
                yield message

    def all_messages(self):
        for message in self.messages:
            yield message


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

