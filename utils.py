#programming_fever
from pickle import FALSE
import cv2
import numpy as np
import time
load_from_disk = False



def record_gesture(keep_recording = True):
    cap = cv2.VideoCapture(0)

    kernel = np.ones((20,20),np.uint8)
    canvas = None
    gesture = []

    x1,y1=0,0
    noiseth = 800

    while(keep_recording):
        _, frame = cap.read()
        frame = cv2.flip( frame, 1 )
        if canvas is None:
            canvas = np.zeros_like(frame)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_range = np.array([110,100,100], dtype=np.uint8)
        upper_range = np.array([130,255,255], dtype=np.uint8)   #blue -> R:14,G:53,B:144      

        mask = cv2.inRange(hsv, lower_range, upper_range)

        res = cv2.bitwise_and(frame,frame, mask= mask)

        mask = cv2.erode(mask,kernel,iterations = 1)
        mask = cv2.dilate(mask,kernel,iterations = 2)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours and cv2.contourArea(max(contours,key = cv2.contourArea)) > noiseth:
            c = max(contours, key = cv2.contourArea)    
            x2,y2,w,h = cv2.boundingRect(c)
            if x1 == 0 and y1 == 0:
                x1,y1= x2,y2     
            else:
                gesture.append([(x1,y1),(x2,y2)])
                canvas = cv2.line(canvas, (x1,y1),(x2,y2), [255,0,0], 10)
            x1,y1= x2,y2
        else:
            x1,y1 =0,0
        frame_new = cv2.add(frame,canvas) 
        stacked = np.hstack((canvas,frame_new)) #side by side #frame_new should replace
        #cv2.imshow('frame',canvas) #Show just the line
        #cv2.imshow('frame',frame) #show the line overlaid on frame
        cv2.imshow('frame',stacked)



        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
        if k == ord('c'):
            #gestures.append(gesture)
            canvas = None
            gesture = []
        if k == ord('q'):
            keep_recording = False

    cv2.destroyAllWindows()
    cap.release()

    return gesture



from utils import record_gesture
gesture = record_gesture()
print(len(gesture))
