# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import distanceCalculator
from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  # print([eval(first)(firstIndex), eval(second)(secondIndex)])
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.time_count = 0; self.food_count = 0

    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    if self.food_count >= 6:
      return self.fall_back(gameState)
    actions = gameState.getLegalActions(self.index)
    if self.time_count > 0:
      self.time_count -= 1
    values = [self.evaluate(gameState, a) for a in actions]
    maxValue = max(values)
    # print("max value for best action= ",maxValue)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    foodLeft = len(self.getFood(gameState).asList())
    # print ("food left = ",foodLeft)
    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction
    ans = random.choice(bestActions)
    succ = self.getSuccessor(gameState,ans)
    succ_pos = succ.getAgentPosition(self.index)
    rem_food = self.getFood(gameState).asList()
    # print("food list = ", rem_food)
    # if self.index == 1:
    if succ_pos in rem_food:
      self.food_count += 1
    return ans

  def fall_back(self,gameState):
    best_dis = 9999
    ans = Directions.STOP
    actions = gameState.getLegalActions(self.index)
    for elem in actions:
      successor = self.getSuccessor(gameState,elem)
      if self.f1(successor) < 5:
          continue
      pos2 = successor.getAgentState(self.index).getPosition()
      maze_dis = self.getMazeDistance(pos2,self.start)
      if maze_dis < best_dis:
        best_dis = maze_dis
        ans = elem
    successor = self.getSuccessor(gameState, ans) 
    if not successor.getAgentState(self.index).isPacman:
      self.food_count = 0
    return ans

  def f0(self,gameState):
    ans = []
    opp = self.getOpponents(gameState)
    for elem in opp:
      if not gameState.getAgentPosition(elem) == None:
        temp = gameState.getAgentState(elem)
        temp1 = gameState.getAgentPosition(elem)
        ans.append((temp,temp1))
    return ans

  def f1(self,gameState):
    ans = 9999
    pos = gameState.getAgentPosition(self.index)
    opp = self.f0(gameState)
    for state,position in opp:
      temp = self.getMazeDistance(pos,position)
      if temp < ans:
        ans = temp
      if temp == 0:
        return 1000
    return ans

  def f2(self,gameState):
    ans = []
    opp = self.f0(gameState)
    for state,position in opp:
      if state.isPacman and state.getPosition() != None:
        ans.append((state,position))
    return ans

  def getSuccessor(self, gameState, action):
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor


  def evaluate(self, gameState, action):
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  # def getFeatures(self, gameState, action):
  #   features = util.Counter()
  #   successor = self.getSuccessor(gameState, action)
  #   features['successorScore'] = self.getScore(successor)
  #   return features

  # def getWeights(self, gameState, action):
  #   return {'successorScore': 1.0}

class OffensiveReflexAgent(DummyAgent):

  def getFeatures(self, gameState, action):
    # print("offensive index =",self.index)
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList)
    features['capsule'] = 0; features['enemy'] = 0

    if len(foodList) > 0: 
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = 200 - minDistance

    if self.f1(successor) <= 5:
      # features['enemy'] = 0
    # else:
      # features['capsule'] = 0; features['successorScore'] = 0
      features['enemy'] = 200 - self.f1(successor)
      return features
    cap = 0
    all_capsules = self.getCapsules(successor)
    if myPos in all_capsules:
      features['capsule'] = 9999
      self.time_count = 40
    if len(all_capsules) != 0:
      temp = []
      for elem in all_capsules:
        dis = self.getMazeDistance(myPos,elem)
        temp.append(dis)
      cap = min(temp)
      if cap != 0:
        features['capsule'] = 1/cap
    if self.time_count > 0:
      features['distanceToFood'] = 9999
      # features['enemy'] = 0; features['capsule'] = 0
    return features

  def getWeights(self, gameState, action):
    # print("getting offensive weights")
    return {'successorScore': 100, 'distanceToFood': 1.5, 'enemy': -1.5, 'capsule': 1}

class DefensiveReflexAgent(DummyAgent):
  def getFeatures(self, gameState, action):
    # print("defensive index = ",self.index)
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0 
    inv = self.f2(successor)
    features['numInvaders'] = len(inv)
    if len(inv) > 0:
      temp = []
      for state,position in inv:
        dis = self.getMazeDistance(myPos,position)
        temp.append(dis)
      features['invaderDistance'] = min(temp)
    if action == Directions.STOP: 
      features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: 
      features['reverse'] = 1
    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -100, 'stop': -100, 'reverse': -2}


  


