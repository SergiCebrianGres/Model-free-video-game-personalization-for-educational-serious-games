import ipywidgets as widgets
from IPython.display import display
import time
import tools
import numpy as np

# --------------------------------------
# ---
# --------------------------------------
class Entity:
    def __init__(self, entity = None):
        self.entityType = ''
        self.score = 0
        self.position = np.array([0,0])
        self.rotation = 0
        self.size = 1

        if (entity != None):
            if (entity['type'] != None): self.entityType = entity['type']
            if (entity['row'] != None): self.position[0] = entity['row']
            if (entity['col'] != None): self.position[1] = entity['col']
            if (entity['rot'] != None): self.rotation = entity['rot']
            if (entity['size'] != None): self.size = entity['size']
    
class PlayerEntity(Entity):
    def __init__(self, entity = None, idleChoices = [(['LOOK_AROUND', [1]],10),(['WALK_FORWARD', [1]],0)]):
        self.vision = 1
        #self.visited_path = []
        self.idleChoices = idleChoices
        if (entity != None):
            if (entity['vision'] != None): self.vision = entity['vision']
        Entity.__init__(self, entity)
        #self.visited_path.append(self.position)

    
    # Action := ['NAME_ACTION',[parameter1,...]]
    # Action_Report := [Action, 'STATUS']
    # status in ('OK','PROGRESS', 'INTERRUPTED')
    def chooseAction(self,seen,action_report):
        # Wasn't doing anything (initial action for every PlayerEntity)
        if action_report[0][0] == 'IDLE':
            return self.idleDecision(seen)

        elif action_report[0][0] == 'LOOK_AROUND' or action_report[0][0] == 'WALK_FORWARD' :
            return self.idleDecision(seen)

        elif action_report[0][0] == 'WALK_TOWARDS':
            if action_report[1] == 'OK':
                #self.visited_path.append(self.position)
                return self.idleDecision(seen)

            elif action_report[1] == 'PROGRESS':
                #self.visited_path.append(self.position)
                return action_report[0]

            elif action_report[1] == 'INTERRUPTED':
                return self.idleDecision(seen)

        elif action_report[0][0] == 'PICK_UP':
            if action_report[1] == 'OK':
                self.score += 10
                return self.idleDecision(seen)
            return self.idleDecision(seen)


    def distanceToPos(self, pos):
        return max(abs(pos-self.position))

    def objectsSeen(self, seen):
        objectsPositions = []
        for o in seen:
            if o.entityType == 'PICKABLE_OBJECT':
                objectsPositions.append(o.position)
        objectsPositions = sorted(objectsPositions, key=lambda pos: self.distanceToPos(pos))   
        return objectsPositions

    def idleDecision(self, seen):
        candidates_walk = self.objectsSeen(seen)         
        if len(candidates_walk) > 0:
            if all(candidates_walk[0] == self.position):
                return ['PICK_UP',[]]
            return ['WALK_TOWARDS',[candidates_walk[0]]]
        return tools.weighted_choice(self.idleChoices)

class AIGuide():
    def __init__(self, sleepTime = 10):
        self.sleepTime = sleepTime

    def chooseAction(self,action_report):
        if action_report[0][0] == 'SLEEP':
            if action_report[1] == 'PROGRESS':
                return action_report[0]
            elif action_report[1] == 'OK':
                return ['SPAWN_OBJECT',['random']]

class AILearningGuide():
    def __init__(self, eps = 0.1, gamma = 0.5, lr = 0.1, sleepTime = 15, Qtable = {}, maxDist = 3):
        self.orientations = range(8)
        self.maxDist = maxDist + 1
        self.actions = [(i,j) for i in self.orientations for j in range(1,self.maxDist)]
        self.sleepTime = sleepTime
        self.lr = lr
        self.gamma = gamma
        self.epsilon = eps
        self.Q = Qtable

    def chooseAction(self, action_report, state):
        if action_report[0][0] == 'SLEEP':
            if action_report[1] == 'PROGRESS':
                return action_report[0]
            elif action_report[1] == 'OK':
                self.check_state_exists(state)
                if np.random.uniform() < self.epsilon:
                    action = self.actions[np.random.randint(len(self.actions))]
                else:
                    mv = max(self.Q[state].values())
                    aux = [k for (k, v) in self.Q[state].items() if v == mv]
                    action = aux[np.random.randint(len(aux))]
                return ['SPAWN_OBJECT',[action]]

    def learn(self, s, a, r, s_):
        self.check_state_exists(s_)
        self.check_state_exists(s)
        q_predict = self.Q[s][a]
        if s_ != 'terminal':
            q_target = r + self.gamma * max(self.Q[s_].values())
        else:
            q_target = r
        self.Q[s][a] = (1-self.lr) * q_predict + self.lr * q_target

    def check_state_exists(self, state):
        if not state in self.Q.keys():
            self.Q[state] = dict((a,1./(len(self.orientations)*(self.maxDist))) for a in self.actions)
