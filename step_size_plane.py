import os
import numpy as np

# ============================================================
# SETTINGS
# ============================================================

folder = r"D:\Hussain\3d_camera\auto\crop"
# folder = r"D:\Hussain\3d_camera\v_t\cropped"

files = [
    "1.3dp",
    "2.3dp",
    "3.3dp",
    "4.3dp",
    "5.3dp",
]



# ============================================================
# LOAD 3DP FILE
# ============================================================

def load_3dp(filepath):

    # load text file
    data = np.loadtxt(filepath)

    # columns:
    # [x_wrtrgbimg, y_wrtrgbimg, x, y, z, r, g, b]

    # extract xyz only
    pts = data[:, 2:5]

    # remove invalid values
    pts = pts[np.isfinite(pts).all(axis=1)]

    return pts




# ============================================================
# FIT PLANE USING SVD
# ============================================================

def fit_plane(points):

    # centroid
    centroid = np.mean(points, axis=0)

    # center points
    centered = points - centroid

    # covariance matrix (3x3 only)
    cov = np.cov(centered.T)

    # SVD on tiny matrix
    _, _, vh = np.linalg.svd(cov)

    # plane normal
    normal = vh[-1]

    a, b, c = normal

    # plane equation
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
# MAIN
# ============================================================

planes = []
centroids = []

print("Reading stair files...\n")

for file in files:


    path = os.path.join(folder, file)

    pts = load_3dp(path)

    print(file)
    print(f"Original points: {len(pts)}")


    print(f"ROI points: {len(pts)}")

    # fit plane
    a, b, c, d, centroid = fit_plane(pts)

    planes.append((a, b, c, d))
    centroids.append(centroid)

    # residual error
    residuals = []

    for p in pts:
        residuals.append(
            point_to_plane_distance(
                p,
                (a, b, c, d)
            )
        )

    residuals = np.array(residuals)

    print(f"Centroid: {centroid}")
    print(f"Plane std: {np.std(residuals)*1000:.3f} mm")

    print("-" * 50)


# ============================================================
# STEP HEIGHTS
# ============================================================

print("\nSTEP HEIGHTS\n")

for i in range(len(planes)-1):

    plane1 = planes[i]

    centroid2 = centroids[i+1]

    dist = point_to_plane_distance(
        centroid2,
        plane1
    )

    print(
        f"Step {i+1} -> Step {i+2}: "
        f"{dist:.6f} m "
        f"({dist*1000:.3f} mm)"
    )