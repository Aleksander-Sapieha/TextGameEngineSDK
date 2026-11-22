# You game entry

from TextGameEngineSDK.engine.engine import *

def main():
    Engine = TextGameEngine(
        webhook_url="", # Change this
        GAME_ID=None,         # Change this
        GAME_SECRET=None  # Change this
    )
    play_intro()

    # Your game code here


if __name__ == "__main__":
    main()