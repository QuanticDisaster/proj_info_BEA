import cv2
import numpy as np
import imutils
from imutils.video import FPS
import os
import shutil

class Video():

    """
        objet video

        ...

        Attributes
        ----------
            controleur : controleur
                référence à l'objet controleur qui gère l'application
            name : string
                nom de l'objet vidéo
            fullPath : string
                emplacement de la vidéo sur le disque
            nbFrames : int
                nombres de frame total dans la vidéo
            objs : list( Obj )
                liste des objets qui ont été définis sur la vidéo
            keyPressed : string
                contient un string renseignant sur l'action qui a été réalisée sur l'interface
            paused : bool
                indique si l'utilisateur a mis en pause la vidéo
            n_frame : int
                index de la frame qui est lue actuellement
            displayBBOX : bool
                indique si on affiche ou non les bbox sur les frames affichées
            frameDimensions : tuple(int,int)
                taille des frames
            fusedMasks : list( array )
                liste dont le ième élèment correspond au masque des différents objets sur la ième frame
            videoCapture : opencv.VideoCapture
                objet permettant la lecture des vidéos dans OpenCV


        Methods
        -------
            getObjByName 
                renvoie l'objet dont le nom est renseigné
            read 
                lit la vidéo et traite les inputs
            maskAll 
                lance le tracking de tous les objets
            fuseMask
                fusionne les masques des objets
            exportFusedMasksToFile 
                enregistre les masques fusionnés sur le disque

    """

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
    videoCapture = None
    

    def __init__(self, name, fullPath, controleur):
        """
        initialise la classe

            Parameters:
            ----------
                name (string) :
                    nom donné à la vidéo
                fullPath (string) :
                    emplacement de la vidéo sur le disque
                controleur (controleur) :
                    référence à l'objet controleur qui gère l'application
                    
        
        """
        self.name = name
        self.fullPath = fullPath
        vs = cv2.VideoCapture(self.fullPath)
        self.nbFrames = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frameDimensions = ( int( vs.get(cv2.CAP_PROP_FRAME_HEIGHT) ), int( vs.get(cv2.CAP_PROP_FRAME_WIDTH) ) )
        vs.release()
        self.controleur = controleur
        self.fusedMasks = [None] * self.nbFrames
        self.videoCapture = cv2.VideoCapture(self.fullPath)
        

    def getObjByName(self,name):
        """
        Renvoie l'objet de la vidéo dont le nom est donné est argument

            Parameters:
            ----------
                name (string) :
                    nom de l'objet qu'on cherche

            Return:
            ------
                o (Obj):
                    référence à l'objet que l'on souhaitait
                    
        
        """
        
        for o in objs:
            if o.name == name:
                return o

        
    
    def read(self):
        """
        lance la lecture de la vidéo via une boucle while et agit en fonction des actions réalisées par l'utilisateur via self.keyPressed
        NB : en l'état actuel (23/01/2021), on ne sort jamais de la boucle while
        
        """
        vs = self.videoCapture        
        # loop over frames from the video stream
        self.n_frame = 0
        timeToWait =  int( 1000 / vs.get(cv2.CAP_PROP_FPS ))
        
        #on affiche la première frame lorsqu'une vidéo est chargée
        success, frame = vs.read()
        self.controleur.showFrame(frame)
        vs.set(cv2.CAP_PROP_POS_FRAMES, 0)
        cv2.waitKey(timeToWait) & 0xFF
        self.controleur.app.processEvents()
        
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
                #on crée une fenête avec resizeable=true (enfin je suppose que c'est ce que le "2" signifie)
                cv2.namedWindow("Image",2)
                initBB = cv2.selectROI("Image", frame, fromCenter=False,
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

    def maskAll(self, tracker ):
        """
        lance le tracking de tous les objets de la vidéo via la fonction maskSequence de la classe Obj

            Parameters:
            ----------
                tracker (string) :
                    nom du tracker utilisé
                    
        
        """
        
        for obj in self.objs:
            for seq in obj.sequences:
                obj.maskSequence( seq["idFrameInit"], seq["initBB"], seq["idFrameBeginTrack"], seq["idFrameEndTrack"], tracker )
                



    def fuseMask(self):
        """
        fusionne les masques de tous les objets et les stocke dans la liste self.fusedMasks en attribut

        """
        for obj in self.objs:
            obj.bboxTrackingToMask()
            
        for i in range(self.nbFrames):
            empty = True
            for obj in self.objs:
                if obj.mask[i] is not None:
                    mask = np.zeros( self.frameDimensions, np.uint8)
                    empty = False
                    mask += obj.mask[i]
                    ret, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)

            if not empty:
                self.fusedMasks[i] = mask



    
    def exportFusedMasksToFile(self, location = ""):
        """
        Enregistre les masques de l'attribut fusedMasks sur le disque à l'emplacement donné

            Parameters:
            ----------
                location (string) :
                    emplacement où stocker les masques sur le disque
                    
        
        """
        

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

                with open(os.path.join(subfolder, "frame_" + str(i) + ".xml"), "w") as text_file:
                        text_file.write("<FileOriMnt>\n")
                        text_file.write("<NameFileMnt>.\\frame_{0}.tif</NameFileMnt>\n".format(i))
                        text_file.write("<NombrePixels>{0} {1}</NombrePixels>\n".format( m.shape[0], m.shape[1] ))
                        text_file.write("<OriginePlani>0 0</OriginePlani>\n")
                        text_file.write("<ResolutionPlani>1 1</ResolutionPlani>\n")
                        text_file.write("<OrigineAlti>0</OrigineAlti>\n")
                        text_file.write("<ResolutionAlti>1</ResolutionAlti>\n")
                        text_file.write("<Geometrie>eGeomMNTFaisceauIm1PrCh_Px1D</Geometrie>\n")
                        text_file.write("</FileOriMnt>\n")
                                    

        print("finished saving")

