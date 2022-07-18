import numpy as np
import glob
import sys
import cv2

file_list = glob.glob("./nuscene_lidar_2d_depth/*")

total = 0

for file in file_list:
    temp = np.array(cv2.imread(file, cv2.IMREAD_GRAYSCALE))
    total += np.count_nonzero(temp)/temp.size

print(total/len(file_list))
