# Projet informatique

### Contexte
Dans le cadre de ses enquêtes le BEA est amené à traiter des vidéos d'accidents impliquant des aéronefs civils.
L'étude de ces vidéos peut permettre de reconstruire la trajectoire des aéronefs par photogrammétrie. Seulement, les objets mobiles qui y apparaissent peuvent perturber la convergence des calculs.

Le but de ce projet était donc de réaliser un outil de masquage automatique de ces élèments gênants ou de suivis de potentiels objets d'intérêt.

### Installation

installer python 3.6 maximum (en raison de openCV)
Puis à l'aide de pip :
  * installer opencv-contrib-python version 3.4.2.17 ou moins (opencv4 non compatible)
  * installer PyQt5 (version 15 mini)
  * installer les autres dépendances (imutils)

lancer le script main.py

####COMPILER EN EXECUTABLE#####
installer pyinstaller à l'aide de pip

pour ubuntu uniquement : installer python3-dev (attention à la sous version du python sur laquelle c'est installé)

dans le terminal :
pyinstaller --onefile -w main.py

L'interface graphique a été faite sous PyQt et le tracking video avec la librairie OpenCV.

### Fonctionnement

![alt text](https://github.com/QuanticDisaster/proj_info_BEA/blob/main/doc/doc_github/result.png "Acceuil")

L'application se décline sous la forme d'une interface graphique permettant de naviguer intuitivement dans les vidéos choisies par l'utlisateur.

De manière modulable, l'utilisateur peut un ou des objets. Chaque objet peut-être suivi sur différentes parties de la vidéo (appelées séquences) définies par une frame de début et de fin

En renseignant une frame d'initialisation, l'utilisateur peut encadrer l'objet d'intérêt

<img src="https://github.com/QuanticDisaster/proj_info_BEA/blob/main/doc/doc_github/initialisation_masque.png" width=75% height=75%>

Le tracking démarre alors automatiquement. Une fois terminé, l'utilisateur peut exporter les masques, séparément ou fusionnés, dans un format compatible avec le logiciel de photogrammétrie MicMac.

<img src="https://github.com/QuanticDisaster/proj_info_BEA/blob/main/doc/doc_github/masques.png" width=60% height=60%>
