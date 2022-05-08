import cv2 as cv
import numpy as np
import screeninfo
import random

colors=[(55,198,243),(56, 79, 255),(161, 80, 135), (1,137,255), (166,201,184)]

drag_start = False
prev = None
color = None

drawings = []
drawing_nav = 0

class Line:
    def __init__(self, color):
        self.color = color
        self.coords = []
    def addPoint(self, point):
        self.coords.append(point)

def draw(event, x, y, flags, param):
    global drag_start, prev, color, drawing_nav, img, cache
    if event == cv.EVENT_LBUTTONDOWN:
        color = random.randint(0, len(colors)-1)
        drawings.append(Line(colors[color]))
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

def select_line(id):
    global img
    for i in range(1, len(drawings[id].coords)):
        cv.line(img, drawings[id].coords[i-1], drawings[id].coords[i], drawings[id].color, thickness = 20)

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
