import numpy as np
import open3d as o3d
import cv2
from tools.Lidar2Camera import *
from nuscenes.utils.data_classes import *
import glob
from scipy.spatial.transform import Rotation as R
from nuscenes.nuscenes import NuScenes

nusc = NuScenes(version='v1.0-mini',
                dataroot='./nuscene_data', verbose=True)

print(len(nusc.scene))

for i in range(len(nusc.scene)):
    first_sample_token = nusc.scene[i]['first_sample_token']
    my_sample = nusc.get('sample', first_sample_token)
    while True:
        cam_front_data = nusc.get(
            'sample_data', my_sample['data']['CAM_FRONT'])
        lidar_top_data = nusc.get(
            'sample_data', my_sample['data']['LIDAR_TOP'])
        camera_file_name = cam_front_data['filename']
        lidar_file_name = lidar_top_data['filename']

        camera_calib_token = cam_front_data['calibrated_sensor_token']
        lidar_calib_token = lidar_top_data['calibrated_sensor_token']

        camera_calib = nusc.get('calibrated_sensor', camera_calib_token)
        lidar_calib = nusc.get('calibrated_sensor', lidar_calib_token)

        camera_intrinsic = np.array(camera_calib['camera_intrinsic'])
        camera_rotation = np.array(camera_calib['rotation'])
        camera_translation = np.array(camera_calib['translation'])
        R_vc = R.from_quat([camera_rotation[x] for x in [1, 2, 3, 0]])
        camera_rotation_matrix = np.array(R_vc.as_matrix())
        T_vc = np.append(
            camera_rotation_matrix, camera_translation.reshape(-1, 1), axis=1)
        T_vc = np.append(T_vc, np.array([[0, 0, 0, 1]]), axis=0)

        lidar_rotation = np.array(lidar_calib['rotation'])
        lidar_translation = np.array(lidar_calib['translation'])
        R_vl = R.from_quat([lidar_rotation[x] for x in [1, 2, 3, 0]])
        lidar_rotation_matrix = np.array(R_vl.as_matrix())
        T_vl = np.append(
            lidar_rotation_matrix, lidar_translation.reshape(-1, 1), axis=1)
        T_vl = np.append(T_vl, np.array([[0, 0, 0, 1]]), axis=0)

        T_lv = np.linalg.inv(T_vl)

        T_lc = np.matmul(T_lv, T_vc)
        T_cl = np.linalg.inv(T_lc)
        print(T_cl)

        camera_file_path = "./nuscene_data/" + camera_file_name
        lidar_file_path = "./nuscene_lidar_pcd/" + \
            lidar_file_name.split('/')[-1].replace(".pcd.bin", ".pcd")
        cam_img = cv2.imread(camera_file_path)
        height, width = cam_img.shape[0:2]
        l2c = Lidar2Camera(camera_intrinsic, T_cl, width, height, 80)
        pcd_origin = np.array(o3d.io.read_point_cloud(lidar_file_path).points)
        l2c.pcd_data_to_2d_img(
            pcd_origin, "./nuscene_lidar_2d_depth/"+camera_file_path.split('/')[-1].replace("CAM_FRONT", "LIDAR_TOP"))
        # print(lidar_file_path)
        # print(camera_file_path)

        if my_sample['next'] == '':
            break
        else:
            my_sample = nusc.get('sample', my_sample['next'])
