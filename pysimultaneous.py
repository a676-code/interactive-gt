# pysimultaneous.py
# Author: Andrew W. Lounsbury
# Date: 3/24/24
# Description: a class for handling simultaneous games with n players, n >= 2
from itertools import chain
import numpy as np
from numpy.polynomial import Polynomial
import sympy
from sympy import solve
from sympy.solvers.solveset import linsolve
from sympy import srepr
from sympy import simplify
import warnings

class ListNode:
    head = None
    payoff = -1
    bestResponse = True
    next = None
    
    def __init__(self, payoff = 0, bestResponse = True):
        self.head = self
        self.payoff = payoff
        self.bestResponse = False
        self.next = None
        return

    def append(self, payoff, bestResponse):
        """Appends a new node to the end of the linked list

        Args:
            payoff (float): the payoff
            bestResponse (bool): whether the payoff is a best response or not
        """
        newNode = ListNode(payoff, bestResponse)
        if self.head is None:
            self.head = newNode
            return
        
        curNode = self.head
        while curNode.next:
            curNode = curNode.next
        
        curNode.next = newNode
        return
        
    def getListNode(self, index):
        """Gets the index-th node in the linked list

        Args:
            index (int): the desired index

        Returns:
            ListNode: the desired node
        """
        if self.head == None:
            return
 
        curNode = self.head
        pos = 0
        if pos == index:
            return curNode
        else:
            while(curNode != None and pos != index):
                pos = pos + 1
                curNode = curNode.next
 
            if curNode != None:
                return curNode
            else:
                print("Index not present")
        return

    def insertAtBeginning(self, payoff, bestResponse):
        newNode = ListNode(payoff, bestResponse)
        if self.head is None:
            self.head = newNode
            return
        else:
            newNode.next = self.head
            self.head = newNode
        return
            
    def insertAtIndex(self, data, index):
        newNode = ListNode(data)
        curNode = self.head
        pos = 0
        if pos == index:
            self.insertAtBeginning(data)
        else:
            while curNode != None and pos != index:
                pos = pos + 1
                curNode = curNode.next
 
            if curNode != None:
                newNode.next = curNode.next
                curNode.next = newNode
            else:
                print("Index not present")
        return
        
    def pop(self):
        """Removes the last node from the linked list
        """
        if self.head is None:
            return
    
        curNode = self.head
        while(curNode.next.next):
            curNode = curNode.next
    
        curNode.next = None
        return
                
    def print(self):
        curNode = self.head
        size = self.size()
        x = 0
        while(curNode):
            if x < size - 1:
                print(curNode.payoff, end=", ")
            else:
                print(curNode.payoff, end=" ")
            curNode = curNode.next
            x += 1
        return
    
    def printBestResponse(self):
        curNode = self.head
        size = self.size()
        x = 0
        while(curNode):
            if x < size - 1:
                print(int(curNode.bestResponse), end=", ")
            else:
                print(int(curNode.bestResponse), end=" ")
            curNode = curNode.next
            x += 1
        return
            
    def printListNode(self, end=""):
        print(self.payoff, end="")
        return
    
    def removeAtIndex(self, index):
        if self.head == None:
            return
 
        curNode = self.head
        pos = 0
        if pos == index:
            self.remove_first_node()
        else:
            while(curNode != None and pos != index):
                pos = pos + 1
                curNode = curNode.next
 
            if curNode != None:
                curNode.next = curNode.next.next
            else:
                print("Index not present")
        return
                
    def decapitate(self):
        """Removes the head ListNode
        """
        if self.head == None:
            return
        
        self.head = self.head.next
        return
    
    def size(self):
        size = 0
        if(self.head):
            current_node = self.head
            while(current_node):
                size = size + 1
                current_node = current_node.next
            return size
        else:
            return 0
        
    def updateListNode(self, val, index):
        curNode = self.head
        pos = 0
        if pos == index:
            curNode.payoff = val
        else:
            while curNode != None and pos != index:
                pos = pos + 1
                curNode = curNode.next
    
            if curNode != None:
                curNode.payoff = val
            else:
                print("Index not present")
        return

class Player:
    numStrats = -1
    rationality = -1
    
    def __init__(self,numStrats = 2, rationality = 0):
        self.numStrats = numStrats
        self.rationality = rationality

