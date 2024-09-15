import os
from moviepy.editor import VideoFileClip, clips_array, concatenate_videoclips, AudioFileClip

def resize_and_crop_video(video_path, target_width, target_height, output_path):
    # Load video
    clip = VideoFileClip(video_path)
    
    # Resize the video to the target width while maintaining aspect ratio
    resized_clip = clip.resize(width=target_width)
    
    # Calculate the center crop coordinates
    x_center = resized_clip.w / 2
    y_center = resized_clip.h / 2
    crop_x1 = x_center - target_width / 2
    crop_x2 = x_center + target_width / 2
    crop_y1 = y_center - target_height / 2
    crop_y2 = y_center + target_height / 2
    
    # Crop video to target dimensions
    cropped_clip = resized_clip.crop(x1=crop_x1, x2=crop_x2, y1=crop_y1, y2=crop_y2)
    
    # Write the result to a file without audio
    cropped_clip = cropped_clip.set_audio(None)
    cropped_clip.write_videofile(output_path, codec='libx264')

def extract_audio(video_path, audio_path):
    # Load video
    clip = VideoFileClip(video_path)
    
    # Extract and write audio to file
    audio = clip.audio
    audio.write_audiofile(audio_path)

def combine_videos(web_scraped_video_path, tang_video_path, output_path):
    # Define final dimensions for 9:16 aspect ratio reel
    final_width = 576  # Width of tang clip
    final_height = int(final_width * (16 / 9))  # Height for 9:16 aspect ratio

    # Define dimensions for the top and bottom parts of the video
    tang_height = 522
    web_scraped_height = final_height - tang_height

    # Define the target duration
    target_duration = 17  # Target duration in seconds

    # Load tang video to get its duration
    tang_clip = VideoFileClip(tang_video_path)
    tang_duration = tang_clip.duration
    print(f"Duration of tang video: {tang_duration} seconds")

    # Resize and crop web scraped video to fit the top part
    web_scraped_resized_path = "temp_web_scraped_resized.mp4"
    resize_and_crop_video(web_scraped_video_path, final_width, web_scraped_height, web_scraped_resized_path)

    # Resize tang video to fit the bottom part
    tang_resized_path = "temp_tang_resized.mp4"
    resize_and_crop_video(tang_video_path, final_width, tang_height, tang_resized_path)

    # Load resized videos
    web_scraped_clip = VideoFileClip(web_scraped_resized_path)
    tang_clip = VideoFileClip(tang_resized_path)

    # Loop the web scraped video to ensure it covers at least the target duration
    web_scraped_duration = web_scraped_clip.duration
    print(f"Duration of web-scraped video: {web_scraped_duration} seconds")

    # Calculate the number of repetitions needed
    num_reps = int(target_duration / web_scraped_duration) + 1
    
    # Create a list of the web-scraped video repeated
    web_scraped_clips = [web_scraped_clip] * num_reps
    web_scraped_looped_clip = concatenate_videoclips(web_scraped_clips)

    # Trim the looped video to the exact length of target duration
    web_scraped_looped_clip = web_scraped_looped_clip.subclip(0, target_duration)

    # Print duration of looped clip
    print(f"Duration of looped web-scraped video: {web_scraped_looped_clip.duration} seconds")

    # Stack the clips vertically
    final_clip = clips_array([[web_scraped_looped_clip], [tang_clip]])

    # Extract and write the audio from tang.mp4
    tang_audio_path = "temp_tang_audio.mp3"
    extract_audio(tang_video_path, tang_audio_path)

    # Set the audio of the final clip to the audio from tang.mp4
    final_audio = AudioFileClip(tang_audio_path)
    final_clip = final_clip.set_audio(final_audio)

    # Trim the final clip to the target duration of 17 seconds
    final_clip = final_clip.subclip(0, target_duration)

    # Write the result to a file
    final_clip.write_videofile(output_path, codec='libx264')

    # Clean up temporary files
    if os.path.isfile(web_scraped_resized_path):
        os.remove(web_scraped_resized_path)
    if os.path.isfile(tang_resized_path):
        os.remove(tang_resized_path)
    if os.path.isfile(tang_audio_path):
        os.remove(tang_audio_path)


def main():
    # Define folder paths
    webscraped_folder = ''
    edited_folder = 'Y:\\.Tadaima81\\editedvideo'
    tang_video_path = 'Y:\\.Tadaima81\\tang.mp4'

    # Ensures folders exist
    os.makedirs(webscraped_folder, exist_ok=True)
    os.makedirs(edited_folder, exist_ok=True)

    # Process files with names like video-{index}.mp4
    i = 1
    while True:
        web_scraped_video_path = os.path.join(webscraped_folder, f'video-{i}.mp4')
        if not os.path.isfile(web_scraped_video_path):
            break  # Exit loop if file does not exist

        output_path = os.path.join(edited_folder, f'combined_video_{i}.mp4')
        
        # Combine the videos and save the output
        try:
            combine_videos(web_scraped_video_path, tang_video_path, output_path)
            print(f"Video 'video-{i}.mp4' has been processed and saved to {output_path}")

            # Delete the original video file after processing
            os.remove(web_scraped_video_path)
            print(f"Deleted original video file: {web_scraped_video_path}")
        
        except Exception as e:
            print(f"Error processing file {web_scraped_video_path}: {e}")

        i += 1

if __name__ == "__main__":
    main()
