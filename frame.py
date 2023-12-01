import cv2
import pygetwindow as gw
import pyautogui
import csv
import datetime
import numpy as np
import os

# Set up video writer with H.264 codec
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output_file_path = 'screen_record_with_timestamp.mp4'

# Get the currently active window
active_window = gw.getActiveWindow()

if active_window is None:
    print('Error: No active window found.')
    exit()

# Get the window size
width, height = active_window.size

# Initialize video writer
out = cv2.VideoWriter(output_file_path, fourcc, 20.0, (width, height))
# Create a directory to store individual frames
frames_directory = 'frames'
os.makedirs(frames_directory, exist_ok=True)

# Open a CSV file for writing timestamps and frame paths
csv_file_path = 'timestamps_and_frames.csv'
csv_file = open(csv_file_path, 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Timestamp', 'Frame Path'])

try:
    while True:
        # Capture the screen of the active window
        screenshot = pyautogui.screenshot(region=(active_window.left, active_window.top, width, height))
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Get the current timestamp
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        # Save the frame as an image file
        frame_filename = f'{frames_directory}/{timestamp.replace(":", "_").replace(".", "_")}.png'
        cv2.imwrite(frame_filename, frame)

         # Write the timestamp and frame path to the CSV file
        csv_writer.writerow([timestamp, frame_filename])

        # Write the frame to the video file
        out.write(frame)

except KeyboardInterrupt:
    # Release resources on keyboard interrupt
    out.release()
    csv_file.close()
    print("Recording stopped.")

# Release resources when finished
out.release()
csv_file.close()