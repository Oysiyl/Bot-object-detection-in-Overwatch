######## Webcam Object Detection Using Tensorflow-trained Classifier #########
#
# Author: Evan Juras
# Date: 1/20/18
# Description:
# This program uses a TensorFlow-trained classifier to perform object detection.
# It loads the classifier uses it to perform object detection on a webcam feed.
# It draws boxes and scores around the objects of interest in each frame from
# the webcam.

## Some of the code is copied from Google's example at
## https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb

## and some is copied from Dat Tran's example at
## https://github.com/datitran/object_detector_app/blob/master/object_detection_app.py

## but I changed it to make it more understandable to me.


# Import packages
import os
import cv2
import numpy as np
import tensorflow as tf
import sys
import time
import mss
import pyautogui
from pyautogui import tweens

# # Speed-up using multithreads
# cv2.setUseOptimized(True)
# cv2.setNumThreads(4)


fps_time = 0

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")

# Import utilites
from utils import label_map_util
from utils import visualization_utils as vis_util

# Name of the directory containing the object detection module we're using
MODEL_NAME = 'inference_graph'

# Grab path to current working directory
CWD_PATH = os.getcwd()

# Path to frozen detection graph .pb file, which contains the model that is used
# for object detection.
PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_NAME, 'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH, 'training', 'labelmap.pbtxt')

# Path to output file
OUTPUT_NAME = 'output3.avi'
PATH_TO_OUTPUT = os.path.join(CWD_PATH, OUTPUT_NAME)

# Number of classes the object detector can identify
NUM_CLASSES = 1

## Load the label map.
# Label maps map indices to category names, so that when our convolution
# network predicts `5`, we know that this corresponds to `king`.
# Here we use internal utility functions, but anything that returns a
# dictionary mapping integers to appropriate string labels would be fine
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load the Tensorflow model into memory.
detection_graph = tf.Graph()
# Because running game already used some fraction of GPU memory, specify to use only n% of GPU RAM.
# For example, in my case using 70% (and remain 30% for actually game) of memory is possible
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.7
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph, config=config)


# Define input and output tensors (i.e. data) for the object detection classifier

# Input tensor is the image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Output tensors are the detection boxes, scores, and classes
# Each box represents a part of the image where a particular object was detected
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

# Each score represents level of confidence for each of the objects.
# The score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# Number of objects detected
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# Initialize webcam feed
# video = cv2.VideoCapture(0)
# ret = video.set(3,1280)
# ret = video.set(4,720)

# Define the codec and create VideoWriter object
# frame_width = int(video.get(3))
# frame_height = int(video.get(4))
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(PATH_TO_OUTPUT, fourcc, 10.0, (1280, 720))

