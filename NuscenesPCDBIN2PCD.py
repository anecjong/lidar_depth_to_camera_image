import numpy as np
import open3d as o3d
import cv2
from tools.Lidar2Camera import *
from nuscenes.utils.data_classes import *
import glob

file_list = glob.glob("./nuscene_data/samples/LIDAR_TOP/*")
save_directory = "./nuscene_lidar_pcd/"
# for Initializing dummy val.
nu_lidar = LidarPointCloud(np.asarray([0, 0, 0, 0]))
for file_path in file_list:
    pcd_npy = (nu_lidar.from_file(file_path).points.transpose()[:, :3])
    pcd_format = o3d.geometry.PointCloud()
    pcd_format.points = o3d.utility.Vector3dVector(pcd_npy)
    o3d.io.write_point_cloud(
        save_directory + file_path.split('/')[-1].replace(".pcd.bin", ".pcd"), pcd_format)
