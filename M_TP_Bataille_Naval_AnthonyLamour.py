#import nécessaire pour le bon fonctionnement du programme
from socket import AF_INET, SOCK_STREAM, socket, setdefaulttimeout, timeout
import socket as socketpackage
import time, sys

#port de jeu sur la machine
PORT_JEU = 8887
#socket
socket_comm = None
#adresse
addr = None
#durée d'attente maximale en secondes
DUREE_ATTENTE_MAX = 30.0

#variables servvant à définir les joueurs
local_player = None
PL_CODE_ONE = 1
PL_CODE_TWO = 2

#quel joueur joue
gamestate = None

#grille locale du joueur
my_grid = {
    'a':[None,]*5,
    'b':[None,]*5,
    'c':[None,]*5,
    'd':[None,]*5,
    'e':[None,]*5
}

#grille local de l'opposant du joueur
opp_grid = {
    'a':[None,]*5,
    'b':[None,]*5,
    'c':[None,]*5,
    'd':[None,]*5,
    'e':[None,]*5
}

#isInit permet de savoir si les grilles sont initialisées
isInit=False

#GameOver permet de savoir quand la partie se termine
GameOver=False

#init_grids permet d'initialiser les grilles du joueur
def init_grids():

    #déclaration et initialisation de la position du sous-marin
    XSM=''
    YSM=''
    
    #demande de la position du sous-marin
    while XSM not in ('a','b','c','d','e') or YSM not in ('1','2','3','4','5'):
        print("Veuillez entrer la position de votre sous-marin (1 case) ? exemple a,1")
        position=input(">>")
        tmp_tab=position.split(',')
        XSM=tmp_tab[0]
        YSM=tmp_tab[1]
        
    #modification du Y pour qu'il soit entre 0 et 4 et puisse servir d'index de tableau
    YSM=int(YSM)-1
    #positionnement du sous-marin dans la grille
    my_grid[XSM][YSM]=1
    
    #déclaration et initialisation de la position et de l'orientation du croiseur
    XC=''
    YC=''
    HOV=''
    #positionvalide sert à savoir si la position choisi pour le croiseur est valide
    positionvalide=False
    
    #demande de la position du croiseur
    while XC not in ('a','b','c','d','e') or YC not in ('1','2','3','4','5') or positionvalide==False:
        print("Veuillez entrer la position de votre croiseur (3 case) et h ou v (pour horizontal, verticale) ? exemple a,1,h")
        position=input(">>")
        tmp_tab=position.split(',')
        XC=tmp_tab[0]
        YC=tmp_tab[1]
        HOV=tmp_tab[2]
        
        #si l'orientation du croiseur est horizontal alors...
        if HOV=='h':
            #...si X est valide alors...
            if XC<'d':
                #... si la grille ne contient rien sur 3 cases alors...
                if my_grid[XC][int(YC)-1]!=1 and my_grid[XC][int(YC)]!=1 and my_grid[XC][int(YC)+1]!=1:
                    #...on positionne le croiseur et on indique que la position est valide
                    my_grid[XC][int(YC)-1]=1
                    my_grid[XC][int(YC)]=1
                    my_grid[XC][int(YC)+1]=1
                    positionvalide=True
                #sinon...
                else:
                    #... on indique que la position est invalide
                    positionvalide=False
            #sinon...
            else:
                #... on indique que la position est invalide
                positionvalide=False
        #sinon si l'orientation du croiseur est verticale alors ...
        elif HOV=="v":
            #...si Y est valide alors...
            if YC<'4':
                #... si la grille ne contient rien sur 3 cases alors...
                if my_grid[XC][int(YC)]!=1 and my_grid[chr(ord(XC)+1)][int(YC)]!=1 and my_grid[chr(ord(XC)+2)][int(YC)]!=1:
                    #...on positionne le croiseur et on indique que la position est valide
                    my_grid[XC][int(YC)-1]=1
                    my_grid[chr(ord(XC)+1)][int(YC)-1]=1
                    my_grid[chr(ord(XC)+2)][int(YC)-1]=1
                    positionvalide=True
                #sinon...
                else:
                    #... on indique que la position est invalide
                    positionvalide=False
            #sinon...
            else:
                #... on indique que la position est invalide
                positionvalide=False
        #on rempli le reste de la grille avec des 0
        for i in ('a','b','c','d','e'):
            for j in ('1','2','3','4','5'):
                if my_grid[i][int(j)-1]!=1:
                    my_grid[i][int(j)-1]=0
        #on affiche la grille
        print(my_grid)
        
        #on rempli la grille de l'opposant avec des 0
        for i in ('a','b','c','d','e'):
            for j in ('1','2','3','4','5'):
                opp_grid[i][int(j)-1]=0
        #on affiche la grille de l'opposant
        print(opp_grid)

