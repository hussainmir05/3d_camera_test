import os
import numpy as np
import open3d as o3d
import sys

mat = "_metal_10_"
PATH = rf"D:\Hussain\3d_camera\auto"
#     jak=i
 
# exp1, exp2, exp3 = "0.8","6.4","51.2"
exp1, exp2, exp3 = "0.8","3.6","6.4"
# exp1, exp2, exp3 = "0.8","6.0","6.4"
# exp1, exp2, exp3 = "3.8","6.4", "12.0"
file1 = rf"{PATH}\{exp1}00000_UV_Depth_region based.3dp"
file2 = rf"{PATH}\{exp2}00000_UV_Depth_region based.3dp"
file3 = rf"{PATH}\{exp3}00000_UV_Depth_region based.3dp"

# ---- derive names for output ----
try:
    parts = PATH.split(os.sep)
    extracted_suffix = parts[-1]                      # e.g. "_01"
    cleaned_material_name = parts[-3].strip('_')   
    # print(cleaned_material_name, "extracted_suffix",extracted_suffix, jak)
    # sys.exit()   # e.g. "ceramic_9"
except Exception:
    print("Error: Path structure too short; using defaults.")
    cleaned_material_name = "default_material"
    extracted_suffix = "_00"

def try_load_any_3dp(path):
    """
    Load .3dp that may be:
    - 5 columns: [x y X Y Z]
    - >=8 columns: [x y X Y Z R G B ...]
    Returns (xy:int32 Nx2, xyz:float64 Nx3, rgb:float64 Nx3 in [0,1])
    """
    try:
        data = np.loadtxt(path)
        if data.ndim == 1:
            data = data[None, :]
        ncol = data.shape[1]
        print(data.shape)
        if ncol < 5:
            raise ValueError(f"{os.path.basename(path)} has < 5 columns.")

        xy   = data[:, :2].astype(np.int32)
        xyz  = data[:, 2:5].astype(np.float64)

        if ncol >= 8:
            rgb = (data[:, -3:].astype(np.float64) / 255.0).clip(0, 1)
        else:
            # No RGB provided; fill with white so pipeline continues
            rgb = np.ones((data.shape[0], 3), dtype=np.float64)

        return xy, xyz, rgb
    except Exception as e:
        print(f"[warn] failed to load {path}: {e}")
        return None

loaded = [try_load_any_3dp(p) for p in [file1, file2, file3]]
loaded = [x for x in loaded if x is not None]
if not loaded:
    raise RuntimeError("No .3dp files could be loaded.")

# ---- stack in order: preserves index alignment ----
xy_all   = np.vstack([x[0] for x in loaded])
pts_all  = np.vstack([x[1] for x in loaded])
cols_all = np.vstack([x[2] for x in loaded])

# ---- build pcd ----
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(pts_all)
pcd.colors = o3d.utility.Vector3dVector(cols_all)

# ---- downsample and keep XY correspondence ----
VOXEL = 0.0001

def downsample_with_trace_keep_xy(pcd, xy_all, voxel_size):
    """Try voxel_down_sample_and_trace (3- or 4-return variants), else KDTree fallback."""
    if hasattr(o3d.geometry.PointCloud, "voxel_down_sample_and_trace"):
        min_b, max_b = pcd.get_min_bound(), pcd.get_max_bound()
        res = pcd.voxel_down_sample_and_trace(voxel_size, min_b, max_b, approximate_class=False)

        # Handle Open3D API differences: 3-return vs 4-return
        inds_list = None
        if isinstance(res, tuple):
            if len(res) == 4:
                print( "four")

                pcd_down, _, _, inds_list = res
            elif len(res) == 3:
                print( "theree")
                # Try to detect which slot holds the list of index arrays
                # We look for a list/sequence whose items are 1D arrays/VectorSize
                a, b, c = res
                candidates = [a, b, c]
                # The downsampled pcd is the one with .points attribute
                if hasattr(a, "points"):
                    pcd_down = a
                    others = [b, c]
                elif hasattr(b, "points"):
                    pcd_down = b
                    others = [a, c]
                else:
                    pcd_down = c
                    others = [a, b]
                # pick inds_list from others
                for obj in others:
                    if isinstance(obj, (list, tuple)) and len(obj) > 0:
                        inds_list = obj
                        break
            else:

                # Unexpected arity—fallback to KDTree
                inds_list = None
        if inds_list is not None:
            # Choose first contributor per voxel
            chosen = []
            for inds in inds_list:
                arr = np.asarray(inds, dtype=np.int64)
                chosen.append(arr[0] if arr.size > 0 else -1)
            chosen = np.asarray(chosen, dtype=np.int64)
            valid_mask = chosen >= 0
            if not np.all(valid_mask):
                pcd_down = pcd_down.select_by_index(np.nonzero(valid_mask)[0])
                chosen = chosen[valid_mask]
            mapped_xy = xy_all[chosen]
            return pcd_down, mapped_xy

    # ---- Fallback: KDTree nearest neighbor mapping ----
    pcd_down = pcd.voxel_down_sample(voxel_size)
    if len(pcd_down.points) == 0:
        raise RuntimeError("Downsampling produced 0 points. Try a smaller voxel size.")
    tree = o3d.geometry.KDTreeFlann(pcd)
    chosen = np.empty((len(pcd_down.points),), dtype=np.int64)
    pts_down = np.asarray(pcd_down.points)
    for i, q in enumerate(pts_down):
        k, idxs, _ = tree.search_knn_vector_3d(q, 1)
        chosen[i] = idxs[0] if k > 0 else 0
    mapped_xy = xy_all[chosen]
    return pcd_down, mapped_xy

pcd_down, mapped_xy = downsample_with_trace_keep_xy(pcd, xy_all, VOXEL)

# ---- save outputs ----
out_base = rf"D:\Hussain\3d_camera\auto\combine{cleaned_material_name}_{exp1}_{exp2}_{exp3}"
# out_base = rf"D:\새 폴더\stone\{mat}\3d\{extracted_suffix}{exp1}_{exp2}_{exp3}"
# print(rf"{cleaned_material_name}{extracted_suffix}_{exp1}_{exp2}_{exp3}")


# ply_out = out_base + ".ply"
# ok = o3d.io.write_point_cloud(ply_out, pcd_down)
# print("Saved .ply:", ok, "->", ply_out)

# Save .3dp with aligned (x,y).  If original file had no RGB, this will be white (255,255,255).
pts_out  = np.asarray(pcd_down.points)
cols_out = (np.asarray(pcd_down.colors) * 255.0).round().astype(np.int32)
out_arr  = np.hstack([mapped_xy.astype(np.int32), pts_out, cols_out])  # [x y X Y Z R G B]
three_dp_out = out_base + ".3dp"
# jak  = np.asarray(out_arr.points)

print("final", out_arr.shape)
np.savetxt(three_dp_out, out_arr, fmt=["%d","%d","%.6f","%.6f","%.6f","%d","%d","%d"])
print("Saved .3dp with aligned xy ->", three_dp_out)
print("==========================><=================================\n\n")

