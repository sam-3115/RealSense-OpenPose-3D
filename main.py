import os
import subprocess
import sys

# --- Define Python executable from venv ---
REALSENSE_PYTHON = os.path.abspath("realsense-env\\Scripts\\python.exe")

# --- Step 1: Ask for bag file path ---
bag_path = input("Enter path to .bag file: ").strip().strip('"')
if not os.path.isfile(bag_path) or not bag_path.endswith(".bag"):
    print("Invalid .bag file.")
    sys.exit(1)

# --- Step 2: Create output folder based on bag name ---
bag_name = os.path.splitext(os.path.basename(bag_path))[0]
base_output_root = r"D:\Interns\Samarth\Work\Examples"
output_dir = os.path.join(base_output_root, bag_name)
os.makedirs(output_dir, exist_ok=True)

# Set dynamic paths
color_output = os.path.join(output_dir, "color_output.avi")
depth_output = os.path.join(output_dir, "depth_output.avi")
json_output_dir = os.path.join(output_dir, "json")
os.makedirs(json_output_dir, exist_ok=True)
openpose_result = os.path.join(output_dir, "result.avi")
keypoints_3d_json = os.path.join(output_dir, "3d.json")
plot_output_html = os.path.join(output_dir, "plot.html")
limb_json = os.path.join(output_dir, "limb_distances.json")
limb_graph_dir = os.path.join(output_dir, "limb_graph")
os.makedirs(limb_graph_dir, exist_ok=True)

# --- Step 3: Run extract.py ---
print("\n[1/5] Extracting video from .bag ...")
subprocess.run([REALSENSE_PYTHON, "extract.py", bag_path, output_dir])

# --- Step 4: Run OpenPose ---
print("\n[2/5] Running OpenPose ...")
subprocess.run([
    "build\\x64\\Release\\OpenPoseDemo.exe",
    "--video", color_output,
    "--write_json", json_output_dir,
    "--write_video", openpose_result,
    "--model_pose", "BODY_135",
    #"--render_pose", "0"
])

# --- Step 5: Run 3dconvert.py ---
print("\n[3/5] Converting to 3D coordinates ...")
subprocess.run([REALSENSE_PYTHON, "3dconvert.py", bag_path, json_output_dir, keypoints_3d_json])

# --- Step 6: Run plotvideo.py (can use system Python) ---
print("\n[4/5] Plotting 3D animation ...")
subprocess.run(["python", "plotvideo.py", keypoints_3d_json, plot_output_html])

# --- Step 7: Run limbgraph.py (can use system Python) ---
print("\n[5/5] Drawing limb distance graphs ...")
subprocess.run(["python", "limbgraph.py", keypoints_3d_json, limb_json, limb_graph_dir])

print("\n All steps completed! Results saved in:", output_dir)
