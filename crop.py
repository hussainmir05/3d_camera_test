import pandas as pd
import open3d as o3d
import numpy as np
import cv2
import os
import sys

def crop_image_polygon(image_path, output_dir, coords):
    os.makedirs(output_dir, exist_ok=True)

    img = cv2.imread(image_path,cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Failed to read image: {image_path}")
        sys.exit()
        return None
    # Create polygon mask
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    pts = np.array(coords, np.int32).reshape((-1, 1, 2))
    cv2.fillPoly(mask, [pts], 255)

    # Apply mask
    masked = cv2.bitwise_and(img, img, mask=mask)

    # Crop bounding rectangle around polygon
    x, y, w, h = cv2.boundingRect(pts)
    cropped = masked[y:y+h, x:x+w]

    filename = os.path.basename(image_path)
    base, ext = os.path.splitext(filename)
    save_path = os.path.join(output_dir, f"{base}_crop{ext}")

    counter = 1
    while os.path.exists(save_path):
        save_path = os.path.join(output_dir, f"{base}_crop{counter}{ext}")
        counter += 1

    cv2.imwrite(save_path, cropped)
    print(f"[RGB] Cropped image saved: {save_path}")
    return save_path


def crop_3dp_polygon(three_dp_path, output_dir, coords):
    os.makedirs(output_dir, exist_ok=True)

    cols = ['x_wrtrgbimg', 'y_wrtrgbimg', 'x', 'y', 'z', 'r', 'g', 'b']
    # data = np.load(three_dp_path, allow_pickle=True)
    # data = np.load(three_dp_path)
    data = np.loadtxt(three_dp_path)

    print("[INFO] Loaded .3dp shape:", data.shape)

    # data = pd.DataFrame(data, columns=cols)
    print("[INFO] Loaded .npy shape:", data.shape)
    # print("[INFO] Loaded .npy shape:", data)
    
    # Handle both cases: structured array or plain ndarray
    if isinstance(data, np.ndarray) and data.dtype.names is None:
        # Plain ndarray -> assume columns order matches `cols`
        df = pd.DataFrame(data, columns=cols)
    else:
        # Structured array
        df = pd.DataFrame(data)
    # sys.exit()

    pts = np.array(coords, np.int32).reshape((-1, 1, 2))
    # ✅ Keep only points inside polygon
    inside_mask = []
    for _, row in df.iterrows():
        point = (row['x_wrtrgbimg'], row['y_wrtrgbimg'])
        inside_mask.append(cv2.pointPolygonTest(pts, point, False) >= 0)

    filtered = df[inside_mask]
    if filtered.empty:
        print("[3D] No points found inside polygon region.")
        return None

    # ✅ Save cropped data as new .npy or .3dp
    filename = os.path.basename(three_dp_path)
    base, ext = os.path.splitext(filename)
    save_path = os.path.join(output_dir, f"{base}_crop.3dp")

    counter = 1
    while os.path.exists(save_path):
        save_path = os.path.join(output_dir, f"{base}_crop{counter}.3dp")
        counter += 1

    filtered.to_csv(save_path, sep='\t', header=False, index=False)
    print(f"[3D] Cropped .3dp saved: {save_path}")
    return save_path

def crop_and_save_polygon(image_path, three_dp_path, output_dir_rgb, output_dir_3d, coords):
    print(f"[INFO] Cropping polygon with coords: {coords}")
    crop_image_polygon(image_path, output_dir_rgb, coords)
    crop_3dp_polygon(three_dp_path, output_dir_3d, coords)

exp = 20.0
exp2=100
ext=""

# Input paths
# image_path = rf"C:\Users\khadi\Desktop\SEM4\YJ_Specular\0203_SpecularDataset\calib\calib_2\rgb\{exp}00000_refWhite_COLOR{ext}.bmp"
# three_dp_path=rf"C:\Users\khadi\Desktop\SEM4\YJ_Specular\0203_SpecularDataset\calib\combined_npy\calib{ext}.npy"
# image_path=rf"D:\Hussain\3d_camera\rgb\hussain.bmp"
image_path=rf"D:\Hussain\3d_camera\stairs_colored.png"
three_dp_path=rf"D:\Hussain\3d_camera\auto\0.8_3.6_6.4.3dp"
output_dir_rgb=rf"D:\Hussain\3d_camera\auto\crop_combine"
output_dir_3d=rf"D:\Hussain\3d_camera\auto\crop_combine"

# step_1
# coords = [(565, 70), (1943, 73),  (1940, 409), (563, 404),]
# # step_2
# coords= [(562, 412), (1940, 420), (1940, 640) , (560, 635)]
# # # step_3
# coords= [(562, 644), (1940, 650),  (1940, 872) ,(556, 863)]
# # step_4
# coords=[(552, 875), (1942, 883), (1940, 1105), (550, 1095)]
# # step_5
coords=[(545, 1113), (1950, 1122), (1940, 1450), (540, 1440)]

# Call polygon crop
crop_and_save_polygon(image_path, three_dp_path, output_dir_rgb, output_dir_3d, coords)