class SimGame:    
    kMatrix = []
    kOutcomes = [] # n-tuples that appear in kMatrix; won't be all of them
    kStrategies = [[] for r in range(4)] # 2D matrix containing the strategies each player would play for k-levels 0, 1, 2, 3
    maxRationality = 4
    mixedEquilibria = []
    numPlayers = -1
    outcomeProbabilities = [] # probability of each outcome in kMatrix stored in kOutcomes; P(s_i, s_j)
    payoffMatrix = []
    players = []
    pureEquilibria = []
    rationalityProbabilities = [0.0 for i in range(4)] # probability a player is L_i, i = 0, 1, 2, 3
    strategyNames = []
    
    def __init__(self, numPlayers = 2):
        numStrats = [2 for i in range(numPlayers)]
        rationalities = [0 for i in range(numPlayers)]
        self.players = [Player(numStrats[i], rationalities[0]) for i in range(numPlayers)]
        
        # Creating kStrategies' 4 arrays of lists of size numPlayers and setting rationalityProbabilities
        for r in range(4):
            # resizing self.kStrategies[r]
            if numPlayers > len(self.kStrategies[r]):
                self.kStrategies[r] += [None] * (numPlayers - len(self.kStrategies[r]))
            else:
                self.kStrategies[r] = self.kStrategies[r][:numPlayers]
            self.rationalityProbabilities[r] = 0.0
        
        # Initializing strategy names
        if self.players[0].numStrats < 3:
            self.strategyNames.append(["U", "D"])
        else:
            if self.players[0].numStrats == 3:
                middle = ["M"]
            else: # > 3
                middle = ["M" + str(i) for i in range(1, self.players[0].numStrats - 1)]
            self.strategyNames.append(["U"] + middle + ["D"])
        if self.players[1].numStrats < 3:
            self.strategyNames.append(["L", "R"])
        else:
            if self.players[1].numStrats == 3:
                center = ["C"]
            else: # > 3
                center = ["C" + str(j) for j in range(1, self.players[1].numStrats - 1)]
            self.strategyNames.append(["L"] + center + ["R"])
        if self.numPlayers > 2:
            for x in range(2, self.numPlayers):
                if self.players[x].numStrats < 3:
                    self.strategyNames.append(["L(" + str(x) + ")", "R(" + str(x) + ")"])
                else: 
                    self.strategyNames.append(["L(" + str(x) + ")"] + ["C(" + str(x) + ", " + str(s) + ")" for s in range(self.players[x].numStrats)] + ["R(" + str(x) + ")"])
        
        self.numPlayers = numPlayers
        
        # Creating the payoff matrix
        self.payoffMatrix = []
        if self.numPlayers < 3:
            matrix = []
            for i in range(self.players[0].numStrats):
                row = []
                for j in range(self.players[1].numStrats):
                    outcome = ListNode()
                    outcome.append(0, True)
                    row.append(outcome)                        
                matrix.append(row)
            self.payoffMatrix.append(matrix)
        else:
            numMatrices = 1
            for x in range(2, self.numPlayers):
                numMatrices *= self.players[x].numStrats
            for m in range(numMatrices):
                matrix = []
                for i in range(self.players[0].numStrats):
                    row = []
                    for j in range(self.players[1].numStrats):
                        outcome = ListNode()
                        for x in range(1, self.numPlayers):
                            outcome.append(0, True)
                        row.append(outcome)                 
                    matrix.append(row)
                self.payoffMatrix.append(matrix)
        return
    
    def computeBestResponses(self):
        for x in range(self.numPlayers):
            if x == 0:
                for m in range(len(self.payoffMatrix)):
                    for j in range(self.players[1].numStrats):
                        maxValue = -1000000
                        # finding the max value
                        for i in range(self.players[0].numStrats):
                            curList = self.payoffMatrix[m][i][j]
                            if curList.getListNode(0).payoff > maxValue:
                                maxValue = curList.getListNode(0).payoff
                        # comparing the payoffs to the max value
                        for i in range(self.players[0].numStrats):
                            curList = self.payoffMatrix[m][i][j]
                            if curList.getListNode(0).payoff == maxValue: # don't need >= because it's the max
                                curList.getListNode(0).bestResponse = True
                            else:
                                curList.getListNode(0).bestResponse = False
            elif x == 1:
                for m in range(len(self.payoffMatrix)):
                    for i in range(self.players[0].numStrats):
                        maxValue = -1000000
                        # finding the max value
                        for j in range(self.players[1].numStrats):
                            curList = self.payoffMatrix[m][i][j]
                            if curList.getListNode(1).payoff > maxValue:
                                maxValue = curList.getListNode(1).payoff
                        # comparing the payoffs to the max value
                        for j in range(self.players[1].numStrats):
                            curList = self.payoffMatrix[m][i][j]
                            if curList.getListNode(1).payoff == maxValue:
                                curList.getListNode(1).bestResponse = True
                            else:
                                curList.getListNode(1).bestResponse = False
            else: # x > 1
                m = 0
                product = 1
                profile = [0 for x in range(self.numPlayers)]
                while m < len(self.payoffMatrix):
                    profile = self.toProfile(m)
                    for i in range(self.players[0].numStrats):
                        for j in range(self.players[1].numStrats):
                            maxValue = -1000000
                            
                            # Comparing player x's strategies with each other, keeping player x's strategy the same, so we vary over player x's strategies (?)
                            
                            # FIXME?
                            # finding maxValue
                            profile[x] = 0
                            while profile[x] < self.players[x].numStrats:
                                curList = self.payoffMatrix[self.toIndex(profile)][i][j]
                                if curList.getListNode(x).payoff > maxValue:
                                    maxValue = curList.getListNode(x).payoff
                                profile[x] += 1
                            
                            # check through ij-entries in each section
                            profile[x] = 0
                            while profile[x] < self.players[x].numStrats:
                                curList = self.payoffMatrix[self.toIndex(profile)][i][j]
                                if curList.getListNode(x).payoff == maxValue:
                                    curList.getListNode(x).bestResponse = True        
                                else:        
                                    curList.getListNode(x).bestResponse = False
                                profile[x] += 1
                    # move to the next m
                    if x > 2 and x < self.numPlayers - 1 and product == 1:
                        for y in range(2, x):
                            product *= self.players[y].numStrats
                    m += product
                return
    
    def computeBestResponses2(self):
        if self.numPlayers < 3:
            for i in range(self.players[0].numStrats):
                for j in range(self.players[1].numStrats):
                    br = self.isBestResponse([i, j])
                    for x in range(self.numPlayers):
                        self.payoffMatrix[0][i][j].getListNode(x).bestResponse = br[x]
        else: 
            for m in range(len(self.payoffMatrix)):
                for i in range(self.players[0].numStrats):
                    for j in range(self.players[1].numStrats):
                        br = self.isBestResponse([i, j] + self.toProfile(m)[2:])
                        for x in range(self.numPlayers):
                            self.payoffMatrix[m][i][j].getListNode(x).bestResponse = br[x]

    def computeEquilibria(self):
        equilibria = self.computePureEquilibria() + self.computeMixedEquilibria()
        numEquilibria = len(equilibria)
        if numEquilibria % 2 == 0:
            warnings.warn(f"An even number ({numEquilibria}) of equilibria was returned. This indicates that the game is degenerate. Consider using another algorithm to investigate.", RuntimeWarning)
        return equilibria

    def computeMixedEquilibria(self):       
        if self.numPlayers < 3:
            pVars = []
            for i in range(self.players[0].numStrats - 1):
                pVars.append(sympy.symbols('p_' + str(i)))
            qVars = []
            for j in range(self.players[1].numStrats - 1):
                qVars.append(sympy.symbols('q_' + str(j)))
            # Getting the coefficients for the polynomials, EU_1_coefs[n] is the set of coefficients for the n-th polynomial
            EU_1_coefs = []
            EU_2_coefs = []
            for i in range(self.players[0].numStrats):
                EU_1_coefs.append([self.payoffMatrix[0][i][j].getListNode(0).payoff for j in range(self.players[1].numStrats)])
            for j in range(self.players[0].numStrats):
                EU_2_coefs.append([self.payoffMatrix[0][i][j].getListNode(1).payoff for i in range(self.players[0].numStrats)])
            
            # Building polynomials for player 1
            polynomials1 = []
            for i in range(self.players[0].numStrats):
                poly = 0
                # building all but the last terms in poly
                # it's range(nS1 - 1) because there are that many variables for all but he last term
                for j in range(self.players[1].numStrats - 1):
                    poly += EU_1_coefs[i][j] * qVars[j]
                # building the last 1 - q0 - q1 - ... - qnS1 term
                lastTerm = 1
                for j in range(self.players[1].numStrats - 1):
                    lastTerm -= qVars[j]
                poly += EU_1_coefs[i][self.players[1].numStrats - 1] * lastTerm
                polynomials1.append(poly)
                
            # Building polynomials for player 2
            polynomials2 = []
            for j in range(self.players[1].numStrats):
                poly = 0
                # building all but the last terms in poly
                # it's range(nS0 - 1) because there are that many variables for all but he last term
                for i in range(self.players[0].numStrats - 1):
                    poly += EU_2_coefs[j][i] * pVars[i]
                # building the last 1 - q0 - q1 - ... - qnS1 term
                lastTerm = 1
                for i in range(self.players[0].numStrats - 1):
                    lastTerm -= pVars[i]
                poly += EU_2_coefs[j][self.players[0].numStrats - 1] * lastTerm
                polynomials2.append(poly)
            
            # Collecting the equations to be solved
            equations1 = []
            if self.players[0].numStrats % 2 == 0:
                for i in range(0, self.players[0].numStrats, 2):
                    equations1.append(sympy.Eq(polynomials1[i], polynomials1[i + 1]))
            else:
                for i in range(0, self.players[0].numStrats - 1, 2):
                    equations1.append(sympy.Eq(polynomials1[i], polynomials1[i + 1]))
                    # adding an equation that contains the last polynomial
                    equations1.append(sympy.Eq(polynomials1[0], polynomials1[-1]))
                    
            equations2 = []
            if self.players[1].numStrats % 2 == 0:
                for j in range(0, self.players[1].numStrats, 2):
                    equations2.append(sympy.Eq(polynomials2[j], polynomials2[j + 1]))
            else:
                for j in range(0, self.players[1].numStrats - 1, 2):
                    equations2.append(sympy.Eq(polynomials2[j], polynomials2[j + 1]))
                    # adding an equation that contains the last polynomial
                    equations2.append(sympy.Eq(polynomials2[0], polynomials2[-1]))
            
            # solving the equations
            dict1 = sympy.solve(tuple(equations1), tuple(qVars), set=True)
            dict2 = sympy.solve(tuple(equations2), tuple(pVars), set=True)
            if dict1[1] == set() or dict2 == set():
                return []
            L1 = []
            L2 = []
            for j in range(1, len(dict1), 2):
                L1.append(float(list(list(dict1[j])[0])[0]))
            for i in range(1, len(dict2), 2):
                L2.append(float(list(list(dict2[i])[0])[0]))
            
            sum1 = sum(L1)
            sum2 = sum(L2)
            if sum1 == 0 or sum2 == 0:
                return []
            else:
                L1.append(1 - sum1)
                L2.append(1 - sum2)
                return [[L1] + [L2]]
        else: # numPLayers >= 3
            if self.numPlayers < 53: # assuming numPlayers <= 26.
                alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                alphabetVars = [[] for x in range(self.numPlayers)]
                for x in range(self.numPlayers):
                    for k in range(self.players[x].numStrats - 1):
                        alphabetVars[x].append(sympy.symbols(alphabet[x] + "_" + str(k)))
                
                # polynomials that are multiplied by the coefficients
                polysToMultiply = [[] for x in range(self.numPlayers)]
                for x in range(self.numPlayers):
                    for k in range(self.players[x].numStrats - 1):
                        polysToMultiply[x].append(alphabetVars[x][k])
                    lastPoly = 1
                    for k in range(self.players[x].numStrats - 1):
                        lastPoly -= polysToMultiply[x][k]
                    polysToMultiply[x].append(lastPoly)

                # Getting the coefficients for the polynomials, EU_coefs[x][k] is the set of coefficients for the k-th polynomial for player x + 1, EU_polynomials[x][k] is the k-th polynomial for player x + 1
                EU_coefs = [[] for x in range(self.numPlayers)]
                EU_polynomials = [[] for x in range(self.numPlayers)]
                # getting for player 1
                for i in range(self.players[0].numStrats):
                    poly_coefs = []
                    poly = 0
                    for m in range(len(self.payoffMatrix)):
                        for j in range(self.players[1].numStrats):
                            coef = self.payoffMatrix[m][i][j].getListNode(0).payoff
                            poly_coefs.append(coef)
                            term = coef
                            for x in range(1, self.numPlayers):
                                if x == 1:
                                    term *= polysToMultiply[x][j]
                                else: # x > 1
                                    term *= polysToMultiply[x][self.toProfile(m)[x]]
                            poly += term
                    EU_coefs[0].append(poly_coefs)
                    EU_polynomials[0].append(poly)
                # getting for player 2
                for j in range(self.players[1].numStrats):
                    poly_coefs = []
                    poly = 0
                    for m in range(len(self.payoffMatrix)):
                        for i in range(self.players[0].numStrats):
                            coef = self.payoffMatrix[m][i][j].getListNode(1).payoff
                            poly_coefs.append(coef)
                            term = coef
                            for x in range(self.numPlayers):
                                if x != 1:
                                    if x == 0:
                                        term *= polysToMultiply[x][i]
                                    else: # x > 1
                                        term *= polysToMultiply[x][self.toProfile(m)[x]]
                            poly += term
                    EU_coefs[1].append(poly_coefs)
                    EU_polynomials[1].append(poly)
                    
                for x in range(2, self.numPlayers):
                    poly_coefs = []
                    for k in range(self.players[x].numStrats - 1):
                        m = 0
                        product = 1
                        firstProfile = [0 for y in range(self.numPlayers)]
                        firstProfile[x] = k
                        
                        numToAdd = 1
                        for y in range(2, self.numPlayers):
                            numToAdd *= self.players[y].numStrats
                                
                        numAdded = 0
                        while numAdded < numToAdd:
                            term = 0
                            poly_coefs = []
                            poly = 0
                            # Add all values in the current matrix
                            for i in range(self.players[0].numStrats):
                                for j in range(self.players[1].numStrats):
                                    coef = self.payoffMatrix[m][i][j].getListNode(x).payoff
                                    poly_coefs.append(coef)
                                    term = coef
                                    for y in range(self.numPlayers):
                                        if y != x:
                                            if y == 0:
                                                term *= polysToMultiply[y][i]
                                            elif y == 1:
                                                term *= polysToMultiply[y][j]
                                            else: # y > 1
                                                term *= polysToMultiply[y][self.toProfile(m)[y]]
                                    poly += term
                            numAdded += 1
                    
                            # obtaining the next profile in the sequence
                            if x == self.numPlayers - 1:
                                product = 1
                            else:
                                if x == 2 and self.numPlayers > 3:
                                    product = self.players[x].numStrats
                                else:
                                    allBelowPlayerAtMaxStrat = True
                                    mProfile = self.toProfile(m)
                                    for y in range(2, x):
                                        if mProfile[y] != self.players[y].numStrats - 1:
                                            allBelowPlayerAtMaxStrat = False
                                    if mProfile[x] == k and allBelowPlayerAtMaxStrat:
                                        productBelowPlayer = 1
                                        for y in range(2, x):
                                            productBelowPlayer *= self.players[y].numStrats
                                        product += productBelowPlayer * (self.players[x].numStrats - 1)
                                    else:
                                        product = 1
                            m += product
                            EU_coefs[x].append(poly_coefs)
                            EU_polynomials[x].append(poly)
                
                # Collecting the equations to be solved
                EU_equations = [[] for x in range(self.numPlayers)]
                for x in range(self.numPlayers):
                    if self.players[x].numStrats % 2 == 0:
                        for k in range(0, self.players[x].numStrats, 2):
                            EU_equations[x].append(sympy.Eq(EU_polynomials[x][k], EU_polynomials[x][k + 1]))
                    else:
                        for k in range(0, self.players[x].numStrats - 1, 2):
                            EU_equations[x].append(sympy.Eq(EU_polynomials[x][k], EU_polynomials[x][k + 1]))       
                            # adding an equation that contains the last polynomial
                            EU_equations[x].append(sympy.Eq(EU_polynomials[x][0], EU_polynomials[x][-1]))
                            
                # Solving the equations
                EU_sets = [sympy.solve(tuple(EU_equations[x]), tuple(alphabetVars[x]), set=True) for x in range(self.numPlayers)]
                
                for x in range(self.numPlayers):
                    if EU_sets[x][1] == set():
                        print("Empty set found. No mixed strategy equilibrium.")
                        return []
                
                # FIXME: finish for n >= 3 players when there actually is a MSE
                
            else: # numPlayers >= 26
                print(f"Error: not enough letters to have variables for all {self.numPlayers} players")
            return []
        return []
 
    def computePureEquilibria(self):
        self.computeBestResponses()
        br = []
        for m in range(len(self.payoffMatrix)):
            for i in range(self.players[0].numStrats):
                for j in range(self.players[1].numStrats):
                    allBR = True
                    for x in range(self.numPlayers):
                        if self.payoffMatrix[m][i][j].getListNode(x).bestResponse == False:
                            allBR = False
                            break
                    if allBR:
                        br.append([i, j] + self.toProfile(m)[2:])
        return br
    
    def enterPayoffs(self, payoffs = [
        [[1, 5], [2, 6]],
        [[3, 7], [4, 8]]
    ], numPlayers = 2, numStrats = [2, 2]):
        oldNumPlayers = self.numPlayers
        self.numPlayers = numPlayers
        
        if self.numPlayers <= oldNumPlayers:
            for x in range(self.numPlayers):
                self.players[x].numStrats = numStrats[x]
        else: # self.numPlayers > oldNumPlayers:
            for x in range(oldNumPlayers):
                self.players[x].numStrats = numStrats[x]
            for x in range(self.numPlayers - oldNumPlayers):
                self.players.append(Player(numStrats[oldNumPlayers + x]))
        
        self.payoffMatrix = []
        if self.numPlayers < 3:
            matrix = []
            for i in range(self.players[0].numStrats):
                row = []
                for j in range(self.players[1].numStrats):
                    outcome = ListNode(payoffs[i][j][0], False)
                    outcome.append(payoffs[i][j][1], False)
                    row.append(outcome)                      
                matrix.append(row)
            self.payoffMatrix.append(matrix)
        else:
            numMatrices = 1
            for i in range(2, self.numPlayers):
                numMatrices *= self.players[i].numStrats
            for m in range(numMatrices):
                matrix = []
                for i in range(self.players[0].numStrats):
                    row = []
                    for j in range(self.players[1].numStrats):
                        outcome = ListNode(payoffs[m][i][j][0], False)
                        for x in range(1, self.numPlayers):
                            outcome.append(payoffs[m][i][j][x], False)
                        row.append(outcome)                 
                    matrix.append(row)
                self.payoffMatrix.append(matrix)
        
        # updating strategy names
        self.strategyNames = []
        if self.players[0].numStrats < 3:
            self.strategyNames.append(["U", "D"])
        else:
            if self.players[0].numStrats == 3:
                middle = ["M"]
            else: # > 3
                middle = ["M" + str(i) for i in range(1, self.players[0].numStrats - 1)]
            self.strategyNames.append(["U"] + middle + ["D"])
        if self.players[1].numStrats < 3:
            self.strategyNames.append(["L", "R"])
        else:
            if self.players[1].numStrats == 3:
                center = ["C"]
            else: # > 3
                center = ["C" + str(j) for j in range(1, self.players[1].numStrats - 1)]
            self.strategyNames.append(["L"] + center + ["R"])
        if self.numPlayers > 2:
            for x in range(2, self.numPlayers):
                if self.players[x].numStrats < 3:
                    self.strategyNames.append(["L(" + str(x) + ")", "R(" + str(x) + ")"])
                else: 
                    self.strategyNames.append(["L(" + str(x) + ")"] + ["C(" + str(x) + ", " + str(s) + ")" for s in range(self.players[x].numStrats)] + ["R(" + str(x) + ")"])
        
    def isBestResponse(self, profile):
        """Checks whether p1Strat and p2Strat are best responses relative to each other

        Args:
            p1Strat (int): p1's strategy
            p2Strat (int): p2's strategy
        """
        br = [True for x in range(self.numPlayers)]
        if self.numPlayers < 3:
            for i in chain(range(profile[0]), range(profile[0] + 1, self.players[0].numStrats)):
                if self.payoffMatrix[0][profile[0]][profile[1]].getListNode(0).payoff < self.payoffMatrix[0][i][profile[1]].getListNode(0).payoff:
                    br[0] = False
            
            for j in chain(range(profile[1]), range(profile[1] + 1, self.players[1].numStrats)):
                if self.payoffMatrix[0][profile[0]][profile[1]].getListNode(1).payoff < self.payoffMatrix[0][profile[1]][j].getListNode(1).payoff:
                    br[1] = False
        else:
            for player in range(self.numPlayers):
                if player == 0:
                    for i in range(self.players[0].numStrats):
                        if self.payoffMatrix[self.toIndex(profile)][profile[0]][profile[1]].getListNode(0).payoff < self.payoffMatrix[self.toIndex(profile)][i][profile[1]].getListNode(0).payoff:
                            br[player] = False
                elif player == 1:
                    for j in range(self.players[1].numStrats):
                        if self.payoffMatrix[self.toIndex(profile)][profile[0]][profile[1]].getListNode(1).payoff < self.payoffMatrix[self.toIndex(profile)][profile[0]][j].getListNode(1).payoff:
                            br[player] = False
                # FIXME: finish computing BRs for players 2,...,numPlayers - 1
                else: # player > 1
                    m = 0
                    product = 1
                    numCompared = 0
                    curProfile = [0 for x in range(self.numPlayers)]
                    
                    # Getting the number of matrices to be compared
                    numToCompare = self.players[2].numStrats
                    for x in range(3, self.numPlayers):
                        if x != player:
                            numToCompare *= self.players[x].numStrats
                    numToCompare -= 1
                    
                    numCompared = 0
                    while numCompared < numToCompare:
                        if m != self.toIndex(profile):
                            if self.payoffMatrix[self.toIndex(profile)][profile[0]][profile[1]].getListNode(player).payoff < self.payoffMatrix[m][profile[0]][profile[1]].getListNode(player).payoff:
                                br[player] = False
                            numCompared += 1

                        # obtaining the next profile in the sequence
                        if player > 2 and player < self.numPlayers - 1 and product == 1:
                            for x in range(2, player):
                                product *= self.players[x].numStrats
                        m += product
        return br
    
    def print(self):
        """Prints the payoff matrix
        """
        if self.numPlayers < 3:
            for i in range(self.players[0].numStrats):
                for j in range(self.players[1].numStrats):
                    self.payoffMatrix[0][i][j].print()
                    if j < self.players[1].numStrats - 1:
                            print("  ", end="")
                    else:
                        print()
            print()
        else:
            for m in range(len(self.payoffMatrix)):
                for i in range(self.players[0].numStrats):
                    for j in range(self.players[1].numStrats):
                        self.payoffMatrix[m][i][j].print()
                        if j < self.players[1].numStrats - 1:
                            print("  ", end="")
                        else:
                            print()
                print()

    def printBestResponses(self):
        """Prints the payoff matrix
        """
        if self.numPlayers < 3:
            for i in range(self.players[0].numStrats):
                for j in range(self.players[1].numStrats):
                    self.payoffMatrix[0][i][j].printBestResponse()
                    if j < self.players[1].numStrats - 1:
                            print("  ", end="")
                    else:
                        print()
            print()
        else:
            for m in range(len(self.payoffMatrix)):
                print("m:", m)
                for i in range(self.players[0].numStrats):
                    for j in range(self.players[1].numStrats):
                        self.payoffMatrix[m][i][j].printBestResponse()
                        if j < self.players[1].numStrats - 1:
                            print("  ", end="")
                        else:
                            print()
                print()

    def readFromFile(self, fileName):
        addMoreOutcomesPast2 = False # kMatrix
        nP = -1 # numPlayers
        nS = -1 # numStrats
        r = -1 # rationality
        oldNumPlayers = -1
        oldNumStrats = [-1 for i in range(self.numPlayers)]
        oldSize = -1
        curList = []
        
        with open(fileName, 'r') as file:
            oldNumPlayers = self.numPlayers
            
            for x in range(self.numPlayers):
                oldNumStrats[x] = self.players[x].numStrats
                
            oldSize = len(self.payoffMatrix)
            
            # reading numPlayers
            nP = file.readline()
            self.numPlayers = int(nP)
            
            # reading numStrats for old players
            if oldNumPlayers <= self.numPlayers:
                nS = file.readline().split(" ")
                for n in nS:
                    n = n.rstrip()
                
                # Getting strategy names
                for x in range(self.numPlayers):
                    self.strategyNames[x] = file.readLine().split(" ")
                
                # Getting rationalities
                rats = file.readline().split(" ")
                for rat in rats:
                    rat = rat.rstrip()
                               
                for x in range(oldNumPlayers):
                    self.players[x].numStrats = int(nS[x])
                    self.players[x].rationality = int(rats[x])
            else:
                nS = file.readline().split(" ")
                for n in nS:
                    n = int(n.rstrip())
                # Getting rationalities
                rats = file.readline.split(" ")
                for rat in rats:
                    rat = int(rat.rstrip())
                
                for x in range(numPlayers):
                    self.players[x].numStrats = int(nS[x])
                    self.players[x].rationality = rats[x]
            
            """
			add new players if there are more,
			resizing payoffMatrix and kMatrix,
			increase the size of kStrategy lists 
            """
            if oldNumPlayers != self.numPlayers:
                if oldNumPLayers < numPlayers:
                    addMoreOutcomesPast2 = True
                # Create new players and read rest of numStrats
                for x in range(oldNumPlayers, self.numPlayers):
                    p = Player(int(nS[x]), rats[x])
                    players.append(p)
                    
            # new matrices added to the end
            size = 1
            if self.numPlayers > 2:
                for x in range(2, self.numPlayers):
                    size *= self.players[x].numStrats
            if size > len(self.payoffMatrix):
                self.payoffMatrix += [] * (size - len(self.payoffMatrix))
            else:
                self.payoffMatrix = self.payoffMatrix[:size]
            
            size = 1
            if self.numPlayers > 2:
                size = 4 ** (self.numPlayers - 2)
            if size > len(self.kMatrix):
                self.kMatrix += [] * (size - len(self.kMatrix))
            else:
                self.kMatrix = self.kMatrix[:size]

            # creating/deleting entries and reading values
            for m in range(len(self.payoffMatrix)):
                if self.players[0].numStrats > len(self.payoffMatrix[m]):
                    self.payoffMatrix[m] += [] * (self.players[0].numStrats - len(self.payoffMatrix[m]))
                else:
                    self.payoffMatrix[m] = self.payoffMatrix[m][:self.players[0].numStrats]
                for i in range(self.players[0].numStrats):
                    # resizing
                    if self.players[1].numStrats > len(self.payoffMatrix[m][i]):
                        self.payoffMatrix[m][i] += [] * (self.players[1].numStrats - len(self.payoffMatrix[m][i]))
                    else:
                        self.payoffMatrix[m][i] = self.payoffMatrix[m][i][:self.players[1].numStrats]
                    # Reading in the next row of payoffs
                    payoffs = file.readline().split(" ")
                    for payoff in payoffs:
                        payoff = float(payoff.rstrip())
                    groupedPayoffs = [payoffs[i:i + self.numPlayers] for i in range(0, len(payoffs), self.numPlayers)]
                    
                    for j in range(self.players[1].numStrats):
                        # Create new list if needed
                        if not self.payoffMatrix[m][i][j]:
                            newList = ListNode(0, False)
                            self.payoffMatrix[m][i][j] = newList
                        curList = self.payoffMatrix[m][i][j]
                        while curList.size() > self.numPlayers:
                            # Deleting
                            curList.removeAtIndex(curList.size() - 1)
                        
                        for x in range(self.numPlayers):
                            if m < oldSize and x < oldNumPlayers and i < oldNumStrats[0] and j < oldNumStrats[1]: # old matrix, old outcome, old payoff
                                curList.updateListNode(float(groupedPayoffs[j][x]), x) # inserting payoff value
                            else: # Everything is new
                                # Adding
                                curList.appendNode(int(payoffs[x]), False)
            if addMoreOutcomesPast2:
                for m in range((len(self.kMatrix))):
                    if 4 > len(self.kMatrix[m]):
                        self.kMatrix[m] += [None] * (4 - len(self.kMatrix[m]))
                    else:
                        self.kMatrix[m] = self.kMatrix[m][:4]
                    for i in range(4):
                        if 4 > len(self.kMatrix[m]):
                            self.kMatrix[m][i] += [None] * (4 - len(self.kMatrix[m][i]))
                        else:
                            self.kMatrix[m][i] = self.kMatrix[m][i][:4]
                        for j in range(4):
                            myList = [-1 for l in range(self.numPlayers)]
                            kMatrix[m][i][j] = myList
        print("Done reading from " + fileName)

    def removeStrategy(self, player, s):
        """Removes strategy s from player x in the payoff matrix

        Args:
            player (int): index of the player
            s (int): index of the strategy
        """
        if player == 0: # x is player 1
            for m in range(len(self.payoffMatrix)):
                del self.payoffMatrix[m][s]
        elif player == 1: # x is player 2
            for m in range(len(self.payoffMatrix)):
                for i in range(len(self.payoffMatrix[m])):
                    del self.payoffMatrix[m][i][s]
        else: # player > 1
            m = 0
            product = 1
            """In this file there's no x to go through, so just cycle through the 
            matrices and delete the appropriate ones. 
            """
            # Starting at the first profile in the sequence
            firstProfile = [0 for x in range(self.numPlayers)]
            firstProfile[player] = s
            m = self.toIndex(firstProfile)
            
            # lastProfile = [-1, -1] + [self.players[x].numStrats - 1 for x in range(2, self.numPlayers)]
            # lastProfile[player] = s
            
            # Getting the number of matrices to be deleted
            numToDelete = 1
            for x in range(2, self.numPlayers):
                if x != player:
                    numToDelete *= self.players[x].numStrats
            
            numDeleted = 0
            while numDeleted < numToDelete:
                del self.payoffMatrix[m - numDeleted]
                numDeleted += 1
                
                # obtaining the next profile in the sequence
                if player == 2 and self.numPlayers > 3:
                    product = self.players[player].numStrats
                else:
                    allBelowPlayerAtMaxStrat = True
                    mProfile = self.toProfile(m)
                    for x in range(2, player):
                        if mProfile[x] != self.players[x].numStrats - 1:
                            allBelowPlayerAtMaxStrat = False
                    if mProfile[player] == s and allBelowPlayerAtMaxStrat:
                        productBelowPlayer = 1
                        for x in range(2, player):
                            productBelowPlayer *= self.players[x].numStrats
                        product += productBelowPlayer * (self.players[player].numStrats - 1)
                    else:
                        product = 1
                m += product
        self.players[player].numStrats -= 1      
    
    def saveToFile(self, fileName):
        """Saves the data of a game to a text file

        Args:
            fileName (str): the file name
        """
        with open(fileName, 'w') as file:
            file.write(str(self.numPlayers) + "\n")
            
            # write numStrats to file
            for x in range(self.numPlayers):
                file.write(str(self.players[x].numStrats))
                if x < self.numPlayers - 1:
                    file.write(" ")
            file.write("\n")
            
            # write strategyNames to file
            for x in range(self.numPlayers):
                for s in range(self.players[x].numStrats):
                    file.write(str(self.strategyNames[x][s]))
                    if s < self.players[x].numStrats - 1:
                        file.write(" ")
                if x < self.numPlayers - 1:
                    file.write("\n")
            file.write("\n")
            
            # write rationalities to the file
            for x in range(self.numPlayers):
                file.write(str(self.players[x].rationality))
                if x < self.numPlayers - 1:
                    file.write(" ")
            file.write("\n")
            
            # write payoffMatrix to file
            for m in range(len(self.payoffMatrix)):
                for i in range(self.players[0].numStrats):
                    for j in range(self.players[1].numStrats):
                        curList = self.payoffMatrix[m][i][j]
                        for x in range(self.numPlayers):
                            file.write(str(curList.getListNode(x).payoff))
                            if x < self.numPlayers - 1:
                                file.write(" ")
                        if j < self.players[1].numStrats - 1:
                            file.write(" ")
                    if i < self.players[0].numStrats - 1:
                        file.write("\n")
                if m < len(self.payoffMatrix) - 1:
                    file.write("\n\n")
            print("Saved to " + fileName + ".\n")
            
    def toIndex(self, profile):
        """Converts a sequence of strategies into the index in a stack of payoff arrays that correspond to that sequence. This is the inverse of the function toProfile. 

        Args:
            profile (list): strategy profile (indices)

        Returns:
            int: the desired index
        """
        sameNumStratsPastPlayer2 = True
        # Checking if players 2,...,numPlayers have the same number of strategies as player 3
        for x in range(2, self.numPlayers):
            if self.players[x].numStrats != self.players[1].numStrats:
                self.sameNumStratsPastPlayer2 = False
        
        # c_2 + sum_{x = 3}^{nP - 1} (nS)^x * c_x
        num = 0 # return 0 if self.numPlayers < 3
        if self.numPlayers > 2:
            num = profile[2]
        if sameNumStratsPastPlayer2: # if all players past player 2 have the same number of strategies
            for x in range(3, self.numPlayers):
                if profile[x] > 0:
                    num += (self.players[2].numStrats ** (x - 2)) * profile[x]
        else: # c_2 + sum_{x=3}^{nP} nS_2 *...* nS_{x-1} * c_x
            if self.numPlayers > 3:
                product = 0
                for x in range(3, self.numPlayers):
                    product = 1
                    if profile[x] > 0:
                        for y in range(2, x - 1):
                            product *= self.players[y].numStrats
                            
                        num += product * profile[x]
        return num
    
    def toProfile(self, m):
        """Converts an index in a stack of payoff arrays into the sequence of strategies that produce that index. This is the inverse of the function toIndex. 

        Args:
            m (int): the index of the payoff array that we're toProfileing

        Returns:
            list: a list of indices (strategies)
        """
        choice = 0
        prevValues = 0 # values from players below P_x
        productNumStrats = 1
        profile = [-1, -1] + [0 for x in range(2, self.numPlayers)]
        
        for x in range(2, self.numPlayers - 1):
            productNumStrats *= self.players[x].numStrats
            
        for x in range(self.numPlayers - 1, 1, -1):
            choice = 0
            while productNumStrats * choice + prevValues < m and choice != self.players[x].numStrats - 1:
                choice += 1
            
            if productNumStrats * choice + prevValues > m:
                choice -= 1
                
            prevValues += productNumStrats * choice
            profile[x] = choice
            productNumStrats = productNumStrats / self.players[x].numStrats
        return profile

