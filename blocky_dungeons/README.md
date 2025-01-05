# BLOCKY DUNGEONS
Dans __**BLOCKY DUNGEONS**__, incarnez un aventurier de Minecraft pris au piège dans un donjon diabolique.
Découvrez des trésors, évitez des pièges et trouvez la sortie au travers d'un nombre quasi-infini de structures générées aléatoirement.  
Serez-vous capable de quitter le donjon ?  
Non ? Ce n'est pas grave, vous pouvez en générer un nouveau.

## Sommaire

1. Installation
2. Démarrage et paramétrage
3. Comment jouer
4. Bugs connus
5. Crédits

## 1. Installation
### Dépendances
Ce projet fonctionne avec python3.11.  
Il nécessite Bukkit, mcpi et RaspberryJuice configurés pour Minecraft 1.6.4.  
La version Java 1.6 doit être installée sur la machine.  
Pour Linux, une version de wine à jour est nécessaire.

### Mise en place
Un setup fonctionnel peut être téléchargé sur le [github du projet](https://github.com/Scrollwarden/minecraft-nsi-projet).  

### Compatibilité
Ce projet à été créé sous une version de Linux Mint dans un environnement wine. Il n'a pas été testé sous d'autres plateformes et peut comporter des bugs.
Ce projet est toutefois théoriquement compatible avec Window.

## 2. Démarrage et paramétrage
### Démarrage
Pour lancer le jeu, suivez précisemment les étapes suivantes :  
0. Si vous êtes sous Linux, ouvrez un explorer window avec wine.
1. Dans le dossier `02 StarterKitPC/AdventuresInMinecraft/Bukkit`, lancez le fichier `start.bat`. (Sous window, le fichier `startBukkit.bat` du dossier parent devrait fonctionner).
2. Dans le dossier `/home/matthew/Bureau/Server TP minecraft/TP Minecraft avec python 3/03 MINECRAFT/Minecraft Portable/Minecraft Portable`, lancez le fichier `StartMinecraft.bat`.
3. Un launcher des temps anciens apparaît devant vous. Cliquez sur **Play** et attendez que le jeu se lance.
4. Entrez dans le menu **Multiplayer**.
5. Créez une **Quick Connect** et renseignez dans l'adresse `localhost`.
6. Connectez-vous au server.
7. Dans le dossier `/home/matthew/Bureau/Server TP minecraft/TP Minecraft avec python 3/02 StarterKitPC/AdventuresInMinecraft/MyAdventures`, ouvrez le fichier `blocky_dungeon_vX.py` (choissisez la version du projet que vous désirez lancer) dans un interpréteur python.
8. Exécutez le programme.

### Paramétrage
Entre chaque génération de donjon, vous pouvez paramétrer certaines données du jeu.  
Ouvrez dans un interpréteur python le fichier `dungeons_settings.py`.  
Différentes constantes s'offrent à vous :  
- `SKIP_MONOLOGUE` permet, si elle est passée à `True`, d'ignorer le dialogue du *Maître du Donjon*.
- `DUNGEON_SIZE` est la taille moyenne du donjon. La taille des donjons peut tout de même varier avec ce même paramètre.
De manière générale, un donjon de taille 2 n'aura qu'une salle devant chaque porte de la première salle,
tandis qu'un donjon de taille 15 offrira un challenge assez important.
- `ROOM_SIZE` permet de définir la taille des salles. **IMPORTANT : Cette valeur doit obligatoirement être impaire.**
- `WALL_BLOCK` est le type de blocs qui constituera les murs du donjon.
- `FLOOR_BLOCK` est le type de blocs qui constituera le sol du donjon.
- `ROOF_BLOCK` est le type de bloc qui constituera le plafond du donjon.
- `WOOD_BLOCK` est le type de bloc qui constituera le bois présent dans le donjon (c'est à dire principalement les ponts).
- `ROOM_WIDTH` **DANGER ZONE : Ce paramètre va certainement causer des bugs s'il est modifié.** permet de définir la largeur de la salle.
Modifier ce paramètre peut causer des problèmes d'alignement des salles ou faire se chevaucher des angles de salles.
- `ROOM_DEPTH` **DANGER ZONE : Ce paramètre va certainement causer des bugs s'il est modifié.** permet de définir la longueur de la salle.
Modifier ce paramètre peut causer des problèmes d'alignement des salles ou faire se chevaucher des angles de salles.

## 3. Comment jouer
### Objectif
Une fois le donjon créé, vous êtes coincé au milieu d'un labyrinthe de salles potentiellement piégées. L'objectif est de sortir vivant avec le plus de trésors possibles.  
Certaines salles comportent des portes en fer. Pour les ouvrir, vous avez besoin de trouver un torche de redstone qui fait office de clef, 
et que vous devrez placer devant la porte (contre le sol).  
Attention, certains pièges peuvent empêcher la pose d'une torche. Dans ce cas, vous aurez besoin de blocs.  
Certaines portes peuvent donner sur des murs. Il s'agissait de caches pour les monstres lorsqu'ils peuplaient ces lieux.
Cela signifie aussi (et surtout) qu'une autre salle est présente derrière, accessible par un autre endroit.  
Certaines salles comportent des portes murées. Cela signifie que cette salle est l'un des bouts du donjon.
C'est dans ces salles qu'une porte de sortie peut potentiellement se trouver.  
_  
**IMPORTANT :** Il est possible que le *Maître du Donjon* ai été très méchant et n'ai laissé aucune porte de sortie.
Dans ce cas, vous êtes condamnés à errer dans les entrailles du donjon jusqu'à la fin de vos jours.  

### Conseils
*Ces conseils sont considérés comme nécessaires à une bonne expérience de jeu.*  
*Les outils utilisés pour la création du projet ne permettaient pas de les mettre en place automatiquement.*  
NOTE : pour vous mettre en créatif, tapez dans la fenêtre de commande du server bukkit `gamemode creative <votre_nom>`.
Lorsque vous voulez commencer l'exploration du donjon, lancez la commande `gamemode survival <votre_nom>`.
_  
****
**Génération**
Le donjon se génère "à l'envers", c'est à dire que les portes de la salle de départ sembleront mener directement à l'extérieur
jusqu'à ce que le donjon soit entièrement généré.  
Ne commencez donc pas l'exploration trop tôt. Attendez d'être téléportés au centre de la salle de départ.
****
**Items**  
Avant de commencer à explorer le donjon, vous aurez besoin des items suivants :
- Blocs (de planches par exemple). Certaines zones des salles peuvent être difficiles à atteindre et vous pouvez vous retrouver coincés à certains moments.
- Pioche. Les trésors sont présents sous forme de blocs de valeur que vous voudrez récupérer.
- Épée. Elle sera utile dans certaines salles malgré le fait que les outils utilisés ne permettent pas l'apparitions de créatures.
- Torches. Elles sont optionnelles, mais certaines pièces peuvent être très sombres.  
****
**Règles**  
Il n'y a pas de règles obligatoires à suivre, mais les propositions suivantes peuvent améliorer votre expérience de jeu.  
Le donjon à été pensé de telle sorte que vous n'avez jamais besoin de creuser un mur ou de casser une porte.
Par ailleur, les portes de fer n'ont pas nécessairement toutes une clef, mais cela fait partie du jeu. Vous devez choisir quelle porte ouvrir, ou trouver des clefs dans des salles sans portes. Vous êtes sensé laisser la torche là où vous l'avez posé tant que vous voulez conserver la porte ouverte. Explorez la pièce, puis reprenez la clef lorsque vous avez fini pour ouvrir la porte suivante.
****
**Trésors cachés**  
Certaines décorations peuvent cacher dans leur base des trésors ou des clefs. Lorsque vous êtes dans une salle au trésor ou dans une salle fermée à clef,
testez les structures suivantes :
- pillier flambeau (avec une flamme au sommet)
- pillier de soutiens
- cuves de liquide

## 4. Bugs connus
Les bugs suivants ont été répertoriés sous Linux Mint :
- **Minecraft Crash.** Le jeu peut freeze et crash au bout d'un certain temps visiblement aléatoire. Ce bug semble lié à la machine sur laquelle le projet à été développé.

## 5. Crédits
### Créateurs
Ce projet à été porté par M.Batt et le studio DICESCREEN. Il a été commandé dans le cadre du *Concours des Tests de NSI*.

### License et juridiction
Voir LICENCE.txt dans le même dossier que ce README.  
Ce projet est construit autour d'une version de Minecraft piratée fournie par les commanditaires du projet.
DICESCREEN Studio décline toute responsabilité légale à ce sujet, et affirme s'être contenté de produire le résultat demandé à partir des outils imposés.

### Histoire du projet
Au départ, le projet consistait en la possibilité de lancer des commandes créatives en survie, limitée par une compétence magique et du mana.
Malheureusement, Minecraft 1.6.4 ne donne accès qu'à un nombre limité de commandes, et la configuration Window des outils a rendu impossible la configuration du projet
pour une version de Minecraft plus récente (en tout cas sur la machine Linux utilisée pour développer le projet).  
En voulant repasser sur la version 1.6.4 de Minecraft, il a été avéré que les outils ne fonctionnaient déjà pas au départ.  
Après une semaine de débug (qui n'aurai pas pu aboutir sans l'aide de mon père), le setup fonctionnait enfin sur l'ordinateur.  
Le projet a donc été reconverti : il s'agissait alors d'un ensemble de sorts prédéfinis et déclenchés grâce à un appel dans le tchat.
Cette idée s'est heurtée aux limites de mcpi, qui propose de nombreuses fonctions et méthodes qui ne marchent en fait pas.
Notamment, la lecture du tchat est impossible, ainsi que l'obtention de la direction dans laquelle le joueur est tourné.  
Dans le but de n'utiliser que du plaçage de blocs (seule méthode dont le fonctionnement effectif était assuré), le projet s'est changé en la formation d'un labyrinthe.
Toutefois, les algorithmes de générations de labyrinthes sont complexes et le temps pour réaliser le projet était très limité.  
Finallement, le projet BLOCKY DUNGEONS débute en remplacement le vendredi 3 janvier.
La méthode d'apparition des entitées ne fonctionne pas, certains blocs du jeu n'ont pas d'identifiant dans mcpi,
il est impossible de faire apparaître des items ou de remplir des inventaires, et d'autres problèmes
ont empêchés le projet d'être aussi perfectionné que voulu. Toutefois, le résultat était satifaisant le dimanche 5 janvier (deux jours avant le rendu).  
Le projet a donc été retenu et publié.

### DICESCREEN Studio, qui sommes-nous ?
DICESCREEN Studio est un studio de développement de jeux vidéos et sites web indépendant. Il a été créé par Matthew Batt le 30 octobre 2023.  
Il a publié son premier jeu vidéo le 11 novembre 2023. Il s'agissait de The game of MOTUS, un jeu à thème rétro basé sur le jeu du motus des émissions télévisées.
Depuis, d'autres projets ont été menés (très majoritairement dans le cadre des *Concours de Tests de NSI*) et l'équipe s'est agrandie.

### Inspirations
Le principe du monologue du *Maître du donjon* est inspiré du monologue des IA dans Portal 2. Le contenu est entièrement inventé en revanche.  
