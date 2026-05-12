import os
import numpy as np
import pandas as pd
import cv2

# ============================================================
# LOAD FULL 3DP
# ============================================================

three_dp_path = r"D:\Hussain\3d_camera\auto\0.8_3.6_6.4.3dp"

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

print("Loaded points:", len(df))


# ============================================================
# STEP POLYGONS
# ============================================================

step_polygons = [

    # step 1
    [(565, 70), (1943, 73), (1940, 409), (563, 404)],

    # step 2
    [(562, 412), (1940, 420), (1940, 640), (560, 635)],

    # step 3
    [(562, 644), (1940, 650), (1940, 872), (556, 863)],

    # step 4
    [(552, 875), (1942, 883), (1940, 1105), (550, 1095)],

    # step 5
    [(545, 1113), (1950, 1122), (1940, 1450), (540, 1440)]

]


# ============================================================
# FIT PLANE
# ============================================================

def fit_plane(points):

    centroid = np.mean(points, axis=0)

    centered = points - centroid

    cov = np.cov(centered.T)

    _, _, vh = np.linalg.svd(cov)

    normal = vh[-1]

    a, b, c = normal

    d = -np.dot(normal, centroid)

    return a, b, c, d, centroid


# ============================================================
# POINT TO PLANE DISTANCE
# ============================================================

def point_to_plane_distance(point, plane):

    a, b, c, d = plane

    x0, y0, z0 = point

    dist = abs(a*x0 + b*y0 + c*z0 + d)

    dist /= np.sqrt(a*a + b*b + c*c)

    return dist


# ============================================================
# PROCESS EACH STEP
# ============================================================

planes = []
centroids = []

for idx, coords in enumerate(step_polygons):

    print(f"\nSTEP {idx+1}")

    polygon = np.array(coords, np.int32)

    inside_mask = []

    for _, row in df.iterrows():

        point_2d = (
            row['x_wrtrgbimg'],
            row['y_wrtrgbimg']
        )

        inside = cv2.pointPolygonTest(
            polygon,
            point_2d,
            False
        ) >= 0

        inside_mask.append(inside)

    filtered = df[inside_mask]

    print("Points inside polygon:", len(filtered))

    pts = filtered[['x', 'y', 'z']].values

    # remove invalid
    pts = pts[np.isfinite(pts).all(axis=1)]

    # fit plane
    a, b, c, d, centroid = fit_plane(pts)

    planes.append((a, b, c, d))
    centroids.append(centroid)

    # residuals
    residuals = []

    for p in pts:

        residuals.append(
            point_to_plane_distance(
                p,
                (a, b, c, d)
            )
        )

    residuals = np.array(residuals)

    print("Centroid:", centroid)
    print(f"Plane std: {np.std(residuals)*1000:.3f} mm")


# ============================================================
# STEP HEIGHTS
# ============================================================

print("\nSTEP HEIGHTS\n")

for i in range(len(planes)-1):

    dist = point_to_plane_distance(
        centroids[i+1],
        planes[i]
    )

    print(
        f"Step {i+1} -> Step {i+2}: "
        f"{dist*1000:.3f} mm"
    )