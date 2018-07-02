from game import Game
import argparse
from entity import Entity, PlayerEntity, AIGuide, AILearningGuide
import numpy as np
import ipywidgets as widgets
from IPython.display import clear_output
from math import ceil
import time

import pickle
def save_obj(obj, name):
    with open('../../obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open('../../obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

sizes = {'SMALL':(9,9,4), 'MEDIUM':(20,25,10), 'BIG':(40,60,25)}
gameEntities = []
playerEntities = []
route = [1e6,[]]
h = 20
w = 25

def loadLevel(level):
    global playerEntities
    global gameEntities
    global h
    global w
    playerEntities = level[0]
    gameEntities = level[1]
    if len(gameEntities) == 4:
        h = 9
        w = 9
    elif len(gameEntities) == 10:
        h = 20
        w = 25
    else:
        h = 40
        w = 60

ticks = []
class LearnManager():
    def __init__(self, Q0 = {}, iterations = 1000, eps = 0, gam = .5, lr = 0.33, sleepTime = 0.005, disp = False, idle = (10,0)):
        self.showDisp = disp
        self.sleepTime = sleepTime
        self.startIterations = iterations
        self.iterations = iterations
        self.Q = Q0
        self.eps = eps
        self.latestTicks = 0
        
        if self.showDisp:
            if self.eps == 0:
                e = 0
            elif self.eps < 0 or self.eps > 1:
                e = 1./(self.startIterations+2-self.iterations)
            else:
                e = self.eps
            self.sGame = SimGame(entities=gameEntities, updateTime = self.sleepTime, pEntities=playerEntities,aiguide=True, learning_rate = lr, gamma = gam,
                             decisionLog = False, guideSleepTime = 13, Q0 = self.Q, eps = e, lm = self, disp = self.showDisp, idle = idle)
        else:  
            while self.iterations > 0:
                if self.eps == 0:
                    e = 0
                elif self.eps < 0 or self.eps > 1:
                    e = 1./(self.startIterations+2-self.iterations)
                else:
                    e = self.eps
                self.sGame = SimGame(entities=gameEntities, updateTime = self.sleepTime, pEntities=playerEntities,aiguide=True, learning_rate = lr, gamma = gam,
                                 decisionLog = False, guideSleepTime = 13, Q0 = self.Q, eps = e, lm = self, disp = self.showDisp, idle = idle)
                self.Q = self.sGame.guide.Q
                self.iterations -= 1
                ticks.append(self.sGame.state['score'])
                self.latestTicks = self.sGame.state['score']
                del self.sGame

CELL_SIZE = 24
rots = [(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]

class SimGame(Game):
    def __init__(self, updateTime = 0.1, entities=None, pEntities=None, learning_rate = .33, gamma = .5,
                 aiguide = True, decisionLog = False, guideSleepTime = 10, 
                 Q0 = {}, eps = 0.01, lm = None, disp = True, idle = (10,0)):
        self.hasGuide = False
        if aiguide:
            self.hasGuide = aiguide
            self.guide = AILearningGuide(eps = eps, gamma = gamma, lr = learning_rate, sleepTime = guideSleepTime, Qtable = Q0)
            self.guideActionReport = [['SLEEP',[5]],'PROGRESS']
            self.goals = []
            self.oldState = 'start'
            self.reward = 0
            self.lastAction = (0,0)
            self.lm = lm
        self.log = decisionLog
        self.board = None
        self.gameEntities = []
        self.playerEntities = []
        self.playerActionReports = []
    
        self.boardHeight = h
        self.boardWidth = w
        self.boardVisits = np.zeros((self.boardHeight,self.boardWidth))
        self.state = {'ticks': 0, 'score': 0}
        
        if entities != None:
            for e in entities:
                self.gameEntities.append(Entity(e))
            if aiguide:
                for e in self.gameEntities:
                    if e.entityType == 'GOAL':
                        self.goals.append(e)
                
        if pEntities != None:        
            for p in pEntities:
                self.playerEntities.append(PlayerEntity(p, idleChoices = [(['LOOK_AROUND', [1]],idle[0]),(['WALK_FORWARD', [1]],idle[1])]))
                self.boardVisits[p['row'],p['col']] += 1
                self.playerActionReports.append([['IDLE',[]],'OK'])
        
        Game.__init__(self, showDisplay=disp, updateTime = updateTime)

    def entitiesInCell(self,row,col):
        entities = []
        for e in self.gameEntities:
            if e.position[0]==row and e.position[1]==col:
                entities.append(e)
            elif e.position[0]<=row and e.position[0]+e.size>row and e.position[1]<=col and e.position[1]+e.size>col:
                entities.append(e)
        for p in self.playerEntities:
            if p.position[0]==row and p.position[1]==col:
                entities.append(p)
            elif p.position[0]<=row and p.position[0]+p.size>row and p.position[1]<=col and p.position[1]+p.size>col:
                entities.append(p)
        return entities
    
    def cellsSeenByPlayer(self, player):
        cells = [(player.position[0],player.position[1])]
        if player.rotation % 2 != 0:
            for i in range(1,player.vision+1):
                cells.append((player.position[0] + i * rots[player.rotation][0],
                              player.position[1] + i * rots[player.rotation][1]))
                for j in range(1,i):
                    cells.append((player.position[0] + i * rots[player.rotation][0],
                                  player.position[1] + j * rots[player.rotation][1]))
                    cells.append((player.position[0] + j * rots[player.rotation][0],
                                  player.position[1] + i * rots[player.rotation][1]))
        else:
            auxRot = (player.rotation + 2) % 8
            for i in range(0,player.vision):
                for j in range(-i,i+1):
                    cells.append((player.position[0] + (i+1) * rots[player.rotation][0] + j * rots[auxRot][0],
                                  player.position[1] + (i+1) * rots[player.rotation][1] + j * rots[auxRot][1]))
        return cells
    
    def entitiesSeenByPlayer(self, player):
        cellsSeen = self.cellsSeenByPlayer(player)
        entitiesSeen = []
        for c in cellsSeen:
            entities = self.entitiesInCell(c[0],c[1])
            for e in entities:
                entitiesSeen.append(e)
        return entitiesSeen

    def getCell(self,row,col):
        cellsSeen = []
        for p in self.playerEntities:
            cellsSeen += self.cellsSeenByPlayer(p)
            
        entities = self.entitiesInCell(row,col)
        if len(entities) > 0:
            entity = entities[0]
            if entity!=None:
                if entity.entityType == 'PICKABLE_OBJECT':
                    cellBackground = '#ff0000'
                elif entity.entityType == 'GOAL':
                    cellBackground = '#ff69b4'
                else: cellBackground = '#ff9900'
        elif (row,col) in cellsSeen:
            cellBackground = '#00ff00'
        else:
            g = hex(int(255*(1-1/(1+(1+self.boardVisits[row,col])*0.33))))
            color = "#33" + str(g)[2:4] + "33"
            cellBackground = color
        return '<td id="%04d" style="width:%dpx;height:%dpx;background:%s;"> </td>' % (row*100+col,CELL_SIZE,CELL_SIZE,cellBackground)

    def buildBoardView(self):
        board = '<table style="background:#000;border-collapse:separate;border-spacing:0px">'
        for row in range(self.boardHeight):
            board += '<tr>'
            for col in range(self.boardWidth):
                board += self.getCell(row,col)
            board += '</tr>'
        board += '</table>'
        return board

    def setBoardView(self):
        self.boardView = widgets.HTML(value=self.buildBoardView(),disabled=False)
        return self.boardView

    def setStateView(self):
        ticks = widgets.Label(value="0000")
        score = widgets.Label(value="%04d" % self.state['score'])
        self.stateView = {'ticks': ticks, 'score': score}
        return widgets.HBox([widgets.VBox([widgets.Label(value="Ticks"),
                                           widgets.Label(value="Score")]),
                                    widgets.VBox([widgets.Label(value=": "),
                                                  widgets.Label(value=": ")]),
                                    widgets.VBox([ticks,score])])

    def setActionButtons(self):
        buttons = '<span>'
        return widgets.HTML(value=buttons,disabled=False)

    def gameStep(self):
        self.executionManager()
        self.state['ticks'] += 1
        if self.display:
            self.stateView['ticks'].value = "%04d" % self.state['ticks']
            self.stateView['score'].value = "%04d" % self.state['score']
            self.boardView.value = self.buildBoardView()
        return False

    def executionManager(self):
        if self.gameStatus != 2:
            for i in range(len(self.playerEntities)):
                p = self.playerEntities[i]
                report = self.playerActionReports[i]
                etitiesSeen = self.entitiesSeenByPlayer(p)

                action = p.chooseAction(etitiesSeen, report)
                if action[0] == 'LOOK_AROUND':
                    p.rotation = (p.rotation + action[1][0]) % 8
                    self.playerActionReports[i] = [action,'OK']

                if action[0] == 'WALK_FORWARD':
                    desiredPosition = p.position + rots[p.rotation]
                    if min(desiredPosition[0],desiredPosition[1]) >= 0 and desiredPosition[0] < self.boardHeight -1 and desiredPosition[1] < self.boardWidth-1:
                        p.position = desiredPosition
                        self.playerActionReports[i] = [action,'OK']
                        self.boardVisits[p.position[0],p.position[1]] += 1
                    else:
                        self.playerActionReports[i] = [action,'INTERRUPTED']

                elif action[0] == 'WALK_TOWARDS':
                    goal = action[1][0]
                    dif = goal - p.position
                    x = np.sign(dif[0])
                    y = np.sign(dif[1])
                    if p.distanceToPos(goal) == 1:
                        self.playerActionReports[i] = [action,'OK']
                    else:
                        self.playerActionReports[i] = [action,'PROGRESS']
                    if p.distanceToPos(goal) > 0: p.rotation = rots.index((x,y))
                    p.position += np.array([x,y])
                    self.boardVisits[p.position[0],p.position[1]] += 1

                elif action[0] == 'PICK_UP':
                    es = self.entitiesInCell(p.position[0],p.position[1])
                    found = False
                    if len(es)>0:
                        for e in es:
                            if e != None and e.entityType == 'PICKABLE_OBJECT':
                                self.gameEntities.remove(e)
                                found = True
                    if found:
                        self.playerActionReports[i] = [action,'OK']
                    else: self.playerActionReports[i] = [action,'INTERRUPTED']
            if self.log: print(self.playerActionReports)

            if self.hasGuide:
                p = self.playerEntities[0]
                self.goals = sorted(self.goals, key=lambda g: p.distanceToPos(g.position))
                if len(self.goals) > 0 and p.distanceToPos(self.goals[0].position) == 0:
                    self.reward = 1.
                    self.gameEntities.remove(self.goals[0])
                    self.goals.remove(self.goals[0])
                if len(self.goals) > 0:
                    g = self.goals[0]
                    state = (g.position[0]-p.position[0],g.position[1]-p.position[1])
                else: 
                    state = 'terminal'
                guideAction = self.guide.chooseAction(self.guideActionReport,state)
                if guideAction[0] == 'SLEEP':
                    guideAction[1][0] -= 1
                    if guideAction[1][0] == 0: 
                        self.guideActionReport = [guideAction,'OK']
                        #learn
                        if self.oldState != 'start':
                            self.guide.learn(self.oldState,self.lastAction,self.reward,state)
                            self.oldState = state
                            self.reward = -0.01
                            if state == 'terminal':
                                self.stopGame()
                        else:
                            self.oldState = state
                    else: self.guideActionReport = [guideAction,'PROGRESS']
                if guideAction[0] == 'SPAWN_OBJECT':
                    newObject = {'type': 'PICKABLE_OBJECT', 'row': 0, 'col': 0, 'size': 1, 'id': 1, 'rot': 0}
                    if guideAction[1][0] == 'random':
                        newObject['row'] = np.random.randint(0, self.boardHeight)
                        newObject['col'] = np.random.randint(0, self.boardWidth)
                        self.gameEntities.append(Entity(newObject))
                    else:
                        self.state['score'] += 1
                        self.lastAction = guideAction[1][0]
                        rot = self.lastAction[0]
                        dist = self.lastAction[1]
                        r = p.position[0] + dist * rots[rot][0]
                        c = p.position[1] + dist * rots[rot][1]
                        if r in range(0, self.boardHeight) and c in range(0, self.boardWidth):
                            newObject['row'] = r
                            newObject['col'] = c
                            self.gameEntities.append(Entity(newObject))
                    self.guideActionReport = [['SLEEP',[self.guide.sleepTime]],'PROGRESS']
        return

def main(exp, gam, lr, DATFILE):
    best_ticks = []
    levels = []
    personalities = [(10,0),(9,1),(8,2),(7,3)]
    levels = load_obj("Levels")

    loadLevel(levels[1])
    for i in range(len(personalities)):
        iterations = 300
        Q = {}
        LM = LearnManager(Q0 = Q, iterations = iterations, eps = exp, gam = gam, lr = lr, disp = False, idle = personalities[i])
        test = []
        for _ in range(10):
            LM = LearnManager(Q0 = Q, iterations = iterations, eps = 0, gam = gam, lr = lr, disp = False, idle = personalities[i])
            test.append(LM.latestTicks)
        best_ticks.append(min(test))

    with open(DATFILE, 'w') as f:
        f.write(str(sum(best_ticks)))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description='Feature Selection using GA with DecisionTreeClassifier')
    ap.add_argument('--exp', dest='exp', type=float, required=True, help='Exploration rate')
    ap.add_argument('--gam', dest='gam', type=float, required=True, help='Gamma value')
    ap.add_argument('--lr', dest='lr', type=float, required=True, help='Learning rate')
    ap.add_argument('--datfile', dest='datfile', type=str, required=True, help='File where it will be save the score (result)')

    args = ap.parse_args()

    main(args.exp, args.gam, args.lr, args.datfile)


