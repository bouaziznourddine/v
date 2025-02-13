"""
Module netlogopy amélioré
-------------------------
Ce module propose une interface orientée objet pour communiquer avec NetLogo via nl4py.
Il fournit également des classes représentant des "turtles" (et des extensions, comme les PyTurtles)
et des "streets" pour simplifier l'interaction avec le modèle NetLogo.
"""

import copy
import os
import shutil
import time
import nl4py
def run_netlogo(netlogo_home="C:/Program Files/NetLogo 6.2.2",path_model=""):
    
    nl4py.initialize(netlogo_home)
    nl4py.startServer(netlogo_home)
    if path_model == "":
        model = os.path.dirname(__file__)+"\\netlogopy.nlogo"
    else :
        model = path_model
    n=nl4py.NetLogoApp()
    n.openModel(model)
    n.command("setup")
    return n

def list2nllist(lst) -> str:
    """
    Convertit une liste Python en une chaîne formatée comme une liste NetLogo.
    Exemple : [1, "test"] → '[ 1  "test" ]'
    """
    s = "["
    for item in lst:
        if isinstance(item, str):
            s += f' "{item}" '
        else:
            s += f' {item} '
    s += "]"
    return s


class NetLogoInterface:
    """
    Interface pour communiquer avec NetLogo via nl4py.
    """
    def __init__(self, netlogo_home: str = "C:/Program Files/NetLogo 6.2.2", model_path: str = None):
        """
        Initialise l'interface avec le chemin d'installation de NetLogo et le modèle à ouvrir.
        Si model_path est None, il est défini par défaut dans le même dossier que ce module.
        """
        self.netlogo_home = netlogo_home
        if model_path is None:
            self.model_path = os.path.join(os.path.dirname(__file__), "netlogopy.nlogo")
        else:
            self.model_path = model_path
        self.app = None

    def initialize(self) -> None:
        """
        Initialise nl4py, démarre le serveur NetLogo, ouvre le modèle et exécute le setup.
        """
        nl4py.initialize(self.netlogo_home)
        nl4py.startServer(self.netlogo_home)
        self.app = nl4py.NetLogoApp()
        self.app.openModel(self.model_path)
        self.command("setup")

    def command(self, cmd: str):
        """
        Exécute une commande NetLogo.
        """
        return self.app.command(cmd)

    def report(self, expression: str):
        """
        Évalue une expression NetLogo et renvoie le résultat.
        """
        return self.app.report(expression)

    def close(self):
        """
        Ferme le modèle NetLogo.
        """
        self.app.close_model()


def netlogoshow(nl: NetLogoInterface, word: str) -> str:
    """
    Affiche un message dans NetLogo en appelant la procédure 'netlogoshow'.
    """
    cmd = "netlogoshow " + list2nllist([word])
    return nl.report(cmd)


def resize_world(nl: NetLogoInterface, x0, xf, y0, yf) -> None:
    """
    Redimensionne le monde NetLogo.
    """
    cmd = "resize_world " + list2nllist([x0, xf, y0, yf])
    nl.report(cmd)


def set_background(nl: NetLogoInterface, image: str) -> None:
    """
    Définit l'image de fond du monde NetLogo.
    """
    cmd = "set_background " + list2nllist([image])
    nl.report(cmd)


def run_command(nl: NetLogoInterface, command: str):
    """
    Exécute une commande arbitraire sur le modèle NetLogo.
    """
    return nl.command(command)


def deep_copy(a):
    """
    Renvoie une copie profonde de l'objet.
    """
    return copy.deepcopy(a)


def distancebetween(nl: NetLogoInterface, from_turtle, target_turtle) -> str:
    """
    Calcule la distance entre deux turtles en utilisant leur id.
    """
    cmd = "distanceto " + list2nllist([from_turtle.id, target_turtle.id])
    return nl.report(cmd)


def getxyturtle(nl: NetLogoInterface, turtle_obj):
    """
    Retourne les coordonnées [x, y] du turtle.
    """
    cmd = "getxyturtle " + list2nllist([turtle_obj.id])
    result = nl.report(cmd)
    return eval(result)  # Attention à l'utilisation de eval ; à sécuriser si nécessaire.


class NetLogoModel:
    """
    Un wrapper pour un modèle NetLogo.
    """
    def __init__(self, netlogo_home: str = "C:/Program Files/NetLogo 6.2.2", model_path: str = None):
        self.interface = NetLogoInterface(netlogo_home, model_path)

    def setup(self):
        """
        Initialise le modèle en appelant la procédure setup de NetLogo.
        """
        self.interface.initialize()


