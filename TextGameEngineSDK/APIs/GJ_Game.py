import urllib.request
import hashlib
import json

URL = "https://api.gamejolt.com/api/game/v1_2/"

def sha1_hash(data: str) -> str:
    # Create SHA-1 hash object
    sha1 = hashlib.sha1()
    # Update with UTF-8 encoded bytes
    sha1.update(data.encode('utf-8'))
    # Return hexadecimal digest
    return sha1.hexdigest()

class GJ_Game:
    def __init__(self, GAME_ID, GAME_SECRET):
        self.GAME_ID = GAME_ID
        self.GAME_SECRET = GAME_SECRET

    def log_in(self, username, token):
        pre_url = f"{URL}users/auth/?game_id={self.GAME_ID}&username={username}&user_token={token}"
        with_key = f"{pre_url}{self.GAME_SECRET}"
        hashed = sha1_hash(with_key)
        post_url = f"{pre_url}&signature={hashed}"
        req = urllib.request.Request(post_url, method="POST")
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode("utf-8"))

    def fetch_user_data(self, username, token):
        pre_url = f"{URL}users/?game_id={self.GAME_ID}&username={username}&user_token={token}"
        with_key = f"{pre_url}{self.GAME_SECRET}"
        hashed = sha1_hash(with_key)
        post_url = f"{pre_url}&signature={hashed}"
        req = urllib.request.Request(post_url, method="POST")
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode("utf-8"))

    def fetch_user_friends(self, username, token):
        pre_url = F"{URL}friends/?game_id={self.GAME_ID}&username={username}&user_token={token}",
        with_key = f"{pre_url}{self.GAME_SECRET}"
        hashed = sha1_hash(with_key)
        post_url = f"{pre_url}&signature={hashed}"
        req = urllib.request.Request(post_url, method="POST")
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode("utf-8"))

    def time(self):
        pre_url = f"{URL}time/?game_id={self.GAME_ID}"
        with_key = f"{pre_url}{self.GAME_SECRET}"
        hashed = sha1_hash(with_key)
        post_url = f"{pre_url}&signature={hashed}"
        req = urllib.request.Request(post_url, method="POST")
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode("utf-8"))

    def addTrophy(self, username, token, trophy_id):
        pre_url = f"{URL}trophies/add-achieved/?game_id={self.GAME_ID}&username={username}&user_token={token}&trophy_id={trophy_id}"
        with_key = f"{pre_url}{self.GAME_SECRET}"
        hashed = sha1_hash(with_key)
        post_url = f"{pre_url}&signature={hashed}"
        req = urllib.request.Request(post_url, method="POST")
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode("utf-8"))

    def removeTrophy(self, username, token, trophy_id):
        pre_url = f"{URL}trophies/remove-achieved/?game_id={self.GAME_ID}&username={username}&user_token={token}&trophy_id={trophy_id}"
        with_key = f"{pre_url}{self.GAME_SECRET}"
        hashed = sha1_hash(with_key)
        post_url = f"{pre_url}&signature={hashed}"
        req = urllib.request.Request(post_url, method="POST")
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode("utf-8"))

if __name__ == "__main__":
    pass