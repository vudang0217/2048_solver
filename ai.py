from __future__ import absolute_import, division, print_function
import pygame
import sys
import time
import math
import random
from pygame.locals import *
import copy
import random


MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}

MAX = 1  # indictor for max player
CHANCE = 0  # indicator for chance player


class Node:
    def __init__(self, gs, s, c, pt):
        self.gameState = gs  # matrix of current state (2D)
        self.theScore = s  # score of the current state
        self.children = c  # list containing the children of the node
        self.playerType = pt  # type of player (MAX/CHANCE)
        # indicate which initial step was taken (for compute_decision)
        self.whereGo = -1
        self.expectiVal = 0  # this is to store the expectimax value


class Gametree:
    """main class for the AI"""
    # Hint: Two operations are important. Grow a game tree, and then compute minimax score.
    # Hint: To grow a tree, you need to simulate the game one step.
    # Hint: Think about the difference between your move and the computer's move.

    def __init__(self, root_state, depth_of_tree, current_score):

        # root player is the max player -- depth 0
        self.root = Node(root_state, current_score, [], MAX)

    def buildTree(self):

        # self.printMatrix(self.root) -- for debug

        for d in range(4):
            matrix = copy.deepcopy(self.root.gameState)  # deep copy of matrix

            chance1 = Node(matrix, self.root.theScore,
                           [], CHANCE)  # child of root

            chance1.whereGo = d

            # instance of simulator to move the tiles and change score
            sim1 = Simulator(chance1)
            sim1.move(d)

            # check if the children node is the same a root, don't do anything if it is
            if chance1.gameState != self.root.gameState:
                self.root.children.append(chance1)
                '''#print for debug
				print("Chance node created : ", d)
				self.printMatrix(chance1.gameState)
				print("Score : ", chance1.theScore)'''
            # else :
                #print("Choice eliminate because identical : ", d)

        # constructing the third second layer of the tree, this is the chance's nodes' children -- the max nodes
        # Chance player turn -- producing max nodes (depth 1)
        for c in self.root.children:
            # self.printMatrix(c.gameState)

            # nested for loop loops through each empty tile and place a 2 there and create a new state node
            # for each 2-tile placed
            for j in range(4):
                for i in range(4):
                    if c.gameState[i][j] == 0:
                        matrix = copy.deepcopy(c.gameState)
                        max2 = Node(matrix, c.theScore, [], MAX)
                        max2.gameState[i][j] = 2
                        c.children.append(max2)
                        '''#print for debug
						print("Max2 node created:", i, j)
						self.printMatrix(max2.gameState)'''

                        # creates the terminal/leaf nodes/final layer of the tree. These are treated as the MAX node
                        # but it wouldn't matter in expectimax since its leaf
                        # Max player turn #2 -- producing leaf nodes(depth 2) -- for each direction
                        for d2 in range(4):
                            matrix = copy.deepcopy(max2.gameState)
                            leaf = Node(matrix, max2.theScore, [], MAX)
                            #leaf.whereGo = d
                            sim2 = Simulator(leaf)
                            sim2.move(d2)

                            # condition to check if leaf nodes are identical to their parent
                            if max2.gameState != leaf.gameState:
                                max2.children.append(leaf)
                                # print for debug
                                '''print("Leaf node created:", d2)
								self.printMatrix(leaf.gameState)
								print("Score : ", leaf.theScore)'''

    # Method prints the game grid on the terminal for debugging purposes
    def printMatrix(self, state):
        for j in range(4):
            for i in range(4):
                print((state.gameState)[i][j], "**", end=" ")
            print()
        print("Score : ", state.theScore)

    # expectimax for computing best move
    # state is a NODE
    def expectimax(self, state):

        # for the case that node is leaf
        if len(state.children) == 0:

            # "payoff" function returns score
            return state.theScore

        # for the case that node the max player
        elif state.playerType == MAX:
            value = -1
            for n in state.children:
                # algorithm given in class
                value = max(value, self.expectimax(n))
            state.expectiVal = value  # record expectimax value to node
            return value

        # for the case that node is the chance player
        elif state.playerType == CHANCE:
            value = 0
            prob = 1/(len(state.children))
            for n in state.children:
                value = value + self.expectimax(n)*prob  # compute the average
            state.expectiVal = value
            return value

        else:
            return -1  # -1 indicating error -- never the case

    # function to return best decision to game

    def compute_decision(self):
        # change this return value when you have implemented the function

        # build the tree to make next decision
        self.buildTree()
        val = self.expectimax(self.root)  # set the expectimax value

        # search for matching value in the root's children
        for i in range(len(self.root.children)):

            if self.root.children[i].expectiVal >= val:
                # print("expectimax move",self.root.children[i].whereGo , "value is ", self.root.children[i].expectiVal)
                return self.root.children[i].whereGo  # return the decision