with mss.mss() as sct:
    # Part of the screen to capture
    # monitor = {"top": 120, "left": 280, "width": 1368, "height": 770}
    monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}

    while "Screen recording":

        last_time = time.time()

        # Get raw pixels from the screen, save it to a Numpy array
        img = np.array(sct.grab(monitor))
        img = cv2.resize(img, (1280, 720))
        frame = img

        frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        rows = frame.shape[0]
        cols = frame.shape[1]
        inp = cv2.resize(frame, (300, 300))
        # inp = inp[:, :, [2, 1, 0]]  # BGR2RGB

        # Run the model
        out1 = sess.run([sess.graph.get_tensor_by_name('num_detections:0'),
                        sess.graph.get_tensor_by_name('detection_scores:0'),
                        sess.graph.get_tensor_by_name('detection_boxes:0'),
                        sess.graph.get_tensor_by_name('detection_classes:0')],
                       feed_dict={'image_tensor:0': inp.reshape(1, inp.shape[0], inp.shape[1], 3)})
        pyautogui.FAILSAFE = False
        # Visualize detected bounding boxes.
        num_detections = int(out1[0][0])

        xl, yl, rightl, bottoml, namel, wl, hl = [], [], [], [], [], [], []
        # centerX, centerY = 0, 0
        for i in range(num_detections):
            classId = int(out1[3][0][i])
            score = float(out1[1][0][i])
            bbox = [float(v) for v in out1[2][0][i]]
            if score > 0.9:

                x = bbox[1] * cols
                y = bbox[0] * rows
                right = bbox[3] * cols
                bottom = bbox[2] * rows

                names = list(category_index.values())
                name = 0
                for i in names:
                    if i['id'] == classId:
                        name = i['name']
                        break
                if name == 0:
                    name = 'not Found'
                screenWidth, screenHeight = pyautogui.size()
                currentMouseX, currentMouseY = pyautogui.position()
                print("Width:{}, height:{}".format(screenWidth, screenHeight))
                print("Current X:{}, Y:{}".format(currentMouseX, currentMouseY))
                currentmouseX, currentmouseY = 960, 540
                W, H = int(currentMouseX/1.5), int(currentMouseY/1.5)
                xl.append(x)
                yl.append(y)
                rightl.append(right)
                bottoml.append(bottom)
                namel.append(name)
                wl.append(W)
                hl.append(H)
                textboxes = "{}: {}".format(name, round(score, 4))
                cv2.rectangle(frame, (int(x), int(y)), (int(right), int(bottom)), (125, 255, 51), thickness=2)

        if xl != []:
            x, y, right, bottom, name, W, H = xl[0], yl[0], rightl[0], bottoml[0], namel[0], wl[0], hl[0]
            del xl, yl, rightl, bottoml, namel, wl, hl

            centerX, centerY = int((x+right)/2 - abs(x-right)*0.1), int((y+bottom)/2 - abs(y-bottom)*0.45)
            print(centerX, centerY)
            moveexp = ""
            moveX, moveY = abs(W-centerX), abs(H-centerY)
            if moveX > 50:
                moveX = 50
            if moveY > 50:
                moveY = 50
            if moveX <= 5:
                moveX = 0
            if moveY <= 5:
                moveY = 0

            print("Moves: {}, {}".format(moveX, moveY))
            if moveX <= 5 and moveY <= 5:
                moveexp += "Center"

                # pyautogui.mouseDown(button='left')
                # time.sleep(1.0)
                # pyautogui.mouseUp(button='left')
                # pyautogui.PAUSE = 1.0
                pyautogui.mouseDown(button='right')
                time.sleep(1.0)
                # pyautogui.PAUSE = 0.01
                pyautogui.click()
                pyautogui.mouseUp(button='right')

            elif centerX > W and centerY > H:
                pyautogui.move(moveX/2, moveY/2, duration=0.1, tween=pyautogui.tweens.easeInOutQuad)
                moveexp += "DownRight"
            elif centerX > W and centerY < H:
                pyautogui.move(moveX/2, -moveY/2, duration=0.1, tween=pyautogui.tweens.easeInOutQuad)
                moveexp += "UpRight"
            elif centerX < W and centerY > H:
                pyautogui.move(-moveX/2, moveY/2, duration=0.1, tween=pyautogui.tweens.easeInOutQuad)
                moveexp += "DownLeft"
            elif centerX < W and centerY < H:
                pyautogui.move(-moveX/2, -moveY/2, duration=0.1, tween=pyautogui.tweens.easeInOutQuad)
                moveexp += "UPLeft"
            cv2.circle(frame, (centerX, centerY), 5, (0, 255, 0), -1)

            textcoord = "Coord: X: {}, Y: {}".format(int(centerX), int(centerY))
            textcurrmouse = "Currmouse: X: {}, Y: {}".format(int(W), int(H))
            textdistance = "Distance: X: {}, Y: {}".format(int(centerX-W), int(centerY-H))
            textmoves = "Moves: X: {}, Y: {}".format(moveX, moveY)
            cv2.putText(frame, textboxes, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, textcoord, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, textcurrmouse, (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, textdistance, (60, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, textmoves, (80, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, moveexp, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # All the results have been drawn on image. Now display the image.
        out.write(frame)
        cv2.imshow('Object detector', frame)

        fps_time = time.time()
        # Press 'q' to quit
        if cv2.waitKey(1) == ord('q'):
            break

# Clean up
# video.release()
out.release()
cv2.destroyAllWindows()