class NL_Turtle:
    """
    Représente une turtle de NetLogo.
    """
    def __init__(self, nl: NetLogoInterface, turtle_id: int = None):
        self.nl = nl
        self.id = turtle_id

    def distanceto(self, target) -> str:
        """
        Calcule la distance jusqu'à une autre turtle.
        """
        cmd = "distanceto " + list2nllist([self.id, target.id])
        return self.nl.report(cmd)

    def face_to(self, target) -> int:
        """
        Oriente la turtle vers la cible.
        """
        cmd = "faceto " + list2nllist([self.id, target.id])
        result = self.nl.report(cmd)
        # La conversion dépend du format renvoyé par NetLogo.
        return int(result.strip()[:-2])

    def move_to(self, target):
        """
        Déplace la turtle vers une autre turtle (en utilisant leur id).
        """
        cmd = "moveto " + list2nllist([self.id, target.id])
        self.nl.report(cmd)

    def hide(self):
        """
        Masque la turtle.
        """
        cmd = "hideturtle " + list2nllist([self.id])
        self.nl.report(cmd)

    def die(self):
        """
        Supprime (fait mourir) la turtle.
        """
        cmd = "dieturtle " + list2nllist([self.id])
        self.nl.report(cmd)

    def set_shape(self, shape: str):
        """
        Change la forme de la turtle.
        """
        cmd = "set_shape " + list2nllist([self.id, shape])
        self.nl.report(cmd)

    def setxy(self, x, y):
        """
        Place la turtle aux coordonnées (x, y).
        """
        cmd = "turtle_setxy " + list2nllist([self.id, x, y])
        self.nl.report(cmd)

    def fd(self, repeat: int = 1):
        """
        Fait avancer la turtle.
        """
        cmd = "fdfd " + list2nllist([self.id, repeat])
        self.nl.report(cmd)


class NL_Street:
    """
    Représente une rue (link dirigé) dans NetLogo.
    """
    def __init__(self, nl: NetLogoInterface, from_turtle: NL_Turtle, to_turtle: NL_Turtle,
                 label: str = "street", labelcolor=0, color=0, shape="aa", thickness=0.5):
        self.nl = nl
        self.create_street(from_turtle.id, to_turtle.id, label, labelcolor, color, shape, thickness)

    def create_street(self, from_id, to_id, label, labelcolor, color, shape, thickness):
        cmd = "create-street-ft " + list2nllist([from_id, to_id, label, labelcolor, color, shape, thickness])
        result = self.nl.report(cmd)
        self.id = result  # identifiant renvoyé par NetLogo
        return self


class PyTurtle(NL_Turtle):
    """
    Extension de NL_Turtle avec des propriétés supplémentaires.
    """
    def __init__(self, nl: NetLogoInterface, x=0, y=0, shape="car", size_shape=4, color=0,
                 name="zn", labelcolor=0, fields: dict = None):
        if fields is None:
            fields = {}
        self.x = x
        self.y = y
        self.shape = shape
        self.size_shape = size_shape
        self.color = color
        self.name = name
        self.labelcolor = labelcolor
        self.fields = fields
        # Initialisation de la turtle via la classe parente.
        super().__init__(nl)
        # Ajout des champs supplémentaires dans l'instance.
        self.__dict__.update(fields)
        self.create_pyturtle(x, y, shape, size_shape, color, name, labelcolor)

    def create_pyturtle(self, x, y, shape, size_shape, color, name, labelcolor):
        """
        Crée une pyturtle dans NetLogo et récupère son identifiant.
        """
        cmd = "create-pyturtle-xyid " + list2nllist([x, y, shape, size_shape, color, name, labelcolor])
        result = self.nl.report(cmd)
        # Conversion en entier en retirant d'éventuels caractères de fin (selon le format renvoyé).
        self.id = int(result.strip()[:-2])
        return self
    def set_label(self, text: str):
        """
        Définit le label de la turtle dans NetLogo.
        """
        # On construit une commande NetLogo du type:
        # ask turtle <id> [ set label "text" ]
        cmd = f'ask turtle {self.id} [ set label "{text}" ]'
        self.nl.command(cmd)



# --- Exemple d'utilisation ---
if __name__ == "__main__":
    # Initialisation de l'interface NetLogo
    nl_interface = NetLogoInterface()
    nl_interface.initialize()

    # Redimensionnement du monde et définition du fond
    resize_world(nl_interface, 0, 60, 0, 60)
    set_background(nl_interface, "D:/cphs2024/netlogopy.png")

    # Création d'une PyTurtle (par exemple, une voiture) avec des champs personnalisés
    my_turtle = PyTurtle(
        nl_interface,
        x=10,
        y=10,
        shape="car",
        size_shape=4,
        color=15,
        name="myCar",
        labelcolor=15,
        fields={"speed": 1}
    )

    # Faire avancer la turtle
    my_turtle.fd(5)

    # Récupérer et afficher les coordonnées de la turtle
    coords = getxyturtle(nl_interface, my_turtle)
    print("Turtle coordinates:", coords)

    # Exemple de création d'une rue entre deux turtles (si nécessaire) :
    # from_turtle = my_turtle
    # to_turtle = PyTurtle(nl_interface, x=20, y=20, shape="house", size_shape=4, color=5, name="zone", labelcolor=5)
    # street = NL_Street(nl_interface, from_turtle, to_turtle, label="route", labelcolor=35, color=35, thickness=0.5)

    # Attendre quelques secondes pour observer les changements (optionnel)
    time.sleep(3)

    # Fermeture du modèle NetLogo
    nl_interface.close()
