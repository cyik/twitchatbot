import cv2
import mss
import numpy as np
import time

TARGET_IMAGE_PATH = r"C:\Users\cheny\OneDrive\Desktop\ITA\twitchatbot\squadeliminated.png"
MONITOR_INDEX = 1  # primary monitor
THRESHOLD = 0.7

# Load target image in grayscale
target = cv2.imread(TARGET_IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
if target is None:
    print(f"Error: Could not load {TARGET_IMAGE_PATH}")
    exit()
h, w = target.shape
print(f"Target image loaded. Shape: {target.shape}")

with mss.mss() as sct:
    print("Starting continuous screen check. Press Ctrl+C to stop.")
    try:
        while True:
            screenshot = sct.grab(sct.monitors[MONITOR_INDEX])
            screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)

            found = False
            for scale in np.linspace(0.5, 1.5, 20):
                new_w, new_h = int(w*scale), int(h*scale)
                if new_w > screen_img.shape[1] or new_h > screen_img.shape[0]:
                    continue
                resized_target = cv2.resize(target, (new_w, new_h))
                res = cv2.matchTemplate(screen_img, resized_target, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)
                if max_val >= THRESHOLD:
                    print(f"Target detected! Scale: {scale}, Max val: {max_val}")
                    found = True
                    break

            if not found:
                print("Target not detected on this monitor.")
            time.sleep(1)  # check every second
    except KeyboardInterrupt:
        print("Stopped by user.")
