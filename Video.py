import cv2
import numpy as np
import imutils
from imutils.video import FPS

class Video():

    controleur = None
    name = None
    fullPath = None
    nbFrames = None
    objs = []
    keyPressed = None
    paused = None
    n_frame = None
    displayBBOX = True
    frameDimensions = (0,0)
    

    def __init__(self, name, fullPath, controleur):
        self.name = name
        self.fullPath = fullPath
        vs = cv2.VideoCapture(self.fullPath)
        self.nbFrames = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frameDimensions = ( int( vs.get(cv2.CAP_PROP_FRAME_HEIGHT) ), int( vs.get(cv2.CAP_PROP_FRAME_WIDTH) ) )
        vs.release()
        self.controleur = controleur
        

    def getObjByName(self,name):
        for o in objs:
            if o.name == name:
                return o

        
    def visualizebbox(self):
        vs = cv2.VideoCapture(self.fullPath)
        # loop over frames from the video stream
        self.n_frame = 0
        while True:

            # grab the current frame
            success, f = vs.read()

            if not success:
                break
            frame = f
            self.n_frame += 1
            # check to see if we have reached the end of the stream

            frame = imutils.resize(frame, width=1000)
            (H, W) = frame.shape[:2]

            # on fait une copie de la frame pour "écrire" dessus sans modifier la frame originale
            display_frame = frame
            for obj in self.objs:
                box = obj.bbox[self.n_frame - 1]
                if box != -999:
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (0, 255, 0), 2)

            cv2.imshow("Frame", display_frame)
            key = cv2.waitKey(1) & 0xFF
        # otherwise, release the file pointer
        vs.release()
        # close all windows
        cv2.destroyAllWindows()

    def read(self):
        vs = cv2.VideoCapture(self.fullPath)
        # loop over frames from the video stream
        self.n_frame = 0
        timeToWait = 25
        
        while True:
            ################ tools to navigate in the video  ####################
            if self.keyPressed == "next":
                #we go 1 frames forward
                vs.set(cv2.CAP_PROP_POS_FRAMES, self.n_frame)
                self.n_frame = int(min( self.n_frame, vs.get(cv2.CAP_PROP_FRAME_COUNT)))

            elif self.keyPressed == "precedent":
                #we go 1 frames backward
                vs.set(cv2.CAP_PROP_POS_FRAMES, self.n_frame - 2)
                self.n_frame = max(0, self.n_frame - 2)

            ###here we handle the keys skipping X frames forward or backward
            elif self.keyPressed == "skip_forward":
                #we go 100 frames forward
                vs.set(cv2.CAP_PROP_POS_FRAMES, self.n_frame + 99)
                self.n_frame = int(min( self.n_frame + 99, vs.get(cv2.CAP_PROP_FRAME_COUNT)))

            elif self.keyPressed == "skip_backward":
                #we go 100 frames backward
                vs.set(cv2.CAP_PROP_POS_FRAMES, self.n_frame - 101)
                self.n_frame = max(0, self.n_frame - 101)

            elif self.keyPressed == "read":
                self.paused = False

            elif self.keyPressed == "go_to_beginning":
                vs.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.n_frame = 0

            elif self.keyPressed == "go_to_end":
                vs.set(cv2.CAP_PROP_POS_FRAMES, vs.get(cv2.CAP_PROP_FRAME_COUNT) - 2)
                self.n_frame = int( vs.get(cv2.CAP_PROP_FRAME_COUNT) - 2 )

            # if the 's' key is selected, we are going to "select" a bounding
            # box to track
            elif self.keyPressed == "select_ROI":
                # select the bounding box of the object we want to track (make
                # sure you press ENTER or SPACE after selecting the ROI)
                initBB = cv2.selectROI("Frame", frame, fromCenter=False,
                                       showCrosshair=True)
                cv2.destroyAllWindows()
                self.controleur.updateBBOX(self.n_frame, initBB)
                self.paused = True

            else:
                pass
            
            ###si la vidéo n'est pas en pause OU en pause mais l'utilisateur clique sur un bouton, on lit la vidéo
            if not ( self.paused and self.keyPressed == None):
                # grab the current frame
                success, frame = vs.read()

                if not success:
                    pass
                else:
                    self.n_frame += 1
                    # check to see if we have reached the end of the stream
                    #cv2.imshow("Frame", frame)
                    display_frame = frame
                    if self.displayBBOX:
                        for obj in self.objs:
                            box = obj.bbox[self.n_frame - 1]
                            if box != -999:
                                (x, y, w, h) = [int(v) for v in box]
                                cv2.rectangle(display_frame, (x, y), (x + w, y + h),
                                              (0, 255, 0), 2)
                    self.controleur.showFrame(display_frame)

            
                    
            self.keyPressed = None
            
            key = cv2.waitKey(timeToWait) & 0xFF
            self.controleur.app.processEvents()

        # otherwise, release the file pointer
        vs.release()
        # close all windows
        #cv2.destroyAllWindows()

    def maskAll(self):
        for obj in self.objs:
            for seq in obj.sequences:
                obj.maskSequence( seq["idFrameInit"], seq["initBB"], seq["idFrameBeginTrack"], seq["idFrameEndTrack"] )
                

    #def bboxTrackingToMask(self, idFrameDebut, idFrameFin):
    #    for i in range(idFrameDebut, idFrameFin):
    #        binaryImage = np.array( self.frameDimension, np.uint8)
    #        Mask
        
    #def resumeRead(self,frameToStart):
        
    """
    def addObjByName(self, nameObj):
        self.objs.append( Obj(nameObj, self))

    def addObjByObj(self, obj):
        self.objs.append( obj )
    """
