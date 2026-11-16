from TextGameEngineSDK.map.main import main as mapMain
from TextGameEngineSDK.hatred.main import main as hatredMain

GAME = "map"

if GAME == "map":
    mapMain()
elif GAME == "hatred":
    hatredMain()