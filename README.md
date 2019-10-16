# OSM_downloader

OSM_Downloader est un outils permettant de télécharger des données OpenStreetMap depuis le net à l'aide d'un fichier contenant une requête Overpass.

--------

Installation des requirements: Le fichier requirement.txt contient les libraires et leur version à installer pour faire tourner les différentes fonctions. Vous devez installer ces libraires dans votre environnement virtuel (tel que Anaconda). Pour ce faire, utilisez la commande suivante: Pour ce faire, utilisez la commande suivante:

 pip install -r requirements.txt   ou   conda install --yes --file requirements.txt

--------

Comment lancer l'outil ?

 python osm_downloader.py osm_requete.txt -o [output file name]

Les paramètres utilisables sont les suivants :
positional arguments:
 
 - overpass_query : Input file contain overpass querry

optional arguments:
 - -o, --output, shapefile output path