#init_roles
def init_roles():
    #utilisation de la variable global local_player
    global local_player
    #demande server ou client
    tmp = input('voulez-vous le role de client ou serveur (s/c) ? ')
    #temps que l'utilisateur ne rentre pas s ou c on redemande
    while tmp not in ('c','s'):
        err_msg = "veuillez taper 's' ou 'c' uniquement (un caractère!) "
        tmp = input(err_msg)
    #initialisation de local_player
    local_player = PL_CODE_ONE if tmp=='s' else PL_CODE_TWO

#initialisation de la connexion entre les machines
def init_connexion():

    #utilisation des variables globales local_player gamestate et socket_comm
    global local_player, gamestate, socket_comm
    
    #si client alors ...
    if local_player==PL_CODE_TWO:
        #...demande de l'adresse IP pour la connexion
        tmp = input('adresse IP? ')
        addr = tmp.strip(' \n')
        
        #tentative de connexion à l'adresse IP
        try:
            socket_comm = socket(AF_INET, SOCK_STREAM)
            socket_comm.connect((addr, PORT_JEU))
        except socketpackage.error:
            #si échec on l'affiche à l'utilisateur
            print('connexion refusée par lhote')
            return False
        
        #on affiche la connexion
        print('connexion établie')
        
        #reset de tmp
        tmp = None
        
        #initialisation de gamestate
        gamestate = '0'
        
        #récupération du gamestate du server
        gamestate=socket_comm.recv(15).decode()
        
        #affichage de gamestate
        print("OK voila gamestate"+gamestate)

        return True

    #si server on attent une connexion d'un client
    setdefaulttimeout(DUREE_ATTENTE_MAX)
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('', PORT_JEU))
    print('attente de connexion client...')
    
    s.listen(5)
    
    #tentative d'acceptation d'un client
    try:
        socket_comm, addr = s.accept()
        print('connexion recue depuis {} !'.format(addr) )

        s = socket_comm

        #initialisation des grilles
        init_grids()
        #set de isInit
        isInit=True
        #set de gamestate
        gamestate='2'
        #envoie du gamestate
        socket_comm.send(str(gamestate).encode())  # attention envoi sur socket exige un type bytes, pas str
        return True

    except timeout:
        
        #si temps écoulé alors on l'affiche à l'utilisateur
        print("INTERRUPTION : période d\'attente max. expirée")
        return False

#check_grid vérifie si la grille de jeu est vide
def check_grid(grid):
    
    #déclaration de res
    res=True
    #on parcoure la grille
    for i in ('a','b','c','d','e'):
        for j in ('1','2','3','4','5'):
            #si on trouve qqch alors...
            if(grid[i][int(j)-1]!=0):
                #...on set res à False
                res=False
    #renvoie de res
    return res
    
#affichage_tir affiche la grille des tirs déjà effectué
def affichage_tir(grid):
    #affichage d'un message expliquant le fonctionnement du tableau
    print("Etat du champ de bataille :")
    print("0=Pas encore ciblé 1=Toucher 2=Rater")
    #affichage du tableau
    print("  1 2 3 4 5")
    #initialisation de ligne
    ligne=""
    #affichage du reste du tableau
    for i in ('a','b','c','d','e'):
        ligne=i
        for j in ('1','2','3','4','5'):
            ligne=ligne+" "+str(grid[i][int(j)-1])
        print(ligne)

#initialisation des roles
init_roles()
#initialisation de la connexion
tmp = init_connexion()

#si un problème de connexion on l'affiche à l'utilisateur
if not tmp:
    sys.exit("Erreur fatale: connexion à l'hôte impossible /réservation de port a échoué")

#reset de tmp
tmp=None
#variables X et Y du coup du joueur
XC=''
YC=''
#coup du joueur sous forme d'une chaine
coupJoueur=""
#coupValide sert à savoir si le coup est valide
coupValide=False
#toucher sert à savoir si le coup à toucher
Toucher="False"

