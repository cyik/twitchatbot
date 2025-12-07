import cv2
import numpy as np
import mss
import time
import threading
import asyncio
import requests
from twitchio.ext import commands

# ======================================================
#                 USER CONFIGURATION
# ======================================================
CLIENT_ID = "zm9ug03fux0cf35xlocjgf59gw42zp"
CLIENT_SECRET = "bv4dqt1a0pljx1n2i2qaybu0ojj7sy"
ACCESS_TOKEN = "7pbd0jmc81ipd4ruprbiovebofmylz"      # From TwitchTokenGenerator (Access Token)
BOT_NICK = "yixl67"
CHANNEL = "Queensell"
TARGET_IMG = "squadeliminated.png"

DETECTION_INTERVAL = 1        # seconds between checks
TRIGGER_COOLDOWN = 300        # 5 minutes
MATCH_THRESHOLD = 0.8
# ======================================================


# ------------------------------
# Automatically fetch bot user ID
# ------------------------------
def get_bot_user_id():
    url = "https://api.twitch.tv/helix/users"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Client-Id": CLIENT_ID,
    }
    resp = requests.get(url, headers=headers)
    data = resp.json()
    if "data" in data and len(data["data"]) > 0:
        return data["data"][0]["id"]
    else:
        print("ERROR: Could not fetch bot user ID.")
        print(data)
        exit()

BOT_USER_ID = get_bot_user_id()
print(f"Bot User ID: {BOT_USER_ID}")


# --------------------------------
# TwitchIO 3.x bot initialization
# --------------------------------
bot = commands.Bot(
    token=ACCESS_TOKEN,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    bot_id=BOT_USER_ID,
    prefix="!",
    initial_channels=[CHANNEL]
)

message_queue = []


# -----------------------------
#        IMAGE DETECTION
# -----------------------------
def detect_image():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = np.array(sct.grab(monitor))
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        template = cv2.imread(TARGET_IMG, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"ERROR: Missing trigger image '{TARGET_IMG}'")
            return False

        res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= MATCH_THRESHOLD)

        return len(loc[0]) > 0


def detection_loop():
    while True:
        if detect_image():
            message_queue.append("Image detected!")
        time.sleep(DETECTION_INTERVAL)


threading.Thread(target=detection_loop, daemon=True).start()


# -----------------------------
#       BOT EVENT LOOP
# -----------------------------
@bot.event()
async def event_ready():
    print(f"Logged in as {BOT_NICK}")
    asyncio.create_task(message_sender())


async def message_sender():
    last_sent = 0
    while True:
        if message_queue and time.time() - last_sent >= TRIGGER_COOLDOWN:
            msg = message_queue.pop(0)
            chan = bot.get_channel(CHANNEL)
            if chan:
                await chan.send(msg)
                print("Sent:", msg)
                last_sent = time.time()
        await asyncio.sleep(1)


# -----------------------------
#           RUN BOT
# -----------------------------
if __name__ == "__main__":
    bot.run()
