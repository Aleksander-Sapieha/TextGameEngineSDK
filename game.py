# You game entry

from TextGameEngineSDK.engine.engine import *

def main():
    Engine = TextGameEngine(
        webhook_url="", # Change this
        GAME_ID=None,         # Change this
        GAME_SECRET=None  # Change this
    )
    Engine.clearGameScreen()
    play_intro("Source Guy", "audio/intro.wav")

    # Your game code here


if __name__ == "__main__":
    main()