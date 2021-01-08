import cv2
import numpy as np
import imutils
from imutils.video import FPS
import os
import shutil

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
    fusedMasks = None
    

    def __init__(self, name, fullPath, controleur):
        self.name = name
        self.fullPath = fullPath
        vs = cv2.VideoCapture(self.fullPath)
        self.nbFrames = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frameDimensions = ( int( vs.get(cv2.CAP_PROP_FRAME_HEIGHT) ), int( vs.get(cv2.CAP_PROP_FRAME_WIDTH) ) )
        vs.release()
        self.controleur = controleur
        self.fusedMasks = [None] * self.nbFrames
        

    def getObjByName(self,name):
        for o in objs:
            if o.name == name:
                return o

        
    
    def read(self):
        """lance la lecture de la vidéo via une boucle while dont on ne sort jamais"""
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
                



    def fuseMask(self):
        """fusionne les masques de tous les objets"""
        for i in range(self.nbFrames):
            mask = np.zeros( self.frameDimensions, np.uint8)
            empty = True
            for obj in self.objs:
                if obj.mask[i] is not None:
                    empty = False
                    mask += obj.mask[i]
            ret, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)

            if not empty:
                print("maj de l'attribut")
                self.fusedMasks[i] = mask




    
    def exportFusedMasksToFile(self, location = ""):

        ###on utilise la librairie Path pour assurer le fonctionnement sous windows ET linux
        folder = os.path.join(location, 'mask')
        if not os.path.isdir(folder):
            #création du dossier s'il n'existe pas
            os.mkdir(folder)

        #si le sous dossier contenant les masques de l'objet existe, on le vide, sinon on le crée
        subfolder = os.path.join(folder,"fusion")
        if not os.path.isdir(subfolder):
            os.mkdir(subfolder)
        else:
            shutil.rmtree(subfolder)
            os.mkdir(subfolder)

        for i,m in enumerate(self.fusedMasks):
            if m is not None:
                filename = os.path.join(subfolder, "frame_" + str(i) + ".tif")
                try:
                    cv2.imwrite(filename, m)
                except:
                    print("couldn't save file {}".format(filename))
        
        print("finished saving")

