import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from elevenlabs import generate, save, set_api_key
from moviepy.editor import *
import argparse
import random
from Tiktok_uploader import uploadVideo

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--upload", action="store_true")
parser.add_argument("--music", action="store_true")
args = parser.parse_args()

set_api_key(os.getenv("ELEVENLABS"))

# Create website screenshot
print("Generowanie \033[95mscreenshot.png\033[0m")

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--hide-scrollbars")

mobile_emulation = {"deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 2.0}}
options.add_experimental_option("mobileEmulation", mobile_emulation)

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

driver.get("https://www.miejski.pl/losuj")

article = driver.find_element(By.TAG_NAME, "article")
title = article.find_element(By.TAG_NAME, "header").text

content = (
    title
    + "\n\n...\n\n"
    + article.find_element(By.TAG_NAME, "p").text
    + "\n\n...\n\n"
    + article.find_element(By.TAG_NAME, "blockquote").text
)

print(f"Tytuł: \x1b[34m{title}\033[0m")

# Accept cookies
driver.find_element(By.LINK_TEXT, "Rozumiem").click()

driver.save_screenshot("screenshot.png")

driver.quit()

# Create voice
print("Generowanie \033[95mvoice.mp3\033[0m")

voice = generate(text=content, voice="Bella", model="eleven_multilingual_v1")

save(voice, "voice.mp3")

# Create video
print("Generowanie \033[95mvideo.mp4\033[0m")

audio = AudioFileClip("voice.mp3")
video_clip = ImageClip("screenshot.png").set_duration(audio.duration)

if (args.music):
    music = AudioFileClip("music/" + random.choice(os.listdir("music")))
    music = music.fx(afx.volumex, 0.2)
    music = music.set_duration(audio.duration)
    final_clip = video_clip.set_audio(CompositeAudioClip([audio, music]))
else:
    final_clip = video_clip.set_audio(audio)
    
final_clip.write_videofile(
    "video.mp4",
    fps=24,
)

# Upload video
if args.upload:
    print("Przesyłanie filmu")

    session_id = os.getenv("TIKTOK")
    file = "video.mp4"
    title = title
    tags = []

    uploadVideo(session_id, file, title, tags, verbose=True)
