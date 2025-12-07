import asyncio
import cv2
import mss
import numpy as np
from twitchAPI.chat import Chat, ChatEvent, ChatMessage, EventData
from twitchAPI.type import AuthScope
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
import dontLeak
import time

# ------------------ CONFIG ------------------
APP_ID = dontLeak.client_id
APP_SECRET = dontLeak.client_secret
TARGET_CHANNEL = 'Queensell'
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.CHANNEL_MANAGE_BROADCAST]
PORT = 17563

TARGET_IMAGE_PATH = r"C:\Users\cheny\OneDrive\Desktop\ITA\twitchatbot\squadeliminated.png"
MONITOR_INDEX = 1  # primary monitor
THRESHOLD = 0.7
CHECK_INTERVAL = 1  # seconds between screen checks
# ------------------------------------------------

# Load target image
target = cv2.imread(TARGET_IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
if target is None:
    print(f"Error: Could not load {TARGET_IMAGE_PATH}")
    exit()
h, w = target.shape
print(f"Target image loaded. Shape: {target.shape}")

# Twitch bot events
async def on_ready(event: EventData):
    await event.chat.join_room(TARGET_CHANNEL)
    print("Bot is ready!")

async def on_message(msg: ChatMessage):
    print(f"{msg.user.display_name} - {msg.text}")

# Function to continuously check the screen for the target
def screen_has_target(sct):
    screenshot = sct.grab(sct.monitors[MONITOR_INDEX])
    screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)

    for scale in np.linspace(0.5, 1.5, 20):
        new_w, new_h = int(w*scale), int(h*scale)
        if new_w > screen_img.shape[1] or new_h > screen_img.shape[0]:
            continue
        resized_target = cv2.resize(target, (new_w, new_h))
        res = cv2.matchTemplate(screen_img, resized_target, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val >= THRESHOLD:
            print(f"Target detected! Scale: {scale}, Max val: {max_val}")
            return True
    return False

# Main bot + image detection loop
async def run_bot():
    bot = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(bot, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await bot.set_user_authentication(token, USER_SCOPE, refresh_token)

    chat = await Chat(bot)
    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)
    chat.start()
    print("Chat started. Listening for messages...")

    try:
        with mss.mss() as sct:
            while True:
                if screen_has_target(sct):
                    # Send Twitch chat message
                    await chat.send_message(TARGET_CHANNEL, "Target image has been detected, chat message has been sent")
                    # Optional: wait a few seconds to prevent spamming
                    await asyncio.sleep(5)
                else:
                    await asyncio.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("Stopping bot...")
    finally:
        chat.stop()
        await bot.close()
        print("Bot stopped.")

# Run the bot
bot_loop = asyncio.new_event_loop()
asyncio.set_event_loop(bot_loop)
bot_loop.run_until_complete(run_bot())
bot_loop.close()
