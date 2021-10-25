#!/usr/bin/env python3

############## Task1.1 - ArUco Detection ##############
### YOU CAN EDIT THIS FILE FOR DEBUGGING PURPOSEs, SO THAT YOU CAN TEST YOUR ArUco_library.py AGAINST THE VIDEO Undetected ArUco markers.avi###
### BUT MAKE SURE THAT YOU UNDO ALL THE CHANGES YOU HAVE MADE FOR DEBUGGING PURPOSES BEFORE TESTING AGAINST THE TEST IMAGES ###

import numpy as np
import cv2
import cv2.aruco as aruco
import time
from SS_1181_aruco_library import * #file name change according to the file name given ArUco_library = aruco_library

vid = cv2.VideoCapture('video4.mp4') #opening the video file

while (vid.isOpened()):
    try:
        _,img = vid.read() #reading each frame
        Detected_ArUco_markers = detect_ArUco(img)									## detecting ArUco ids and returning ArUco dictionary
        angle = Calculate_orientation_in_degree(Detected_ArUco_markers)				## finding orientation of aruco with respective to the menitoned scale in problem statement
        frame = mark_ArUco(img,Detected_ArUco_markers,angle)					## marking the parameters of aruco which are mentioned in the problem statement
        cv2.imshow("Frame", img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
    except:
        print("Done Successfully")
        break

vid.release()
cv2.destroyAllWindows()
