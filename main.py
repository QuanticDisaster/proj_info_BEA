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
    """
        Classe controleur, elle reçoit les messages de la vue, lance les calculs du modèle (vidéo) et renvoie les résultats à la vue

        ...

        Attributes
        ----------
            vue : MyWindow
                référence à l'interface graphique
            current_video : Video
                référence à la vidéo en cours de lecture
            app : PyQt5.QApplication
                référence à l'application. Ne sert qu'à utiliser la fonction processEvent()


        Methods
        -------
            goToFrame 
                positionne la vidéo à une frame particulière
            deleteCurrentMask 
                supprime le masque sur la frame
            editCurrentMask 
                lance un masque manuel sur la frame
            exportObjectMask
                lance le tracking puis sauvegarde les masques de l'objet sur le disque
            exportFusedMasks 
                fusionne les masques de la vidéo et enregistre les masques sur le disque
            loadVideo
                charge une vidéo et lance sa lecture
            displayBBOX
                change l'option qui affiche ou non les bbox
            maskSequence
                lance le tracking d'une séquence
            maskAll
                lance le tracking de toutes les séquences
                
            next_frame
                passe à la frame suivante
            precedent_frame
                passe à la frame précèdente
            skip_forward
                avance de 100 frames
            skip_backward
                recule de 100 frames
            goToVideoBeginning
                va au début de la vidéo
            goToVideoEnd
                va à la fin de la vidéo
            pauseVideo
                met en pause
            readVideo
                continue la lecture
                
            initializeMask
                lance l'initialisation d'une bbox par l'utilisateur
            updateBBOX
                enregistre la bbox initialisée dans la séquence
            showFrame
                affiche une frame dans la vue
            updateParameters
                enregistre tout changement dans les paramètres de la séquence
            getObjByName
                renvoie l'objet dont le nom est donné
            getSeqByName
                renvoie la séquence dont l'objet et le nom sont donnés
            
            addObject
                ajoute un objet à la vidéo
            renameObject
                renomme l'objet dont le nom est donné
            deleteObject
                supprime l'objet dont le nom est donné
            addSequence
                ajoute un objet à la vidéo
            renameSequence
                renomme la séquence dont l'objet et le nom sont donnés
            deleteSequence
                supprime la séquence dont l'objet et le nom sont donnés


    """

    vue = None
    current_video = None
    app = None

    def __init__(self,app):
        self.app = app

    def goToFrame(self,idFrame):
        """
        va à la frame donnée

            Parameters:
            ----------
                idFrame (int) :
                    index de la frame à laquelle on se rend  
        
        """
        vs = self.current_video.videoCapture
        #l'humain compte à partir de 1 donc la frame 1 pour l'humain est la frame 0 pour l'ordi
        vs.set(cv2.CAP_PROP_POS_FRAMES, idFrame - 1)
        self.current_video.n_frame = idFrame - 1

        
    def deleteCurrentMask(self, obj):
        """
        supprime le masque et bbox de l'objet sur la frame actuelle

            Parameters:
            ----------
                obj (Obj) :
                    objet dont on supprime le masque
        
        """
        currentFrame = self.current_video.n_frame - 1 
        obj.bbox[currentFrame] = (-1, -1, -1, -1)
        obj.mask[currentFrame] = None

    def editCurrentMask(self,obj):
        """
        crée un masque manuel sur l'objet sur la frame actuelle et remplace toute bbox et/masque précédemment définie

            Parameters:
            ----------
                obj (Obj) :
                    objet dont on modifie le masque
        
        """
        currentFrame = self.current_video.n_frame - 1 
        obj.manualBBOX(currentFrame)

    def exportObjectMask(self):
        """
        Exporte les masques de l'objet sélectionné dans un dossier sur le disque
        
        """
        obj = self.getObjByName( self.vue.findChild(QComboBox, "liste_objets").currentText() )
        print(obj.name)
        obj.bboxTrackingToMask()
        obj.exportMaskToFile()

    def exportFusedMasks(self):
        """
        fusionne les masques de la vidéo et les renregistre sur le disque
        
        """
        print("export fused masks")
        self.current_video.fuseMask()
        self.current_video.exportFusedMasksToFile()
    
    def loadVideo(self,fullPath):
        """
        Charge la vidéo donnée par l'utilisateur depuis le disque

            Parameters:
            ----------
                fullPath (string) :
                    emplacement de la vidéosur le disque
        
        """
        #change la vidéo en cours d'édition
        #cette fonction est appelée par la vue après un click sur "Load Video"
        self.current_video = Video("video1",fullPath,self)
        self.current_video.paused = True

        #on force la création d'au moins un objet 
        self.vue.create_object("default")
        
        self.current_video.read()

    def displayBBOX(self):
        """
        Affiche les bbox si elles étaient désactivées et les retire si elles étaient activées
        
        """
        self.current_video.displayBBOX = not self.current_video.displayBBOX

        
    def maskSequence(self, obj, seq, tracker):
        """
        lance le tracking d'une séquence

            Parameters:
            ----------
                obj (Obj) :
                    objet à tracker
                seq (dict):
                    séquence à traiter
                tracker (string):
                    tracker à utiliser
                
        """
        obj.maskSequence( seq["idFrameInit"], seq["initBB"], seq["idFrameBeginTrack"], seq["idFrameEndTrack"], tracker ) 

    def maskAll(self, tracker):
        """
        lance le tracking de tous les objets

            Parameters:
            ----------
                tracker (string):
                    nom du tracker à utiliser
        
        """
        self.current_video.maskAll(tracker)
        
    def next_frame(self):
        """
        avance d'1 frame
        
        """
        self.current_video.keyPressed = "next"

    def precedent_frame(self):
        """
        recule d'1 frame
        
        """
        self.current_video.keyPressed = "precedent" 

    def skip_forward(self):
        """
        avance de 100 frames
        
        """
        self.current_video.keyPressed = "skip_forward"

    def skip_backward(self):
        """
        recule de 100 frames
        """
        self.current_video.keyPressed = "skip_backward"

    def goToVideoBeginning(self):
        """
        va au début de la vidéo
        
        """
        self.current_video.keyPressed = "go_to_beginning"
        
    def goToVideoEnd(self):
        """
        va à la fin de la vidéo
        
        """
        self.current_video.keyPressed = "go_to_end"
        
    def pauseVideo(self):
        """
        met en pause
        
        """
        self.current_video.paused = True

    def readVideo(self):
        """
        relance la lecture
        
        """
        self.current_video.keyPressed = "read"
        
    def initializeMask(self):
        """
        indique au modèle que l'utilisateur souhaite initialiser un masque
        """
        self.current_video.keyPressed = "select_ROI"

    def updateBBOX(self, idFrame, bbox):
        """
        enregistre le masque initialisé par l'utilisateur dans le modèle et met à jour l'affichage
        fonction appelée par le modèle une fois le masque initialisé pour maj le paramètre initBB de la séquence et maj l'affichage

            Parameters:
            ----------
                idFrame (int) :
                    index de la frame sur laquelle le masque a été initialisé
                bbox (tuple(int,int,int,int)):
                    bbox que l'utilisateur a choisi
        
        """
        obj = self.getObjByName( self.vue.findChild(QComboBox, "liste_objets").currentText())
        seq = self.getSeqByName( obj, self.vue.findChild(QComboBox, "liste_sequences").currentText())
        seq["initBB"] = bbox

        self.vue.updateInitFrame(idFrame)
        
        
    def showFrame(self,frame):
        """
        lance l'affichage de la frame en entrée dans l'interface graphique

            Parameters:
            ----------
                frame (array) :
                    image
        
        """
        idFrame = self.current_video.n_frame
        nbFrames = self.current_video.nbFrames
        self.vue.showFrame(frame, idFrame, nbFrames)
        
        
    def updateParameters(self, obj_name, seq_name, begin, end, init):
        """
        enregistre toute modification des paramètres de la séquence par l'utilisateur

            Parameters:
            ----------
                obj_name (string) :
                    nom de l'objet à mettre à jour
                seq_name (string):
                    nom de la séquence à mettre à jour
                begin (int):
                    index de la frame de début de la séquence
                end (int):
                    index de la frame de fin de la séquence
                init (int):
                    index de la frame où le masque a été initialisé
        
        """
        
        current_obj = self.getObjByName(obj_name)
        if current_obj != None:
            current_seq = self.getSeqByName(current_obj, seq_name)
            if current_seq != None:
                current_seq["idFrameBeginTrack"] = begin
                current_seq["idFrameEndTrack"] = end
                current_seq["idFrameInit"] = init
        
    def getObjByName(self,name):
        """
        renvoie l'objet de nom 'name'

            Parameters:
            ----------
                name (string) :
                    nom de l'objet à chercher

            Return:
            ------
                o (Obj) :
                    référence à l'objet
                OU
                None 
        
        """
        for o in self.current_video.objs:
            if o.name == name:
                return o
        return None

    def getSeqByName(self,obj,name):
        """
        renvoie la séquence de nom 'name'

            Parameters:
            ----------
                obj (Obj):
                    référence à l'objet dans lequel chercher la séquence
                name (string) :
                    nom de la séquence à chercher

            Return:
            ------
                s (dict):
                    référence au dictionnaire de la séquence
                OU
                None
        
        """
        for s in obj.sequences:
            if s["name"] == name:
                return s
        return None

    def addObject(self,name):
        """
        ajout un objet à la vidéo

            Parameters:
            ----------
                name (string) :
                    nom de l'objet nouvellement créé
        
        """
        print(name)
        obj = Obj(name, self.current_video)
        self.current_video.objs.append(obj)

    def renameObject(self,obj, new_name):
        """
        renomme un objet existant

            Parameters:
            ----------
                obj (Obj) :
                    objet à renommer
                new_name (string):
                    nouveau nom de l'objet
        
        """
        for o in self.current_video.objs:
            if o.name == obj.name:
                o.name = new_name
                break
            
    def deleteObject(self,obj):
        """
        supprime l'objet

            Parameters:
            ----------
                obj (Obj) :
                    objet à supprimer
        
        """
        list_without_obj = []
        for o in self.current_video.objs:
            if o.name != obj.name:
                list_without_obj.append(o)
        self.current_video.objs = list_without_obj

    
    def addSequence(self,obj,name):
        """
        ajoute une séquence à la vidéo

            Parameters:
            ----------
                obj (Obj):
                    objet auquel ajouter la séquence
                name (string) :
                    nom de la séquence nouvellement créée
        
        """
        print(obj.name)
        obj.sequences.append(
            {   "name" : name,
                "idFrameInit" : 0,
                "initBB" : (0,0,0,0),
                "idFrameBeginTrack" : 0,
                "idFrameEndTrack" : 0})

    def renameSequence(self,obj,old_name,new_name):
        """
        renomme une séquence

            Parameters:
            ----------
                obj (Obj):
                    objet dans lequel la séquence se trouve
                old_name (string):
                    nom de la séquence
                new_name (string):
                    nouveau nom de la séquence
        
        """
        for s in obj.sequences:
            if s["name"] == old_name:
                s["name"] = new_name

    def deleteSequence(self, obj, name):
        """
        supprime la séquence

            Parameters:
            ----------
                obj (Obj) :
                    objet où se trouve la séquence
                name (string):
                    nom de la séquence à supprimer
        
        """
        list_without_seq = []
        for s in obj.sequences:
            if s["name"] != name:
                list_without_seq.append(s)
        obj.sequences = list_without_seq

    
if __name__ == '__main__':

    #fonction utilisé pour le débuggage
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)

    #ainsi en cas d'erreur, l'application ne plante pas (toujours) et ouvre pdb à la place à l'endroit où l'erreur est arrivée
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
        controleur.getObjByName("objet 1").maskSequence(126, (224, 404, 150, 158), 100, 210, "crst")
        controleur.getObjByName("objet 1").bboxTrackingToMask()
        controleur.getObjByName("objet 1").exportMaskToFile()

        controleur.addObject("objet 2")
        controleur.addSequence(controleur.getObjByName("objet 2"), "sequence 1" )
        controleur.getObjByName("objet 2").maskSequence(150, (275, 475, 220, 228), 130, 250, "crst")
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

