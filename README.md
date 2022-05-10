# Collaborative Drawing Tool


[Full project walkthrough](https://docs.google.com/document/d/12rxb3U1-YJq_cB1daeqb204G5D9D5gdaPoI1SY52Kgc/edit?usp=sharing)


# Installation
* In the terminal, run:
``` pip install sparkfun-qwiic-joystick screeninfo sparkfun-qwiic-button```

# Running the system
* In the terminal, run:
``` python3 main.py```

# Troubleshooting
## Configuring the right audio channel for the microphone
* Use the `tests/test_audio.py` script to test which audio channel the microphone is using
## Testing whether the button works
* Use the `tests/test_button.py` script to test whether the button can be detected
## Cannot hear audio?
* Try typing this command to turn the raspi volume up: `amixer sset Master 95%`
## Other tips
* Ensure all dependencies are installed


# References
* [Full-screen code](https://gist.github.com/ronekko/dc3747211543165108b11073f929b85e) 
* [Draw continuously with mouse](https://stackoverflow.com/questions/28340950/opencv-how-to-draw-continously-with-a-mouse)
* [OpenCV common functions](https://github.com/opencv/opencv/blob/master/samples/python/common.py)
* [Detecting keyboard presses](https://stackoverflow.com/questions/24072790/how-to-detect-key-presses)
* [Delete drawn lines on image python](https://stackoverflow.com/questions/33548150/how-to-delete-drawn-lines-on-image-in-python)
