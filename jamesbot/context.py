import configparser
import os.path
from user import User
from chat import Chat

config_paths = [
    "./jamesbot.cfg",
    "~/.config/jamesbot.cfg",
    "/etc/jamesbot.cfg"
]

def read_config(local_path = None):
    config = configparser.ConfigParser()

    if local_path:
        if not os.path.isfile(local_path):
            raise Exception(
                "Configuration file " + local_path + " not found."
            )
        config.read(local_path)
    else:
        #Read first found config file
        for path in config_paths:
            if os.path.isfile(path):
                config.read(path)
                break
        else:
            raise Exception("No configuration file found.")

    return config

class Context:
    def __init__(self, local_config_path = None):
        self.chats = {}

        self.config = read_config(local_config_path)
        self.persistent_dir = self.config['General']['persistent_dir']

        self.users = {}
        self.users_file = open(
            os.path.join(self.persistent_dir, 'users'),
            'a+'
        )
        self.users_file.seek(0)

        for line in self.users_file:
            user = User.from_json(line)
            self.users[user.user_id] = user

    def get_chat(self, chat_id):
        if chat_id not in self.chats:
            self.chats[chat_id] = Chat(self.persistent_dir, chat_id)
        return self.chats[chat_id]

    def add_user(self, user):
        if user.user_id not in self.users:
            self.users[user.user_id] = user
            self.users_file.write(user.to_json()+"\n")
            self.users_file.flush()

    def get_user_by_id(self, user_id):
        if user_id in self.users:
            return self.users[user_id]
        return None

