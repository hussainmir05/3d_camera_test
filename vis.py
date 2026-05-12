import os
import numpy as np
import open3d as o3d
PATH = r'C:\Program Files\FLIR Systems\v2_Capure_T\Spinnaker\src\Trigger_QuickSpin\output'
# PATH =r"C:\Program Files\FLIR Systems\v2_Capure_T_auto\Spinnaker\src\Trigger_QuickSpin\SKKU3DCAM_20251002_105405"
exp_time = '6.4'
exp_time = '96.0'
data = r'\{}00000'.format(exp_time)

file_path = PATH + data + '_UV_Depth_region based.3dp'
file_path=rf"D:\Hussain\3d_camera\auto\crop\1.3dp"
# Validate file existence and contents
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")
elif os.path.getsize(file_path) == 0:
    raise ValueError(f"File is empty: {file_path}")
# Load data
data_3dp = np.loadtxt(file_path)
# Validate data shape
if data_3dp.ndim != 2 or data_3dp.shape[1] < 6:
    raise ValueError(f"Unexpected data shape: {data_3dp.shape}")

# Extract points and color


pts = data_3dp[:, 2:5]
colors = data_3dp[:, -3:] / 255.0

# Create point cloud
pcdm = o3d.geometry.PointCloud()
pcdm.points = o3d.utility.Vector3dVector(pts)
pcdm.colors = o3d.utility.Vector3dVector(colors)

# Optional: remove outliers
pcdm, _ = pcdm.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)

# Visualize
o3d.visualization.draw_geometries([pcdm])