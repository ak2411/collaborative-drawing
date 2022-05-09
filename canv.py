from sre_parse import State
import cv2 as cv
import numpy as np
import screeninfo
import random
from enum import Enum
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
###########################################################
my_state = States.VIEW
drawings = []
drawing_nav = 0
rectangle_rolodex = []

class Line:
    def __init__(self, color):
        self.color = color
        self.coords = []
        self.recording = ""
    def addPoint(self, point):
        self.coords.append(point)
    def addRecording(self, recording):
        self.recording = recording

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

    if event == cv.EVENT_RBUTTONDOWN:
        img = cache.copy()
        cv.imshow('Display', img)
        drawing_nav = (drawing_nav+1)%len(drawings)
        select_line(drawing_nav)
        if my_state == States.RECORD:
            switch_state(States.VIEW)
        elif my_state == States.VIEW:
            switch_state(States.RECORD)

def select_line(id):
    global img
    for i in range(1, len(drawings[id].coords)):
        cv.line(img, drawings[id].coords[i-1], drawings[id].coords[i], drawings[id].color, thickness = 20)

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



screen = screeninfo.get_monitors()[0]
width, height = screen.width, screen.height

img = np.zeros((height,width,3), np.uint8)

cv.namedWindow('Display',cv.WND_PROP_FULLSCREEN)
cv.setMouseCallback('Display', draw)


cache = img.copy()

while(True):
    cv.imshow('Display', img)
    if cv.waitKey(20)&0xFF == 27:
        break
cv.destroyAllWindows()
