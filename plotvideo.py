'''
Plots 3D coordinates as animation
- Loads 3D keypoints from a JSON file.
- Defines connection pairs for body, left hand, and right hand.
- Visualizes the pose data as a 3D animation using Plotly.
- Adds interactive slider and play/pause controls.
- Saves the animation as an HTML file.
'''

import json
import plotly.graph_objects as go

import sys

input_3d_json = sys.argv[1]   # 3D keypoints JSON
output_html = sys.argv[2]    

# Constants and Keypoint Offsets
H135 = 25   # Starting index of left hand keypoints
F135 = 65   # Face keypoints start index

# Connection pairs
body_connections = [
    (0, 17), 
    (0, 1), (1, 3),
    (0, 2), (2, 4),
    (17, 5), (5, 7), (7, 9),
    (17, 6), (6, 8), (8, 10),
    (5, 11), (6, 12),
    (13, 15), (14, 16),
    (15, 19), (19, 20), (15, 21),
    (16, 22), (22, 23), (16, 24)
]

left_hand_connections = [
    (9, 25), (25, 26), (26, 27), (27, 28),
    (9, 29), (29, 30), (30, 31), (31, 32),
    (9, 33), (33, 34), (34, 35), (35, 36),
    (9, 37), (37, 38), (38, 39), (39, 40),
    (9, 41), (41, 42), (42, 43), (43, 44)
]

right_hand_connections = [
    (10, H135+20), (H135+20, H135+21), (H135+21, H135+22), (H135+22, H135+23),
    (10, H135+24), (H135+24, H135+25), (H135+25, H135+26), (H135+26, H135+27),
    (10, H135+28), (H135+28, H135+29), (H135+29, H135+30), (H135+30, H135+31),
    (10, H135+32), (H135+32, H135+33), (H135+33, H135+34), (H135+34, H135+35),
    (10, H135+36), (H135+36, H135+37), (H135+37, H135+38), (H135+38, H135+39)
]
# Optional
#face_contour_connections = [(F135 + i, F135 + i + 1) for i in range(16)]

connections = body_connections + left_hand_connections + right_hand_connections 
#+ face_contour_connections

# Load JSON keypoints frames
with open(input_3d_json, 'r') as f:
    data = json.load(f)


frames_data = [frame_obj['keypoints_3d'] for frame_obj in data]

def get_lines_coords(keypoints, pairs):
    #Generate line coordinates (x, y, z) from keypoint index pairs for Plotly 3D lines.
    xs, ys, zs = [], [], []
    for i, j in pairs:
        if i < len(keypoints) and j < len(keypoints):
            x0, y0, z0 = keypoints[i]
            x1, y1, z1 = keypoints[j]
            xs += [x0, x1, None]
            ys += [y0, y1, None]
            zs += [z0, z1, None]
    return xs, ys, zs

def get_keypoint_labels_coords(keypoints):
    #Extract coordinates and labels for keypoints and returns x, y, z coordinates and string index labels
    xs = [p[0] for p in keypoints]
    ys = [p[1] for p in keypoints]
    zs = [p[2] for p in keypoints]
    labels = [str(i) for i in range(len(keypoints))]
    return xs, ys, zs, labels

# Prepare initial frame
init_points = frames_data[0]
x_init = [p[0] for p in init_points]
y_init = [p[1] for p in init_points]
z_init = [p[2] for p in init_points]

x_lines, y_lines, z_lines = get_lines_coords(init_points, connections)
x_labels, y_labels, z_labels, labels = get_keypoint_labels_coords(init_points)

# Create slider steps
slider_steps = []
for i in range(len(frames_data)):
    step = dict(
        method="animate",
        label=str(i),
        args=[[f"frame{i}"],
              {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]
    )
    slider_steps.append(step)

# Create Figure with Keypoints and Connections
fig = go.Figure(
    data=[
        # 3D Keypoints
        go.Scatter3d(
            x=x_init, y=y_init, z=z_init,
            mode='markers',
            marker=dict(size=4, color='blue'),
            name='keypoints'
        ),
         # Limb connections
        go.Scatter3d(
            x=x_lines, y=y_lines, z=z_lines,
            mode='lines',
            line=dict(color='red', width=3),
            name='connections'
        ),
        # Keypoint index labels
        go.Scatter3d(
            x=x_labels, y=y_labels, z=z_labels,
            mode='text',
            text=labels,
            textposition="top center",
            textfont=dict(color='black', size=14),
            showlegend=True,
            name='labels'
        )
    ],
    layout=go.Layout(
        scene=dict(
            xaxis=dict(range=[-1, 1], autorange=False),
            yaxis=dict(range=[-1, 1], autorange=False),
            zaxis=dict(range=[-1, 2], autorange=False),
        ),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            y=0.1,
            x=1.1,
            xanchor="right",
            yanchor="top",
            buttons=[
                dict(label="Play",
                     method="animate",
                     args=[None, {"frame": {"duration": 300, "redraw": True},
                                  "fromcurrent": True}]),
                dict(label="Pause",
                     method="animate",
                     args=[[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0}}])
            ]
        )],
        sliders=[dict(
            active=0,
            pad={"t": 50},
            currentvalue={"prefix": "Frame: "},
            steps=slider_steps
        )]
    ),
    frames=[
        #ANIMATION FRAMES
        go.Frame(
            data=[
                # Keypoints
                go.Scatter3d(
                    x=[p[0] for p in frame],
                    y=[p[1] for p in frame],
                    z=[p[2] for p in frame],
                    mode='markers',
                    marker=dict(size=4, color='blue')
                ),
                # Limb lines
                go.Scatter3d(
                    x=get_lines_coords(frame, connections)[0],
                    y=get_lines_coords(frame, connections)[1],
                    z=get_lines_coords(frame, connections)[2],
                    mode='lines',
                    line=dict(color='red', width=3)
                ),
                # Labels
                go.Scatter3d(
                    x=[p[0] for p in frame],
                    y=[p[1] for p in frame],
                    z=[p[2] for p in frame],
                    mode='text',
                    text=[str(i) for i in range(len(frame))],
                    textposition="top center",
                    textfont=dict(color='black', size=14),
                    showlegend=True
                )
            ],
            name=f"frame{i}"
        ) for i, frame in enumerate(frames_data)
    ]
)


fig.write_html(output_html)
print(f"Saved animation with slider as {output_html}")