import numpy as np
import pandas as pd
import cv2
import yaml
from pathlib import Path


# ============================================================
# LOAD YAML CONFIG
# ============================================================

def load_config(config_path, dataset_name):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    if dataset_name not in config:
        raise ValueError(f"{dataset_name} not found in config")

    return config[dataset_name]["step_polygons"]


# ============================================================
# LOAD 3DP FILE
# ============================================================

def load_3dp(three_dp_path):

    cols = [
        'x_wrtrgbimg',
        'y_wrtrgbimg',
        'x',
        'y',
        'z',
        'r',
        'g',
        'b'
    ]

    data = np.loadtxt(three_dp_path)
    df = pd.DataFrame(data, columns=cols)

    return df


# ============================================================
# FAST POLYGON MASKING (IMPORTANT)
# ============================================================

def get_polygon_mask(df, polygon):

    # convert YAML list safely
    polygon = np.array([[int(x), int(y)] for x, y in polygon], dtype=np.int32)

    H = int(df['y_wrtrgbimg'].max() + 1)
    W = int(df['x_wrtrgbimg'].max() + 1)

    mask_img = np.zeros((H, W), dtype=np.uint8)
    cv2.fillPoly(mask_img, [polygon], 1)

    x = df['x_wrtrgbimg'].astype(int).values
    y = df['y_wrtrgbimg'].astype(int).values

    valid = (x >= 0) & (x < W) & (y >= 0) & (y < H)

    mask = np.zeros(len(df), dtype=bool)
    mask[valid] = mask_img[y[valid], x[valid]].astype(bool)

    return mask


# ============================================================
# FIT PLANE (PCA / SVD)
# ============================================================

def fit_plane(points):

    centroid = np.mean(points, axis=0)
    centered = points - centroid

    _, _, vh = np.linalg.svd(centered, full_matrices=False)

    normal = vh[-1]

    a, b, c = normal
    d = -np.dot(normal, centroid)

    return (a, b, c, d), centroid


# ============================================================
# POINT TO PLANE DISTANCE
# ============================================================

def point_to_plane_distance(point, plane):

    a, b, c, d = plane
    x, y, z = point

    return abs(a*x + b*y + c*z + d) / np.sqrt(a*a + b*b + c*c)


# ============================================================
# PROCESS ONE STEP
# ============================================================

def process_step(df, polygon):

    mask = get_polygon_mask(df, polygon)
    filtered = df[mask]

    pts = filtered[['x', 'y', 'z']].values
    pts = pts[np.isfinite(pts).all(axis=1)]

    plane, centroid = fit_plane(pts)

    residuals = np.array([
        point_to_plane_distance(p, plane)
        for p in pts
    ])

    return {
        "points": pts,
        "plane": plane,
        "centroid": centroid,
        "std_mm": np.std(residuals) * 1000,
        "mae_mm": np.mean(np.abs(residuals)) * 1000,
        "count": len(pts)
    }


# ============================================================
# STEP HEIGHTS
# ============================================================

def compute_step_heights(planes, centroids):

    heights = []

    for i in range(len(planes) - 1):

        dist = point_to_plane_distance(
            centroids[i + 1],
            planes[i]
        )

        heights.append(dist * 1000)

    return heights


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    # three_dp_path = r"C:\Users\khadi\Desktop\SEM5\3d_camera\data_2_45cm\v_t\6.400000_UV_Depth_region based.3dp"
    three_dp_path = r"C:\Users\khadi\Desktop\SEM5\3d_camera\data_4_70cm\auto\0.8_2.5_4.3.3dp"
    config_path = r"C:\Users\khadi\Desktop\SEM5\3d_camera\config\config.yaml"

    # dataset name
    path = Path(three_dp_path)
    dataset_name = path.parents[1].name

    print("Dataset:", dataset_name)

    # load data
    df = load_3dp(three_dp_path)
    step_polygons = load_config(config_path, dataset_name)

    print("Loaded points:", len(df))

    planes = []
    centroids = []

    # process each step
    for i, poly in enumerate(step_polygons):

        print(f"\nSTEP {i+1}")

        result = process_step(df, poly)

        planes.append(result["plane"])
        centroids.append(result["centroid"])

        print("Points:", result["count"])
        print(f"Plane std: {result['std_mm']:.3f} mm")
        print(f"mae_mm: {result['mae_mm']:.3f} mm")
        print("Centroid:", result["centroid"])

    # step heights
    print("\nSTEP HEIGHTS\n")

    heights = compute_step_heights(planes, centroids)

    for i, h in enumerate(heights):
        print(f"Step {i+1} -> Step {i+2}: {h:.3f} mm")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()