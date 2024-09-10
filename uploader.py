from playwright.sync_api import sync_playwright
import os
import random

INSTAGRAM_USERNAME = 'tadaima81'
INSTAGRAM_PASSWORD = 'Aj>Ri]*^W%62dLq'

def upload_video_to_instagram(video_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Login
        page.goto("https://www.instagram.com/accounts/login/")
        page.wait_for_selector('input[name="username"]')
        page.fill('input[name="username"]', INSTAGRAM_USERNAME)
        page.fill('input[name="password"]', INSTAGRAM_PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_navigation()

        # Upload video
        page.goto("https://www.instagram.com/create/style/")
        page.wait_for_selector('input[type="file"]')
        page.click('input[type="file"]')
        page.set_input_files('input[type="file"]', video_path)
        page.click('button[type="submit"]')
        page.wait_for_timeout(10000)  # Wait for upload to complete

        browser.close()

def process_videos():
    edited_folder = 'editedvideos'  # Ensure this is the correct folder name

    # Get a list of video files in the editedvideos folder
    video_files = [f for f in os.listdir(edited_folder) if f.endswith('.mp4')]

    if not video_files:
        print("No video files found in the editedvideos folder.")
        return

    # Select a random video file
    video_file = random.choice(video_files)
    video_path = os.path.join(edited_folder, video_file)
    
    try:
        upload_video_to_instagram(video_path)
        os.remove(video_path)  # Delete the video from the local folder
        print(f"Video '{video_file}' has been uploaded and deleted from local folder.")
    except Exception as e:
        print(f"An error occurred: {e}")