class Simulator:

    def __init__(self, theNode):
        #self.total_points = theNode.theScore
        self.node = theNode
        self.default_tile = 2
        self.board_size = 4
        # pygame.init()
        #self.surface = pygame.display.set_mode((400, 500), 0, 32)
        # pygame.display.set_caption("2048")
        #self.myfont = pygame.font.SysFont("arial", 40)
        #self.scorefont = pygame.font.SysFont("arial", 30)
        self.tileMatrix = theNode.gameState

    # MOVE TILES BASED ON GIVEN DIRECTION
    def move(self, direction):
        # self.addToUndo()
        for i in range(0, direction):
            self.rotateMatrixClockwise()
        if self.canMove():
            self.moveTiles()
            self.mergeTiles()
            # self.placeRandomTile()
        for j in range(0, (4 - direction) % 4):
            self.rotateMatrixClockwise()

    def placeRandomTile(self):
        while True:
            i = random.randint(0, self.board_size-1)
            j = random.randint(0, self.board_size-1)
            if self.tileMatrix[i][j] == 0:
                break
        self.tileMatrix[i][j] = 2

    def moveTiles(self):
        tm = self.tileMatrix
        for i in range(0, self.board_size):
            for j in range(0, self.board_size - 1):
                while tm[i][j] == 0 and sum(tm[i][j:]) > 0:
                    for k in range(j, self.board_size - 1):
                        tm[i][k] = tm[i][k + 1]
                    tm[i][self.board_size - 1] = 0

    def mergeTiles(self):
        tm = self.tileMatrix
        for i in range(0, self.board_size):
            for k in range(0, self.board_size - 1):
                if tm[i][k] == tm[i][k + 1] and tm[i][k] != 0:
                    tm[i][k] = tm[i][k] * 2
                    tm[i][k + 1] = 0
                    self.node.theScore += tm[i][k]
                    self.moveTiles()

    def checkIfCanGo(self):
        tm = self.tileMatrix
        for i in range(0, self.board_size ** 2):
            if tm[int(i / self.board_size)][i % self.board_size] == 0:
                return True
        for i in range(0, self.board_size):
            for j in range(0, self.board_size - 1):
                if tm[i][j] == tm[i][j + 1]:
                    return True
                elif tm[j][i] == tm[j + 1][i]:
                    return True
        return False

    def canMove(self):
        tm = self.tileMatrix
        for i in range(0, self.board_size):
            for j in range(1, self.board_size):
                if tm[i][j-1] == 0 and tm[i][j] > 0:
                    return True
                elif (tm[i][j-1] == tm[i][j]) and tm[i][j-1] != 0:
                    return True
        return False

    def rotateMatrixClockwise(self):
        tm = self.tileMatrix
        for i in range(0, int(self.board_size/2)):
            for k in range(i, self.board_size - i - 1):
                temp1 = tm[i][k]
                temp2 = tm[self.board_size - 1 - k][i]
                temp3 = tm[self.board_size - 1 - i][self.board_size - 1 - k]
                temp4 = tm[k][self.board_size - 1 - i]
                tm[self.board_size - 1 - k][i] = temp1
                tm[self.board_size - 1 - i][self.board_size - 1 - k] = temp2
                tm[k][self.board_size - 1 - i] = temp3
                tm[i][k] = temp4

    def isArrow(self, k):
        return(k == pygame.K_UP or k == pygame.K_DOWN or k == pygame.K_LEFT or k == pygame.K_RIGHT)

    def getRotations(self, k):
        if k == pygame.K_UP:
            return 0
        elif k == pygame.K_DOWN:
            return 2
        elif k == pygame.K_LEFT:
            return 1
        elif k == pygame.K_RIGHT:
            return 3

    def convertToLinearMatrix(self):
        m = []
        for i in range(0, self.board_size ** 2):
            m.append(
                self.tileMatrix[int(i / self.board_size)][i % self.board_size])
        m.append(self.node.theScore)
        return m
