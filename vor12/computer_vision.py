#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Jérémie DECOCK (http://www.jdhp.org)

"""
OpenCV - Extract one color.

Required: opencv library (Debian: aptitude install python-opencv)

See: https://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_imgproc/py_houghcircles/py_houghcircles.html#hough-circles
     https://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_imgproc/py_colorspaces/py_colorspaces.html#object-tracking
     Oreilly's book "Learning OpenCV" (first edition) p.158 for details about Hough transforms.

     http://txt.arboreus.com/2014/10/21/remove-circles-from-an-image-in-python.html
     http://wiki.elphel.com/index.php?title=OpenCV_Tennis_balls_recognizing_tutorial
     http://stackoverflow.com/questions/28521783/python-opencv-houghcircles-not-giving-good-results
     http://computer-vision-talks.com/articles/how-to-detect-circles-in-noisy-image/
     http://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
"""

from __future__ import print_function

import cv2 as cv
import numpy as np
import argparse

LOWER_COLOR_H = 105
LOWER_COLOR_S = 135
LOWER_COLOR_V = 68
                    
UPPER_COLOR_H = 120
UPPER_COLOR_S = 220
UPPER_COLOR_V = 180

HCT_ACCUMULATOR_RESOLUTION = 1.2
HCT_CANNY_EDGE_THRESHOLD = 50
HCT_ACCUMULATOR_THRESHOLD = 10
HCT_MIN_RADIUS = 0
HCT_MAX_RADIUS = 0

MOTIONLESS_AREA_X_RATIO = 0.3  # Ratio of the motionless area on the image width (should be between 0.0 and 1.0)
MOTIONLESS_AREA_Y_RATIO = 0.3  # Ratio of the motionless area on the image height (should be between 0.0 and 1.0)

def main():

    # Parse the programm options (get the path of the image file to read) #####

    parser = argparse.ArgumentParser(description='An opencv snippet.')
    parser.add_argument("--cameraid", "-i",  help="The camera ID number (default: 0)", type=int, default=0, metavar="INTEGER")
    args = parser.parse_args()

    device_number = args.cameraid

    # OpenCV ##################################################################

# As said in https://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_imgproc/py_colorspaces/py_colorspaces.html:
#
#   "In HSV, it is easier to represent a color than RGB color-space. In our
#   application, we will try to extract a blue colored object. So here is the
#   method:
#   
#   1. Take each frame of the video
#   2. Convert from BGR to HSV color-space
#   3. We threshold the HSV image for a range of blue color
#   4. Now extract the blue object alone, we can do whatever on that image we want."

