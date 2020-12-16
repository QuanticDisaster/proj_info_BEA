# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import numpy as np
# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2
from Video import Video
from Obj import Obj

def main():

    video_filename = r"D:\Mes documents\_PPMD\Projet informatique BEA\donnees_BEA\parachute.mp4"


    videoObj = Video("video1", video_filename)

    objet = Obj("element1", videoObj)
    videoObj.objs.append(objet)

    #(frameInit, initBB, frameBeginTrack, frameEndTrack) = objet.initElements()

    (frameInit, initBB, frameBeginTrack, frameEndTrack) = (126, (224, 404, 150, 158), 14, 210)
    result = objet.maskSequence(frameInit, initBB, frameBeginTrack, frameEndTrack)
    #result = videoObj.mask(frameInit, initBB, frameBeginTrack, frameEndTrack, videoObj.objs[0])
    import pdb; pdb.set_trace()


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    import pdb, traceback, sys
    try:
        main()
    except:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