arr_2players = [
    [[1, 5], [2, 6]],
    [[3, 7], [4, 8]]
]

bos = [
    [[2, 1], [0, 0]],
    [[0, 0], [1, 2]]
]

rps = [
    [[0, 0], [-1, 1], [1, -1]],
    [[1, -1], [0, 0], [-1, 1]],
    [[-1, 1], [1, -1], [0, 0]]
]

arr_3players = [
    [
        [[1, 2, 3], [4, 5, 6]],
        [[7, 8, 9], [10, 11, 12]]
    ],
    [
        [[1.1, 2.1, 3.1], [4.1, 5.1, 6.1]],
        [[7.1, 8.1, 9.1], [10.1, 11.1, 12.1]]
    ]
]

brTest_3players = [
    [
        [[0, 0, 1], [0, 0, 2]],
        [[0, 0, 3], [0, 0, 1]]
    ],
    [
        [[0, 0, 0], [0, 0, 1]],
        [[0, 0, 3], [0, 0, 4]]
    ]
]

brTest2_3players = [
    [
        [[1, 2, 1], [3, 4, 2]],
        [[5, 6, 3], [7, 8, 1]]
    ],
    [
        [[2, 4, 0], [6, 8, 1]],
        [[10, 12, 3], [14, 16, 4]]
    ]
]

