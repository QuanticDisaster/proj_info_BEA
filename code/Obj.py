import cv2
import time
import imutils
import numpy as np
from imutils.video import FPS
import os
import shutil
import time



class Obj():
    """
        Objet

        ...

        Attributes
        ----------
            name : string
                nom de l'objet
            video : Video
                vidéo à laquelle est rattaché l'objet
            mask : list[ array ]
                liste dont le ième élèment est le masque de l'objet sur la ième frame de la vidéo
            bbox : list[ tuple(int,int,int,int) ]
                liste dont le ième élèment est la bounding box de l'objet sur la ième frame de la vidéo
        

        Methods
        -------
            manualBBOX 
                permet de créer manuellement une bbox
            maskSequence 
                traque un objet sur la séquence
            bboxTrackingToMask 
                convertit les bbox en masques rectangulaires
            exportMaskToFile 
                enregistre les masques sur le disque

    """

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
        """
        initialise la classe

            Parameters:
            ----------
                name (string) :
                    nom de l'objet
                video (video) :
                    objet video auquel est rattaché l'objet
        
        """
        self.name = name
        self.video = video
        self.bbox = [(-1, -1, -1, -1)] *  video.nbFrames
        self.mask = [None] *  video.nbFrames
        self.sequences = []


    def manualBBOX(self, current_frame):
        """
        permet à l'utilisateur de choisir manuellement une bbox et donc le masque sur l'image

            Parameters:
            ----------
                current_frame (int) : index de l'image
        
        """

        i = current_frame

        vs = cv2.VideoCapture(self.video.fullPath)
        vs.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        frame = vs.read()[1]
                
        ##changement bbox
        #on crée une fenête avec resizeable=true (enfin je suppose que c'est ce que le "2" signifie)
        cv2.namedWindow("Image",2)
        box = cv2.selectROI("Image", frame, fromCenter=False,
                                       showCrosshair=True)
        cv2.destroyAllWindows()
        self.bbox[i] = box

        ##changement massque
        binaryImage = np.zeros( self.video.frameDimensions, np.uint8)
        (x, y, w, h) = [int(v) for v in self.bbox[i]]
        cv2.rectangle( binaryImage, (x,y), (x + w, y + h), 255, -1)
        self.mask[i] = binaryImage
        

        
    def maskSequence(self, frameInit, initBB, frameBeginTrack, frameEndTrack, tracker):
        """
        Lance le tracking d'un objet et maj les bbox l'encadrant sur chaque frame. Ne crée pas réellement de masque, voir bboxTrackingToMask pour cela

            Parameters:
            ----------
                frameInit (np.array)  :
                    image sur laquelle on a initialisé la bbox
                initBB ( (int,int,int,int) ) :
                    bbox d'initialisation, sous la forme (x, y, width, height) #NB : à vérifier si c'est pas (x, y, x+w, y+h) directement
                frameBeginTrack (int) :
                    index de l'image de début de la séquence
                frameEndTrack   (int) :
                    index de l'image de fin de la séquence
                tracker (string) :
                    tracker à utiliser pour le suivi sur les frames
                
        
        """
        print("tracker : ", tracker)

        frameInit, initBB, frameBeginTrack, frameEndTrack = int(frameInit), initBB, int(frameBeginTrack), int(frameEndTrack)
        
        #tracker = "csrt"
        # extract the OpenCV version info
        (major, minor) = cv2.__version__.split(".")[:2]

        # if we are using OpenCV 3.2 OR BEFORE, we can use a special factory
        # function to create our object tracker
        if int(major) == 3 and int(minor) < 3:
            tracker_forward = cv2.Tracker_create(tracker.upper())
            tracker_backward = cv2.Tracker_create(tracker.upper())

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
            tracker_forward = OPENCV_OBJECT_TRACKERS[tracker]()
            tracker_backward = OPENCV_OBJECT_TRACKERS[tracker]()

        vs = cv2.VideoCapture(self.video.fullPath)
        # initialize the FPS throughput estimator
        fps = None

        #création d'une fenête pour afficher les images
        cv2.namedWindow("Frame", 2)

        ####################  handle FORWARD tracking ########################

        vs.set(cv2.CAP_PROP_POS_FRAMES, frameInit)
        fps = FPS().start()
        for i in range(frameInit, frameEndTrack):

            frame = vs.read()[1]
            #frame = imutils.resize(frame, width=1000)
            (H, W) = frame.shape[:2]



            if i == frameInit:
                tracker_forward.init(frame, initBB)
                self.bbox[frameInit] = initBB

            (success, box) = tracker_forward.update(frame)
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
                ("Progress (%)", round((i - frameInit) / max(1,(frameEndTrack - frameInit)), 2))
            ]
            # loop over the info tuples and draw them on our frame
            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # on affiche l'image de sortie sur la cv2.namedWindow "frame" créée plus haut
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
                tracker_backward.init(frame, initBB)
                self.bbox[frameInit] = initBB

            (success, box) = tracker_backward.update(frame)
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

            # on affiche l'image de sortie sur la cv2.namedWindow "frame" créée plus haut
            cv2.imshow("Frame", frame)
            # unused, but necessary to make application work otherwise grey windows appears
            key = cv2.waitKey(1) & 0xFF

        # otherwise, release the file pointer
        vs.release()
        # close all windows
        cv2.destroyAllWindows()

    def maskGrosObjet(self, frameInit, initBB, frameBeginTrack, frameEndTrack):
        print("track")
        frameInit, initBB, frameBeginTrack, frameEndTrack = int(frameInit), initBB, int(frameBeginTrack), int(frameEndTrack)


        maskInit = self.drawMask(frameInit)


        vs = cv2.VideoCapture(self.video.fullPath)
        # initialize the FPS throughput estimator
        fps = None

        #création d'une fenête pour afficher les images
        cv2.namedWindow("Frame", 2)

        ####################  handle FORWARD tracking ########################

        vs.set(cv2.CAP_PROP_POS_FRAMES, frameInit)
        frame = vs.read()[1]
        
        #on croppe l'image pour ne garder que ce qui est dans le rectangle englobant le masque
        cropped = frame#frame[np.ix_(maskInit.any(1), maskInit.any(0))]

        

        #-------------------------------------------------------
        


        
        mask = maskInit
        for f_index in range(frameInit+1, frameEndTrack):
            
            # l'objet à trouver est la partie croppé, dans la frame suivante
            #img_object = cropped
            img_scene = vs.read()[1]
            
            #-------------------------- Segmentation -------------------------------
            tic = time.time()
            src = cv2.GaussianBlur(img_scene,(13,13),0)
            src_lab = cv2.cvtColor(src,cv2.COLOR_BGR2LAB) # convert to LAB
            cv_slic = cv2.ximgproc.createSuperpixelSLIC(src_lab, region_size = 200,algorithm=100)
            cv_slic.iterate()
            toc = time.time()

            print("durée segmentation : ", toc - tic)


            #---------------------------- Erosien, dilatation-------------------------

            ##érosion du masque
            #TODO : adapter taille du kernel à la taile de l'objet ?
            #kernel = np.ones((5,5), np.uint8)
            #core_mask = cv2.erode(mask, kernel, iterations=1)

            #build the new mask
            new_mask = cv_slic.getLabelContourMask()

            display = img_scene
            display[new_mask > 1] = 0

            cv2.imshow('Segmentation', display)
            cv2.waitKey(1)

            #update the mask to find in the next frame
            cropped = img_scene[np.ix_(maskInit.any(1), maskInit.any(0))]


            pixIndexRegion = cv_slic.getLabels()

            new_mask = 125 * np.ones( mask.shape)
            #je ne sais plus pourquoi j'ai mis ces deux lignes mais je crois qu'il y a une raison
            new_mask[0][0] = 0
            new_mask[0][1] = 255

            
            ##éroder le masque et considérer l'intérieur comme appartenant au masque de manière sure
            kernel = np.ones((33,33), np.uint8)
            erode = cv2.erode(mask, kernel)
            #cv2.imshow("erode", erode)
            #cv2.waitKey(1)
            ##dilater le masque et considérer l'extérieur comme appartenant au masque de manière sure
            dilate = cv2.dilate(mask, kernel)
            #cv2.imshow("dilate", dilate)
            #cv2.waitKey(1)
            
            new_mask[ erode == 255 ] = 255
            new_mask[ dilate == 0] = 0

            print(np.max(new_mask))
            print(np.min(new_mask))
            print((new_mask == 125).any())
            #import pdb; pdb.set_trace()

            #on cherche l'id des régiosn appartenant au masque sûr et au non-masque sûr
            #classe 1 = masque
            #classe 2 = non masque
            index_classe1_regions = pixIndexRegion[ new_mask == 255]
            index_classe2_regions = pixIndexRegion[ new_mask == 0 ]

            #import pdb; pdb.set_trace()


            #------------------------------K-moyennes---------------------------------

            incomplete_labels_img = 125 * np.ones( (img_scene.shape[0], img_scene.shape[1]) )

            #on applique kmeans sur la région masque sûr et sur la région non-masque sûr
            # convert to RGB
            tic = time.time()
            image = cv2.cvtColor(img_scene, cv2.COLOR_BGR2RGB)

            #we take only pixels in mask ( we end with a 2D shaped array, but it's okay because kmeans asks for a 2D array)
            pixel_values1 = image[new_mask == 255 ]
            # covert to float
            pixel_values1 = np.float32(pixel_values1)
            # define stopping criteria
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
            # number of clusters (K)
            k = 6
            _, labels1, (centers1) = cv2.kmeans(pixel_values1, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            # convert back to 8 bit values
            centers1 = np.uint8(centers1)
            # flatten the labels array
            labels1 = labels1.flatten()
            # convert all pixels to the color of the centroids
            segmented_image1 = centers1[labels1.flatten()]
            # reshape back to the original image dimension
            
            idx = np.where(new_mask == 255)
            image[idx[0], idx[1] ] = segmented_image1
            incomplete_labels_img[ idx[0], idx[1] ] = labels1
            #segmented_image1 = segmented_image1.reshape(image.shape)
            # show the image
            #plt.imshow(segmented_image2)
            #plt.show()

            pixel_values2 = image[new_mask == 0 ]
            pixel_values2 = np.float32(pixel_values2)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
            k = 6
            _, labels2, (centers2) = cv2.kmeans(pixel_values2, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            centers2 = np.uint8(centers2)
            labels2 = labels2.flatten()
            segmented_image2 = centers2[labels2.flatten()]
            
            idx = np.where(new_mask == 0)
            image[idx[0], idx[1] ] = segmented_image2
            incomplete_labels_img[ idx[0], idx[1] ] = labels2 + np.max(labels1)
            #segmented_image1 = segmented_image1.reshape(image.shape)
            # show the image


            #label_map = -1 * np.ones(( image.shape[0], image.shape[1] ))
            #image[idx[0], idx[1] ] = labels2
            toc = time.time()
            print("durée des k moyennes : ", toc - tic )
            print("end")




            #-------------------------assignation des régions indécises---------------

            #TODO : je pense que cette partie peut être amélioré (temps de calcul notamment) en calculant
            #intelligemment avec numpy plutôt qu'avec les boucles
            
            centers = np.vstack((centers1, centers2))
            labels = np.hstack( (labels1, labels2 + np.max(labels1) ))


            #On associe chaque région "indécise" de la segmentation à une des classes
            distance = []
            means = []
            centers = centers.astype(float)
            classes = []
            for i,region_index in enumerate(np.unique(pixIndexRegion[ new_mask == 125 ])):
                if i % 100 == 0:
                    print(i)
                im =  img_scene[pixIndexRegion == region_index ]
                mR, mV, mB = np.mean( im[:,0]), np.mean(im[:,1]), np.mean(im[:,2])
                #import pdb; pdb.set_trace()
                means.append([mR, mV, mB] )

                d = np.sqrt( (mR - centers[:,0]) ** 2 +
                          (mV - centers[:,1]) ** 2 +
                          (mB - centers[:,2]) ** 2 )
                distance.append( d )

                if i < 10:
                    print("distance", d)
                    print("argmin : ", np.argmin(d))
                classes.append( np.argmin(d) )
            classes = np.array(classes)
            distance = np.array(distance)
            distance = distance.reshape( distance.shape[1], distance.shape[0] )


            for i,region_index in enumerate(np.unique(pixIndexRegion[ new_mask == 125 ])):
                if i % 100 == 0:
                    print(i)
                image[pixIndexRegion == region_index ] = centers[classes][i]
                incomplete_labels_img[ pixIndexRegion == region_index ] = classes[i]

            labels_img = incomplete_labels_img
            #import matplotlib.pyplot as plt
            #plt.imshow(image)
            cv2.imshow("sortie",image)
            cv2.waitKey(1)

            

            temp_mask = np.zeros( (img_scene.shape[0], img_scene.shape[1] ))
            temp_mask[ np.isin(labels_img, labels1) ] = 255
            display_new_mask = cv2.addWeighted(img_scene,0.8,(np.stack((temp_mask,)*3, axis = -1)).astype(np.uint8),0.25,0)
            
            cv2.imshow("nouveau masque enregistré", display_new_mask)
            cv2.waitKey(1)

            cv2.imshow("labels",labels_img.astype(np.uint8))
            cv2.waitKey(1)
            #plt.figure()
            #plt.imshow(segmented_image2)
            #plt.show()
            #import pdb; pdb.set_trace()
            cropped = new_mask
            mask = new_mask
            
            added_image = cv2.addWeighted(img_scene,0.8,(np.stack((new_mask,)*3, axis = -1)).astype(np.uint8),0.25,0)         
            cv2.imshow('mask',added_image)
            cv2.waitKey(200)

        # otherwise, release the file pointer
        #vs.release()
        # close all windows
        #cv2.destroyAllWindows()

            
        
    def drawMask(self, im_index):
        drawing=False # true if mouse is pressed
        mode=True # if True, draw rectangle. Press 'm' to toggle to curve

        poly = []


        # mouse callback function
        def begueradj_draw(event,former_x,former_y,flags,param):
            global current_former_x,current_former_y
            nonlocal drawing, mode

            if event==cv2.EVENT_LBUTTONDOWN:
                drawing=True
                current_former_x,current_former_y=former_x,former_y

            elif event==cv2.EVENT_MOUSEMOVE:
                if drawing==True:
                    if mode==True:
                        cv2.line(im,(current_former_x,current_former_y),(former_x,former_y),(0,0,255),2)
                        poly.append((current_former_x, current_former_y))
                        current_former_x = former_x
                        current_former_y = former_y
                        #print former_x,former_y
            elif event==cv2.EVENT_LBUTTONUP:
                drawing=False
                if mode==True:
                    cv2.line(im,(current_former_x,current_former_y),(former_x,former_y),(0,0,255),5)
                    current_former_x = former_x
                    current_former_y = former_y
            return former_x,former_y
    

        vs = cv2.VideoCapture(self.video.fullPath)
        vs.set(cv2.CAP_PROP_POS_FRAMES, im_index)
        im = vs.read()[1]
        cv2.namedWindow("Bill BEGUERADJ OpenCV")
        cv2.setMouseCallback('Bill BEGUERADJ OpenCV',begueradj_draw)
        while(1):
            cv2.imshow('Bill BEGUERADJ OpenCV',im)
            k=cv2.waitKey(1)&0xFF
            if k==27:
                break
        cv2.destroyAllWindows()
                
        contours = np.array(poly)
        mask = np.zeros( tuple(im.shape[0:2]) ) # create a single channel 200x200 pixel black image 
        cv2.fillPoly(mask, pts =[contours], color=(255,255,255))
        #cv2.imshow(" ", mask)
        #cv2.waitKey(1)

        return mask

                    

    def bboxTrackingToMask(self):
        """
        Convertit les bbox de l'objet en masques (rectangulaires) et l'enregistre en attribut (pas sur le disque)
        
        """
        for i in range(self.video.nbFrames):
            binaryImage = np.zeros( self.video.frameDimensions, np.uint8)
            (x, y, w, h) = [int(v) for v in self.bbox[i]]
            if x != -1:
                cv2.rectangle( binaryImage, (x,y), (x + w, y + h), 255, -1)
                self.mask[i] = binaryImage
                
    #Enregistrement des masques tif et xml (NB : honnêtement sur windows, 2 fois sur 3 l'explorateur bloque l'écriture en disant qu'un autre processus utilise déjà le dossier/fichier)
    def exportMaskToFile(self, location = ""):
        """
        Enregistre les masques en attribut sur le disque dans le dossier location/mask/nom_objet

            Parameters:
            ----------
                location string:
                    emplacement sur le disque où enregistrer les masques
        """
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

        #Enregistrement des masques tif
        for i,m in enumerate(self.mask):
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
                                    
                                    
