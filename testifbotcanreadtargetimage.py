import cv2

TARGET_IMAGE_PATH = r'C:\Users\cheny\OneDrive\Desktop\ITA\twitchatbot\apple.jpg'

target = cv2.imread(TARGET_IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
if target is None:
    print("Error: Could not load target image")
else:
    print("Target image loaded successfully! Shape:", target.shape)
