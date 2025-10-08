
#RealSense .bag File Color and Depth Extraction
#- Extract color and depth frames
#- Convert and visualize the depth data using a colormap
#- Save two separate `.mp4` video files

import pyrealsense2 as rs
import cv2
import os
import numpy as np

import sys

bag_path = sys.argv[1]
output_path = sys.argv[2]

# Paths
BAG_PATH = bag_path
OUTPUT_PATH = output_path

os.makedirs(OUTPUT_PATH, exist_ok=True)

# Output video file names
OUTPUT_COLOR_VIDEO = os.path.join(OUTPUT_PATH, "color_output.avi")
OUTPUT_DEPTH_VIDEO = os.path.join(OUTPUT_PATH, "depth_output.avi")

#prints path
print(f"Output color video: {OUTPUT_COLOR_VIDEO}")
print(f"Output depth video: {OUTPUT_DEPTH_VIDEO}")

#  Start RealSense Pipeline
pipeline = rs.pipeline()
config = rs.config()
# Use recorded .bag file and Enable all available streams 
config.enable_device_from_file(BAG_PATH, repeat_playback=False) 
config.enable_all_streams()

#Start streaming pipeline
profile = pipeline.start(config)
device = profile.get_device()
playback = device.as_playback()
playback.set_real_time(False)  

# Get stream info (frame size and frame rate)
color_stream = profile.get_stream(rs.stream.color)
video_width = color_stream.as_video_stream_profile().width()
video_height = color_stream.as_video_stream_profile().height()
fps = int(color_stream.as_video_stream_profile().fps())

print(f"Stream resolution: {video_width}x{video_height} @ {fps} FPS")

# Initialize video writers
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
color_out = cv2.VideoWriter(OUTPUT_COLOR_VIDEO, fourcc, fps, (video_width, video_height))
depth_out = cv2.VideoWriter(OUTPUT_DEPTH_VIDEO, fourcc, fps, (video_width, video_height))

# Checks if video writers opened successfully
if not color_out.isOpened() or not depth_out.isOpened():
    print("Error: Could not open one or both video writers.")
    pipeline.stop()
    exit(1)

# Frame processing loop 
frame_idx = 0
last_timestamp = None
no_frame_count = 0
MAX_NO_FRAME_COUNT = 50

try:
    while True:
        try:
            # Wait for the next set of frames
            frames = pipeline.wait_for_frames(timeout_ms=1000)
        except Exception as e:
            print(f"Playback ended or error occurred: {e}")
            break

        if not frames:
            # Count how many times no frame is received
            no_frame_count += 1
            if no_frame_count > MAX_NO_FRAME_COUNT:
                print("No frames received for too long, exiting.")
                break
            continue
        
        # Reset missing frame counter if frame received
        no_frame_count = 0

        # Get color and depth frames
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()

        if not color_frame or not depth_frame:
            print(f"No valid frames at index {frame_idx}, skipping...")
            continue
        
        # Skip duplicate frames based on timestamp
        timestamp = color_frame.get_timestamp()
        if timestamp == last_timestamp:
            continue  
        last_timestamp = timestamp

        # Convert and write color 
        color_image = np.asanyarray(color_frame.get_data())
        color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR) # Convert to BGR for OpenCV
        color_out.write(color_image)

        # Convert and write depth 
        depth_image = np.asanyarray(depth_frame.get_data())
        depth_colormap = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_image, alpha=0.03), # Convert depth to 8-bit for display
            cv2.COLORMAP_JET # Apply false color map for visualization
        )
        depth_out.write(depth_colormap)

        if frame_idx % 50 == 0:
            print(f"Writing frame {frame_idx}")

        frame_idx += 1

except Exception as e:
    print(f"Exception during writing: {e}")

finally:
    pipeline.stop()
    color_out.release()
    depth_out.release()
    cv2.destroyAllWindows()
    print(f"Color video: {OUTPUT_COLOR_VIDEO}")
    print(f"Depth video: {OUTPUT_DEPTH_VIDEO}")










