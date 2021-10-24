#!/usr/bin/env python3
############## Task1.1 - ArUco Detection ##############

import numpy as np
import cv2
import cv2.aruco as aruco
import sys
import math
import time

def params(corners):
    (topLeft, topRight, bottomRight, bottomLeft) = corners
    #corners
    topLeft = (int(topLeft[0]),int(topLeft[1]))
    topRight = (int(topRight[0]),int(topRight[1]))
    bottomLeft = (int(bottomLeft[0]),int(bottomLeft[1]))
    bottomRight = (int(bottomRight[0]) , int(bottomRight[1]))

    #center
    cX = int((topLeft[0] + bottomRight[0]) / 2.0)
    cY = int((topLeft[1] + bottomRight[1]) / 2.0)
    cXY = (cX,cY)

    #mid point of top left nad top right
    midPoint_tLtr =(int((topLeft[0] + topRight[0]) / 2), int((topLeft[1] +topRight[1]) / 2))

    return [topLeft, topRight, bottomRight, bottomLeft ,cXY ,midPoint_tLtr]
def detect_ArUco(img):
	## function to detect ArUco markers in the image using ArUco library
	## argument: img is the test image
	## return: dictionary named Detected_ArUco_markers of the format {ArUco_id_no : corners}, where ArUco_id_no indicates ArUco id and corners indicates the four corner position of the aruco(numpy array)
	## 		   for instance, if there is an ArUco(0) in some orientation then, ArUco_list can be like
	## 				{0: array([[315, 163],
	#							[319, 263],
	#							[219, 267],
	#							[215,167]], dtype=float32)}

    Detected_ArUco_markers = {}
    ## enter your code here ##
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)
    parameters = aruco.DetectorParameters_create()
    corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters = parameters)
    ids1 = []
    for i in ids:
        for j in i:
            ids1.append(j)
    cou = 0
    for ii in ids1:
        Detected_ArUco_markers[ii] = corners[cou]
        cou+=1
    return Detected_ArUco_markers


def Calculate_orientation_in_degree(Detected_ArUco_markers):
    ## function to calculate orientation of ArUco with respective to the scale mentioned in problem statement
	## argument: Detected_ArUco_markers  is the dictionary returned by the function detect_ArUco(img)
	## return : Dictionary named ArUco_marker_angles in which keys are ArUco ids and the values are angles (angles have to be calculated as mentioned in the problem statement)
	##			for instance, if there are two ArUco markers with id 1 and 2 with angles 120 and 164 respectively, the
	##			function should return: {1: 120 , 2: 164}
    ArUco_marker_angles = {}
    for markerID,markerCorner in Detected_ArUco_markers.items():
        corners = markerCorner.reshape((4,2))
        tbcm = params(corners)
        #x,y co-ordinate of each corners
        topLeft = tbcm[0]
        topRight = tbcm[1]
        bottomLeft = tbcm[2]
        bottomRight = tbcm[3]
        #center
        cXY = tbcm[4]
        #midpoint
        midPoint_tLtr = tbcm[5]
        #angle finding
        xx = (cXY[0] - midPoint_tLtr[0]) **2
        yy = (cXY[1] - midPoint_tLtr[1]) **2
        aa = math.sqrt(xx + yy)
        ref = ( cXY[0] + aa, cXY[1])
        cRef = ((ref[0] - cXY[0]) , (ref[1] - cXY[1]))
        cMid = ((midPoint_tLtr[0] - cXY[0]), (midPoint_tLtr[1] - cXY[1]))
        bam = math.sqrt((cRef[0])**2 + (cRef[1])**2)
        bcm = math.sqrt((cMid[0])**2 + (cMid[1])**2)
        cxxx = ((cRef[0] * cMid[0]) + (cRef[1] * cMid[1])) / (bam * bcm)
        result = math.acos(cxxx)
        cva = math.ceil(math.degrees(result))
        if midPoint_tLtr[1] > cXY[1]:
            cva = 360 - cva
        ArUco_marker_angles[markerID] = cva
    return ArUco_marker_angles	## returning the angles of the ArUco markers in degrees as a dictionary


def mark_ArUco(img,Detected_ArUco_markers,ArUco_marker_angles):

	## function to mark ArUco in the test image as per the instructions given in problem statement
	## arguments: img is the test image
	##			  Detected_ArUco_markers is the dictionary returned by function detect_ArUco(img)
	##			  ArUco_marker_angles is the return value of Calculate_orientation_in_degree(Detected_ArUco_markers)
	## return: image namely img after marking the aruco as per the instruction given in problem statement


    ## enter your code here ##
    font = cv2.FONT_HERSHEY_SIMPLEX
    for markerID, markerCorner in Detected_ArUco_markers.items():
        corners = markerCorner.reshape((4,2))
        tbcm = params(corners)
        #x,y co-ordinate of each corners
        topLeft = tbcm[0]
        topRight = tbcm[1]
        bottomLeft = tbcm[2]
        bottomRight = tbcm[3]
        cv2.circle(img, topLeft, 4, color=(125,125,125), thickness=-1)
        cv2.circle(img, topRight, 4, color=(0,255,0), thickness=-1)
        cv2.circle(img, bottomLeft, 4, color=(255,255,255), thickness=-1)
        cv2.circle(img, bottomRight, 4, color=(180,105,255), thickness=-1)

        #center
        cXY = tbcm[4]
        cv2.circle(img, cXY, 4, (0, 0, 255), -1)

        #midpoint
        midPoint_tLtr = tbcm[5]
        cv2.line(img, midPoint_tLtr, cXY, (255, 0, 0), 3)

        # draw the ArUco marker ID on the image
        cv2.putText(img, str(markerID), (cXY[0] + 40, cXY[1]), font, 1, (0, 0, 255), 2)

        #angle
        ang = ArUco_marker_angles
        cv2.putText(img, str(ang[markerID]), (cXY[0] - 100, cXY[1]), font, 1, (0, 255,0), 2)
        team_name = "SS_1181(EYRC)"
        cv2.putText(img, team_name,(500 ,30) ,font,0.5,(0,0,255),1)
    return img
