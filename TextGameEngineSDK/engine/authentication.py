from ..APIs import GJ_Game

class Auth:
    def __init__(self, api):
        self.logged_in = False
        self.username = None
        self.token = None

    def login(self, username, token, api):
        self.username = username
        self.token = token
        gj_game = GJ_Game.GJ_Game(api.GAME_ID, api.GAME_SECRET)
        response = gj_game.log_in(username, token)
        if "success" in response.lower():
            self.logged_in = True
            print("Login successful!")
            with open("credentials.txt", "w") as f:
                f.write(f"{username}\n{token}")
            return True
        else:
            print("Login failed. Please check your credentials.")
            self.logged_in = False
            return False
        return False