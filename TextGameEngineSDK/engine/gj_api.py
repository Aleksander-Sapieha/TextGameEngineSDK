from . import GJ_Game

class Api:
    def __init__(self, GAME_ID, GAME_SECRET):
        self.GAME_ID = GAME_ID
        self.GAME_SECRET = GAME_SECRET
        self.gj_game = GJ_Game.GJ_Game(GAME_ID=GAME_ID, GAME_SECRET=GAME_SECRET)