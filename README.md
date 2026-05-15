# 3d_camera_test
## Plane to Plane Distance
Method 
1. Load RGB + 3D point cloud data
2. Crop each stair region using polygon ROI
3. Fit a plane to each stair surface using SVD
4. Compute perpendicular plane-to-plane distance
5. Compare measured distances with ground truth
The stair regions used for plane fitting and measurement were segmented manually on the RGB image as shown below 

| Original RGB Image | Segmented Stair Regions |
|---|---|
| <img src="ground_truth_rgb_img.bmp" width="250">| <img src="segment_rgb.png" width="250">  |


| Cam Distance     | Step 1 → 2 (mm) | Step 2 → 3 (mm) | Step 3 → 4 (mm) | Step 4 → 5 (mm) | Error (RMSE mm) |
| ---------------- | --------------- | --------------- | --------------- | --------------- | --------------- |
| 43 cm            | 1.013           | 1.993           | 4.012           | 8.060           | 0.022           |
| 53 cm            | 1.009           | 1.983           | 3.976           | 8.041           | 0.022           |
| 63 cm            | 0.994           | 1.956           | 3.938           | 7.973           | 0.047           |
| 73 cm            | 15.319          | 1.890           | 3.851           | 7.705           | 3.580           |
| **Ground Truth** | **1**           | **2**           | **4**           | **8**           | —               |

##  Point to Plane Error 
After fitting a plane to each segmented stair surface using SVD, the point-to-plane residuals are computed to evaluate surface fitting quality and noise consistency across different camera distances.

The error metrics are reported as:

MAE (Mean Absolute Error): average deviation of points from the fitted plane
STD (Standard Deviation): spread of point-to-plane residuals (surface noise)
 MAE (mm)
| Step | 45 cm | 53 cm | 63 cm | 70 cm |
| ---- | ----- | ----- | ----- | ----- |
| 1    | 0.216 | 0.265 | 0.189 | 0.267 |
| 2    | 0.215 | 0.268 | 0.186 | 0.268 |
| 3    | 0.222 | 0.265 | 0.185 | 0.266 |
| 4    | 0.224 | 0.256 | 0.186 | 0.259 |
| 5    | 0.220 | 0.237 | 0.190 | 0.251 |

STD (mm)
| Step | 45 cm | 53 cm | 63 cm | 70 cm |
| ---- | ----- | ----- | ----- | ----- |
| 1    | 0.148 | 0.188 | 0.150 | 0.256 |
| 2    | 0.148 | 0.200 | 0.149 | 0.220 |
| 3    | 0.159 | 0.197 | 0.153 | 0.220 |
| 4    | 0.154 | 0.189 | 0.148 | 0.208 |
| 5    | 0.283 | 0.177 | 0.149 | 0.205 |

Number of Points per Plane
| Step | 45 cm   | 53 cm   | 63 cm   | 70 cm   |
| ---- | ------- | ------- | ------- | ------- |
| 1    | 375,926 | 594,901 | 663,107 | 340,247 |
| 2    | 486,701 | 473,272 | 443,501 | 223,287 |
| 3    | 481,151 | 465,429 | 440,647 | 221,181 |
| 4    | 482,891 | 478,708 | 441,686 | 221,604 |
| 5    | 717,197 | 624,440 | 658,972 | 336,100 |