twoEq_3players = [
    [
        [[-3, -3, 2],[0, -5, 4]],
        [[-5, 0, 1],[-1, -1, 1]]
    ],
    [
        [[0, 0, 1], [5, 1, 3]],
        [[1, 5, 0], [6, 6, 2]]
    ]
]

arr_4players = [
    [
        [[0, 1, 1, 1], [1, 1, 1, 1]],
        [[1, 1, 1, 1], [1, 1, 1, 1]]
    ],
    [
        [[1, 1, 1, 1], [1, 1, 1, 1]],
        [[1, 1, 1, 1], [1, 1, 1, 1]]
    ],
    [
        [[2, 1, 1, 1], [1, 1, 1, 1]],
        [[1, 1, 1, 1], [1, 1, 1, 1]]
    ],
    [
        [[3, 1, 1, 1], [1, 1, 1, 1]],
        [[1, 1, 1, 1], [1, 1, 1, 1]]
    ],
    [
        [[4, 1, 1, 1], [1, 1, 1, 1]],
        [[1, 1, 1, 1], [1, 1, 1, 1]]
    ],
    [
        [[5, 1, 1, 1], [1, 1, 1, 1]],
        [[1, 1, 1, 1], [1, 1, 1, 1]]
    ],
    [
        [[6, 1, 1, 1], [1, 1, 1, 1]],
        [[1, 1, 1, 1], [1, 1, 1, 1]]
    ],
    [
        [[7, 1, 1, 1], [1, 1, 1, 1]],
        [[1, 1, 1, 1], [1, 1, 1, 1]]
    ],
    [
        [[8, 1, 1, 1], [1, 1, 1, 1]],
        [[1, 1, 1, 1], [1, 1, 1, 1]]
    ],
]

