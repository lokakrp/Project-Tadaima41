from playwright.sync_api import sync_playwright
import os
import random
import configparser
import schedule
import time

# Replace with your own credentials!
INSTAGRAM_USERNAME = 'tadaima47'
INSTAGRAM_PASSWORD = ''

# Load captions from the 'caption.ini' file
def load_random_caption():
    config = configparser.ConfigParser()
    with open('caption.ini', 'r', encoding='utf-8') as file:
        config.read_file(file)
    
    captions = [config.get('CAPTIONS', f'caption{i}') for i in range(1, len(config['CAPTIONS']) + 1)]
    return random.choice(captions)

def upload_video_to_instagram(page, video_path, caption):
    try:
        # Navigate to the Create section
        create_button = page.locator('text="Create"')
        if create_button.is_visible():
            create_button.click()
            print("Navigated to Create section.")
            page.wait_for_timeout(5000)
        else:
            print("Create text not found or not visible.")
        
        post_button = page.locator('text="Post"')
        if post_button.is_visible():
            post_button.click()
            print("Post button clicked.")
            page.wait_for_timeout(5000)
        else:
            print("Post button not found or not visible.")

        # Look for file input directly and upload the video
        try:
            file_input = page.locator('input[type="file"]')
            file_input.set_input_files(video_path)
            print(f"Uploaded file: {video_path}")
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"Failed to upload the file: {e}")

        # Find and click the "OK" button
        try:
            ok_button = page.wait_for_selector('button:has-text("OK")', timeout=3000)
            if ok_button.is_visible():
                ok_button.click()
                print("OK button clicked.")
                page.wait_for_timeout(2000)
            else:
                print("OK button not found or not visible.")
        except Exception as e:
            print(f"An error occurred while finding or clicking the OK button: {e}")

        # Select crop and set to 9:16
        select_crop_button = page.locator('[aria-label="Select crop"]')
        if select_crop_button.is_visible():
            select_crop_button.click()
            print("Select Crop button clicked.")
            page.wait_for_timeout(2000)
        else:
            print("Select Crop button not found or not visible.")

        nine_sixteen_button = page.locator('text="9:16"')
        if nine_sixteen_button.is_visible():
            nine_sixteen_button.click()
            print("9:16 button clicked.")
            page.wait_for_timeout(2000)
        else:
            print("9:16 button not found or not visible.")

        # Click "Next" twice to proceed
        next_button = page.locator('text="Next"')
        if next_button.is_visible():
            next_button.click()
            print("First 'Next' button clicked.")
            page.wait_for_timeout(2000)
            next_button.click()
            print("Second 'Next' button clicked.")
        else:
            print("'Next' button not found or not visible.")

        # Add the caption
        try:
            contenteditable_div = page.wait_for_selector('div[aria-placeholder="Write a caption..."]', timeout=10000)
            if contenteditable_div:
                contenteditable_div.click()
                contenteditable_div.fill(caption)
                print("Caption added.")
            else:
                print("Contenteditable div not found.")
        except Exception as e:
            print(f"An error occurred while adding the caption: {e}")

        # Click "Share" to upload
        share_button = page.locator('text="Share"')
        if share_button.is_visible():
            share_button.click()
            print("Share button clicked.")
            page.wait_for_timeout(10000)
        else:
            print("Share button not found or not visible.")

        # Wait for the text "Your reel has been shared." to appear
        shared_text_locator = page.locator('text="Your reel has been shared."')
        shared_text_locator.wait_for(state='visible', timeout=10000)  

        # Once the text is visible, locate the "Close" button by its aria-label attribute
        close_button = page.locator('svg[aria-label="Close"]')
        
        # Check if the button is visible
        if close_button.is_visible():
            close_button.click()
            print("Close button clicked to close the dialog.")
            page.wait_for_timeout(2000)  # Wait for the dialog to close
        else:
            print("Close button not found or not visible.")

    except Exception as e:
        print(f"An error occurred while finding or clicking the close button: {e}")
        page.screenshot(path='error_screenshot.png')  


# Process and upload a random video
def process_videos(page):
    edited_folder = 'editedvideos'
    video_files = [f for f in os.listdir(edited_folder) if f.endswith('.mp4')]

    if not video_files:
        print("No video files found in the editedvideos folder.")
        return

    video_file = random.choice(video_files)
    video_path = os.path.join(edited_folder, video_file)
    
    caption = load_random_caption()
    
    try:
        upload_video_to_instagram(page, video_path, caption)
        os.remove(video_path)
        print(f"Video '{video_file}' has been uploaded with the caption '{caption}' and deleted from local folder.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main function to handle the scheduling and browser management
def schedule_uploads():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to the login page
            page.goto("https://www.instagram.com/accounts/login/")
            
            # Handle cookie consent
            try:
                page.wait_for_selector('button:has-text("Allow All Cookies")', timeout=5000)
                page.click('button:has-text("Allow All Cookies")')
                print("Cookie consent accepted.")
            except Exception as e:
                print("Cookie consent button not found or already accepted.", e)
            
            # Login to Instagram
            try:
                page.wait_for_selector('input[name="username"]')
                page.fill('input[name="username"]', INSTAGRAM_USERNAME)
                page.fill('input[name="password"]', INSTAGRAM_PASSWORD)
                page.click('button:has-text("Log In")')
                page.wait_for_selector('svg[aria-label="Home"]', timeout=15000)
                print("Login successful.")
            except Exception as e:
                print("Login failed or took too long.", e)
                return

            # Schedule the uploads to run every minute
            print("Scheduling the uploads to run every minute...")
            schedule.every(1).minutes.do(lambda: process_videos(page))

            # Run the scheduling loop
            while True:
                schedule.run_pending()
                time.sleep(1)
        finally:
            browser.close()

# Start the scheduler
if __name__ == "__main__":
    schedule_uploads()
