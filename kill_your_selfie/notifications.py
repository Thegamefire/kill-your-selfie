import requests


class NtfyController:
    def __init__(self, auth_key, endpoint):
        self.auth_key = auth_key
        self.endpoint = endpoint

    def sendNotification(self, data: str, title: str = None, tags: str = None, priority: str = None):
        headers = {
            "Authorization": self.auth_key,
            "Markdown": "yes",
            "Priority": priority,
            "Title": title,
            "Tags": tags,
            "Icon": None
        }
        requests.post(self.endpoint, data=data, headers=headers)

    def sendNewOccurrenceNotification(self, occurrence: dict, user):
        self.sendNotification(
            title=f"New occurrence was added by {user.username}",
            data=f"time: {occurrence["time"]}, location: {occurrence["location"]}, target: {occurrence["target"]}, context: {occurrence["context"]}",
            tags="newoccurrence",
            priority="3"  # If priority is lower than 3, the notification won't make any sound
        )

    def sendNewUserNotification(self, username: str, is_admin: bool, email: str):
        self.sendNotification(
            title=f"User {username} was given access to kys",
            data=f"admin: {is_admin}, email: {email}",
            tags="newuser",
            priority="4"
        )


class DummyNtfyController(NtfyController):
    """NtfyController that does nothing. Used if no ntfy endpoint is set,
    e.g. if you don't have a working ntfy instance.
    """

    def __init__(self):
        super().__init__(None, None)

    def sendNotification(self, data: str, title: str = None, tags: str = None, priority: str = None): ...

    def sendNewOccurrenceNotification(self, occurrence: dict, user): ...

    def sendNewUserNotification(self, username: str, is_admin: bool, email: str): ...
