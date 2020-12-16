import cv2
import numpy as np
import imutils
from imutils.video import FPS

class Video():

    name = None
    fullPath = None
    nbFrames = None
    objs = []

    def __init__(self, name, fullPath):
        self.name = name
        self.fullPath = fullPath
        vs = cv2.VideoCapture(self.fullPath)
        self.nbFrames = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
        vs.release()





    """
    def addObjByName(self, nameObj):
        self.objs.append( Obj(nameObj, self))

    def addObjByObj(self, obj):
        self.objs.append( obj )
    """