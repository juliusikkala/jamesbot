import json

class User:
    def __init__(self, user_id, username, first_name, last_name):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

    def from_telegram(tg_user):
        return User(
            tg_user.id,
            tg_user.username,
            tg_user.first_name,
            tg_user.last_name
        )

    def from_json(json_user):
        user_dict = json.loads(json_user)
        return User(
            user_dict["user_id"],
            user_dict["username"],
            user_dict["first_name"],
            user_dict["last_name"]
        )
    
    def to_json(self):
        return json.dumps({
            "user_id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name
        });

    def matches(self, mention):
        mention = mention.lower()
        if self.username and mention == "@" + self.username.lower():
            return 3
        if self.last_name and (self.first_name+" "+self.last_name).lower() == mention:
            return 2
        if self.first_name.lower() == mention:
            return 1
        return 0
