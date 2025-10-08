# 🖱️ 3D Coordinates from RealSense Camera using Mouse Click

**3D Human Pose Estimation and Analysis using Intel RealSense & OpenPose**

---

## 🧠 Overview
This document demonstrates how to **retrieve 3D real-world coordinates** (X, Y, Z) from any pixel position on an RGB image captured using the **Intel RealSense Depth Camera**.

By clicking a point on the RGB image, the system reads the **depth value** from the corresponding location in the aligned depth map and converts it into 3D coordinates.

---

## ⚙️ Process Flow

1. **Capture** RGB and depth frames from RealSense (`.bag` file).  
2. **Align** the depth frame with the color frame using `pyrealsense2.align()`.  
3. **Display** the RGB frame using OpenCV.  
4. **On Mouse Click:**  
   - Get pixel coordinates `(u, v)`.  
   - Retrieve depth value `Z = depth_frame.get_distance(u, v)`.  
   - Compute 3D coordinates `(X, Y, Z)` using intrinsic parameters.  
5. **Display/Print** the resulting 3D coordinates in real time.

---

