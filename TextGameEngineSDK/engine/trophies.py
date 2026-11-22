from ..APIs import GJ_Game

class Trophies:
    def __init__(self, api):
        self.api = api
        self.gj_game = GJ_Game.GJ_Game(self.api.GAME_ID, self.api.GAME_SECRET)
    def add_trophy(self, username, token, trophy_id):
        response = self.gj_game.addTrophy(username, token, trophy_id)
        return response

    def remove_trophy(self, username, token, trophy_id):
        response = self.gj_game.removeTrophy(username, token, trophy_id)
        return response