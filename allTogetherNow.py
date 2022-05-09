# from __future__ import print_function
import board
import pyaudio
import cv2 as cv
import numpy as np
import screeninfo
import random
from enum import Enum
import qwiic_joystick
from adafruit_seesaw import seesaw, rotaryio, digitalio
import tkinter
import time
import os
import pyaudio
import wave

###################### CONSTANTS ##########################
COLORS=[(55,198,243),(56, 79, 255),(161, 80, 135), (1,137,255), (166,201,184)]

TEXT_FONTFACE = cv.FONT_HERSHEY_SIMPLEX
TEXT_SCALE = 2
TEXT_THICKNESS = 3
TEXT_COLOR = (255,255,255)
TEXT_LINETYPE = cv.LINE_8
TEXT_OFFSET = (5,5)

class States(Enum):
    RECORD = 0
    RECORDING = 1
    VIEW = 2

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
# seesaw = seesaw.Seesaw(board.I2C(), addr=0x20)

# seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF
# print("Found product {}".format(seesaw_product))
# if seesaw_product != 4991:
#     print("Wrong firmware loaded?  Expected 4991")

# seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
# button = digitalio.DigitalIO(seesaw, 24)

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
dev_index = 3 # device index found by p.get_device_info_by_index(ii)
# wav_output_filename = 'record.wav' # name of .wav file
audio = pyaudio.PyAudio() # create pyaudio instantiation

# Uncomment to test what device we're using
# for i in range(audio.get_device_count()):
#     print(audio.get_device_info_by_index(i))
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

def select_line(id):
    global img
    img = cache.copy()
    cv.imshow('Display', img)
    for i in range(1, len(drawings[id].coords)):
        cv.line(img, drawings[id].coords[i-1], drawings[id].coords[i], drawings[id].color, thickness = 20)

def PlayRecording(filename):
    os.system('./' + filename)

def switch_state(state):
    global img, my_state
    my_state = state
    text = ""
    if state == States.RECORD:
        text = "Record"
    elif state == States.VIEW:
        text = "View Drawings"
    textSize = cv.getTextSize(text, TEXT_FONTFACE, TEXT_SCALE, TEXT_THICKNESS)
    cv.rectangle(img, (3, 3), (textSize[0][0], 100), (0,0,0))
    cv.putText(img, text, (TEXT_OFFSET[0],textSize[0][1] + TEXT_OFFSET[1]), TEXT_FONTFACE, TEXT_SCALE, TEXT_COLOR, TEXT_THICKNESS, TEXT_LINETYPE, False)

def checkTime():
    global action_time
    return (time.time()-action_time > 0.5)

def StartRecording():
    global stream
    # create pyaudio stream
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=chunk)
    print("recording")

def StopRecording():
    global stream, audio
    stream.stop_stream()
    stream.close()
    audio.terminate()
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

def record():
    global my_state
    if((my_state == States.VIEW) or (my_state == States.RECORD)):
        print("start recording")
        my_state = States.RECORDING
        StartRecording()
    elif(my_state == States.RECORDING):
        print("Stop recording")
        my_state = States.RECORD
        StopRecording()

###########################################################

while(True):
    # detect button press A
    # if pressed, check record state
    # if button.value:
    #     switch_state()
    if(my_state == States.RECORDING):
        data = stream.read(chunk)
        frames.append(data)
    # detect joystick press
    if(joystick.button == 0 and checkTime()):
        action_time = time.time()
        record()
        print("button pressed")
    joystick_x = joystick.horizontal
    joystick_y = joystick.vertical
    # if moved, check what the current position is
    if (len(drawings) != 0):
        if joystick_x > 575 and checkTime():
            drawing_nav = (drawing_nav-1)%len(drawings)
            select_line(drawing_nav)
            action_time = time.time()
            print("L")
        # Weird check to prevent accidental triggers
        elif joystick_x < 450 and joystick_x > 0 and checkTime():
            drawing_nav = (drawing_nav+1)%len(drawings)
            select_line(drawing_nav)
            action_time = time.time()
            print("R"+str(joystick_x))
    cv.imshow('Display', img)
    if cv.waitKey(20)&0xFF == 27:
        break
cv.destroyAllWindows()