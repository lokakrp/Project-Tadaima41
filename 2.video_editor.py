import os
import random
from moviepy.editor import VideoFileClip, clips_array

def combine_videos(web_scraped_video_path, tang_video_path, output_path):
    # Load the video clips
    web_scraped_clip = VideoFileClip(web_scraped_video_path)
    tang_clip = VideoFileClip(tang_video_path)

    # Resize the web scraped video to fit the top part of the final video
    web_scraped_resized = web_scraped_clip.resize(height=tang_clip.h - 100)

    # Create a combined clip with the web scraped video on top and the tang video at the bottom
    final_clip = clips_array([[web_scraped_resized], [tang_clip]])

    # Write the result to a file
    final_clip.write_videofile(output_path, codec='libx264')

def main():
    # Define folder paths
    webscraped_folder = 'webscrapedvideos'
    edited_folder = 'editedvideos'
    tang_video_path = 'tang.mp4'

    # Ensure both folders exist
    os.makedirs(webscraped_folder, exist_ok=True)
    os.makedirs(edited_folder, exist_ok=True)

    # Get a list of video files in the webscrapedvideos folder
    video_files = [f for f in os.listdir(webscraped_folder) if f.endswith('.mp4')]

    if not video_files:
        print("No video files found in the webscrapedvideos folder.")
        return

    for i, video_file in enumerate(video_files):
        web_scraped_video_path = os.path.join(webscraped_folder, video_file)
        output_path = os.path.join(edited_folder, f'combined_video_{i+1}.mp4')
        
        # Combine the videos and save the output
        combine_videos(web_scraped_video_path, tang_video_path, output_path)
        print(f"Video '{video_file}' has been processed and saved to {output_path}")

if __name__ == "__main__":
    main()
