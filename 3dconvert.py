
#Conversion of openpose 2D coordinates to 3D camera coordinates
#- Loads a recorded .bag file from an Intel RealSense camera.
#- Aligns depth frames to the color stream.
#- Loads corresponding OpenPose 2D keypoints.
#- Uses camera intrinsics and depth data to convert 2D keypoints to 3D.
#- Saves the 3D keypoints for all frames into a single JSON file.




import pyrealsense2 as rs
import numpy as np
import json
import os

import sys
bag_file = sys.argv[1]            # path to .bag file
openpose_json_dir = sys.argv[2]   # path to OpenPose json directory
output_3d_path = sys.argv[3]    

# INPUT PATHS 
#bag_file = r"C:\Users\hp\Documents\20250606_132745.bag" 
#openpose_json_dir = r"D:\Interns\Samarth\openpose\output\json"
#output_3d_path = r"D:\Interns\Samarth\openpose\output\3d.json"

# Make sure output folder exists 
os.makedirs(os.path.dirname(output_3d_path), exist_ok=True)

# RealSense setup
pipeline = rs.pipeline()
config = rs.config()
config.enable_device_from_file(bag_file, repeat_playback=False)
profile = pipeline.start(config)

# Extract camera intrinsics for deprojection
color_stream = profile.get_stream(rs.stream.color)
video_profile = color_stream.as_video_stream_profile()
intrinsics = video_profile.get_intrinsics()
print("Camera Intrinsics:", intrinsics.fx, intrinsics.fy, intrinsics.ppx, intrinsics.ppy)

# Get depth scale (convert depth units to meters)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("Depth Scale:", depth_scale)

# Align depth to color frame
align_to = rs.stream.color
align = rs.align(align_to)

# Define filters
'''
Spatial reduces noise in the depth image by smoothing neighboring pixels, especially around edges.
Temporal reduces flickering or inconsistent depth values over time (across frames)
Hole filling fill missing holes with estimated values from surrounding pixels, making the depth image more complete.
for more: https://dev.intelrealsense.com/docs/post-processing-filters
'''
spatial = rs.spatial_filter()
#temporal = rs.temporal_filter()
#hole_filling = rs.hole_filling_filter()

# Playback control for bag file 
playback = profile.get_device().as_playback()
playback.set_real_time(False)

# Get sorted list of OpenPose JSON files 
json_files = sorted(
    [f for f in os.listdir(openpose_json_dir) if f.endswith('.json')],
    key=lambda x: int(''.join(filter(str.isdigit, x)))
)
# Store 3D keypoints for each frame
all_frames_3d = []
frame_idx = 0

try:
    for json_file in json_files:
        frames = pipeline.wait_for_frames()
        if not frames:
            print("No more frames from bag.")
            break

        # Align depth frame to color frame
        aligned_frames = align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        # Skip frames missing either stream
        if not depth_frame or not color_frame:
            print("Skipping frame, missing depth or color frame.")
            continue

        # Apply filters to depth frame
        depth_frame = spatial.process(depth_frame)
        #depth_frame = temporal.process(depth_frame)
        #depth_frame = hole_filling.process(depth_frame)

        # Convert depth frame to numpy array (depth in raw units)
        depth_image = np.asanyarray(depth_frame.get_data())

        # Load OpenPose 2D keypoints JSON for current frame
        with open(os.path.join(openpose_json_dir, json_file), 'r') as f:
            pose_data = json.load(f)

        people = pose_data.get("people", [])
        keypoints_3d_all_people = []

        for person in people:
            keypoints = person.get("pose_keypoints_2d", [])

            # keypoints is flat list [x1, y1, c1, x2, y2, c2, ...]
            for i in range(0, len(keypoints), 3):
                u = int(keypoints[i])  # X coordinate
                v = int(keypoints[i + 1])  # Y coordinate
                confidence = keypoints[i + 2]
               
                # Skip low-confidence or out-of-bounds points
                if confidence < 0.1 or not (0 <= u < intrinsics.width and 0 <= v < intrinsics.height):
                    keypoints_3d_all_people.append([None, None, None])
                    continue

                # Get depth value in meters
                z = depth_image[v, u] * depth_scale
                if z == 0:
                    keypoints_3d_all_people.append([None, None, None])
                    continue

                # Deproject 2D pixel to 3D point in space
                X, Y, Z = rs.rs2_deproject_pixel_to_point(intrinsics, [u, v], z)
                keypoints_3d_all_people.append([X, Y, Z])

        # Save frame data
        all_frames_3d.append({
            "frame": frame_idx,
            "keypoints_3d": keypoints_3d_all_people
        })

        frame_idx += 1

        if playback.current_status == rs.playback_status.stopped:
            print("Playback ended.")
            break

finally:
    pipeline.stop()
    print("Processing done.")

# Save all frames data into single JSON file
with open(output_3d_path, "w") as f:
    json.dump(all_frames_3d, f, indent=2)

print(f"Saved all frames to: {output_3d_path}")
