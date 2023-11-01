# Projet informatique

### Contexte
Dans le cadre de ses enquêtes le BEA est amené à traiter des vidéos d'accidents impliquant des aéronefs civils.
L'étude de ces vidéos peut permettre de reconstruire la trajectoire des aéronefs par photogrammétrie. Seulement, les objets mobiles qui y apparaissent peuvent perturber la convergence des calculs.

Le but de ce projet était donc de réaliser un outil de masquage automatique de ces élèments gênants.

### Installation

TODO

### Fonctionnement

![alt text](https://github.com/QuanticDisaster/proj_info_BEA/blob/main/doc/doc_github/result.png "Acceuil")

L'application se décline sous la forme d'une interface graphique permettant de naviguer intuitivement dans les vidéos choisies par l'utlisateur.

De manière modulable, l'utilisateur peut un ou des objets. Chaque objet peut-être suivi sur différentes parties de la vidéo (appelées séquences) définies par une frame de début et de fin

En renseignant une frame d'initialisation, l'utilisateur peut encadrer l'objet d'intérêt

![alt text](https://github.com/QuanticDisaster/proj_info_BEA/blob/main/doc/doc_github/initialisation_masque.png "initialisation")

Le tracking démarre alors automatiquement.

Une fois terminé, l'utilisateur peut exporter les masques séparément ou une fusion de ceux ci

![alt text](https://github.com/QuanticDisaster/proj_info_BEA/blob/main/doc/doc_github/masques.png "masques")