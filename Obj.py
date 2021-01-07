import cv2
import time
import imutils
import numpy as np
from imutils.video import FPS
import os
import shutil



class Obj():

    name = None
    video = None
    mask =  None
    bbox = None
    sequences = None
    ## on définit les séquences comme une liste de dictionnaires
    ## sequence1 = { "name" : "sequence1",
    ##               "idFrameInit" : 174,
    ##               "initBB" : (0,0,0,0),
    ##               "idFrameBeginTrack" : 100,
    ##               "idFrameEndTrack" : 200}

    def __init__(self, name, video):
        self.name = name
        self.video = video
        self.bbox = [(-1, -1, -1, -1)] *  video.nbFrames
        self.mask = [None] *  video.nbFrames
        self.sequences = []

    def initElements(self):
        """
        Cette fonction renvoie
        """

        idFrameInit, initBB, idFrameBeginTrack, idFrameEndTrack = -1, -1, -1, -1

        vs = cv2.VideoCapture(self.video.fullPath)
        # loop over frames from the video stream
        n_frame = 0
        timeToWait = 100
        showFrameInformation = True
        while True:

            # grab the current frame
            success, f = vs.read()

            if success:
                frame = f
                n_frame += 1
            else:
                #en cas d'échec, on récupère la dernière frame
                vs.set(cv2.CAP_PROP_POS_FRAMES,vs.get(cv2.CAP_PROP_FRAME_COUNT)-1)
                frame = vs.read()[1]
            # check to see if we have reached the end of the stream

            frame = imutils.resize(frame, width=1000)
            (H, W) = frame.shape[:2]



            #on fait une copie de la frame pour "écrire" dessus sans modifier la frame originale
            display_frame = frame
            speed_text = ""
            if timeToWait == 1:
                speed_text = "MAX"
            elif timeToWait == 0:
                speed_text = ""
            else:
                speed_text = round(100 / timeToWait, 2)
            info = [
                ("frame", n_frame),
                ("speed", speed_text),
                ("paused", timeToWait == 0),
            ]
            if showFrameInformation:
                # show the output frame

                for (i, (k, v)) in enumerate(info):
                    print(i, H - ((i * 20) + 20))
                    text = "{}: {}".format(k, v)
                    cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            cv2.imshow("Frame", display_frame)
            key = cv2.waitKey(timeToWait) & 0xFF



            ################ tools to navigate in the video  ####################

            ###here we handle the keys skipping X frames forward or backward
            if key == ord("e"):
                #we go 100 frames forward
                vs.set(cv2.CAP_PROP_POS_FRAMES, n_frame + 100)
                n_frame = int(min( n_frame + 100, vs.get(cv2.CAP_PROP_FRAME_COUNT)))

            if key == ord("a"):
                #we go 100 frames backward
                vs.set(cv2.CAP_PROP_POS_FRAMES, n_frame - 100)
                n_frame = max(0, n_frame - 100)

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

            ###we speed up or down the reading of the video
            if key == ord("w"):
                timeToWait += 10
            #fasta, fasta, fasta !
            if key == ord("x"):
                if timeToWait == 0:
                    timeToWait = 150
                timeToWait = max(1, timeToWait - 10)

            ###pause
            if key == ord("p"):
                if timeToWait == 0:
                    timeToWait = 150
                timeToWait = 0

            ###hide information
            if key == ord("h"):
                showFrameInformation = not showFrameInformation


            #################### selecting BBOX and frames ########################

            # if the 's' key is selected, we are going to "select" a bounding
            # box to track
            if key == ord("s"):
                # select the bounding box of the object we want to track (make
                # sure you press ENTER or SPACE after selecting the ROI)
                initBB = cv2.selectROI("Frame", frame, fromCenter=False,
                                       showCrosshair=True)
                idFrameInit = n_frame

            ###if u is pressed, frame is considered beginning of the sequence to track object. Same for i with end of the sequence
            if key == ord("u"):
                idFrameBeginTrack = n_frame
            if key == ord("i"):
                idFrameEndTrack = n_frame


            ##################### returning the sequence/BBOX choice ##################

            if key == ord("t"):
                cv2.destroyAllWindows()
                return (idFrameInit, initBB, idFrameBeginTrack, idFrameEndTrack)

        vs.release()
        cv2.destroyAllWindows()

    def maskSequence(self, frameInit, initBB, frameBeginTrack, frameEndTrack):

        frameInit, initBB, frameBeginTrack, frameEndTrack = int(frameInit), initBB, int(frameBeginTrack), int(frameEndTrack)
        
        tracker = "csrt"
        # extract the OpenCV version info
        (major, minor) = cv2.__version__.split(".")[:2]

        # if we are using OpenCV 3.2 OR BEFORE, we can use a special factory
        # function to create our object tracker
        if int(major) == 3 and int(minor) < 3:
            tracker = cv2.Tracker_create(tracker.upper())

        # otherwise, for OpenCV 3.3 OR NEWER, we need to explicity call the
        # approrpiate object tracker constructor:
        else:
            # initialize a dictionary that maps strings to their corresponding
            # OpenCV object tracker implementations
            OPENCV_OBJECT_TRACKERS = {
                "csrt": cv2.TrackerCSRT_create,  # O : more accurate than KCF but slower
                "kcf": cv2.TrackerKCF_create,  # O : doest not handle occlusions very well
                "boosting": cv2.TrackerBoosting_create,  # X : very old, not recommended
                "mil": cv2.TrackerMIL_create,  # O : better than boosting, badly handles failures
                "tld": cv2.TrackerTLD_create,  # : lot of false positives ?
                "medianflow": cv2.TrackerMedianFlow_create,
                # O : handles failures well, but fails often when handling fast-moving objects or on quick appereance change
                "mosse": cv2.TrackerMOSSE_create  # X : speed-oriented
            }
            # grab the appropriate object tracker using our dictionary of
            # OpenCV object tracker objects
            tracker = OPENCV_OBJECT_TRACKERS[tracker]()

            vs = cv2.VideoCapture(self.video.fullPath)
            # initialize the FPS throughput estimator
            fps = None

            ####################  handle FORWARD tracking ########################

            vs.set(cv2.CAP_PROP_POS_FRAMES, frameInit)
            fps = FPS().start()
            for i in range(frameInit, frameEndTrack):

                frame = vs.read()[1]
                #frame = imutils.resize(frame, width=1000)
                (H, W) = frame.shape[:2]



                if i == frameInit:
                    tracker.init(frame, initBB)
                    self.bbox[frameInit] = initBB

                (success, box) = tracker.update(frame)
                # check to see if the tracking was a success
                if success:
                    self.bbox[i] = box
                    
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (0, 255, 0), 2)
                else:
                    self.bbox[i] = -1
                # update the FPS counter
                fps.update()
                fps.stop()
                # initialize the set of information we'll be displaying on
                # the frame
                info = [
                    ("frame", i),
                    ("Success", "Yes" if success else "No"),
                    ("FPS", "{:.2f}".format(fps.fps())),
                    ("Progress (%)", round((i - frameInit) / max(1,(frameEndTrack - frameInit)), 2))
                ]
                # loop over the info tuples and draw them on our frame
                for (i, (k, v)) in enumerate(info):
                    text = "{}: {}".format(k, v)
                    cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # show the output frame
                cv2.imshow("Frame", frame)
                # unused, but necessary to make application work otherwise grey windows appears
                key = cv2.waitKey(1) & 0xFF


            ####################  handle BACKWARD tracking ########################

            fps = FPS().start()
            vs.set(cv2.CAP_PROP_POS_FRAMES, frameInit)
            for i in range(frameInit, frameBeginTrack - 1, -1):
                vs.set(cv2.CAP_PROP_POS_FRAMES, i)
                frame = vs.read()[1]
                #frame = imutils.resize(frame, width=1000)
                (H, W) = frame.shape[:2]

                if i == frameInit:
                    #TODO
                    #le tracker ne peutpas être initialisé 2 fois semble-t-il, à corriger ! 
                    tracker.init(frame, initBB)
                    self.bbox[frameInit] = initBB

                (success, box) = tracker.update(frame)
                # check to see if the tracking was a success
                if success:
                    self.bbox[i] = box
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (0, 255, 0), 2)
                # update the FPS counter
                fps.update()
                fps.stop()
                # initialize the set of information we'll be displaying on
                # the frame
                info = [
                    ("frame", i),
                    ("Success", "Yes" if success else "No"),
                    ("FPS", "{:.2f}".format(fps.fps())),
                    ("Progress (%)", round(1 - (i - frameBeginTrack) / max(1,(frameInit - frameBeginTrack)), 2))
                ]
                # loop over the info tuples and draw them on our frame
                for (i, (k, v)) in enumerate(info):
                    text = "{}: {}".format(k, v)
                    cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # show the output frame
                cv2.imshow("Frame", frame)
                # unused, but necessary to make application work otherwise grey windows appears
                key = cv2.waitKey(1) & 0xFF

            # otherwise, release the file pointer
            vs.release()
            # close all windows
            cv2.destroyAllWindows()

    def visualizebbox(self):
        vs = cv2.VideoCapture(self.video.fullPath)
        # loop over frames from the video stream
        n_frame = 0
        while True:

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
            box = self.bbox[n_frame - 1 ]
            if box[0] != -1:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                          (0, 255, 0), 2)

            cv2.imshow("Frame", display_frame)
            key = cv2.waitKey(1) & 0xFF
        # otherwise, release the file pointer
        vs.release()
        # close all windows
        cv2.destroyAllWindows()

    def bboxTrackingToMask(self):
        for i in range(self.video.nbFrames):
            binaryImage = np.zeros( self.video.frameDimensions, np.uint8)
            (x, y, w, h) = [int(v) for v in self.bbox[i]]
            if x != -1:
                cv2.rectangle( binaryImage, (x,y), (x + w, y + h), 255, -1)
                self.mask[i] = binaryImage

    def exportMaskToFile(self, location = ""):
        ###on utilise la librairie Path pour assurer le fonctionnement sous windows ET linux
        folder = os.path.join(location, 'mask')
        if not os.path.isdir(folder):
            #création du dossier s'il n'existe pas
            os.mkdir(folder)

        #si le sous dossier contenant les masques de l'objet existe, on le vide, sinon on le crée
        subfolder = os.path.join(folder,self.name)
        if not os.path.isdir(subfolder):
            os.mkdir(subfolder)
        else:
            shutil.rmtree(subfolder)
            os.mkdir(subfolder)

        for i,m in enumerate(self.mask):
            if m is not None:
                filename = os.path.join(subfolder, "frame_" + str(i) + ".tif")
                try:
                    cv2.imwrite(filename, m)
                except:
                    print("couldn't save file {}".format(filename))
        
        
