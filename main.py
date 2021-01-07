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

from window import MyWindow
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *




class Controleur():

    vue = None
    current_video = None
    read = True
    key3 = None
    app = None

    def __init__(self,app):
        self.app = app

    def exportObjectMask(self):
        obj = self.getObjByName( self.vue.findChild(QComboBox, "liste_objets").currentText() )
        print(obj.name)
        obj.bboxTrackingToMask()
        obj.exportMaskToFile()

    def exportFusedMasks(self):
        print("export fused masks")
        self.current_video.fuseMask()
        self.current_video.exportFusedMasksToFile()
    
    def loadVideo(self,fullPath):
        #change la vidéo en cours d'édition
        #cette fonction est appelée par la vue après un click sur "Load Video"
        self.current_video = Video("video1",fullPath,self)
        self.current_video.paused = True
        self.current_video.read()

    def displayBBOX(self):
        self.current_video.displayBBOX = not self.current_video.displayBBOX

        
    def maskSequence(self, obj, seq):
        obj.maskSequence( seq["idFrameInit"], seq["initBB"], seq["idFrameBeginTrack"], seq["idFrameEndTrack"] ) 

    def maskAll(self):
        self.current_video.maskAll()
        
    def next_frame(self):
        self.current_video.keyPressed = "next"

    def precedent_frame(self):
        self.current_video.keyPressed = "precedent" 

    def skip_forward(self):
        self.current_video.keyPressed = "skip_forward"

    def skip_backward(self):
        self.current_video.keyPressed = "skip_backward"

    def goToVideoBeginning(self):
        self.current_video.keyPressed = "go_to_beginning"
        
    def goToVideoEnd(self):
        self.current_video.keyPressed = "go_to_end"
        
    def pauseVideo(self):
        self.current_video.paused = True

    def readVideo(self):
        self.current_video.keyPressed = "read"
        
    def initializeMask(self):
        self.current_video.keyPressed = "select_ROI"

    def updateBBOX(self, idFrame, bbox):
        obj = self.getObjByName( self.vue.findChild(QComboBox, "liste_objets").currentText())
        seq = self.getSeqByName( obj, self.vue.findChild(QComboBox, "liste_sequences").currentText())
        seq["initBB"] = bbox

        self.vue.updateInitFrame(idFrame)
        
        
    def showFrame(self,frame):
        idFrame = self.current_video.n_frame
        nbFrames = self.current_video.nbFrames
        self.vue.showFrame(frame, idFrame, nbFrames)
        
        
    def updateParameters(self, obj_name, seq_name, begin, end, init):
        current_obj = self.getObjByName(obj_name)
        if current_obj != None:
            current_seq = self.getSeqByName(current_obj, seq_name)
            if current_seq != None:
                current_seq["idFrameBeginTrack"] = begin
                current_seq["idFrameEndTrack"] = end
                current_seq["idFrameInit"] = init
        
    def getObjByName(self,name):
        for o in self.current_video.objs:
            if o.name == name:
                return o
        return None

    def getSeqByName(self,obj,name):
        for s in obj.sequences:
            if s["name"] == name:
                return s
        return None

    def addObject(self,name):
        print(name)
        obj = Obj(name, self.current_video)
        self.current_video.objs.append(obj)

    def renameObject(self,obj, new_name):
        for o in self.current_video.objs:
            if o.name == obj.name:
                o.name = new_name
                break
            
    def deleteObject(self,obj):
        list_without_obj = []
        for o in self.current_video.objs:
            if o.name != obj.name:
                list_without_obj.append(o)
        self.current_video.objs = list_without_obj

    
    def addSequence(self,obj,name):
        print(obj.name)
        obj.sequences.append(
            {   "name" : name,
                "idFrameInit" : 0,
                "initBB" : (0,0,0,0),
                "idFrameBeginTrack" : 0,
                "idFrameEndTrack" : 0})

    def renameSequence(self,obj,old_name,new_name):
        for s in obj.sequences:
            if s["name"] == old_name:
                s["name"] = new_name

    def deleteSequence(self, obj, name):
            list_without_seq = []
            for s in obj.sequences:
                if s["name"] != name:
                    list_without_seq.append(s)
            obj.sequences = list_without_seq
            
        
    """def readVideo(self, fullPath):
        self.fullPath = fullPath
        self.objs= []
        vs = cv2.VideoCapture(self.fullPath)
        # loop over frames from the video stream
        n_frame = 0

    

        
        print("hop")
        
        key2 = None

        def forward():
            #self.read = False
            print("backwaaaaard")
            self.key3 = ord("a")
            #self.read = True
        self.vue.findChild(QPushButton, "pause").clicked.connect(forward)
        #key2 = ord('a')
        while self.read:

            print(self.key3)
        
            # grab the current frame
            success, f = vs.read()

            if not success:
                break
            frame = f
            n_frame += 1
            # check to see if we have reached the end of the stream

            frame = imutils.resize(frame, width=1000)
            (H, W) = frame.shape[:2]

            # on fait une copie de la frame pour "écrire" dessus sans modifier la frame originale
            display_frame = frame
            for obj in self.objs:
                box = obj.bbox[n_frame - 1]
                if box != -999:
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (0, 255, 0), 2)

            
            
            cv2.imshow("Frame", display_frame)
            key = cv2.waitKey(1) & 0xFF

            if self.key3 == ord("a"):
                #we go 100 frames backward
                vs.set(cv2.CAP_PROP_POS_FRAMES, n_frame - 100)
                n_frame = max(0, n_frame - 100)
                self.key3 = None

            
        # otherwise, release the file pointer
        vs.release()
        # close all windows
        cv2.destroyAllWindows()
        """
        
        


