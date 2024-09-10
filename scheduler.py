import schedule
import time
from uploader import process_videos  # Update import path if necessary

def get_schedule_interval():
    while True:
        try:
            minutes = int(input("Enter the scheduling interval in minutes: "))
            if minutes > 0:
                return minutes
            else:
                print("Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

def main():
    interval = get_schedule_interval()
    
    # Set the schedule
    schedule.every(interval).minutes.do(process_videos)

    print(f"Scheduling video uploads every {interval} minutes.")

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
