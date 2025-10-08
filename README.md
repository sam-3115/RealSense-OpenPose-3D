# 🤖 3D Human Pose Estimation and Analysis using Intel RealSense & OpenPose  

### 🧩 Internship Project – IIT (BHU), Varanasi  
---
## 🎯 Overview  
This project was developed during my internship at **IIT (BHU), Varanasi** under the **School of Biomedical Engineering**.  
It focuses on extracting and analyzing **3D human body keypoints** from videos captured using the **Intel RealSense Depth Camera** and processed through **OpenPose**.

The pipeline performs:
1. Capturing color & depth video data  
2. Detecting 2D keypoints using OpenPose  
3. Converting 2D keypoints to 3D coordinates  
4. Visualizing animated 3D skeletons  
5. Calculating limb distances and motion graphs  

---

## ⚙️ Workflow

### 1️⃣ Data Capture
- Captured RGB and Depth frames using Intel RealSense (stored as `.bag` files).  
- Extracted videos and images automatically using `extract.py` or RealSense SDK.

### 2️⃣ Pose Detection (OpenPose)
- Processed video/image data with **OpenPose** models: `BODY_25`, `BODY_25B`, `BODY_135`, and `MPI`.  
- Generated 2D body keypoints and JSON outputs.  
- Numbered and verified keypoints on both images and videos.

### 3️⃣ 2D → 3D Conversion
- Mapped 2D keypoints with corresponding depth data using `pyrealsense2`.  
- Generated real-world 3D coordinates for each body keypoint.

### 4️⃣ 3D Visualization
- Created animated 3D skeletons using **Plotly**.  
- Enabled play/pause and slider controls for frame-by-frame visualization.

### 5️⃣ Limb Distance & Motion Analysis
- Computed per-frame distance (Δx, Δy, Δz, Euclidean).  
- Plotted motion trend graphs using **Matplotlib**.  
- Analyzed movement stability and symmetry across frames.

---

## 📊 Example Output  
Each example folder contains:
- Extracted color and depth videos  
- OpenPose JSON results  
- 3D skeleton animation  
- Limb distance graphs  


---

## 🛠️ Tech Stack  
| Category | Tools / Libraries |
|-----------|------------------|
| Hardware | Intel RealSense D435 Depth Camera |
| Languages | Python, C++ |
| Libraries | OpenPose, pyrealsense2, Plotly, Matplotlib, NumPy |
| Tools | RealSense SDK, ROS, OpenPose Demo |
| OS | Windows 11 |

---

## 🧑‍🔬 Internship Details  
**Institute:** IIT (BHU), Varanasi  
**Department:** School of Biomedical Engineering  
**Role:** Research Intern  
**Duration:** 12 May – 25 June 2025  
**Affiliation:** NIT Warangal (Biotechnology, 2nd Year)

---

## 🌟 Future Scope  
- Integration of live OpenPose feed for **real-time 3D skeleton visualization**.  
- Implementing **gesture tracking and movement classification**.

---

## 📬 Contact  
If you found this useful or have questions, feel free to connect!  
📧 **Email:** samarthghogare@gmail.com
