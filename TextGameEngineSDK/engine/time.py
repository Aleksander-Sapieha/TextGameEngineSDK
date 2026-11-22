from .engine import GJ_Game

class Time:
    def __init__(self, api):
        self.api = api
        self.gj_game = GJ_Game.GJ_Game(self.api.GAME_ID, self.api.GAME_SECRET)

    def time_fetch(self):
        response = self.gj_game.time()
        return response