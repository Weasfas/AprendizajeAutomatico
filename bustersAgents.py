# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import util
from game import *
from keyboardAgents import KeyboardAgent
import inference
import busters
import random, util, math
import sys
from distanceCalculator import Distancer

class NullGraphics:
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs

class BustersAgent:
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable

    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
        #for index, inf in enumerate(self.inferenceModules):
        #    if not self.firstMove and self.elapseTimeEnable:
        #        inf.elapseTime(gameState)
        #    self.firstMove = False
        #    if self.observeEnable:
        #        inf.observeState(gameState)
        #    self.ghostBeliefs[index] = inf.getBeliefDistribution()
        #self.display.updateDistributions(self.ghostBeliefs)
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
        return Directions.STOP

class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)
        self.countActions = 0

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
     self.countActions = self.countActions + 1
     return KeyboardAgent.getAction(self, gameState)

    def hola(self, gameState):
     array = gameState.getLegalPacmanActions()
     mW=0
     mE=0
     mP=1
     mN=0
     mS=0
     distancias=map(lambda a: 9999 if (a==None) else a, gameState.data.ghostDistances)
     index=distancias.index(min(x for x in distancias if x is not None))
     pacx = gameState.getPacmanPosition()[0]
     pacy = gameState.getPacmanPosition()[1]
     ghox=gameState.getGhostPositions()[index][0]
     ghoy=gameState.getGhostPositions()[index][1]
     move1=Directions.STOP
     move2=Directions.STOP
     if ( pacx-ghox > 0 ): move1 = Directions.WEST
     if ( pacx-ghox < 0 ): move1 = Directions.EAST
     if ( pacy-ghoy < 0 ): move2 = Directions.NORTH
     if ( pacy-ghoy > 0 ): move2 = Directions.SOUTH
     if ( "West" in array): mW = 1
     if ( "East" in array): mE = 1
     if ( "North" in array): mN = 1
     if ( "South" in array): mS = 1
     GD=min (distancias)
     mensaje = "\t" + str(mW) + "," + str(mP) + "," + str(mE) + "," + str(mN) + "," + str(mS) + "," + str(move1) + "," + str(move2) + "," + str(GD) + "," + str(gameState.getScore()) + "," + str(gameState.data.agentStates[0].getDirection()) + "," + '\n' +'\t'
     return mensaje

    def evaluator(self, gameState):

        distancias=map(lambda a: 9999 if (a==None) else a, gameState.data.ghostDistances)
        d=min(distancias)

        vivos=0
        for i in gameState.getLivingGhosts():
         if(i==True): vivos=vivos+1

        tick=self.countActions

        #almacen=[]
        #almacen[0]=str()
        #almacen[1]=gameState.getLivingGhosts()
        #almacen[2]=self.countActions

        mensaje = str(d) + "," + str(vivos) + "," + str(tick) + "\n"
        return mensaje

# Random PacMan Agent
class RandomPAgent(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        ##print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table
        
    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move

class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def chooseAction(self, gameState):
        """
        First computes the most likely position of each ghost that has
        not yet been captured, then chooses an action that brings
        Pacman closer to the closest ghost (according to mazeDistance!).

        To find the mazeDistance between any two positions, use:
          self.distancer.getDistance(pos1, pos2)

        To find the successor position of a position after an action:
          successorPosition = Actions.getSuccessor(position, action)

        livingGhostPositionDistributions, defined below, is a list of
        util.Counter objects equal to the position belief
        distributions for each of the ghosts that are still alive.  It
        is defined based on (these are implementation details about
        which you need not be concerned):

          1) gameState.getLivingGhosts(), a list of booleans, one for each
             agent, indicating whether or not the agent is alive.  Note
             that pacman is always agent 0, so the ghosts are agents 1,
             onwards (just as before).

          2) self.ghostBeliefs, the list of belief distributions for each
             of the ghosts (including ghosts that are not alive).  The
             indices into this list should be 1 less than indices into the
             gameState.getLivingGhosts() list.
        """
        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]
        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = \
            [beliefs for i, beliefs in enumerate(self.ghostBeliefs)
             if livingGhosts[i+1]]
        return Directions.EAST