#temps que la partie n'est pas fini
while(not GameOver):
    
    #réinitialisation des variables afin d'éviter une boucle infinie
    XC=''
    YC=''
    coupJoueur=""
    coupValide=False
    
    #si le server joue et que nous sommes le server alors...
    if(gamestate=='1' and local_player==PL_CODE_ONE):
        #demande d'un coup
        while(XC not in ('a','b','c','d','e') or YC not in ('1','2','3','4','5') or coupValide==False):
            affichage_tir(opp_grid)
            print("Entrez votre coup :")
            coupJoueur=input(">>")
            tmp_tab=coupJoueur.split(',')
            XC=tmp_tab[0]
            YC=tmp_tab[1]
            if(opp_grid[XC][int(YC)-1]!=0):
                coupValide=False
            else:
                coupValide=True
        #envoi du coup
        socket_comm.send(coupJoueur.encode())
        #réception de Toucher
        Toucher=socket_comm.recv(15).decode()
        #si toucher alors...
        if(Toucher=="True"):
            #... mise à jour du tableau + affichage
            opp_grid[XC][int(YC)-1]=1
            print("Toucher")
        #sinon si rater alors...
        elif(Toucher=="False"):
            #mise à jour du tableau + affichage
            opp_grid[XC][int(YC)-1]=2
            print("Rater")
        #sinon si GameOver alors...
        elif(Toucher=="GameOver"):
            #affichage du message de victoire et fin de la partie
            print("Victoire félécitation")
            GameOver=True
        #set de gamestate
        gamestate='2'
        #envoie de gamestate
        socket_comm.send(gamestate.encode())
    #si le client joue et que nous sommes le client alors...
    elif(gamestate=='2' and local_player==PL_CODE_TWO):
        #...si les grilles ne sont pas initialiser alors...
        if(isInit==False):
            #... on les initialises
            init_grids()
            isInit=True
        #sinon...
        else:
            #... demande de coup
            while(XC not in ('a','b','c','d','e') or YC not in ('1','2','3','4','5') or coupValide==False):
                affichage_tir(opp_grid)
                print("Entrez votre coup :")
                coupJoueur=input(">>")
                tmp_tab=coupJoueur.split(',')
                XC=tmp_tab[0]
                YC=tmp_tab[1]
                if(opp_grid[XC][int(YC)-1]!=0):
                    coupValide=False
                else:
                    coupValide=True
            #envoie du coup
            socket_comm.send(coupJoueur.encode())
            #réception de toucher
            Toucher=socket_comm.recv(15).decode()
            #si toucher alros...
            if(Toucher=="True"):
                #... mise à jour du tableau + affichage
                opp_grid[XC][int(YC)-1]=1
                print("Toucher")
            #sinon si rater alors...
            elif(Toucher=="False"):
                #... mise à jour du tableau + affichage
                opp_grid[XC][int(YC)-1]=2
                print("Rater")
            #sinon si GameOver alors...
            elif(Toucher=="GameOver"):
                #affichage du message de victoire et fin de la partie
                print("Victoire félécitation")
                GameOver=True
        #set de gamestate
        gamestate='1'
        #envoie de gamestate
        socket_comm.send(gamestate.encode())
    #si le server joue et que nous sommes le client alors...
    elif(gamestate=='1' and local_player==PL_CODE_TWO):
        #... on récupère les données envoyées par le server
        donnee=socket_comm.recv(15).decode()
        #si il s'agit du gamestate alors...
        if(len(donnee)==1):
            #...mise à jour du gamestate
            gamestate=donnee
        #sinon...
        else:
            #... on récupère la position du coup
            tmp_tab=donnee.split(',')
            XC=tmp_tab[0]
            YC=tmp_tab[1]
            #on vérifie que le coup touche
            if(my_grid[XC][int(YC)-1]==1):
                print("\n L'énnemi a touché en : "+XC+","+YC+"\n")
                #si oui modification de la grille
                my_grid[XC][int(YC)-1]=0
                #envoie de True
                Toucher="True"
                #si il ne reste aucun bateau alors...
                if(check_grid(my_grid)):
                    #...on envoie GameOver
                    Toucher="GameOver"
                    #on affichage le message de défaite
                    print("Défaite")
                    #on termine la partie
                    GameOver=True
            #sinon
            else:
                print("\n L'énnemi a raté son tire en : "+XC+","+YC+"\n")
                #envoi de False
                Toucher="False"
            #envoi de toucher
            socket_comm.send(Toucher.encode())
    #si le client joue et que nous sommes le server alors...
    elif(gamestate=='2' and local_player==PL_CODE_ONE):
        #... on récupère les données envoyées par le client
        donnee=socket_comm.recv(15).decode()
        #si il s'agit du gamestate alors...
        if(len(donnee)==1):
            #...mise à jour du gamestate
            gamestate=donnee
        #sinon...
        else:
            #... on récupère la position du coup
            tmp_tab=donnee.split(',')
            XC=tmp_tab[0]
            YC=tmp_tab[1]
            #on vérifie que le coup touche
            if(my_grid[XC][int(YC)-1]==1):
                print("\n L'énnemi a touché en : "+XC+","+YC+"\n")
                #si oui modification de la grille
                my_grid[XC][int(YC)-1]=0
                Toucher="True"
                #si il ne reste aucun bateau alors...
                if(check_grid(my_grid)):
                    #... on envoi GameOver
                    Toucher="GameOver"
                    #on affichage le message de défaite
                    print("Défaite")
                    #on termine la partie
                    GameOver=True
            #sinon
            else:
                print("\n L'énnemi a raté son tire en : "+XC+","+YC+"\n")
                #envoi de False
                Toucher="False"
            #envoi de toucher
            socket_comm.send(Toucher.encode())
            
#affichage d'un message au joueur pour indiqué la fin de la partie   
print("Merci d'avoir joué")