# How to find HSV values to track?
#
#   As said in https://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_imgproc/py_colorspaces/py_colorspaces.html:
#   This is a common question found in stackoverflow.com. It is very simple and
#   you can use the same function, cv2.cvtColor(). Instead of passing an image,
#   you just pass the BGR values you want. For example, to find the HSV value of
#   Green, try following commands in Python terminal:
#
#     >>> green = np.uint8([[[0,255,0 ]]])
#     >>> hsv_green = cv2.cvtColor(green,cv2.COLOR_BGR2HSV)
#     >>> print hsv_green
#     [[[ 60 255 255]]]
#
#   Now you take [H-10, 100,100] and [H+10, 255, 255] as lower bound and upper
#   bound respectively. Apart from this method, you can use any image editing
#   tools like GIMP or any online converters to find these values, but don’t
#   forget to adjust the HSV ranges."

    video_capture = cv.VideoCapture(device_number)

    print("Press q to quit.")

    while(True):
        # Capture frame-by-frame.

        # 'ret' is a boolean ('True' if frame is read correctly, 'False' otherwise).
        # 'img_np' is an numpy array.
        ret, img_bgr = video_capture.read()

        # IMAGE PROCESSING ################################

        img_blur = cv.GaussianBlur(img_bgr, (5,5), 0)

        # Convert BGR color space to HSV
        img_hsv = cv.cvtColor(img_blur, cv.COLOR_BGR2HSV)

        # Define range of blue color in HSV
        lower_blue = np.array([LOWER_COLOR_H, LOWER_COLOR_S, LOWER_COLOR_V])
        upper_blue = np.array([UPPER_COLOR_H, UPPER_COLOR_S, UPPER_COLOR_V])

        # Threshold the HSV image to get only blue colors
        img_mask = cv.inRange(img_hsv, lower_blue, upper_blue)

        # Hough Circle Transform
        # See Oreilly's book "Learning OpenCV" (first edition) p.158 for details about Hough transforms.
        # - method : the only method available is CV_HOUGH_GRADIENT so...
        # - dp : the resolution of the accumumator image used (allow to create
        #   an accumulator of a lower resolution than the input image). It must
        #   be greater or equal to 1. A value of "1" keep the original size; a
        #   value of "2" divide the resolution by 2, ...
        # - min_dist : the minimum distance between 2 circles (distances in
        #   pixels). Should be proportional to the image size (img_bgr.shape[0]
        #   and img_bgr.shape[1]).
        # - param1 : the edge (Canny) threshold.
        # - param2 : the accumulator threshold.
        # - minRadius : the minimum radius of circles that can be found (radius
        #   in pixels). Should be proportional to the image size
        #   (img_bgr.shape[0] and img_bgr.shape[1]).
        # - maxRadius : the maximum radius of circles that can be found (radius
        #   in pixels). Should be proportional to the image size
        #   (img_bgr.shape[0] and img_bgr.shape[1]).
        method = cv.cv.CV_HOUGH_GRADIENT  # The only method available is CV_HOUGH_GRADIENT
        dp = HCT_ACCUMULATOR_RESOLUTION   # The resolution of the accumumator.
        min_dist = max(img_bgr.shape[0], img_bgr.shape[1])   # The minimum distance between 2 circles.
        canny_edge_threshold = HCT_CANNY_EDGE_THRESHOLD
        accumulator_threshold = HCT_ACCUMULATOR_THRESHOLD
        min_radius = HCT_MIN_RADIUS
        max_radius = HCT_MAX_RADIUS
        #circles = cv.HoughCircles(img_mask, method, dp, min_dist)
        circles = cv.HoughCircles(img_mask, method, dp, min_dist, param1=canny_edge_threshold, param2=accumulator_threshold, minRadius=min_radius, maxRadius=max_radius)

        # DRAW THE MOTIONLESS AREA ########################

        image_height = img_bgr.shape[0]
        image_width = img_bgr.shape[1]

        motionless_area_width = image_width * MOTIONLESS_AREA_X_RATIO
        motionless_area_height = image_height * MOTIONLESS_AREA_Y_RATIO

        motionless_area_range_x = (int((image_width - motionless_area_width)/2),   int(image_width - (image_width - motionless_area_width)/2))
        motionless_area_range_y = (int((image_height - motionless_area_height)/2), int(image_height - (image_height - motionless_area_height)/2))

        color = (0, 0, 255)
        thickness = 1
        cv.rectangle(img_bgr, (motionless_area_range_x[0], motionless_area_range_y[0]), (motionless_area_range_x[1], motionless_area_range_y[1]), color, thickness)

        # CONTROL AND DRAW ################################

        if circles is not None:
            circles = np.uint16(np.around(circles))

            if circles.shape[1] > 1:
                raise Exception("Error: more than 1 circle have been found ; increase the min_dist parameter.")

            circle = circles[0, 0]

            target_center = (circle[0], circle[1])
            target_radius = circle[2]

            # Draw the outer circle
            center_point = (target_center[0], target_center[1])
            radius = target_radius
            color = (0, 255, 0)
            thickness = 2
            line_type = cv.CV_AA  # Anti-Aliased
            cv.circle(img_bgr, center_point, radius, color, thickness, line_type)

            # Draw the center of the circle
            center_point = (target_center[0], target_center[1])
            radius = 2
            color = (0, 0, 255)
            thickness = 3
            line_type = cv.CV_AA  # Anti-Aliased
            cv.circle(img_bgr, center_point, radius, color, thickness, line_type)

            # Add text coordinates
            text = "{0}, {1}, {2}".format(target_center[0], target_center[1], target_radius)
            start_point = (15, 50)
            font = cv.FONT_HERSHEY_SIMPLEX
            font_scale = 0.75
            color = (0, 0, 255)
            thickness = 2
            line_type = cv.CV_AA  # Anti-Aliased
            cv.putText(img_bgr, text, start_point, font, font_scale, color, thickness, line_type)

            # Control
            cmd_x = 0
            if target_center[0] < motionless_area_range_x[0]:
                cmd_x = 1
            elif target_center[0] > motionless_area_range_x[1]:
                cmd_x = -1

            cmd_y = 0
            if target_center[1] < motionless_area_range_y[0]:
                cmd_y = 1
            elif target_center[1] > motionless_area_range_y[1]:
                cmd_y = -1

            # Add text coordinates
            cmd_text = ""

            if cmd_y > 0:
                cmd_text += "up "
            elif cmd_y < 0:
                cmd_text += "down "

            if cmd_x > 0:
                cmd_text += "right"
            elif cmd_x < 0:
                cmd_text += "left"

            start_point = (15, 100)
            font = cv.FONT_HERSHEY_SIMPLEX
            font_scale = 0.75
            color = (0, 0, 255)
            thickness = 2
            line_type = cv.CV_AA  # Anti-Aliased
            cv.putText(img_bgr, cmd_text, start_point, font, font_scale, color, thickness, line_type)
            

        # DISPLAY IMAGES ##################################

        # Display the resulting frame (Mask)
        cv.imshow('Mask', img_mask)

        # Display the resulting frame (BGR)
        cv.imshow('BGR', img_bgr)

        # KEYBOARD LISTENER ###############################

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
