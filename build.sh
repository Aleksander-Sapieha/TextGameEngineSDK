python3 -m py_compile run.py TextGameEngineSDK/engine.py TextGameEngineSDK/videoExporter.py TextGameEngineSDK/GJ_Game.py TextGameEngineSDK/renderer.py TextGameEngineSDK/map/main.py
mv __pycache__/run.cpython-312.pyc build/run.pyc
mv TextGameEngineSDK/__pycache__/engine.cpython-312.pyc build/TextGameEngineSDK/engine.pyc
mv TextGameEngineSDK/__pycache__/GJ_Game.cpython-312.pyc build/TextGameEngineSDK/GJ_Game.pyc
mv TextGameEngineSDK/__pycache__/renderer.cpython-312.pyc build/TextGameEngineSDK/renderer.pyc
mv TextGameEngineSDK/__pycache__/videoExporter.cpython-312.pyc build/TextGameEngineSDK/videoExporter.pyc
mv TextGameEngineSDK/map/__pycache__/main.cpython-312.pyc build/TextGameEngineSDK/map/main.pyc