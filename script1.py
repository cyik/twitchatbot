from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch

import asyncio
import dontLeak
import cv2
import numpy as np
import mss
import time

APP_ID = dontLeak.client_id
APP_SECRET = dontLeak.client_secret
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.CHANNEL_MANAGE_BROADCAST]
TARGET_CHANNEL = 'Queensell'

TARGET_IMAGE_PATH = r"C:\Users\cheny\OneDrive\Desktop\ITA\twitchatbot\apple.jpg"
DETECTION_INTERVAL = 2        # seconds between each screenshot check
TRIGGER_COOLDOWN = 300        # seconds before sending another message

last_trigger_time = 0  # Track last time message was sent

# ---------------- Twitch bot callbacks ----------------
async def on_ready(ready_event: EventData):
    await ready_event.chat.join_room(TARGET_CHANNEL)
    print('Bot is ready!!')
    
async def on_message(msg: ChatMessage):
    print(f'{msg.user.display_name} - {msg.text}')

# ---------------- Image detection ----------------
def screen_has_target():
    
    """Capture the screen and check for the target image."""
    with mss.mss() as sct:
        screenshot = np.array(sct.grab(sct.monitors[0]))  # Full screen
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        target = cv2.imread(TARGET_IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
        if target is None:
            print(f"Error: Could not load {TARGET_IMAGE_PATH}")
            return False
        
        # Template matching
        result = cv2.matchTemplate(screenshot_gray, target, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        # You can adjust threshold
        return max_val >= 0.9
    
    

async def monitor_screen(chat: Chat):
    """Continuously monitor the screen and send message if image detected."""
    global last_trigger_time
    while True:
        try:
            now = time.time()
            if now - last_trigger_time >= TRIGGER_COOLDOWN:
                if screen_has_target():
                    print("Target image detected! Sending chat message...")
                    await chat.send_message(TARGET_CHANNEL, "Squad has been eliminated")
                    last_trigger_time = now
        except Exception as e:
            print(f"Error in screen monitor: {e}")
        await asyncio.sleep(DETECTION_INTERVAL)

# ---------------- Run bot ----------------
async def run_bot():
    bot = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(bot, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await bot.set_user_authentication(token, USER_SCOPE, refresh_token)
    
    chat = await Chat(bot)
    
    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)
    
    chat.start()
    
    # Start screen monitor task
    monitor_task = asyncio.create_task(monitor_screen(chat))
    
    try:
        input('Press Enter TO Stop Bot \n')
    finally:
        monitor_task.cancel()
        chat.stop()
        await bot.close()

# ---------------- Main ----------------
bot_loop = asyncio.new_event_loop()
asyncio.set_event_loop(bot_loop)
bot_loop.run_until_complete(run_bot())
bot_loop.close()