arr_5players = [
    [
        [[0, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[2, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[3, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[4, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[5, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[6, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[7, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[8, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[9, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[10, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[11, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[12, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[13, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[14, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[15, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[16, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[17, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[18, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[19, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[20, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[21, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[22, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[23, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[24, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[25, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ],
    [
        [[26, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    ]
]

# G = SimGame(2)
# G.enterPayoffs(bos, 2, [2, 2])
# G.saveToFile("text files/rps.txt")
# G.print()
# G.computeBestResponses()
# eqs = G.computePureEquilibria()
# G.printBestResponses()
# print("EQS:", G.computeEquilibria())

# for eq in eqs:
#     print(eq)

# H = SimGame(3)
# H.print()
# H.enterPayoffs(twoEq_3players, 3, [2, 2, 2])
# print("br test:")
# H.print()
# H.computeBestResponses()
# H.printBestResponses()
# print(H.computePureEquilibria())
# print(H.computeEquilibria())

# I = SimGame(4)
# I.enterPayoffs(arr_4players, 4, [2, 2, 3, 3])
# I.removeStrategy(0, 1)
# I.print()

# J = SimGame(5)
# J.enterPayoffs(arr_5players, 5, [2, 2, 3, 3, 3])
# J.removeStrategy(2, 0)
# print("J:")
# J.print()