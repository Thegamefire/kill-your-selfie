import requests

class NtfyController:
    
    def __init__(self, auth_key, endpoint):
        self.auth_key = auth_key
        self.endpoint = endpoint
        
    def sendNotification(self, data:str, title:str=None, tags:str=None, priority:str=None):
        headers={
            "Authorization":self.auth_key,
            "Markdown":"yes",
            "Priority":priority,
            "Title":title,
            "Tags":tags,
            "Icon":None
        }
        requests.post(self.endpoint, data=data, headers=headers)
        
    def sendNewOccurrenceNotification(self, occurrence:dict, user):
        self.sendNotification(
            title=f"New Occurrence Was Added by {user.username}", 
            data=f"time: {occurrence["time"]}, location: {occurrence["location"]}, target: {occurrence["target"]}, context: {occurrence["context"]}",
            tags="newoccurrence",
            priority="3" # If priority is lower than 3, the notification won't make any sound
            )