# NUESTRO AGENTE CON CLUSTERS PRACTICA2
class ClusAgentAA(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0

    def hola(self, gameState):
        array = gameState.getLegalPacmanActions()
        mW=0
        mE=0
        mP=1
        mN=0
        mS=0
        distancias=map(lambda a: 9999 if (a==None) else a, gameState.data.ghostDistances)
        index=distancias.index(min(x for x in distancias if x is not None))
        pacx = gameState.getPacmanPosition()[0]
        pacy = gameState.getPacmanPosition()[1]
        ghox=gameState.getGhostPositions()[index][0]
        ghoy=gameState.getGhostPositions()[index][1]
        move1=Directions.STOP
        move2=Directions.STOP
        if   ( pacx-ghox > 0 ): move1 = Directions.WEST
        if   ( pacx-ghox < 0 ): move1 = Directions.EAST
        if   ( pacy-ghoy < 0 ): move2 = Directions.NORTH
        if   ( pacy-ghoy > 0 ): move2 = Directions.SOUTH
        if ( "West" in array): mW = 1
        if ( "East" in array): mE = 1
        if ( "North" in array): mN = 1
        if ( "South" in array): mS = 1
        GD=min (distancias)
        mensaje = "\t" + str(mW) + "," + str(mP) + "," + str(mE) + "," + str(mN) + "," + str(mS) + "," + str(move1) + "," + str(move2) + "," + str(GD) + "," + str(gameState.getScore()) + "," + str(gameState.data.agentStates[0].getDirection()) + "," + '\n' +'\t'
        return mensaje

    def evaluator(self, gameState):

        distancias=map(lambda a: 9999 if (a==None) else a, gameState.data.ghostDistances)
        d=min(distancias)

        vivos=0
        for i in gameState.getLivingGhosts():
         if(i==True): vivos=vivos+1

        tick=self.countActions

        #almacen=[]
        #almacen[0]=str()
        #almacen[1]=gameState.getLivingGhosts()
        #almacen[2]=self.countActions

        mensaje = str(d) + "," + str(vivos) + "," + str(tick) + "\n"
        return mensaje

    def chooseAction(self, gameState):
        self.countActions = self.countActions + 1
        self.hola(gameState)
        move = Directions.STOP
        array = gameState.getLegalPacmanActions()
        mW=0
        mE=0
        mN=0
        mS=0
        distancias=map(lambda a: 9999 if (a==None) else a, gameState.data.ghostDistances)
        index=distancias.index(min(x for x in distancias if x is not None))
        pacx = gameState.getPacmanPosition()[0]
        pacy = gameState.getPacmanPosition()[1]
        ghox=gameState.getGhostPositions()[index][0]
        ghoy=gameState.getGhostPositions()[index][1]
        move1=0 #Stop is 0
        move2=0 #Stop is 0
        if ( pacx-ghox > 0 ): move1 = 1  #Move is 1
        if ( pacx-ghox < 0 ): move1 = 1  #Move is 1
        if ( pacy-ghoy < 0 ): move2 = 1  #Move is 1
        if ( pacy-ghoy > 0 ): move2 = 1  #Move is 1
        if ( "West" in array): mW = 1
        if ( "East" in array): mE = 1
        if ( "North" in array): mN = 1
        if ( "South" in array): mS = 1
        gD=min (distancias)
        self.countActions = self.countActions + 1
        move = Directions.STOP
        with open("C:\\Users\\nacho\\Desktop\\AprendizajeAutomatico-Practica2Version3\\Centroides.txt", 'r') as f:
         data = [map(str, line.split()) for line in f]
        vectorDistancia = []
        for j in range(len(data)):
         a = math.pow((float(data[j][0]) - mW), 2)
         b = math.pow((float(data[j][1]) - mE), 2)
         c = math.pow((float(data[j][2]) - mN), 2)
         d = math.pow((float(data[j][3]) - mS), 2)
         if ( data[j][4] == "Stop" ):
          e = math.pow((0 - move1), 2)
         else:
          e = math.pow((1 - move1), 2)
         if ( data[j][5] == "Stop" ):
          f = math.pow((0 - move2), 2)
         else:
          f = math.pow((1 - move2), 2)
         g = math.pow((float(data[j][6]) - gD), 2)
         h = math.pow((float(data[j][7]) - gameState.getScore()), 2)
         result = math.sqrt(a + b + c + d + e + f + g + h)
         vectorDistancia.append(result)
        cluster=vectorDistancia.index(min(x for x in vectorDistancia if x is not None))

        #print(cluster)
        a=random.randint(1,100)

        if(cluster==0):
          if("East" in array and a < 4):
           return Directions.EAST
          elif("West" in array and a >= 4 and a < 40):
           return Directions.WEST
          elif("South" in array and a>=40 and a < 71):
           return Directions.SOUTH
          elif("North" in array and a >= 71):
           return Directions.NORTH
          else:
           return random.choice(array)

        if(cluster==1):
          if("North" in array and a < 15):
           return Directions.NORTH
          elif("West" in array and a >= 15 and a < 67):
           return Directions.WEST
          elif("East" in array and a>=67):
           return Directions.EAST
          else:
           return random.choice(array)

        if(cluster==2):
          if("North" in array and a < 10):
           return Directions.NORTH
          elif("South" in array and a >= 10 and a < 20):
           return Directions.SOUTH
          elif("West" in array and a>=20 and a < 30):
           return Directions.WEST
          elif("East" in array and a >= 30):
           return Directions.EAST
          else:
           return random.choice(array)

        if(cluster==3):
          if("North" in array and a < 22):
           return Directions.NORTH
          elif("East" in array and a>=22 and a < 44):
           return Directions.EAST
          elif("West" in array and a >= 44):
           return Directions.WEST
          else:
           return random.choice(array)

        if(cluster==4):
         if("East" in array and a < 14):
           return Directions.EAST
         elif("West" in array and a >= 14 and a < 46):
          return Directions.WEST
         elif("South" in array and a>=46):
          return Directions.SOUTH
         else:
          return random.choice(array)

        if(cluster==5):
         if("East" in array and a < 25):
           return Directions.EAST
         elif("West" in array and a >= 25 and a < 49):
          return Directions.WEST
         elif("South" in array and a>=49 and a < 88):
          return Directions.SOUTH
         elif("North" in array and a >= 88):
          return Directions.NORTH
         else:
          return random.choice(array)

        if(cluster==6):
         if("East" in array and a < 39):
           return Directions.EAST
         elif("West" in array and a >= 39 and a < 42):
          return Directions.WEST
         elif("South" in array and a>=42 and a < 60):
          return Directions.SOUTH
         elif("North" in array and a >= 60):
          return Directions.NORTH
         else:
          return random.choice(array)

        if(cluster==7):
         if("East" in array and a < 38):
           return Directions.EAST
         elif("West" in array and a >= 38 and a < 81):
          return Directions.WEST
         elif("North" in array and a >= 81):
          return Directions.NORTH
         else:
          return random.choice(array)

        if(cluster==8):
         if("East" in array and a < 22):
           return Directions.EAST
         elif("West" in array and a >= 22 and a < 46):
          return Directions.WEST
         elif("South" in array and a>=46 and a < 96):
          return Directions.SOUTH
         elif("North" in array and a >= 96):
          return Directions.NORTH
         else:
          return random.choice(array)

        if(cluster==9):
         if("East" in array and a < 30):
           return Directions.EAST
         elif("West" in array and a >= 30 and a < 43):
          return Directions.WEST
         elif("South" in array and a>=43 and a < 68):
          return Directions.SOUTH
         elif("North" in array and a >= 68):
          return Directions.NORTH
         else:
           return random.choice(array)

# AGENTE DE APRENDIZAJE AUTOMATICO UC3M
class BasicAgentAA(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        #print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table

    def printInfo(self, gameState):
        print "---------------- TICK ", self.countActions, " --------------------------"
        # Dimensiones del mapa
        width, height = gameState.data.layout.width, gameState.data.layout.height
        print "Width: ", width, " Height: ", height
        # Posicion del Pacman
        print "Pacman position: ", gameState.getPacmanPosition()
        # Acciones legales de pacman en la posicion actual
        print "Legal actions: ", gameState.getLegalPacmanActions()
        # Direccion de pacman
        print "Pacman direction: ", gameState.data.agentStates[0].getDirection()
        # Numero de fantasmas
        print "Number of ghosts: ", gameState.getNumAgents() - 1
        # Fantasmas que estan vivos (el indice 0 del array que se devuelve corresponde a pacman y siempre es false)
        print "Living ghosts: ", gameState.getLivingGhosts()
        # Posicion de los fantasmas
        print "Ghosts positions: ", gameState.getGhostPositions()
        # Direciones de los fantasmas
        print "Ghosts directions: ", [gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)]
        # Distancia de manhattan a los fantasmas
        print "Ghosts distances: ", gameState.data.ghostDistances
        # Puntos de comida restantes
        print "Pac dots: ", gameState.getNumFood()
        # Distancia de manhattan a la comida mas cercada
        print "Distance nearest pac dots: ", gameState.getDistanceNearestFood()
        # Paredes del mapa
        print "Maze:  \n", gameState.getWalls()
        # Puntuacion
        print "Score: ", gameState.getScore()
   
    def hola(self, gameState):
        array = gameState.getLegalPacmanActions()
        mW=0
        mE=0
        mP=1
        mN=0
        mS=0
        distancias=map(lambda a: 9999 if (a==None) else a, gameState.data.ghostDistances)
        index=distancias.index(min(x for x in distancias if x is not None))
        pacx = gameState.getPacmanPosition()[0]
        pacy = gameState.getPacmanPosition()[1]
        ghox=gameState.getGhostPositions()[index][0]
        ghoy=gameState.getGhostPositions()[index][1]
        move1=Directions.STOP
        move2=Directions.STOP
        if   ( pacx-ghox > 0 ): move1 = Directions.WEST
        if   ( pacx-ghox < 0 ): move1 = Directions.EAST
        if   ( pacy-ghoy < 0 ): move2 = Directions.NORTH
        if   ( pacy-ghoy > 0 ): move2 = Directions.SOUTH
        if ( "West" in array): mW = 1
        if ( "East" in array): mE = 1
        if ( "North" in array): mN = 1
        if ( "South" in array): mS = 1
        GD=min (distancias)
        mensaje = "\t" + str(mW) + "," + str(mP) + "," + str(mE) + "," + str(mN) + "," + str(mS) + "," + str(move1) + "," + str(move2) + "," + str(GD) + "," + str(gameState.getScore()) + "," + str(gameState.data.agentStates[0].getDirection()) + "," + '\n' +'\t'
        return mensaje

    def evaluator(self, gameState):

        distancias=map(lambda a: 9999 if (a==None) else a, gameState.data.ghostDistances)
        d=min(distancias)

        vivos=0
        for i in gameState.getLivingGhosts():
         if(i==True): vivos=vivos+1

        tick=self.countActions

        #almacen=[]
        #almacen[0]=str()
        #almacen[1]=gameState.getLivingGhosts()
        #almacen[2]=self.countActions

        mensaje = str(d) + "," + str(vivos) + "," + str(tick) + "\n"
        return mensaje

    def chooseAction(self, gameState):
        
        self.countActions = self.countActions + 1
        self.printInfo(gameState)
        self.evaluator(gameState)
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        #Se coge las distancias a cada fantasma
        distancias=gameState.data.ghostDistances
        #Se calcula el indice que tiene menor distancia
        index=distancias.index(min(x for x in distancias if x is not None))
        #Se guardan los valores de las coordenadas x, y del Pac-Man
        pacx = gameState.getPacmanPosition()[0]
        pacy = gameState.getPacmanPosition()[1]
        #Se guarda la direccion a la que mira el Pac-Man
        pacdir = gameState.data.agentStates[0].getDirection()
        #Se guarda la posicion x, y del fantasma mas cercano al Pac-Man
        ghox=gameState.getGhostPositions()[index][0]
        ghoy=gameState.getGhostPositions()[index][1]
        
        #Computo para sacar el proximo movimiento del Pac-Man
        if   ( pacx-ghox > 0 ):
         if (Directions.WEST in legal):  move = Directions.WEST

        if   ( pacx-ghox < 0 ):
         if (Directions.EAST in legal):  move = Directions.EAST

        if   ( pacy-ghoy < 0 ):
         if (Directions.NORTH in legal):  move = Directions.NORTH
 
        if   ( pacy-ghoy > 0 ):
         if (Directions.SOUTH in legal):  move = Directions.SOUTH
 
        return move



from learningAgents import ReinforcementAgent
from featureExtractors import *
#QLearningAgent_100330413_100315581
#class Agente1 (ReinforcementAgent, BustersAgent):
class Agente1 (BustersAgent):

    def __init__(self, index = 0, inference = "ExactInference", ghostAgents = None):
        #ReinforcementAgent.__init__(self, None, 100, 0.5, 0.5, 1)
        BustersAgent.__init__(self, index, inference, ghostAgents)
                
        self.countActions = 0

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0
        self.lastState = None
        self.actions = {"North":0, "East":1, "South":2, "West":3, "Stop":4}
        self.table_file = open("qtable.txt", "r+")
        self.q_table = self.readQtable()
        self.epsilon = 0.05
        self.alpha = 0.2
        self.gamma = 0.5
        self.state = gameState
        self.previousState = gameState
        self.currentAction = random.choice(gameState.getLegalActions())
        self.living = gameState.getLivingGhosts()

    def readQtable(self):
        "Read qtable from disc"
        table = self.table_file.readlines()
        q_table = []

        for i, line in enumerate(table):
            row = line.split()
            row = [float(x) for x in row]
            q_table.append(row)

        return q_table

    def writeQtable(self):
        "Write qtable to disc"
        self.table_file.seek(0)
        self.table_file.truncate()

        for line in self.q_table:
            for item in line:
                self.table_file.write(str(item)+" ")
            self.table_file.write("\n")

    def __del__(self):
        "Destructor. Invokation at the end of each episode"
        print "dest"
        self.writeQtable()
        self.table_file.close()

    def computePosition(self, gameState):
        """
        Compute the row of the qtable for a given state.
        For instance, the state (3,1) is the row 7
        """
        array = gameState.getLegalPacmanActions()
        distancias=map(lambda a: 9999 if (a==None) else a, gameState.data.ghostDistances)
        index=distancias.index(min(x for x in distancias if x is not None))
        pacx = gameState.getPacmanPosition()[0]
        pacy = gameState.getPacmanPosition()[1]
        ghox=gameState.getGhostPositions()[index][0]
        ghoy=gameState.getGhostPositions()[index][1]
        move1=Directions.STOP
        move2=Directions.STOP
        if   ( pacx-ghox > 0 ): move1 = Directions.WEST
        if   ( pacx-ghox < 0 ): move1 = Directions.EAST
        if   ( pacy-ghoy < 0 ): move2 = Directions.NORTH
        if   ( pacy-ghoy > 0 ): move2 = Directions.SOUTH
        GDMin=min(distancias)
		
        #print "Posicion " + str(move1) + " " + str(move2) + " " + str(GDMin)
		
        if(move1=="Stop" and move2=="North"): 
         return ((GDMin)-1)
        if(move1=="East" and move2=="North"): 
         return ((GDMin*2)-1)
        if(move1=="East" and move2=="Stop"):  
         return ((GDMin*3)-1)
        if(move1=="East" and move2=="South"): 
         return ((GDMin*4)-1)
        if(move1=="Stop" and move2=="South"): 
         return ((GDMin*5)-1)
        if(move1=="West" and move2=="South"): 
         return ((GDMin*6)-1)
        if(move1=="West" and move2=="Stop"):  
         return ((GDMin*7)-1)
        if(move1=="West" and move2=="North"): 
         return ((GDMin*8)-1)
        
    def getQValue(self, gameState, action):

        """
        Returns Q(state,action)
        Should return 0.0 if we have never seen a state
        or the Q node value otherwise
        """
        
        position = self.computePosition(gameState)
        action_column = self.actions[action]
        print "Positio2m: " + str(position) + " Coo2l: " + str(action_column)        	

        return self.q_table[position][action_column]

    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        #print str(state)
     	legalActions = state.getLegalActions(0)
        if len(legalActions)==0:
          return 0
        return max(self.q_table[self.computePosition(state)])

    def computeActionFromQValues(self, gameState):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
       
        legalActions = gameState.getLegalPacmanActions()
        if len(legalActions)==0:
          return None

        best_actions = [legalActions[0]]
        best_value = self.getQValue(gameState, legalActions[0])
        for action in legalActions:
            value = self.getQValue(gameState, action)
            if value == best_value:
                best_actions.append(action)
            if value > best_value:
                best_actions = [action]
                best_value = value
        print str(best_actions) + " " + str(best_value) + "\n"
        return random.choice(best_actions)

    def getAction(self, gameState):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
        """
        legalActions = gameState.getLegalPacmanActions()
        print "aaaa: " + str(legalActions)
        action = None
        if len(legalActions) == 0:
             return action
			 
        action=self.getPolicy(gameState)

        print "Primero"
	if (self.countActions == 1):
         self.state = gameState
         self.currentAction = self.getPolicy(gameState)

        self.previousState = self.state
        self.currentAction = self.getPolicy(self.previousState)
        self.state = gameState
         
        #print "holaaaaa" + str(self.previousState) + str(self.currentAction)+ str(self.state)
		
        #print "Voy a pasar a update: " + str(gameState) + str(action)
        #nextState
        #reward
       
        #print "Hi: " + str(gameState) + " EY" + str(action)
        
        reward=0

        distancias = []
        distancias1 = []
        minNext = 0
        minD1 = 0

        for i in range (0,len(gameState.getLivingGhosts())-1):
         distancias.append(self.distancer.getDistance(gameState.getGhostPositions()[i],gameState.getPacmanPosition()))
        minNext = min (distancias)

        for i in range (0,len(self.previousState.getLivingGhosts())-1):
         distancias1.append(self.distancer.getDistance(self.previousState.getGhostPositions()[i],self.previousState.getPacmanPosition()))
        minD1 = min (distancias1)

        print "minD: " + str(minNext) + "mindD1: " + str(minD1)

        if (minNext < minD1): reward = 1 
        elif (minNext > minD1): reward = -1
        else: reward =0      
        
		

        self.update(self.previousState, self.currentAction, gameState, reward);
		
	
		
        flip = util.flipCoin(self.epsilon)

        if flip:
         return random.choice(legalActions)
        print str(self.getPolicy(self.state))
        return self.getPolicy(self.state)
        
    def setQValue(self,state,action,value):
        position = self.computePosition(state)
        action_column = self.actions[action]
        print "Positiom: " + str(position) + " Cool: " + str(action_column)
        self.q_table[position][action_column]= value

    def update(self, state, action, nextState, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here

          Good Terminal state -> reward 1
          Bad Terminal state -> reward -1
          Otherwise -> reward 0

          Q-Learning update:

          if terminal_state:
           Q(state,action) <- (1-self.alpha) Q(state,action) + self.alpha * (r + 0)
          else:
           Q(state,action) <- (1-self.alpha) Q(state,action) + self.alpha * (r + self.discount * max a' Q(nextState, a'))

        """
        "*** YOUR CODE HERE ***"
        print "Update en proceso:"
        print str(reward)
        if reward==1 or reward==-1:
         new_value = (1 - self.alpha) * self.getQValue(state,action) + self.alpha * (reward + 0)
        else:
         new_value = (1 - self.alpha) * self.getQValue(state,action) + self.alpha * (reward + self.gamma * self.getValue(nextState))
        print str(new_value)        
        self.setQValue(state,action,new_value)

    def getPolicy(self, gameState):
	"Return the best action in the qtable for a given state"
        return self.computeActionFromQValues(gameState)

    def getValue(self, state):
	"Return the highest q value for a given state"
        return self.computeValueFromQValues(state)
