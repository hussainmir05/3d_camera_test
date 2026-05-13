# 3d_camera_test
## Method

1. Load RGB + 3D point cloud data
2. Crop each stair region using polygon ROI
3. Fit a plane to each stair surface using SVD
4. Compute perpendicular plane-to-plane distance
5. Compare measured distances with ground truth


The stair regions used for plane fitting and measurement were segmented manually on the RGB image as shown below 


| Original RGB Image | Segmented Stair Regions |
|---|---|
| <img src="ground_truth_rgb_img.bmp" width="250">| <img src="segment_rgb.png" width="250">  |
## Measured Step Heights wit Camera object height =63

| Step Pair | Auto Exposure (0.8, 3.6, 6.4) | Error | Exposure (3.6) | Error | Auto Exposure (6.4) | Error | Auto Exposure (51.2) | Error | Ground Truth |
|---|---|---|---|---|---|---|---|---|---|
| Step 1 → Step 2 | 0.994 mm | 0.006 mm | 0.994 mm | 0.006 mm | 1.000 mm | 0.000 mm | 0.986 mm | 0.014 mm | 1 mm |
| Step 2 → Step 3 | 1.955 mm | 0.045 mm | 1.976 mm | 0.024 mm | 1.941 mm | 0.059 mm | 1.932 mm | 0.068 mm | 2 mm |
| Step 3 → Step 4 | 3.938 mm | 0.062 mm | 3.932 mm | 0.068 mm | 3.948 mm | 0.052 mm | 3.908 mm | 0.092 mm | 4 mm |
| Step 4 → Step 5 | 7.973 mm | 0.027 mm | 7.969 mm | 0.031 mm | 7.980 mm | 0.020 mm | 7.909 mm | 0.091 mm | 8 mm |
| **Average Error** |  | **0.035 mm** |  | **0.032 mm** |  | **0.033 mm** |  | **0.066 mm** |  |

## Measured Step exposure = 6.4

## Measured Step Exposure = 6.4

| Step Pair | 70 cm | Error | 63 cm | Error | 53 cm | Error | 43 cm | Error | Ground Truth |
|---|---|---|---|---|---|---|---|---|---|
| Step 1 → Step 2 | 0.981 mm | 0.019 mm | 1.000 mm | 0.000 mm | 1.015 mm | 0.015 mm | 1.018 mm | 0.018 mm | 1 mm |
| Step 2 → Step 3 | 1.953 mm | 0.047 mm | 1.941 mm | 0.059 mm | 1.981 mm | 0.019 mm | 1.988 mm | 0.012 mm | 2 mm |
| Step 3 → Step 4 | 3.875 mm | 0.125 mm | 3.948 mm | 0.052 mm | 3.971 mm | 0.029 mm | 4.010 mm | 0.010 mm | 4 mm |
| Step 4 → Step 5 | 7.738 mm | 0.262 mm | 7.980 mm | 0.020 mm | 8.038 mm | 0.038 mm | 8.044 mm | 0.044 mm | 8 mm |
| **Average Error** |  | **0.113 mm** |  | **0.033 mm** |  | **0.025 mm** |  | **0.021 mm** |  |
