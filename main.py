import qwiic_joystick
from adafruit_seesaw import seesaw, rotaryio, digitalio
import tkinter

MAX_DRAWINGS = 100
COLOR_RANGES = []
# List storing the audio and array of coordinates
records= []
curr_record_pos = 0


# Use like: Record("address",[list of coords])
class Record:
    def __init__(self, recording, coordinates):
        self.recording = recording
        self.coordinates = coordinates

# init canvas
root = tkinter.Tk()
canvas = tkinter.Canvas(root, bg="black", height =500, width=500 )
canvas.pack(fill="both", expand=True)

# Get button
seesaw = seesaw.Seesaw(board.I2C(), addr=0x36)

seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF
print("Found product {}".format(seesaw_product))
if seesaw_product != 4991:
    print("Wrong firmware loaded?  Expected 4991")

seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
button = digitalio.DigitalIO(seesaw, 24)


# initialize joystick
joystick = qwiic_joystick.QwiicJoystick()

if joystick.connected == False:
    print("The Qwiic Joystick device isn't connected to the system. Please check your connection", \
        file=sys.stderr)
    return

joystick.begin()
print("Joystick initialized")

def record():
    print("Record")

def playRecord():
    print(curr_record_pos)

def nav_next():
    curr_record_pos = (curr_record_pos+1)%len(records)

def  nav_prev():
    curr_record_pos = (curr_record_pos-1)%len(records)

def draw(start_coord, end_coord):
    print("drawing")
    # randomize color, interpolate the color range
    color="blue"
    canvas.create_line(start_coord.x, end_coord.x, start_coord.y, end_coord.y, fill=color )

while True:
    # detect button press A
    # if pressed, check record state
    if button.value:
        record()
    # detect joystick press
    if(joystick.button == 0):
        print("button pressed")
    joystick_x = joystick.horizontal
    joystick_y = joystick.vertical
    # if moved, check what the current position is
    if joystick_x > 575:
        print("L")
    elif joystick_x < 450:
        print("R")
    elif y > 575:
        print("U")
    elif y < 575:
        print("D")
