import qwiic_button

my_button = qwiic_button.QwiicButton()
if my_button.begin() == False:
    print("\nThe Qwiic Button isn't connected to the system. Please check your connection", \
        file=sys.stderr)

print("\nButton ready!")

while(True):
    if my_button.is_button_pressed() == True:
        print("\nThe button is pressed!")