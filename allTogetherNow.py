# from __future__ import print_function
import pyaudio
import cv2 as cv
import numpy as np
import screeninfo
import random
from enum import Enum
import qwiic_joystick
import qwiic_button
import tkinter
import time
import os
import pyaudio
import wave
import sys

###################### CONSTANTS ##########################
COLORS=[(55,198,243),(56, 79, 255),(161, 80, 135), (1,137,255), (166,201,184)]

TEXT_FONTFACE = cv.FONT_HERSHEY_SIMPLEX
TEXT_SCALE = 0.4
TEXT_THICKNESS = 1
TEXT_COLOR = (255,255,255)
TEXT_LINETYPE = cv.LINE_8
TEXT_OFFSET = (5,5)

CAM_FRAME_SHAPE = (480, 640, 3)
CAM_LOWER_RANGE = np.array([110,100,100], dtype=np.uint8)
CAM_UPPER_RANGE = np.array([130,255,255], dtype=np.uint8)

class States(Enum):
    START_CAMERA = 0
    STOP_CAMERA = 1
    START_VOICE = 2
    STOP_VOICE = 3
    VIEW = 4

class Line:
    def __init__(self, color):
        self.color = color
        self.coords = []
        self.recording = ""
    def addPoint(self, point):
        self.coords.append(point)
    def addRecording(self, recording):
        self.recording = recording
###########################################################
# System state
my_state = States.VIEW
action_time = time.time()

# Drawing
drawings = []
drawing_nav = 0

# Get button
button = qwiic_button.QwiicButton()
if button.begin() == False:
    print("\nThe Qwiic Button isn't connected to the system. Please check your connection", \
        file=sys.stderr)

print("\nButton ready!")

# initialize joystick
joystick = qwiic_joystick.QwiicJoystick()

if joystick.connected == False:
    print("The Qwiic Joystick device isn't connected to the system. Please check your connection", \
        file=sys.stderr)

joystick.begin()
print("Joystick initialized")

# Initialize window
screen = screeninfo.get_monitors()[0]
width, height = screen.width, screen.height

img = np.zeros(CAM_FRAME_SHAPE, np.uint8)
img_no_select = np.zeros(CAM_FRAME_SHAPE, np.uint8)
img_text = np.zeros(CAM_FRAME_SHAPE, np.uint8)

cv.namedWindow('Display',cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty('Display', 0, 1)
cache = img.copy()
print("Window initialized")

# initialize recorder
form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 4096 # 2^12 samples for buffer
dev_index = 4 # device index found by p.get_device_info_by_index(ii)
# wav_output_filename = 'record.wav' # name of .wav file
audio = pyaudio.PyAudio() # create pyaudio instantiation
frames = []
stream = None
is_play_recording = False
print("Recorder initialized")

# initialize camera
cap = None
kernel = np.ones((20,20),np.uint8)
noiseth = 800
has_draw_started = False

###################### HELPER FUNCTIONS ##########################
def show_image():
    global img, img_text
    frame_new = cv.add(img, img_text)
    cv.imshow('Display', frame_new)

def select_drawing(id):
    global img
    img = cache.copy()
    cv.imshow('Display', img)
    for i in range(1, len(drawings[id].coords)):
        cv.line(img, drawings[id].coords[i-1], drawings[id].coords[i], drawings[id].color, thickness = 20)

def play_voice_recording(filename):
    os.system('aplay ./' + filename)

# jump between states, add text
def switch_state(state):
    global img, my_state
    my_state = state
    text = ""
    if state == States.VIEW:
        text = "View Drawings. Please use joystick to navigate."
    print_text(text)
    
def checkTime():
    global action_time
    return (time.time()-action_time > 0.5)

def start_voice_recording():
    global stream
    # create pyaudio stream
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=chunk)
    print_text("Audio recording")
    print("recording")

