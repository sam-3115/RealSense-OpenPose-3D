'''
3D Limb distances graph
- Loads 3D pose keypoints from a JSON file
- Define limb connections (body and hands).
- Calculates per frame distance changes (dx, dy, dz, and Euclidean) for each limb.
- Saves the distance data as a new JSON file.
- Generates and saves plots showing how each limb’s distance changes across frames.

'''

import numpy as np
import json
import os
import matplotlib.pyplot as plt


import sys
input_path = sys.argv[1]          # input 3d.json
json_output_path = sys.argv[2]    # output limb_distances.json
plot_output_dir = sys.argv[3]     # directory to save plots


# Load your input JSON file 
#input_path = r"D:\Interns\Samarth\openpose\output\3d1.json"

with open(input_path, "r") as f:
    data = json.load(f)  # This is a list of frames

#  Define the limb pairs (by keypoint indices)
left_hand_pairs = [
    (25, 26), (26, 27), (27, 28),          
    (29, 30), (30, 31), (31, 32),          
    (33, 34), (34, 35), (35, 36),          
    (37, 38), (38, 39), (39, 40),          
    (41, 42), (42, 43), (43, 44),          
    (9, 25), (9, 29), (9, 33), (9, 41), (9, 37)    # Wrist to finger base connections
]


# Right Hand (45–64)
right_hand_pairs = [
    (45, 46), (46, 47), (47, 48),                
    (49, 50), (50, 51), (51, 52),        
    (53, 54), (54, 55), (55, 56),        
    (57, 58), (58, 59), (59, 60),       
    (61, 62), (62, 63), (63, 64),
    (10,45),(10,49), (10,53), (10,61),(10,57)   # Wrist to finger base connections
]       


limb_pairs = [
    (5, 7), (5, 11),(5, 17), (6, 8),(6, 12),(6, 17), (7, 9), (8, 10), 
    (10, 48), (10, 52), (10, 56), (10, 60), (10, 64),(9,28),(9,32),(9,36),(9,40),(9,44)
] + left_hand_pairs + right_hand_pairs

# Process distances for each frame 
all_distances = []

# Interpolates missing (NaN) values
def interpolate_nans(data):
    data = np.array(data, dtype=np.float64)
    nans = np.isnan(data)
    not_nans = ~nans
    indices = np.arange(len(data))
    if np.sum(not_nans) > 1:
        interpolated = np.interp(indices, indices[not_nans], data[not_nans])
        return interpolated
    else:
        return data


# Define your desired frame range
frame_start = 30
frame_end = 170

scale = 100  # meters to centimeters, adjust if needed

# Loop through each frame in input data
for frame_data in data:
    frame_idx = frame_data["frame"]
    if not (frame_start <= frame_idx <= frame_end):
        continue # Skip frames outside range
    keypoints = np.array(frame_data["keypoints_3d"])  # Shape: (num_keypoints, 3)
    frame_result = {"frame": frame_idx, "limbs": {}}

    # Process each limb pair
    for kp1, kp2 in limb_pairs:
        try:
            pt1 = keypoints[kp1]
            pt2 = keypoints[kp2]
        except IndexError:
            continue # Skip if keypoint index out of range

        if pt1 is None or pt2 is None:
            continue # Skip if missing keypoints

        pt1 = np.array(pt1, dtype=np.float64)
        pt2 = np.array(pt2, dtype=np.float64)

        if np.any(np.isnan(pt1)) or np.any(np.isnan(pt2)):
            continue  # Skip if coordinates are NaN


        pt1 = np.array(pt1)
        pt2 = np.array(pt2)
        # Compute distances (in cm)
        diff = np.abs(pt2 - pt1) * scale
        euclidean = np.linalg.norm(pt2 - pt1) * scale

        limb_name = f"{kp1}_{kp2}"
        frame_result["limbs"][limb_name] = {
            "dx": float(diff[0]),
            "dy": float(diff[1]),
            "dz": float(diff[2]),
            "euclidean": float(euclidean)
        }

    all_distances.append(frame_result)

# Save distances to JSON 
os.makedirs("output", exist_ok=True)
#json_output_path = r"D:\Interns\Samarth\openpose\output\limb_distances.json"

with open(json_output_path, "w") as f:
    json.dump(all_distances, f, indent=2)

print(f"Saved limb distances to {json_output_path}")

# Plot each limbs distances over frames 
#plot_output_dir =r"D:\Interns\Samarth\openpose\output\limb_graph"
os.makedirs(plot_output_dir, exist_ok=True)

# Get list of all limb names
limb_names = all_distances[0]['limbs'].keys()

# Plot each limb
for limb in limb_names:
    frames = []
    dx_vals = []
    dy_vals = []
    dz_vals = []
    euclidean_vals = []
    # Gather values across all frames
    for frame_result in all_distances:
        frames.append(frame_result["frame"])
        limb_data = frame_result["limbs"].get(limb)
        if limb_data:
            dx_vals.append(limb_data["dx"])
            dy_vals.append(limb_data["dy"])
            dz_vals.append(limb_data["dz"])
            euclidean_vals.append(limb_data["euclidean"])
        else:
            dx_vals.append(np.nan)
            dy_vals.append(np.nan)
            dz_vals.append(np.nan)
            euclidean_vals.append(np.nan)

    # Interpolate NaNs after collecting all frame data
    dx_np = interpolate_nans(np.array(dx_vals, dtype=np.float64))
    dy_np = interpolate_nans(np.array(dy_vals, dtype=np.float64))
    dz_np = interpolate_nans(np.array(dz_vals, dtype=np.float64))
    euclidean_np = interpolate_nans(np.array(euclidean_vals, dtype=np.float64))
    frames_np = np.array(frames)

    # Plot interpolated data
    fig, axs = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
    fig.suptitle(f"Limb {limb} Distance Changes vs Frames")

    axs[0].plot(frames_np, dx_np, color='r')
    axs[0].set_ylabel("Δx")
    axs[0].grid(True)

    axs[1].plot(frames_np, dy_np, color='g')
    axs[1].set_ylabel("Δy")
    axs[1].grid(True)

    axs[2].plot(frames_np, dz_np, color='b')
    axs[2].set_ylabel("Δz")
    axs[2].grid(True)

    axs[3].plot(frames_np, euclidean_np, color='k')
    axs[3].set_ylabel("Euclidean")
    axs[3].set_xlabel("Frame")
    axs[3].grid(True)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plot_path = os.path.join(plot_output_dir, f"limb_{limb}.png")
    plt.savefig(plot_path)
    plt.close(fig)


print(f"Saved plots to {plot_output_dir}")
