import shutil
import os
import eel
import time
import asyncio
import websockets
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from game_state import GameState

eel.init('web')

# Global variables
start_time = None
elapsed_time = 0.0
running = False
game_state = GameState()
polling_task = None
event_loop = None

# WebSocket connection details
WS_URI = "ws://localhost:20727/tokens"
TOKENS_TO_MONITOR = [
    'mapsetid', 'mapid', 'titleRoman', 'artistRoman', 'creator', 'diffName', 'drainingtime', 'mapBreaks',
    'rankedStatus', 'gameMode', 'modsEnum', 'starsNomod', 'mStars',
    'cs', 'ar', 'od', 'hp', 'mCS', 'mAR', 'mOD', 'mHP',
    'circles', 'sliders', 'spinners', 'maxCombo', 'mainBpm',
    'c300', 'c100', 'c50', 'geki', 'katsu', 'miss', 'currentMaxCombo', 'score', 'grade', 'acc',
    'status'
]

async def connect_and_monitor():
    global game_state, elapsed_time
    while True:
        try:
            async with websockets.connect(WS_URI) as websocket:
                print(f"Connected to {WS_URI}")
                
                await websocket.send(json.dumps(TOKENS_TO_MONITOR))
                print(f"Sent tokens to monitor: {TOKENS_TO_MONITOR}")
                
                while True:
                    try:
                        data = await websocket.recv()
                        elapsed_time = time.time() - start_time
                        current_time = str(datetime.now())
                        print(f"Received data: {data}")
                        parsed_data = json.loads(data)
                        game_state.update(current_time, elapsed_time, **parsed_data)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                    except websockets.exceptions.ConnectionClosed as e:
                        print(f"Connection closed: {e}")
                        break
        except (websockets.exceptions.InvalidURI, websockets.exceptions.InvalidHandshake, OSError) as e:
            print(f"Failed to connect to {WS_URI}: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

def run_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

@eel.expose
def start_stopwatch():
    global start_time, running, polling_task, event_loop, game_state
    if not running:
        start_time = time.time()
        running = True
        game_state = GameState()
        
        # Start event polling
        if polling_task is None or polling_task.done():
            event_loop = asyncio.new_event_loop()
            executor = ThreadPoolExecutor(max_workers=1)
            executor.submit(run_asyncio_loop, event_loop)
            polling_task = asyncio.run_coroutine_threadsafe(connect_and_monitor(), event_loop)

@eel.expose
def stop_stopwatch():
    global elapsed_time, running, polling_task, event_loop
    if running:
        elapsed_time = time.time() - start_time
        running = False

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        source_file = "web/activity_history.json"
        destination_file = f"logs/log_{timestamp}.json"
        shutil.copyfile(source_file, destination_file)
        
        # Stop event polling
        if polling_task and not polling_task.done():
            polling_task.cancel()
        if event_loop:
            event_loop.call_soon_threadsafe(event_loop.stop)

@eel.expose
def reset_stopwatch():
    global start_time, elapsed_time, running
    start_time = None
    elapsed_time = 0.0
    running = False

@eel.expose
def get_elapsed_time():
    global start_time, elapsed_time
    if running:
        elapsed_time = time.time() - start_time
    millis = int((elapsed_time % 1) * 1000)
    seconds = int(elapsed_time % 60)
    minutes = int((elapsed_time // 60) % 60)
    hours = int((elapsed_time // 3600) % 24)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{millis:03}"

def cleanup():
    """Cleanup resources when the app is closing."""
    global polling_task, event_loop
    print("Cleaning up resources...")

    if polling_task and not polling_task.done():
        polling_task.cancel()
        print("Polling task cancelled.")
    
    if event_loop and event_loop.is_running():
        event_loop.call_soon_threadsafe(event_loop.stop)
        print("Event loop stopped.")

if __name__ == '__main__':
    window_size = {
        'size': (950, 680),
        'position': (100, 100),
        'resizable': False
    }
    try:
        eel.start('index.html', mode='chrome', **window_size, block=True)
    except (SystemExit, KeyboardInterrupt):
        cleanup()
