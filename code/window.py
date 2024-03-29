from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap,QImage
from windowUI import Ui_MainWindow


class MyWindow(QtWidgets.QMainWindow):
    """
        classe MyWindow qui représente l'interface graphique et la partie "Vue" de l'application

        ...

        Attributes
        ----------
            controleur : controleur
                référence à l'objet controleur qui gère l'application

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
    
    def __init__(self, controleur):
        super(MyWindow,self).__init__()
        self.controleur = controleur
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #uic.loadUi("window.ui",self)
        
        self.findChild(QPushButton, "load_video").clicked.connect(self.select_video_file)
        self.findChild(QPushButton, "new_object").clicked.connect(self.create_object)
        self.findChild(QPushButton, "rename_object").clicked.connect(self.rename_obj)
        self.findChild(QPushButton, "delete_object").clicked.connect(self.delete_obj)
        self.findChild(QPushButton, "new_sequence").clicked.connect(self.create_seq)
        self.findChild(QPushButton, "rename_sequence").clicked.connect(self.rename_seq)
        self.findChild(QPushButton, "delete_sequence").clicked.connect(self.delete_seq)
        
        self.findChild(QComboBox, "liste_objets").currentIndexChanged.connect(self.changeObject)
        self.findChild(QComboBox, "liste_sequences").currentIndexChanged.connect(self.changeSequence)
        self.findChild(QLineEdit, "frame_debut").textEdited.connect(self.parameters_changed)
        self.findChild(QLineEdit, "frame_fin").textEdited.connect(self.parameters_changed)

        self.findChild(QPushButton, "read").clicked.connect(self.readVideo)
        self.findChild(QPushButton, "pause").clicked.connect(self.pauseVideo)
        self.findChild(QPushButton, "nextFrame").clicked.connect(self.controleur.next_frame)
        self.findChild(QPushButton, "precedentFrame").clicked.connect(self.controleur.precedent_frame)
        self.findChild(QPushButton, "skipForward").clicked.connect(self.controleur.skip_forward)
        self.findChild(QPushButton, "skipBackward").clicked.connect(self.controleur.skip_backward)
        self.findChild(QPushButton, "goToBeginning").clicked.connect(self.controleur.goToVideoBeginning)
        self.findChild(QPushButton, "goToEnd").clicked.connect(self.controleur.goToVideoEnd)
        self.findChild(QPushButton, "initMask").clicked.connect(self.controleur.initializeMask)

        self.findChild(QPushButton, "mask_sequence").clicked.connect(self.maskSequence)
        self.findChild(QPushButton, "mask_sequence_big").clicked.connect(self.maskSequenceBig)
        self.findChild(QPushButton, "display_bbox").clicked.connect(self.displayBBOX)

        self.findChild(QPushButton, "export_fused_masks").clicked.connect(self.controleur.exportFusedMasks)
        self.findChild(QPushButton, "export_object_mask").clicked.connect(self.controleur.exportObjectMask)
        self.findChild(QPushButton, "debug").clicked.connect(self.debug)


        self.findChild(QPushButton, "delete_mask").clicked.connect(self.deleteMask)
        self.findChild(QPushButton, "edit_mask").clicked.connect(self.editMask)
        self.findChild(QPushButton, "goToButton").clicked.connect(self.goToFrame)


        #liste_trackers
        trackers = ["csrt",     # O : more accurate than KCF but slower
                    "kcf",      # O : doest not handle occlusions very well
                    "boosting", # X : very old, not recommended
                    "mil",      # O : better than boosting, badly handles failures
                    "tld",      # : lot of false positives ?
                    "medianflow",# O : handles failures well, but fails often when handling fast-moving objects or on quick appereance change
                    "mosse"     # X : speed-oriented
            ]

        for t in trackers:
            self.findChild(QComboBox, "tracker").addItem(t)
        
        

        ##TODO, delete
        #self.select_video_file_debug()

    def goToFrame(self):
        """
        indique au controleur d'aller à la frame X quand l'utilisateur clique sur "Go"
        
        """
        idFrame = int( self.findChild(QLineEdit, "frameToGo").text() )
        self.controleur.goToFrame(idFrame)
        

        
    def editMask(self):
        """
        informe le controleur de modifier le masque  pour la frame actuelle par un masque manuel
        
        """
        liste = self.findChild(QListWidget, "list_mask")
        masque = liste.item(liste.currentRow()).text()

        obj_name= masque
        obj = self.controleur.getObjByName(obj_name)

        self.controleur.editCurrentMask(obj)


        
    def deleteMask(self):
        """
        on supprime le masque de la frame actuelle

            Parameters:
            ----------
                current_frame (int) : index de l'image
        
        """
        
        ##VUE
        liste = self.findChild(QListWidget, "list_mask")
        masque = ( liste.takeItem(liste.currentRow()) ).text()

        ##CONTROLEUR
        
        #Ayant posé une nomenclature arbitraire au nom des masques affichés (par exemple "objet"), on récupère l'objet
        obj_name = masque
        obj = self.controleur.getObjByName(obj_name)
        
        self.controleur.deleteCurrentMask(obj)
        
        

    def debug(self):
        import pdb; pdb.set_trace()

        
    def displayBBOX(self):
        """
        Active/désactive la visualisation des masques sur la vidéo de l'interface
        
        """
        text = self.findChild(QPushButton, "display_bbox").text()
        if text == "Cacher les bbox":
            self.findChild(QPushButton, "display_bbox").setText("Afficher les bbox")
        elif text == "Afficher les bbox":
            self.findChild(QPushButton, "display_bbox").setText("Cacher les bbox")

        self.controleur.displayBBOX()
        
    def maskSequence(self):
        """
        lance tracking de la séquence
        
        """
        
        tracker = self.findChild(QComboBox, "tracker").currentText()
        obj = self.controleur.getObjByName( self.findChild(QComboBox, "liste_objets").currentText() )
        seq = self.controleur.getSeqByName( obj, self.findChild(QComboBox, "liste_sequences").currentText() )
        self.controleur.maskSequence(obj,seq, tracker)

    def maskSequenceBig(self):
        """
        lance le masquage d'un gros objet
        
        """
        obj = self.controleur.getObjByName( self.findChild(QComboBox, "liste_objets").currentText() )
        seq = self.controleur.getSeqByName( obj, self.findChild(QComboBox, "liste_sequences").currentText() )
        self.controleur.maskSequenceBig(obj,seq)
            
        
    def updateInitFrame(self, idFrame):
        """
        met à jour l'affichage en indiquant sur quelle frame on a initialisé le masque

            Parameters:
            ----------
                idFrame (int) :
                    index de la frame
            
        """
        
        self.findChild(QLabel, "frame_init").setText(str(idFrame))
        
    def readVideo(self):
        """
        relance la lecture
        
        """
        self.controleur.readVideo()
        
    def pauseVideo(self):
        """
        mets en pause la vidéo
        """
        self.controleur.pauseVideo()
        
    def parameters_changed(self):
        """
        indique au controleur que les paramètres de la séquence ont changé. Activé lorsque l'utilisateur modifie les valeurs dans l'interface
        """
        debut = self.findChild(QLineEdit, "frame_debut").text()
        fin   = self.findChild(QLineEdit, "frame_fin").text()
        init  = self.findChild(QLabel, "frame_init").text()
        obj   = self.findChild(QComboBox, "liste_objets").currentText()
        seq   = self.findChild(QComboBox, "liste_sequences").currentText()
        self.controleur.updateParameters(obj,seq,debut,fin,init)
        
    def create_object(self, text = False):
        """
        crée un objet de nom 'text' si text est différent de la valeur par défaut

            Parameters:
            ----------
                text (string/bool):
                    nom du nouvel objet
        
        """
        ok = True

        if text == False:
            text, ok = QInputDialog.getText(self, "nouvel objet", "nom du nouvel objet", text = "objet " + str(len(self.controleur.current_video.objs) + 1))

        while self.controleur.getObjByName(text) != None:
            text, ok = QInputDialog.getText(self, "nouvel objet", "l'objet existe déjà", text = "objet " + str(len(self.controleur.current_video.objs) + 1))

        if (ok and text != ""):

            #on retire les espaces à la fin et au début
            text = text.strip()
            
            #####CONTROLEUR#####
            
            #On ajoute l'objet à la video

            self.controleur.addObject(text)

            
            ########VUE#########
            
            ##NB : self.findchild(etc...) et self.nomdelobjet sont identiques
            print(text)
            self.findChild(QComboBox,"liste_objets").addItem(text)

            #on vide les séquences
            for i in range(self.findChild(QComboBox, "liste_sequences").count()):
                self.findChild(QComboBox, "liste_sequences").removeItem(0)

            self.findChild(QLineEdit, "frame_debut").setText("")
            self.findChild(QLabel, "frame_init").setText("")
            self.findChild(QLineEdit, "frame_fin").setText("")

            self.findChild(QComboBox,"liste_objets").setCurrentIndex( self.findChild(QComboBox,"liste_objets").count() - 1)

            #on force la création d'au moins une séquence dans l'objet
            self.create_seq('default')

    def rename_obj(self):
        """
        renomme l'objet actuellement sélectionné
        """
        
        ok = True
        new_name, ok = QInputDialog.getText(self, "renommer objet", "renommer en ", text = "objet " + str(len(self.controleur.current_video.objs) + 1))

        while self.controleur.getObjByName(new_name) != None:
            new_name, ok = QInputDialog.getText(self, "renommer objet", "l'objet existe déjà", text = "objet " + str(len(self.controleur.current_video.objs) + 1))
            
        old_name = self.findChild(QComboBox,"liste_objets").currentText()
        if ok:
            #####CONTROLEUR#####
            for o in self.controleur.current_video.objs:
                if o.name == old_name:
                   
                    self.controleur.renameObject(o, new_name)
                    break
                
            ########VUE#########
            index = self.findChild(QComboBox,"liste_objets").currentIndex()
            self.findChild(QComboBox,"liste_objets").removeItem(index)
            self.findChild(QComboBox,"liste_objets").addItem(new_name)
            self.findChild(QComboBox,"liste_objets").setCurrentIndex( self.findChild(QComboBox,"liste_objets").count() -1 )

        
    def delete_obj(self):
        """
        supprime l'objet actuellement sélectionné
        
        """
        current_obj = self.findChild(QComboBox,"liste_objets").currentText()
        #####CONTROLEUR#####
        for o in self.controleur.current_video.objs:
            if o.name == current_obj:
                self.controleur.deleteObject(o)
                break
            
        ########VUE#########
        self.findChild(QComboBox,"liste_objets").removeItem(self.findChild(QComboBox,"liste_objets").currentIndex())

        #si on supprime tous les objets, on force la création d'au moins un objet ainsi qu'une séquence
        if self.findChild(QComboBox,"liste_objets").count() == 0:
            self.create_object("default")

    def create_seq(self, text = False):
        """
        crée une séquence de nom 'text' si text est différent de la valeur par défaut

            Parameters:
            ----------
                text (string/bool):
                    nom de la nouvelle séquence
        
        """
        ok = True
        current_obj = self.controleur.getObjByName(self.findChild(QComboBox,"liste_objets").currentText())
        
        if text == False:
            text, ok = QInputDialog.getText(self, "nouvelle séquence", "nom de la nouvelle séquence", text = "sequence " + str(len(current_obj.sequences) + 1))

        while self.controleur.getSeqByName(current_obj, text) != None:
            text, ok = QInputDialog.getText(self, "nouvelle séquence", "la séquence existe déjà", text = "sequence " + str(len(current_obj.sequences) + 1))
            
        if (ok and text != ""):

            #on retire les espaces à la fin et au début
            text = text.strip()
            
            #####CONTROLEUR#####
            
            #On ajoute la séquence à la video

            self.controleur.addSequence(current_obj,text)

            
            ########VUE#########
            
            ##NB : self.findchild(etc...) et self.nomdelobjet sont identiques
            self.findChild(QComboBox,"liste_sequences").addItem(text)

            self.findChild(QLineEdit, "frame_debut").setText("")
            self.findChild(QLabel, "frame_init").setText("")
            self.findChild(QLineEdit, "frame_fin").setText("")

            self.findChild(QComboBox,"liste_sequences").setCurrentIndex( self.findChild(QComboBox,"liste_sequences").count() - 1)

    def rename_seq(self):
        """
        renomme la séquence actuellement sélectionnée
        """
        ok = True
        current_obj = self.controleur.getObjByName(self.findChild(QComboBox,"liste_objets").currentText())
        new_name, ok = QInputDialog.getText(self, "renommer séquence", "renommer en ", text = "sequence " + str(len(current_obj.sequences) + 1))

        while self.controleur.getSeqByName(current_obj, new_name) != None:
            new_name, ok = QInputDialog.getText(self, "renommer séquence", "la séquence existe déjà", text = "sequence " + str(len(current_obj.sequences) + 1))
            
        old_name = self.findChild(QComboBox,"liste_sequences").currentText()
        if ok:
            #####CONTROLEUR#####
            for s in current_obj.sequences:
                if s["name"] == old_name:
                    self.controleur.renameSequence(current_obj, old_name,new_name)
                    break
                
            ########VUE#########
            index = self.findChild(QComboBox,"liste_sequences").currentIndex()
            self.findChild(QComboBox,"liste_sequences").removeItem(index)
            self.findChild(QComboBox,"liste_sequences").addItem(new_name)
            self.findChild(QComboBox,"liste_sequences").setCurrentIndex( self.findChild(QComboBox,"liste_sequences").count() -1 )
            
            seq = self.controleur.getSeqByName(new_name)
            self.findChild(QLineEdit, "frame_debut").setText(seq["idFrameBeginTrack"])
            self.findChild(QLabel, "frame_init").setText(seq["idFrameEndTrack"])
            self.findChild(QLineEdit, "frame_fin").setText(seq["idFrameInit"])
            
        
    def delete_seq(self):
        """
        supprime la séquence actuellement sélectionnée
        
        """
        current_obj_name = self.findChild(QComboBox,"liste_objets").currentText()
        current_obj = self.controleur.getObjByName(current_obj_name)
        current_seq_name = self.findChild(QComboBox,"liste_sequences").currentText()
        #####CONTROLEUR#####
        for s in current_obj.sequences:
            if s["name"] == current_seq_name:
                self.controleur.deleteSequence(current_obj,s['name'])
                break
            
        ########VUE#########
        self.findChild(QComboBox,"liste_sequences").removeItem(self.findChild(QComboBox,"liste_sequences").currentIndex())

        #si on supprime toutes les séquences, on force a création d'une séquence par défault
        if self.findChild(QComboBox,"liste_sequences").count() == 0 :
            self.create_seq("default")

    def changeObject(self):
        """
        appelé lorsque l'utilisateur change d'objet. met à jour les paramètres affichés en conséquence (séquence, nom objet etc...)
        
        """

        self.findChild(QComboBox,"liste_sequences").clear()     
        current_obj = self.controleur.getObjByName(self.findChild(QComboBox,"liste_objets").currentText())

        if current_obj is not None:
            if len(current_obj.sequences) != 0:
                for s in current_obj.sequences:
                    self.findChild(QComboBox,"liste_sequences").addItem(s["name"])

    def changeSequence(self):
        """
        appelé lorsque l'utilisateur change de séquence. met à jour les paramètres affichés en conséquence (paramètres etc...)
        
        """
        current_obj = self.controleur.getObjByName(self.findChild(QComboBox,"liste_objets").currentText())
        if current_obj is not None:
            current_seq = self.controleur.getSeqByName(current_obj, self.findChild(QComboBox,"liste_sequences").currentText())
            if current_seq is not None:
                self.findChild(QLabel,"frame_init").setText(str(current_seq["idFrameInit"]))
                self.findChild(QLineEdit,"frame_debut").setText(str(current_seq["idFrameBeginTrack"]))
                self.findChild(QLineEdit,"frame_fin").setText(str(current_seq["idFrameEndTrack"]))

        
    def select_video_file(self):
        """
        Ouvre une fenêtre pour que l'utilisateur choisisse la vidéo à charger
        
        """
        print("good !")
        #choix du fichier
        filename, _filter = QFileDialog.getOpenFileName(
            self, "Select video file ","")
        if filename != "":


            ########VUE#########
            
            #changement du nom affiché
            self.findChild(QLabel, "currentvideo").setText(filename)
            
            #on vide la liste des objets
            self.findChild(QComboBox, "liste_objets").clear()
                
            #on vide les séquences
            self.findChild(QComboBox, "liste_sequences").clear()

            self.findChild(QLineEdit, "frame_debut").setText("")
            self.findChild(QLabel, "frame_init").setText("")
            self.findChild(QLineEdit, "frame_fin").setText("")

            #####CONTROLEUR#####
            
            #changement de la video
            self.controleur.loadVideo(filename)

        
            

    def showFrame(self, frame, id_frame, nbFrames):
        """
        affiche une image

            Parameters:
            ----------
                frame (array):
                    image à afficher
                id_frame (int) :
                    index de la frame à afficher
                nbFrames (int) :
                    nombre total de frames sur la vidéo
        
        """

        #affichage image
        h, w = self.findChild(QLabel, "label").size().height(), self.findChild(QLabel, "label").size().width()

        qtImg = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
        self.findChild(QLabel, "label").setPixmap(QPixmap.fromImage(qtImg).scaled(QSize(w,h)))

        #MAJ du compteur de frame
        self.findChild(QLabel, "idFrame").setText("Frame : " + str(id_frame) + " / " + str(nbFrames))

        #MAJ de masques de la liste
        #on vide la liste
        self.findChild(QListWidget, "list_mask").clear()
        for obj in self.controleur.current_video.objs:
            if obj.bbox[id_frame -1] != (-1, -1, -1, -1):
                self.findChild(QListWidget, "list_mask").addItem(obj.name)

            
    ##TODO, debug
    def select_video_file_debug(self):
        print("good !")
        #choix du fichier
        filename = r"D:\Mes documents\_PPMD\Projet informatique BEA\local\donnees\videos_youtube\Top 5 POV Plane Emergency Landings.mp4"
        
        if filename != "":

            ########VUE#########
            
            #changement du nom affiché
            self.findChild(QLabel, "currentvideo").setText(filename)
            
            #on vide la liste des objets
            self.findChild(QComboBox, "liste_objets").clear()
                
            #on vide les séquences
            self.findChild(QComboBox, "liste_sequences").clear()

            self.findChild(QLineEdit, "frame_debut").setText("")
            self.findChild(QLabel, "frame_init").setText("")
            self.findChild(QLineEdit, "frame_fin").setText("")
            
            #####CONTROLEUR#####
            
            #changement de la video
            self.controleur.loadVideo(filename)


            
        


    
