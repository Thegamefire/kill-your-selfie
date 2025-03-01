import requests

class NtfyController:
    
    def __init__(self, auth_key, endpoint):
        self.auth_key = auth_key
        self.endpoint = endpoint
        
    def sendNotification(self, data:str, headers:dict):
        headers["Authentication"]=self.auth_key
        requests.post(self.endpoint,
            data=data,
            headers=headers)