def stop_voice_recording():
    global stream
    global audio
    stream.stop_stream()
    stream.close()
    audio.terminate()
    print_text("Stopped audio recording. Press button again to view all drawings.")
    print("stopped")
    filename = time.strftime("%Y%m%d-%H%M%S")+".wav"
    wavefile = wave.open(filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()
    audio = pyaudio.PyAudio() # create pyaudio instantiation
    stream = None
    while not os.path.isfile(filename):
        print("not yet")
        continue
    print("New file created: "+filename)
    drawings[-1].addRecording(filename)

def start_camera_recording():
    global cap
    print_text("Gesture recording")
    cap = cv.VideoCapture(0)
    print("scr")

def stop_camera_recording():
    global has_draw_started, cap, img
    has_draw_started = False
    img = cache.copy()
    print_text("Stopped gesture recording. Press button again to start voice recording.")
    cap.release()
    print("stopcr")

def print_text(text):
    global img_text
    textSize = cv.getTextSize(text, TEXT_FONTFACE, TEXT_SCALE, TEXT_THICKNESS)
    cv.rectangle(img_text, (3, 3), (1000, textSize[0][1]+10), (0,0,0), thickness = -1)
    cv.putText(img_text, text, (TEXT_OFFSET[0],textSize[0][1] + TEXT_OFFSET[1]), TEXT_FONTFACE, TEXT_SCALE, TEXT_COLOR, TEXT_THICKNESS, TEXT_LINETYPE, False)

def button_press():
    global my_state,cache, img, img_no_select
    if(my_state == States.VIEW):
        my_state = States.START_CAMERA
        img = img_no_select.copy()
        # Call start camera recording
        start_camera_recording()
    elif(my_state == States.START_CAMERA):
        stop_camera_recording()
        # Call stop camera recording
        my_state = States.STOP_CAMERA
    elif(my_state == States.STOP_CAMERA):
        start_voice_recording()
        my_state = States.START_VOICE
    elif(my_state == States.START_VOICE):
        my_state = States.STOP_VOICE
        stop_voice_recording()
    elif(my_state == States.STOP_VOICE):
        switch_state(States.VIEW)
        my_state = States.VIEW

def reset():
    print("reset")
    # delete all the recordings
    # reset the drawings list
    # drawing_nav = 0
###########################################################

while(True):
    ############################## detect single button press #############################
    # if pressed, check record state
    if (button.is_button_pressed() and checkTime()):
        action_time = time.time()
        button_press()
    ############################## camera recording ##############################
    if(my_state == States.START_CAMERA):
        _, frame = cap.read()
        frame = cv.flip( frame, 1 )
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, CAM_LOWER_RANGE, CAM_UPPER_RANGE)
        res = cv.bitwise_and(frame,frame, mask= mask)
        mask = cv.erode(mask,kernel,iterations = 1)
        mask = cv.dilate(mask,kernel,iterations = 2)
        contours, hierarchy = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        if contours and cv.contourArea(max(contours,key = cv.contourArea)) > noiseth:
            c = max(contours, key = cv.contourArea)
            x,y,w,h = cv.boundingRect(c)
            if not has_draw_started:
                color = random.randint(0, len(COLORS)-1)
                drawings.append(Line(COLORS[color]))
                drawings[-1].addPoint((x,y))
                has_draw_started = True
            else:
                cv.line(img, drawings[-1].coords[-1], (x,y), drawings[-1].color,thickness = 5)
                drawings[-1].addPoint((x,y))
                cache = img.copy()
                img_no_select = img.copy()
        frame_new = cv.add(frame, img)
        frame_new_with_text = cv.add(frame_new, img_text)
        cv.imshow('Display', frame_new_with_text)
    ############################# voice recording #############################
    if(my_state == States.START_VOICE):
        data = stream.read(chunk, exception_on_overflow = False)
        frames.append(data)
    ############################## detect joystick press #############################
    if(my_state == States.VIEW):
        if(joystick.button == 0 and checkTime()):
            action_time = time.time()
            img = img_no_select.copy()
            print("button pressed")
    ############################# detect horizontal vertical #############################
        joystick_x = joystick.horizontal
        joystick_y = joystick.vertical
        # if moved, check what the current position is
        if (len(drawings) != 0):
            if joystick_x > 575 and checkTime():
                drawing_nav = abs(drawing_nav-1)%len(drawings)
                select_drawing(drawing_nav)
                action_time = time.time()
                is_play_recording = True
            # Weird check to prevent accidental triggers
            elif joystick_x < 450 and joystick_x > 0 and checkTime():
                drawing_nav = (drawing_nav+1)%len(drawings)
                select_drawing(drawing_nav)
                action_time = time.time()
                is_play_recording = True
    #######################################################################################
    if(my_state != States.START_CAMERA):
        show_image()
    if cv.waitKey(20)&0xFF == 27:
        break
    if(is_play_recording):
        time.sleep(0.5)
        play_voice_recording(drawings[drawing_nav].recording)
        is_play_recording = False
    
cv.destroyAllWindows()