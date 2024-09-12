#import the necessary packages
from scipy.spatial import distance as dist # to compute the euclidean distance between facial landmarks
from imutils.video import VideoStream # handles webcam input for video streams
from imutils import face_utils # contains utility functions for facial landmarks
from threading import Thread    # enables multi-threading to play the alarm sound 
import numpy as np
import playsound
import argparse
import imutils
import time
import dlib  # to detect and localize facial landmarks 
import cv2  # OpenCV for image processing
import os


def sound_alarm(path):
    # play an alarm sound
    playsound.playsound(path)


def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # compute the euclidean distance between the horizontal eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])

    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # return the eye aspect ratio
    return ear


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True,help="path to facial landmark predictor")
ap.add_argument("-a", "--alarm", type=str, default="",help="path alarm .mp3 file")
ap.add_argument("-w", "--webcam", type=int, default=0,help="index of webcam on system")   
args = vars(ap.parse_args())

EYE_AR_THRESH = 0.3 # The threshold value for EAR below which eyes are considered closed
EYE_AR_CONSEC_FRAMES = 48 # 48 frames = 1 second -> The number of consecutive frames the EAR must be below the threshold to trigger the drowsiness alarm

# initialize the frame counters and the total number of blinks
COUNTER = 0 # Counts the number of consecutive frames where EAR is below the threshold.
ALARM_ON = False


# initialize dlib's face detector (HOG-based) and then create the facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector() # Uses dlib's HOG-based face detector to detect faces in the frame.
predictor = dlib.shape_predictor(args["shape_predictor"]) # Uses dlib's HOG-based face detector to detect faces in the frame.


# grab the indexes of the facial landmarks for the left and right eye, respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]


# start the video stream thread
print("[INFO] starting video stream thread...")
vs = VideoStream(src=args["webcam"]).start()
time.sleep(1.0)

# loop over frames from the video stream
while True:
    frame = vs.read() # capture the frame from the video stream
    frame = imutils.resize(frame, width=800) # resize the frame 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert the frame to grayscale
    rects = detector(gray, 0) # detect faces in the grayscale frame

    # loop over the face detections
    for rect in rects:
        shape = predictor(gray, rect) # Detects the facial landmarks in the face region
        shape = face_utils.shape_to_np(shape) # Converts the facial landmarks to a NumPy array
        
        print(f"Facial landmarks detected: {shape}") # print the facial landmarks detected

        # extract the left and right eye coordinates, then use the coordinates to compute the eye aspect ratio for both eyes
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        # average the eye aspect ratio together for both eyes
        ear = (leftEAR + rightEAR) / 2.0

        # compute the convex hull for the left and right eye, then visualize each of the eyes
        leftEyeHull = cv2.convexHull(leftEye) 
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1) 
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        # check to see if the eye aspect ratio is below the blink threshold, and if so, increment the blink frame counter
        if ear < EYE_AR_THRESH:
            COUNTER += 1

            # if the eyes were closed for a sufficient number of frames, then sound the alarm
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                # if the alarm is not on, turn it on
                if not ALARM_ON:
                    ALARM_ON = True

                    # check to see if an alarm file was supplied, and if so, start a thread to have the alarm sound played in the background
                    if args["alarm"] != "":
                        t = Thread(target=sound_alarm, args=(args["alarm"],))
                        t.daemon = True
                        t.start()

                # draw an alarm on the frame
                cv2.putText(frame, "DROWSINESS ALERT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # otherwise, the eye aspect ratio is not below the blink threshold, so reset the counter and alarm
        else:
            COUNTER = 0
            ALARM_ON = False


        # draw the computed eye aspect ratio on the frame to help with debugging and setting the correct eye aspect ratio threshold
        cv2.putText(frame, "EAR: {:.2f}".format(ear), (650, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


    # show the frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF


    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()




# python test.py --shape-predictor shape_predictor_68_face_landmarks.dat --alarm alarm.mp3