# NauteffVision
## Présentation
Ce logiciel est en l'état actuel une maquette d'afficheur de données de navigation

## Objectifs du projet
Ce projet a pour objectif d'afficher des 
  - Aider à la mise au point du pilote automatique ;
  - Fournir au navigateur une vue des données de son navire

## Avancement

NauteffVision, en l'état actuel, affiche déjà quelques données
pour le développement du pilote automatique .
Sa spécification en encore en cours de rédaction.
Il reste encore à développer.

## Installation et utilisation (linux)

### Téléchargement
le téléchargement est fait par git, git doit préalablement être installé.
La commande est la suivante :
git clone git@github.com:EmmGautier/NauteffVision.git
Cette commande crée un répertoire NauteffVision, taper alors:
cd NauteffVision
Il y a plusieurs branches, choisissez la branche flux avec :
git checkout Flux

Dans le répertoire data créez un tube nomé ("pipe")  avec la commande :
mknod  data/tubeNV p

Un petit programme de simulation envoie des données vers ce tube, pour l'utiliser taper :
sh ./simul.sh &
Il est conçu pour s'exécuter en arrière plan, avec 'en fin de ligne.
Pour voir le programe d'affichage taper

sh ./run.sh


