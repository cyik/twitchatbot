import mss
import cv2
import numpy as np

with mss.mss() as sct:
    screenshot = sct.grab(sct.monitors[0])  # primary monitor
    screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)
    cv2.imwrite("screen_test.png", screen_img)  # save to check

print("Screenshot saved. Open screen_test.png to see what the bot sees.")
