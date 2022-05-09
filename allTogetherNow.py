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
TEXT_SCALE = 1
TEXT_THICKNESS = 2
TEXT_COLOR = (255,255,255)
TEXT_LINETYPE = cv.LINE_8
TEXT_OFFSET = (5,5)

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

# Get button 0x36
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

img = np.zeros((height,width,3), np.uint8)

cv.namedWindow('Display',cv.WND_PROP_FULLSCREEN)

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
print("Recorder initialized")

###################### HELPER FUNCTIONS ##########################
drag_start = False
def draw(event, x, y, flags, param):
    global drag_start, drawing_nav, img, cache, my_state
    if(my_state == States.VIEW):
        if event == cv.EVENT_LBUTTONDOWN:
            color = random.randint(0, len(COLORS)-1)
            drawings.append(Line(COLORS[color]))
            drawings[-1].addPoint((x,y))
            drag_start = True
        elif event == cv.EVENT_LBUTTONUP:
            drag_start = False
        elif event == cv.EVENT_MOUSEMOVE:
            if drag_start:
                cv.line(img, drawings[-1].coords[-1], (x,y), drawings[-1].color,thickness = 5)
                drawings[-1].addPoint((x,y))
                cache = img.copy()
cv.setMouseCallback('Display', draw)

def select_drawing(id):
    global img
    img = cache.copy()
    cv.imshow('Display', img)
    for i in range(1, len(drawings[id].coords)):
        cv.line(img, drawings[id].coords[i-1], drawings[id].coords[i], drawings[id].color, thickness = 20)
    play_voice_recording(drawings[id].recording)

def play_voice_recording(filename):
    os.system('aplay ./' + filename)

# jump between states, add text
def switch_state(state):
    global img, my_state
    my_state = state
    text = ""
    if state == States.START_CAMERA:
        text = "Record"
    elif state == States.VIEW:
        text = "View Drawings"
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
    print_text("Stopped audio recording. \n Press button again to view all drawings.")
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
    print_text("Gesture recording")
    print("scr")

def stop_camera_recording():
    print_text("Stopped gesture recording.\n  Press button again to start voice recording.")
    print("stopcr")

def print_text(text):
    global img
    textSize = cv.getTextSize(text, TEXT_FONTFACE, TEXT_SCALE, TEXT_THICKNESS)
    cv.rectangle(img, (3, 3), (textSize[0][0], 120), (0,0,0), thickness = -1)
    cv.putText(img, text, (TEXT_OFFSET[0],textSize[0][1] + TEXT_OFFSET[1]), TEXT_FONTFACE, TEXT_SCALE, TEXT_COLOR, TEXT_THICKNESS, TEXT_LINETYPE, False)

def button_press():
    global my_state
    if(my_state == States.VIEW):
        switch_state(States.START_CAMERA)
        # Call start camera recording
        start_camera_recording()
        my_state = States.START_CAMERA
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
    ############################# voice recording #############################
    if(my_state == States.START_VOICE):
        data = stream.read(chunk, exception_on_overflow = False)
        frames.append(data)
    ############################## detect joystick press #############################
    if(joystick.button == 0 and checkTime()):
        action_time = time.time()
        button_press()
        print("button pressed")
    ############################# detect horizontal vertical #############################
    joystick_x = joystick.horizontal
    joystick_y = joystick.vertical
    # if moved, check what the current position is
    if (len(drawings) != 0):
        if joystick_x > 575 and checkTime():
            drawing_nav = (drawing_nav-1)%len(drawings)
            select_drawing(drawing_nav)
            action_time = time.time()
            print("L")
        # Weird check to prevent accidental triggers
        elif joystick_x < 450 and joystick_x > 0 and checkTime():
            drawing_nav = (drawing_nav+1)%len(drawings)
            select_drawing(drawing_nav)
            action_time = time.time()
            print("R"+str(joystick_x))
    #######################################################################################
    cv.imshow('Display', img)
    if cv.waitKey(20)&0xFF == 27:
        break
cv.destroyAllWindows()