def main():

    video_filename = r"D:\Mes documents\_PPMD\Projet informatique BEA\local\donnees\donnees_BEA\parachute.mp4"

    import os.path
    if not os.path.isfile(video_filename):
        print("File not found")
        raise


    videoObj = Video("video1", video_filename)

    objet = Obj("element1", videoObj)
    videoObj.objs.append(objet)

    objet2 = Obj("element2", videoObj)
    videoObj.objs.append(objet2)

    (frameInit, initBB, frameBeginTrack, frameEndTrack) = (0, (616.247802734375, 544.9813232421875, 23.529401779174805, 29.411752700805664), 0, 210)#objet2.initElements()
    result2 = objet2.maskSequence(frameInit, initBB, frameBeginTrack, frameEndTrack)
    (frameInit, initBB, frameBeginTrack, frameEndTrack) = (126, (224, 404, 150, 158), 14, 210)
    result = objet.maskSequence(frameInit, initBB, frameBeginTrack, frameEndTrack)

    #result = videoObj.mask(frameInit, initBB, frameBeginTrack, frameEndTrack, videoObj.objs[0])
    objet.visualizebbox()
    import pdb; pdb.set_trace()


def loadVideo(fullPath):
    current_video = Video("video1",fullPath)

def loadVideoView(fullPath):
    MyWindow.label_4.t


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


    
# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    import pdb, traceback, sys
    sys.excepthook = except_hook
    try:
        import sys
        
        
        #app = QtWidgets.QApplication(sys.argv)
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        controleur = Controleur(app)
        controleur.vue = MyWindow(controleur)
        
        ####VERSION AVEC INTERFACE
        controleur.vue.show()

        ####VERSION SANS INTERFACE
        """
        fullPath = r"D:\Mes documents\_PPMD\Projet informatique BEA\local\donnees\videos_youtube\Top 5 POV Plane Emergency Landings.mp4"
        controleur.current_video = Video("video1",fullPath,controleur)
        controleur.current_video.paused = True
        print("ok")
        controleur.addObject("objet 1")
        controleur.addSequence(controleur.getObjByName("objet 1"), "sequence 1" )
        controleur.getObjByName("objet 1").maskSequence(126, (224, 404, 150, 158), 100, 210)
        controleur.getObjByName("objet 1").bboxTrackingToMask()
        controleur.getObjByName("objet 1").exportMaskToFile()

        controleur.addObject("objet 2")
        controleur.addSequence(controleur.getObjByName("objet 2"), "sequence 1" )
        controleur.getObjByName("objet 2").maskSequence(150, (275, 475, 220, 228), 130, 250)
        controleur.getObjByName("objet 2").bboxTrackingToMask()
        controleur.getObjByName("objet 2").exportMaskToFile()
        

        controleur.current_video.fuseMask()
        """
        #
        #controleur.readVideo(r"D:\Mes documents\_PPMD\Projet informatique BEA\local\donnees\donnees_BEA\paramoteur.mp4")


        #controleur.vue.select_video_file_debug()

        
        sys.exit(app.exec_())

        import pdb; pdb.set_trace()

        
        
        print("the end")
        #main()

        
    except:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
