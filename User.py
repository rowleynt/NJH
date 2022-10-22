class User:
    def __init__(self, user_id: int = -1, username: str = "DEFAULT_USER_NAME", join_date: str = "DEFAULT_PASSWORD"):
        self.user_id = user_id
        self.username = username
        self.join_date = join_date

    def getUserID(self):
        return self.user_id

    def getUsername(self):
        return self.username

    def getJoinDate(self):
        return self.join_date

    def updateUsername(self, new_name):
        self.username = new_name

    def __str__(self):
        return f"{self.user_id}, {self.username}, {self.join_date}"
