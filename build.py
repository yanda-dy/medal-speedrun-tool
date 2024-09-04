import PyInstaller.__main__

PyInstaller.__main__.run([
    'app.py',
    '--onedir',
    '--windowed',
    '--icon=medal-speedrun-tool.ico',
    '--add-data=game_state.py:.',
    '--add-data=medal.py:.',
    '--add-data=medal_processor.py:.',
    '--add-data=web:web',
    '--add-data=logs:logs',
    '--add-data=data:data',
    '--contents-directory=.',
    '--name=MedalSpeedrunTool'
])