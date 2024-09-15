from playwright.sync_api import sync_playwright
import os
import time
import subprocess

# ENTER YOUR OWN CREDENTIALS
INSTAGRAM_USERNAME = 'tadaima47'
INSTAGRAM_PASSWORD = ''

def scrape_instagram_reels(username, password, target_users):
    # Ensure the output directory exists
    output_dir = 'Y:\\.Tadaima81\\webscrapedvideos'
    os.makedirs(output_dir, exist_ok=True)

    reel_urls = []

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()

        # Navigate to the login page
        page.goto("https://www.instagram.com/accounts/login/")
        
        # Handle cookie consent
        try:
            page.wait_for_selector('button:has-text("Allow All Cookies")', timeout=5000)
            page.click('button:has-text("Allow All Cookies")')
        except Exception as e:
            print("Cookie consent button not found or already accepted.", e)
        
        # Login to Instagram
        page.wait_for_selector('input[name="username"]')
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button:has-text("Log In")')

        # Wait for login to complete
        try:
            page.wait_for_selector('svg[aria-label="Home"]', timeout=15000)
            print("Login successful.")
        except Exception as e:
            print("Login failed or took too long.", e)
            browser.close()
            return reel_urls

        for target_user in target_users:
            print(f"Navigating to user: {target_user}")
            # Navigate to the target user's page
            page.goto(f"https://www.instagram.com/{target_user}/")
            page.wait_for_load_state('networkidle')

            # Scroll to load more content
            last_height = page.evaluate('document.body.scrollHeight')
            while True:
                page.evaluate('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(2)
                new_height = page.evaluate('document.body.scrollHeight')
                if new_height == last_height:
                    break
                last_height = new_height

            # Collect both Posts and Reels URLs
            reels_links = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
            for link in reels_links:
                href = link.get_attribute('href')
                if href:
                    print(f"Found URL: {href}")
                    reel_urls.append(href)

        browser.close()

    return reel_urls

def extract_post_tokens(reel_urls):
    # Extract the post shortcode from the URL
    return [url.split('/')[-2] for url in reel_urls]

def download_video_with_instaloader(post_token, output_dir, temp_dir):
    # Construct the instaloader command with the correct post shortcode format
    command = ['instaloader', '--dirname-pattern', temp_dir, '--', '-' + post_token]

    # Run instaloader for each post token
    print(f"Downloading video for post token: {post_token}")
    result = subprocess.run(
        command,
        capture_output=True, text=True
    )

    # Log output for debugging
    print("Instaloader Output:")
    print(result.stdout)
    if result.returncode == 0:
        print(f"Successfully downloaded video for token: {post_token}")
    else:
        print(f"Failed to download video for token: {post_token}")
        print("Error:", result.stderr)

def rename_videos(output_dir):
    # Rename videos in the output directory to video-(number).mp4
    video_files = [f for f in os.listdir(output_dir) if f.endswith('.mp4')]
    for index, file_name in enumerate(video_files):
        old_file_path = os.path.join(output_dir, file_name)
        new_file_name = f"video-{index + 1}.mp4"
        new_file_path = os.path.join(output_dir, new_file_name)
        os.rename(old_file_path, new_file_path)
        print(f"Renamed {old_file_path} to {new_file_path}")

def delete_non_mp4_files(directory):
    for filename in os.listdir(directory):
        if not filename.endswith(".mp4"):
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)
                print(f"Deleted non-mp4 file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

def main():
    # Username input
    users_input = input("Enter target Instagram usernames, separated by commas for multiple: ")
    target_users = [user.strip() for user in users_input.split(',')]

    # Scrape Reels and Post URLs
    reel_urls = scrape_instagram_reels(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, target_users)
    
    # Extract post tokens from the URLs
    post_tokens = extract_post_tokens(reel_urls)
    
    # Output directory for downloading
    output_dir = 'Y:\\.Tadaima81\\webscrapedvideos'
    temp_dir = 'Y:\\.Tadaima81\\temp_downloads'
    os.makedirs(temp_dir, exist_ok=True)

    # Download each video using instaloader
    for token in post_tokens:
        download_video_with_instaloader(token, output_dir, temp_dir)

    # Move videos from temp_dir to output_dir and rename them
    for file_name in os.listdir(temp_dir):
        old_file_path = os.path.join(temp_dir, file_name)
        new_file_path = os.path.join(output_dir, file_name)
        os.rename(old_file_path, new_file_path)
    
    rename_videos(output_dir)

    # Delete any non-MP4 files from the output directory
    delete_non_mp4_files(output_dir)

if __name__ == "__main__":
    main()
