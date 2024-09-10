from playwright.sync_api import sync_playwright
import requests
import os

INSTAGRAM_USERNAME = 'tadaima81'
INSTAGRAM_PASSWORD = 'Aj>Ri]*^W%62dLq'

def scrape_instagram_videos(username, password, target_users):
    # Ensure the output directory exists
    output_dir = 'webscrapedvideos'
    os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # to run in background
        page = browser.new_page()

        # Login
        page.goto("https://www.instagram.com/accounts/login/")
        page.wait_for_selector('input[name="username"]')  # Adjust selector if needed
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_navigation()

        for target_user in target_users:
            # Navigate to target user's page
            page.goto(f"https://www.instagram.com/{target_user}/")
            page.wait_for_load_state('networkidle')

            # Collect video URLs
            video_urls = [video.get_attribute('src') for video in page.query_selector_all('video')]

            # Download videos
            for i, url in enumerate(video_urls):
                response = requests.get(url)
                video_path = os.path.join(output_dir, f"{target_user}_video_{i}.mp4")
                with open(video_path, 'wb') as file:
                    file.write(response.content)

        browser.close()

def main():
    # Username inputter
    users_input = input("Enter target Instagram usernames, separated by commas for multiple: ")
    target_users = [user.strip() for user in users_input.split(',')]
    
    # Function using my credentials
    scrape_instagram_videos(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, target_users)

if __name__ == "__main__":
    main()
