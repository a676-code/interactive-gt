# pysimultaneous.py
# Author: Andrew W. Lounsbury
# Date: 3/24/24
# Description: a class for handling simultaneous games with n players, n >= 2
from itertools import chain
from itertools import combinations
import numpy as np
import sympy
from sympy import solve
from sympy import simplify
import warnings
from pprint import pprint
import colorama
from colorama import init, Fore, Style

init()

def checkIfFloats(myList):
    allFloats = True
    t = ""
    for i in range(len(myList)):
        if not isinstance(myList[i], float):
            t = type(myList[i]).__name__
            if t != "float" or "int":
                allFloats = False
                break
            if t == "int":
                myList[i] = float(myList[i])
    return (allFloats, t, myList) 

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
    
    def checkIfFloats(self):
        allFloats = True
        curNode = self.head
        t = ""
        while curNode:
            if not isinstance(curNode.payoff, float):
                t = type(curNode.payoff).__name__
                if t != "float" or "int":
                    allFloats = False
                    break
                if t == "int":
                    curNode.payoff = float(curNode.payoff)
        return (allFloats, t, self)
    
    def decapitate(self):
        """Removes the head ListNode
        """
        if self.head == None:
            return
        
        self.head = self.head.next
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
    
    def load(self, payoffs):
        self = ListNode(payoffs[0], False)
        for payoff in payoffs[1:]:
            self.append(payoff, False)
        return self
        
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
        while curNode:
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
    kChoice = -1
    numStrats = -1
    rationality = -1
    
    def __init__(self,numStrats = 2, rationality = 0):
        self.kChoice = -1
        self.numStrats = numStrats
        self.rationality = rationality

class SimGame:
    kMatrix = []
    kOutcomes = [] # n-tuples that appear in kMatrix; won't be all of them
    kStrategies = [[] for r in range(4)] # 2D matrix containing the strategies each player would play for k-levels 0, 1, 2, 3
    maxRationality = 4
    mixedEquilibria = []
    numIESDSSteps = 0
    numPlayers = -1
    originalNumPlayers = -1 
    originalNumStrats = []
    originalPayoffMatrix = []
    outcomeProbabilities = [] # probability of each outcome in kMatrix stored in kOutcomes; P(i, j)
    payoffMatrix = []
    players = []
    pureEquilibria = []
    rationalityProbabilities = [0.0 for i in range(4)] # probability a player is L_i, i = 0, 1, 2, 3
    removedCols = []
    removedMatrices = []
    removedRows = []
    removedStrategies = []
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
            
        # maximum rationality is 3, meaning there are 4 rationality levels
        numMatrices = 1
        if numPlayers > 2:
            numMatrices = 4 ** self.numPlayers
        
        for m in range(numMatrices):
            self.kMatrix.append([])
            for i in range(4):
                self.kMatrix[m].append([])
                for j in range(4):
                    ell = [-1 for x in range(self.numPlayers)]
                    self.kMatrix[m][i].append(ell)
        
        # Initializing strategy names
        if self.players[0].numStrats < 3:
            self.strategyNames.append(["U", "D"])
        else:
            if self.players[0].numStrats == 3:
                middle = ["M"]
            else: # [0].numStrats > 3
                middle = ["M" + str(i) for i in range(1, self.players[0].numStrats - 1)]
            self.strategyNames.append(["U"] + middle + ["D"])
        if self.players[1].numStrats < 3:
            self.strategyNames.append(["L", "R"])
        else:
            if self.players[1].numStrats == 3:
                center = ["C"]
            else: # [1].numStrats > 3
                center = ["C" + str(j) for j in range(1, self.players[1].numStrats - 1)]
            self.strategyNames.append(["L"] + center + ["R"])
        if self.numPlayers > 2:
            for x in range(2, self.numPlayers):
                center = []
                if self.players[x].numStrats < 3:
                    center = []
                elif self.players[x].numStrats == 3:
                    center = ["C(" + str(x + 1) + ")"]
                else:
                    center = ["C(" + str(x + 1) + ", " + str(s) + ")" for s in range(1, self.players[x].numStrats - 1)]
                self.strategyNames.append(["L(" + str(x + 1) + ")"] + center + ["R(" + str(x + 1) + ")"])
        
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
        
        self.originalNumPlayers = self.numPlayers
        self.originalNumStrats = [self.players[x].numStrats for x in range(self.numPlayers)]
        self.originalPayoffMatrix = self.payoffMatrix
        return
    
    def appendStrategy(self, x, payoffs):
        """Appends a strategy to player x + 1's list of strategies

        Args:
            x (int): the index of the player
            payoffs (list of lists of ListNodes or list of lists of lists of ListNodes): the payoffs of the strategy to be appended, lists of outcomes
        """
        if not isinstance(x, int):
            print(Fore.RED + f"appendStrategy: invalid input. Expected an integer player index, but received {x} instead." + Style.RESET_ALL)
            return
        #################################################################
        if x == 0: # add a new row to every matrix
            # if list of list of lists, convert to list of list of ListNodes
            if isinstance(payoffs[0][0], list):
                newPayoffs = []
                for row in payoffs:
                    newRow = []
                    for ell in row:
                        if isinstance(ell, list):
                            outcome = ListNode()
                            outcome = outcome.load(ell)
                            newRow.append(outcome)
                        elif isinstance(ell, ListNode):
                            newRow.append(ell)
                        else:
                            print(Fore.RED + f"appendStrategy: invalid input. The outcomes must be either lists or ListNodes. Received {type(ell).__name__} instead." + Style.RESET_ALL)
                            return
                    newPayoffs.append(newRow)
                payoffs = newPayoffs
            
            # payoffs will be a list of list of ListNodes that should be numPlayers-long.
            inputValid = True
            numMatrices = 1
            for y in range(2, self.numPlayers):
                numMatrices *= self.players[y].numStrats
            correctNumRows = True
            if len(payoffs) != numMatrices:
                correctNumRows = False
                
            correctNumOutcomes = True
            for row in payoffs:
                if len(row) != self.players[x].numStrats:
                    wrongNumOutcomes = len(row)
                    correctNumOutcomes = False
                    break
                
            correctNumPayoffs = True
            for row in payoffs:
                for outcome in row:
                    if outcome.size() != self.numPlayers:
                        wrongSize = outcome.size()
                        correctNumPayoffs = False
                        
            allFloats = True
            broke = False
            wrongType = ""
            for row in payoffs:
                for outcome in row:
                    triple = outcome.checkIfFloats()
                    if not triple[0]:
                        wrongType = triple[1]
                        # if wrongType is integer, we can simply convert it to a float
                        if wrongType == "int":
                            outcome = triple[2]
                        else:
                            allFloats = False
                            broke = True
                            break
                if broke:
                    break
                    
            if correctNumRows and correctNumOutcomes and correctNumPayoffs and isinstance(x, int) and x > -1 and x < self.numPlayers and isinstance(payoffs, list) and len(payoffs) > 0 and allFloats:
                inputValid = True
            else:
                inputValid = False
            if inputValid:
                self.players[x].numStrats += 1
                for m in range(numMatrices):
                    self.payoffMatrix[m].append(payoffs[m])
            elif not correctNumRows:
                if numMatrices == 1:
                    if len(payoffs) == 1:
                        print(Fore.RED + f"appendStrategy: invalid input. Expected {numMatrices} row, but {len(payoffs)} was provided." + Style.RESET_ALL)
                    else: 
                        print(Fore.RED + f"appendStrategy: invalid input. Expected {numMatrices} row, but {len(payoffs)} were provided." + Style.RESET_ALL)
                else:
                    if len(payoffs) == 1:
                        print(Fore.RED + f"appendStrategy: invalid input. Expected {numMatrices} rows, but {len(payoffs)} was provided." + Style.RESET_ALL)
                    else:
                        print(Fore.RED + f"appendStrategy: invalid input. Expected {numMatrices} rows, but {len(payoffs)} were provided." + Style.RESET_ALL)
            elif not correctNumOutcomes:
                if wrongNumOutcomes == 1:
                    print(Fore.RED + f"appendStrategy: invalid input. Expected {self.players[x].numStrats} outcomes. Received a row with {wrongNumOutcomes} outcome." + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"appendStrategy: invalid input. Expected {self.players[x].numStrats} outcomes. Received a row with {wrongNumOutcomes} outcomes." + Style.RESET_ALL)
            elif not correctNumPayoffs:
                if wrongSize == 1:
                    print(Fore.RED + f"appendStrategy: invalid input. expected outcomes with {self.numPlayers} payoffs. An outcome with {wrongSize} payoff was provided." + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"appendStrategy: invalid input. expected outcomes with {self.numPlayers} payoffs. An outcome with {wrongSize} payoffs was provided." + Style.RESET_ALL)
            elif not isinstance(x, int):
                print(Fore.RED + f"appendStrategy: invalid input. Expected an integer player index, but received {x} instead." + Style.RESET_ALL)
            elif x < 0 or x >= self.numPlayers:
                print(Fore.RED + f"appendStrategy: invalid input. Expected a player index between 0 and {self.numPlayers - 1}, but received {x} instead." + Style.RESET_ALL)
            elif not isinstance(payoffs, list):
                print(Fore.RED + f"appendStrategy: invalid input. Expected a list of payoffs, but received a {type(payoffs).__name__} instead" + Style.RESET_ALL)
            elif len(payoffs) == 0:
                print(Fore.RED + f"appendStrategy: invalid input. The payoffs parameter must be a nonempty list." + Style.RESET_ALL)
            elif not allFloats:
                print(Fore.RED + f"appendStrategy: invalid input. The payoffs must be floats. Received {wrongType} instead." + Style.RESET_ALL)      
        #################################################################
        elif x == 1: # add a new column to every matrix
            # if list of list of lists, convert to list of list of ListNodes
            if isinstance(payoffs[0][0], list):
                newPayoffs = []
                for col in payoffs:
                    newCol = []
                    for ell in col:
                        if isinstance(ell, list):
                            outcome = ListNode()
                            outcome = outcome.load(ell)
                            newCol.append(outcome)
                        elif isinstance(ell, ListNode):
                            newCol.append(ell)
                        else:
                            print(Fore.RED + f"appendStrategy: invalid input. The outcomes must be either lists or ListNodes. Received {type(ell).__name__} instead." + Style.RESET_ALL)
                            return
                    newPayoffs.append(newCol)
                payoffs = newPayoffs
            
            inputValid = True
            numMatrices = 1
            for y in range(2, self.numPlayers):
                numMatrices *= self.players[y].numStrats
            correctNumCols = True
            if len(payoffs) != numMatrices:
                correctNumRows = False
            
            correctNumOutcomes = True
            for col in payoffs:
                if len(col) != self.players[x].numStrats:
                    wrongNumOutcomes = len(col)
                    correctNumOutcomes = False
                    break
                
            correctNumPayoffs = True
            for row in payoffs:
                for outcome in row:
                    if isinstance(outcome, ListNode):
                        if outcome.size() != self.numPlayers:
                            wrongSize = outcome.size()
                            correctNumPayoffs = False
                    elif isinstance(outcome, list):
                        if len(outcome) != self.numPlayers:
                            wrongSize = outcome.size()
                            correctNumPayoffs = False
                    else:
                        print(Fore.RED + f"appendStrategy: invalid input. Outcomes must be either lists or ListNodes. Received {type(outcome).__name__} instead." + Style.RESET_ALL) 
                        
            allFloats = True
            broke = False
            wrongType = ""
            for row in payoffs:
                for outcome in row:
                    if isinstance(outcome, ListNode): 
                        triple = outcome.checkIfFloats()
                        if not triple[0]:
                            wrongType = triple[1]
                            if wrongType == "int":
                                outcome = triple[2]
                            else:
                                allFloats = False
                                broke = True
                                break
                    elif isinstance(outcome, list):
                        triple = checkIfFloats(outcome)
                        if not triple[0]:
                            wrongType = triple[1]
                            if wrongType == "int":
                                outcome = triple[2]
                            else:
                                allFloats = False
                                broke = True
                                break
                if broke:
                    break
                        
            if correctNumCols and correctNumOutcomes and correctNumPayoffs and isinstance(x, int) and x > -1 and x < self.numPlayers and isinstance(payoffs, list) and len(payoffs) > 0 and allFloats:
                inputValid = True
            else:
                inputValid = False
            if inputValid:
                self.players[x].numStrats += 1
                
                for m in range(numMatrices):
                    # FIXME
                    print("len 1: ", len(self.payoffMatrix[m]))
                    print("len 2: ", len(payoffs[m]))
                    for j in range(len(payoffs[0])):
                        print("\tj: ", j)
                        self.payoffMatrix[m][j].append(payoffs[m][j])
            elif not correctNumCols:
                if numMatrices == 1:
                    if len(payoffs) == 1:
                        print(Fore.RED + f"appendStrategy: invalid input. Expected {numMatrices} column, but {len(payoffs)} was provided." + Style.RESET_ALL)
                    else:
                        print(Fore.RED + f"appendStrategy: invalid input. Expected {numMatrices} column, but {len(payoffs)} were provided." + Style.RESET_ALL)
                else:
                    if len(payoffs) == 1:
                        print(Fore.RED + f"appendStrategy: invalid input. Expected {numMatrices} columns, but {len(payoffs)} was provided." + Style.RESET_ALL)
                    else:
                        print(Fore.RED + f"appendStrategy: invalid input. Expected {numMatrices} columns, but {len(payoffs)} were provided." + Style.RESET_ALL)
            elif not correctNumOutcomes:
                if wrongNumOutcomes == 1:
                    print(Fore.RED + f"appendStrategy: invalid input. Expected {self.players[x].numStrats} outcomes. Received a column with {wrongNumOutcomes} outcome." + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"appendStrategy: invalid input. Expected {self.players[x].numStrats} outcomes. Received a column with {wrongNumOutcomes} outcomes." + Style.RESET_ALL)
            elif not correctNumPayoffs:
                if wrongSize == 1:
                    print(Fore.RED + f"appendStrategy: invalid input. expected outcomes with {self.numPlayers} payoffs. An outcome with {wrongSize} payoff was provided." + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"appendStrategy: invalid input. expected outcomes with {self.numPlayers} payoffs. An outcome with {wrongSize} payoffs was provided." + Style.RESET_ALL)
            elif not isinstance(x, int):
                print(Fore.RED + f"appendStrategy: invalid input. Expected an integer player index, but received {x} instead." + Style.RESET_ALL)
            elif x < 0 or x >= self.numPlayers:
                print(Fore.RED + f"appendStrategy: invalid input. Expected a player index between 0 and {self.numPlayers - 1}, but received {x} instead." + Style.RESET_ALL)
            elif not isinstance(payoffs, list):
                print(Fore.RED + f"appendStrategy: invalid input. Expected a list of payoffs, but received a {type(payoffs).__name__} instead" + Style.RESET_ALL)
            elif len(payoffs) == 0:
                print(Fore.RED + f"appendStrategy: invalid input. The payoffs parameter must be a nonempty list." + Style.RESET_ALL)
            elif not allFloats:
                print(Fore.RED + f"appendStrategy: invalid input. The payoffs must be floats. Received {wrongType} instead." + Style.RESET_ALL)  
        #################################################################
        else: # x > 1 add new matrices
            # if list of list of lists, convert to list of list of ListNodes
            if isinstance(payoffs[0][0][0], list):
                newPayoffs = []
                for matrix in payoffs:
                    newMatrix = []
                    for col in matrix:
                        newCol = []
                        for ell in col:
                            if isinstance(ell, list):
                                outcome = ListNode()
                                outcome = outcome.load(ell)
                                newCol.append(outcome)
                            elif isinstance(ell, ListNode):
                                newCol.append(ell)
                            else:
                                print(Fore.RED + f"appendStrategy: invalid input. The outcomes must be either lists or ListNodes. Received {type(ell).__name__} instead." + Style.RESET_ALL)
                                return
                        newMatrix.append(newCol)
                    newPayoffs.append(newMatrix)
                payoffs = newPayoffs
            # We want to insert after the product of numStrats *below* player x + 1 for each number 1, 2,...,prodNumStratsAboveX, *plus* the number of matrices we've added
            inputValid = True
            numMatricesToAdd = 1
            for y in range(2, self.numPlayers):
                if y != x:
                    numMatricesToAdd *= self.players[y].numStrats
            correctNumMatrices = True
            if len(payoffs) != numMatricesToAdd:
                correctNumMatrices = False
            
            # Ensuring the arrays have the correct dimensions
            correctNumRows = True
            correctNumCols = True
            broke = False
            for matrix in payoffs:
                if len(matrix) != self.players[0].numStrats:
                    wrongNumRows = len(matrix)
                    correctNumRows = False
                for row in matrix:
                    if len(row) != self.players[1].numStrats:
                        wrongNumCols = len(row)
                        correctNumCols = False
                        broke = True
                        break
                if broke:
                    break
            
            correctNumPayoffs = True
            for matrix in payoffs:
                for row in matrix:
                    for outcome in row:
                        if outcome.size() != self.numPlayers:
                            wrongSize = outcome.size()
                            correctNumPayoffs = False
            
            # Ensuring all the payoffs are floats
            allFloats = True
            broke = False
            wrongType = ""
            for matrix in payoffs:
                for row in matrix:
                    for outcome in row:
                        triple = outcome.checkIfFloats()
                        if not triple[0]:
                            wrongType = triple[1]
                            if wrongType == "int":
                                outcome = triple[2]
                            else:
                                allFloats = False
                                broke = True
                                break
                    if broke:
                        if not broke:
                            broke = True
                        break   
                if broke:
                    break
            
            # Input validation
            if correctNumMatrices and correctNumRows and correctNumCols and correctNumPayoffs and isinstance(x, int) and x > -1 and x < self.numPlayers and isinstance(payoffs, list) and len(payoffs) > 0 and allFloats:
                inputValid = True
            else:
                inputValid = False
            if inputValid:
                numMatricesBeforeX = 1
                for y in range(2, x):
                    numMatricesBeforeX *= self.players[y].numStrats
                numMatricesUpToX = 1
                for y in range(2, x + 1):
                    numMatricesUpToX *= self.players[y].numStrats
                productNumStratsAboveX = 1
                for y in range(x + 1, self.numPlayers):
                    productNumStratsAboveX *= self.players[y].numStrats
                numMatricesAdded = 0
                multiplicand = 1
                while len(payoffs) > 0:
                    # Inserting the new matrix
                    self.payoffMatrix.insert(numMatricesUpToX * multiplicand + numMatricesAdded, payoffs[0])
                    payoffs.pop(0)
                    numMatricesAdded += 1
                    if numMatricesAdded % numMatricesBeforeX == 0:
                        multiplicand += 1
                self.players[x].numStrats += 1
            elif not correctNumMatrices:
                if numMatricesToAdd == 1:
                    if len(payoffs) == 1:
                        print(Fore.RED + f"appendStrategy: invalid input. Expected {numMatricesToAdd} array. Payoffs with {len(payoffs)} array were provided." + Style.RESET_ALL)
                    else: 
                        print(Fore.RED + f"appendStrategy: invalid input. Expected {numMatricesToAdd} array. Payoffs with {len(payoffs)} arrays were provided." + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"appendStrategy: invalid input. Expected {numMatricesToAdd} arrays. Payoffs with {len(payoffs)} arrays were provided." + Style.RESET_ALL)
            elif not correctNumRows and not correctNumCols:
                print(Fore.RED + f"appendStrategy: invalid input. Expected arrays with {self.players[0].numStrats} rows and {self.players[1].numStrats} columns. An array with {wrongNumRows} rows and {wrongNumCols} columns was provided." + Style.RESET_ALL)
            elif not correctNumRows and correctNumCols:
                print(Fore.RED + f"appendStrategy: invalid input. Expected arrays with {self.players[0].numStrats} rows and {self.players[1].numStrats} columns. An array with {wrongNumRows} rows was provided." + Style.RESET_ALL)
            elif correctNumRows and not correctNumCols:
                print(Fore.RED + f"appendStrategy: invalid input. Expected arrays with {self.players[0].numStrats} rows and {self.players[1].numStrats} columns. An array with {wrongNumCols} columns was provided." + Style.RESET_ALL)
            elif not correctNumRows:
                if wrongNumRows == 1:
                    print(Fore.RED + f"appendStrategy: invalid input. Expected arrays with {self.players[0].numStrats} rows. Received a matrix with {wrongNumRows} row.")
                else:
                    print(Fore.RED + f"appendStrategy: invalid input. Expected arrays with {self.players[0].numStrats} rows. Received a matrix with {wrongNumRows} rows.")
            elif not correctNumCols:
                if wrongNumRows == 1:
                    print(Fore.RED + f"appendStrategy: invalid input. Expected arrays with {self.players[0].numStrats} columns. Received a matrix with {wrongNumCols} colum.")
                else:
                    print(Fore.RED + f"appendStrategy: invalid input. Expected arrays with {self.players[0].numStrats} rows. Received a matrix with {wrongNumCols} columns.")
            elif not correctNumPayoffs:
                if wrongSize == 1:
                    print(Fore.RED + f"appendStrategy: invalid input. expected outcomes with {self.numPlayers} payoffs. An outcome with {wrongSize} payoff was provided." + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"appendStrategy: invalid input. expected outcomes with {self.numPlayers} payoffs. An outcome with {wrongSize} payoffs was provided." + Style.RESET_ALL)
            elif not isinstance(x, int):
                print(Fore.RED + f"appendStrategy: invalid input. Expected an integer player index, but received {x} instead." + Style.RESET_ALL)
            elif x < 0 or x >= self.numPlayers:
                print(Fore.RED + f"appendStrategy: invalid input. Expected a player index between 0 and {self.numPlayers - 1}, but received {x} instead." + Style.RESET_ALL)
            elif not isinstance(payoffs, list):
                print(Fore.RED + f"appendStrategy: invalid input. Expected a list of payoffs, but received a {type(payoffs).__name__} instead" + Style.RESET_ALL)
            elif len(payoffs) == 0:
                print(Fore.RED + f"appendStrategy: invalid input. The payoffs parameter must be a nonempty list." + Style.RESET_ALL)
            elif not allFloats:
                print(Fore.RED + f"appendStrategy: invalid input. The payoffs must be floats. Received {wrongType} instead." + Style.RESET_ALL)
        return
    
    def computeBestResponses(self):
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
        return

    def computeEquilibria(self):
        equilibria = self.computePureEquilibria() + self.computeMixedEquilibria()
        numEquilibria = len(equilibria)
        if numEquilibria % 2 == 0:
            warnings.warn(f"An even number ({numEquilibria}) of equilibria was returned. This indicates that the game is degenerate. Consider using another algorithm to investigate.", RuntimeWarning)
        return equilibria
    
    def computeKChoices(self):
        computeKStrategies()
        return
    
    def computeKExpectedUtilities(self):
        EU = [0.0 for x in range(self.numPlayers)]
        for x in range(self.numPlayers):
            EU[x] = 0.0
            for num in range(len(self.kOutcomes)):
                if self.numPlayers < 3:
                    curList = self.payoffMatrix[0][self.kOutcomes[num][0]][self.kOutcomes[num][1]]
                else:
                    curList = payoffMatrix[self.toIndex(self.kOutcomes[num])][self.kOutcomes[num][0]][self.kOutcomes[num][1]]
                EU[x] += curList.getListNode(x).payoff * self.outcomeProbabilities[num]
        return EU
    
    def computeKMatrix(self, probabilities):
        """Computes the kMatrix as well as kOutcomes in the process
        """
        curEntry = []
        temp = []
        inOutcomes = False
        probability = -1.0
        self.kOutcomes = []
        self.computeKStrategies()
        for m in range(len(self.kMatrix)):
            for r1 in range(4):
                for r2 in range(4):
                    temp.append(self.kStrategies[r1][0])
                    temp.append(self.kStrategies[r2][1])
                    for x in range(2, self.numPlayers):
                        temp.append(kStrategies[kToProfile(m)[x]][x])
                        
                    self.kMatrix[m][r1][r2] = temp
                    
                    inOutcomes = False
                    for n in range(len(self.kOutcomes)):
                        if self.kOutcomes[n] == temp:
                            inOutcomes = True
                    if not inOutcomes:
                        self.kOutcomes.append(temp)
                    temp = []
        
        self.computeOutcomeProbabilities()
        
        EU = self.computeKExpectedUtilities()
                
        self.probabilizeKChoices()
        print()
        for x in range(self.numPlayers):
            print("EU_" + str(x) + " = " + str(EU[x]))
        
    def computeKOutcomes(self):
        """Computes kOutcomes
        """
        curEntry = []
        temp = []
        inOutcomes = False
        probability = -1.0
        EU = [0.0 for x in range(self.numPlayers)]
        self.kOutcomes = []
        self.computeKStrategies()
        for m in range(len(self.kMatrix)):
            for r1 in range(4):
                for r2 in range(4):
                    temp.append(self.kStrategies[r1][0])
                    temp.append(self.kStrategies[r2][1])
                    for x in range(2, self.numPlayers):
                        temp.append(kStrategies[kToProfile(m)[x]][x])
                    
                    inOutcomes = False
                    for n in range(len(self.kOutcomes)):
                        if self.kOutcomes[n] == temp:
                            inOutcomes = True
                    if not inOutcomes:
                        self.kOutcomes.append(temp)
                    temp = []
    
    def computeKStrategies(self):
        """Computes the strategies that would be chosen for each rationality level
        """
        self.computeBestResponses()
        maxStrat = -10000000
        num = -1
        others = []
        
        for r in range(4):
            for x in range(self.numPlayers):
                maxStrat = -10000000
                
                if r == 0:
                    num = self.maxStrat(x) # num is what player x will do at L_0
                    self.kStrategies[0][x] = num
                else:
                    # FIXME: finish after writing maxStrat function
                    others = [0 for y in range(self.numPlayers)]
                    for y in range(self.numPlayers):
                        if y == x:
                            others[y] = -1
                        else:
                            others[y] = self.kStrategies[r - 1][y]
                            
                    # Finding the maximum in each row/column/array that has already been chosen
                    if x == 0:
                        for i in range(self.players[x].numStrats):
                            if self.payoffMatrix[self.toIndex(others)][i][others[1]].getListNode(x).bestResponse:
                                maxStrat = i
                    elif x == 1:
                        for j in range(self.players[x].numStrats):
                            if self.payoffMatrix[self.toIndex(others)][others[0]][j].getListNode(x).bestResponse:
                                maxStrat = j
                    else: # x > 1
                        for m in range(len(self.payoffMatrix)):
                            for i in range(self.players[0].numStrats):
                                for j in range(self.players[1].numStrats):
                                    if self.payoffMatrix[m][others[0]][others[1]].getListNode(x).bestResponse:
                                        maxStrat = self.toProfile(m)[x]
                    self.kStrategies[r][x] = maxStrat
                if r == self.players[x].rationality:
                    self.players[x].kChoice = self.kStrategies[r][x]
        return

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
    
    def computeOutcomeProbabilities(self):
        self.computeKStrategies()
        self.computeKOutcomes()

        self.outcomeProbabilities = [0.0 for n in range(len(self.kOutcomes))]
        
        for r1 in range(4):
            for r2 in range(4):
                probability = 0.0
                
                # find which outcome the kMatrix entry corresponds to
                index = 0 
                while self.kOutcomes[index][0] != self.kStrategies[r1][0] or self.kOutcomes[index][1] != self.kStrategies[r2][1]:
                    index += 1
                
                probability += self.rationalityProbabilities[r1] * self.rationalityProbabilities[r2]
                
                self.outcomeProbabilities[index] += probability
 
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
    
    def eliminateStrictlyDominatedStrategies_full(self):
        self.originalNumPlayers = self.numPlayers
        self.originalNumStrats = [self.players[x].numStrats for x in range(self.numPlayers)]
        self.originalPayoffMatrix = self.payoffMatrix
        
        self.removedCols = []
        self.removedMatrices = []
        self.removedRows = []
        
        strategyIndices = [[k for k in range(self.players[x].numStrats)] for x in range(self.numPlayers)]
        # pairs[x] contains numPlayers-long tuples of strategy indices
        # pairs[x][0] and pairs[x][1] are the strategies being compared
        pairs = [combinations(strategyIndices[x], r=2) for x in range(self.numPlayers)]
        numCombos = [sum(1 for pair in pairs[x]) for x in range(self.numPlayers)]
        greaterThanFound = [False for x in range(self.numPlayers)]
        lessThanFound = [False for x in range(self.numPlayers)]
        equalFound = [False for x in range(self.numPlayers)]
        multipleStrats = [True for x in range(self.numPlayers)]
        oneWithMultipleStrats = False
        for ms in multipleStrats:
            if ms:
                oneWithMultipleStrats = True
                break
        stratRemoved = [True for x in range(self.numPlayers)]
        oneStratRemoved = False
        for sr in stratRemoved:
            if sr:
                oneStratRemoved = True
                break
        checked = [False for x in range(self.numPlayers)]
        oneNotChecked = False
        for p in checked:
            if not p:
                oneNotChecked = True
                break
        x = -1
        k = 0
        # Stop when you can't eliminate a strategy for either player or when only one strategy is left for each players or when all players have been checked
        # Stop when all players have only one strat or when all players' strategies have been checked...or when there isn't a strat that can be removed? No, when we remove a strat, we should check all other player's strategies. 
        # Continue if one player has multiple strategies and one player hasn't been checked and you can eliminate a strategy for one player
        oneWithMultipleStratsAndNotChecked = False
        for x in range(self.numPlayers):
            if multipleStrats[x] and not checked[x]:
                oneWithMultipleStratsAndNotChecked = True
                break
        while oneWithMultipleStratsAndNotChecked:
            x += 1
            for y in range(self.numPlayers):
                stratRemoved[y] = False
            # recomputing the pairs that need to be checked because the number of strategies may have changed
            strategyIndices = [[k for k in range(self.players[y].numStrats)] for y in range(self.numPlayers)]
            pairs = [combinations(strategyIndices[y], r=2) for y in range(self.numPlayers)]
            numCombos = [sum(1 for pair in pairs[y]) for y in range(self.numPlayers)]
            pairs = [combinations(strategyIndices[y], r=2) for y in range(self.numPlayers)]
            
            numMatrices = 1
            for y in range(2, self.numPlayers):
                numMatrices *= self.players[y].numStrats
            
            multipleStrats = [True for y in range(self.numPlayers)]
            for y in range(self.numPlayers):
                if self.players[y].numStrats == 1:
                    multipleStrats[y] = False
            stratRemoved = [False for x in range(self.numPlayers)]
            oneNotChecked = True
            
            # if the player has multiple strats and hasn't been checked
            if multipleStrats[x % self.numPlayers] and not checked[x % self.numPlayers]:
                checked[x % self.numPlayers] = True
                if x % self.numPlayers == 0:
                    for pair in pairs[x % self.numPlayers]:
                        greaterThanFound[0] = False
                        lessThanFound[0] = False
                        equalFound[0] = False
                        # Searching for < or > among the payoffs
                        # Fixing all other player's strategies
                        for m in range(numMatrices):  
                            for j in range(self.players[1].numStrats):
                                # if p1 has only one strategy lef
                                if len(self.payoffMatrix[0]) == 1: 
                                    multipleStrats1 = False
                                    break
                                # Comparing two payoffs
                                if self.payoffMatrix[m][pair[0]][j].getListNode(x % self.numPlayers).payoff < self.payoffMatrix[m][pair[1]][j].getListNode(x % self.numPlayers).payoff:
                                    lessThanFound[x % self.numPlayers] = True
                                elif self.payoffMatrix[m][pair[0]][j].getListNode(x % self.numPlayers).payoff > self.payoffMatrix[m][pair[1]][j].getListNode(x % self.numPlayers).payoff:
                                    greaterThanFound[x % self.numPlayers] = True
                                else: # equal payoffs found
                                    equalFound[x % self.numPlayers] = True
                                    break
                        
                        # Removing strategies based on the results
                        if lessThanFound[x % self.numPlayers] and not greaterThanFound[x % self.numPlayers] and not equalFound[x % self.numPlayers]: # remove strategy pair[0]
                            self.removeStrategy(x % self.numPlayers, pair[0])
                            strategyIndices[x % self.numPlayers].pop()
                            stratRemoved[x % self.numPlayers] = True
                            for y in range(self.numPlayers):
                                if y != x % self.numPlayers:
                                    checked[y] = False
                        elif greaterThanFound[x % self.numPlayers] and not lessThanFound[x % self.numPlayers] and not equalFound[x % self.numPlayers]: # remove strategy pair[1]
                            self.removeStrategy(x % self.numPlayers, pair[1])
                            strategyIndices[x % self.numPlayers].pop()
                            stratRemoved[x % self.numPlayers] = True
                            for y in range(self.numPlayers):
                                if y != x % self.numPlayers:
                                    checked[y] = False
                        else: # (not lessThanFound[x % self.numPlayers] and not greaterThanFound[x % self.numPlayers])(all equal) or (lessThanFound[x % self.numPlayers] and greaterThanFound[x % self.numPlayers])(no dominance)
                            stratRemoved[x % self.numPlayers] = False
                        
                        if stratRemoved[x % self.numPlayers]:
                            break
                elif x % self.numPlayers == 1:
                    for pair in pairs[x % self.numPlayers]:
                        greaterThanFound[1] = False
                        lessThanFound[1] = False
                        equalFound[1] = False
                        # Searching for < or > among the payoffs
                        # Fixing all other player's strategies
                        for m in range(numMatrices):
                            for i in range(self.players[0].numStrats):
                                if len(self.payoffMatrix[m][pair[0]]) == 1: # if p2 only has one strategy left
                                    multipleStrats2 = False
                                    break
                                # Comparing two payoffs
                                if self.payoffMatrix[m][i][pair[0]].getListNode(x % self.numPlayers).payoff < self.payoffMatrix[m][i][pair[1]].getListNode(x % self.numPlayers).payoff:
                                    lessThanFound[x % self.numPlayers] = True
                                elif self.payoffMatrix[m][i][pair[0]].getListNode(x % self.numPlayers).payoff > self.payoffMatrix[m][i][pair[1]].getListNode(x % self.numPlayers).payoff:
                                    greaterThanFound[x % self.numPlayers] = True
                                else: # equal payoffs were found
                                    equalFound[x % self.numPlayers] = True
                                    break
                        
                        # Removing strategies based on the results
                        if lessThanFound[x % self.numPlayers] and not greaterThanFound[x % self.numPlayers] and not equalFound[x % self.numPlayers]: # remove strategy pair[0]
                            self.removeStrategy(x % self.numPlayers, pair[0])
                            strategyIndices[x % self.numPlayers].pop()
                            stratRemoved[x % self.numPlayers] = True
                            for y in range(self.numPlayers):
                                if y != x % self.numPlayers:
                                    checked[y] = False
                        elif greaterThanFound[x % self.numPlayers] and not lessThanFound[x % self.numPlayers] and not equalFound[x % self.numPlayers]: # remove strategy pair[1]
                            self.removeStrategy(x % self.numPlayers, pair[1])
                            strategyIndices[x % self.numPlayers].pop()
                            stratRemoved[x % self.numPlayers] = True
                            for y in range(self.numPlayers):
                                if y != x % self.numPlayers:
                                    checked[y] = False
                        else: # (not lessThanFound[1] and not greaterThanFound[1]) or (lessThanFound[1] and greaterThanFound[1])
                            stratRemoved[x % self.numPlayers] = False
                        
                        if stratRemoved[x % self.numPlayers]:
                            break
                else: # x > 1
                    greaterThanFound[x % self.numPlayers] = False
                    lessThanFound[x % self.numPlayers] = False
                    equalFound[x % self.numPlayers] = False
                    for pair in pairs[x % self.numPlayers]:
                        greaterThanFound[x % self.numPlayers] = False
                        lessThanFound[x % self.numPlayers] = False
                        equalFound[x % self.numPlayers] = False
                        # Searching for < or > among the payoffs
                        # Fixing all other player's strategies
                        firstProfile1 = [0 for y in range(self.numPlayers)]
                        firstProfile2 = [0 for y  in range(self.numPlayers)]
                        firstProfile1[x % self.numPlayers] = pair[0] # start at the first array for the first strategy
                        firstProfile2[x % self.numPlayers] = pair[1] # start at the first array for the second strategy
                        m1 = self.toIndex(firstProfile1)
                        m2 = self.toIndex(firstProfile2)
                        product = 1
                        
                        # Getting the number of matrices to compare
                        numToCompare = 1
                        for y in range(2, self.numPlayers):
                            if y != x % self.numPlayers:
                                numToCompare *= self.players[y].numStrats
                                
                        numCompared = 0
                        while numCompared < numToCompare:
                            # Comparing
                            for i in range(self.players[0].numStrats):
                                for j in range(self.players[1].numStrats):
                                    if self.payoffMatrix[m1][i][j].getListNode(x % self.numPlayers).payoff < self.payoffMatrix[m2][i][j].getListNode(x % self.numPlayers).payoff:
                                        lessThanFound[x % self.numPlayers] = True
                                    elif self.payoffMatrix[m1][i][j].getListNode(x % self.numPlayers).payoff > self.payoffMatrix[m2][i][j].getListNode(x % self.numPlayers).payoff:
                                        greaterThanFound[x % self.numPlayers] = True
                                    else: # equal payoffs found
                                        equalFound[x % self.numPlayers] = True
                            numCompared += 1
                                    
                            # Move both profiles to the next matrix in the section
                            # obtaining the next profile in the sequence
                            if x % self.numPlayers == 2 and self.numPlayers > 3:
                                product = self.players[x % self.numPlayers].numStrats
                            else:
                                allBelowPlayerAtMaxStrat = True
                                m1Profile = self.toProfile(m1)
                                for y in range(2, x % self.numPlayers):
                                    if m1Profile[y] != self.players[y].numStrats - 1:
                                        allBelowPlayerAtMaxStrat = False
                                if m1Profile[x % self.numPlayers] == pair[0] and allBelowPlayerAtMaxStrat:
                                    productBelowPlayer = 1
                                    for y in range(2, x):
                                        productBelowPlayer *= self.players[y].numStrats
                                    product += productBelowPlayer * (self.players[x % self.numPlayers].numStrats - 1)
                                else:
                                    product = 1
                            m1 += product
                            if x % self.numPlayers == 2 and self.numPlayers > 3:
                                product = self.players[x % self.numPlayers].numStrats
                            else:
                                allBelowPlayerAtMaxStrat = True
                                m2Profile = self.toProfile(m2)
                                for y in range(2, x % self.numPlayers):
                                    if m2Profile[y] != self.players[y].numStrats - 1:
                                        allBelowPlayerAtMaxStrat = False
                                if m2Profile[x % self.numPlayers] == pair[1] and allBelowPlayerAtMaxStrat:
                                    productBelowPlayer = 1
                                    for y in range(2, x % self.numPlayers):
                                        productBelowPlayer *= self.players[y].numStrats
                                    product += productBelowPlayer * (self.players[x % self.numPlayers].numStrats - 1)
                                else:
                                    product = 1
                            m2 += product
                                                        
                        # Removing strategies based on the results
                        if lessThanFound[x % self.numPlayers] and not greaterThanFound[x % self.numPlayers] and not equalFound[x % self.numPlayers]: # remove strategy pair[0]
                            self.removeStrategy(x % self.numPlayers, pair[0])
                            strategyIndices[x % self.numPlayers].pop()
                            stratRemoved[x % self.numPlayers] = True
                            for y in range(self.numPlayers):
                                if y != x % self.numPlayers:
                                    checked[y] = False
                        elif greaterThanFound[x % self.numPlayers] and not lessThanFound[x % self.numPlayers] and not equalFound[x % self.numPlayers]: # remove strategy pair[1]
                            self.removeStrategy(x % self.numPlayers, pair[1])
                            strategyIndices[x % self.numPlayers].pop()
                            stratRemoved[x % self.numPlayers] = True
                            for y in range(self.numPlayers):
                                if y != x % self.numPlayers:
                                    checked[y] = False
                        else: # (not lessThanFound[1] and not greaterThanFound[1]) or (lessThanFound[1] and greaterThanFound[1])
                            stratRemoved[x % self.numPlayers] = False
                        
                        if stratRemoved[x % self.numPlayers]:
                            break
                if self.players[x % self.numPlayers].numStrats == 1:
                    multipleStrats[x % self.numPlayers] = False
                oneWithMultipleStratsAndNotChecked = False
                for y in range(self.numPlayers):
                    if multipleStrats[y] and not checked[y]:
                        oneWithMultipleStratsAndNotChecked = True
                        break        
        return
    
    def eliminateStrictlyDominatedStrategies_step(self):
        if self.numIESDSSteps == 0:
            self.originalNumPlayers = self.numPlayers
            self.originalNumStrats = [self.players[x].numStrats for x in range(self.numPlayers)]
            self.originalPayoffMatrix = self.payoffMatrix
        
        self.removedMatrices = []
        self.removedRows = []
        self.removedCols = []
        self.numIESDSSteps += 1
        # strategyIndices[x] is the set of indices (0, 1, 2,...,numStrats[x] - 1) for the x-th player
        # strategyIndices[x][k] is the k-th strategy index for the x-th player
        strategyIndices = [[k for k in range(self.players[x].numStrats)] for x in range(self.numPlayers)]    
        pairs = [combinations(strategyIndices[x], r=2) for x in range(self.numPlayers)] # pairs of p(x + 1)'s strategies to compare; indices
        numCombos = [sum(1 for pair in pairs[x]) for x in range(self.numPlayers)]
        oneStratEliminated = False
        
        greaterThanFound = [False for y in range(self.numPlayers)]
        lessThanFound = [False for y in range(self.numPlayers)]
        equalFound = [False for y in range(self.numPlayers)]
        multipleStrats = [True for y in range(self.numPlayers)]
        for y in range(self.numPlayers):
            if self.players[y].numStrats == 1:
                multipleStrats[y] = False
        stratRemoved = [False for x in range(self.numPlayers)]
        oneNotChecked = True
        checked = [False for x in range(self.numPlayers)]
        oneNotChecked = False
        for p in checked:
            if not p:
                oneNotChecked = True
                break
        
        """
        We want to check player 1 first, then player 2, then player 3,... with the first click, then player numPlayers, then player 1, player 2, and so on with each succeeding click until we can't remove a strategy. 
        """
        # if not oneStratEliminated and the player has multiple strats and hasn't been checked
        
        oneWithMultipleStratsAndNotChecked = False
        for y in range(self.numPlayers):
            if multipleStrats[y] and not checked[y]:
                oneWithMultipleStratsAndNotChecked = True
                break
        x = 0
        while x < self.numPlayers and not oneStratEliminated and oneWithMultipleStratsAndNotChecked:
            # recomputing the pairs that need to be checked because the number of strategies may have changed
            strategyIndices = [[k for k in range(self.players[y].numStrats)] for y in range(self.numPlayers)]
            pairs = [combinations(strategyIndices[y], r=2) for y in range(self.numPlayers)]
            numCombos = [sum(1 for pair in pairs[y]) for y in range(self.numPlayers)]
            pairs = [combinations(strategyIndices[y], r=2) for y in range(self.numPlayers)]
            
            numMatrices = 1
            for y in range(2, self.numPlayers):
                numMatrices *= self.players[y].numStrats
            
            multipleStrats = [True for y in range(self.numPlayers)]
            for y in range(self.numPlayers):
                if self.players[y].numStrats == 1:
                    multipleStrats[y] = False
            stratRemoved = [False for y in range(self.numPlayers)]
            oneNotChecked = True
            
            # if the player has multiple strats and hasn't been checked
            if multipleStrats[x] and not checked[x]:
                checked[x] = True
                if x == 0:
                    for pair in pairs[x]:
                        greaterThanFound[0] = False
                        lessThanFound[0] = False
                        equalFound[0] = False
                        # Searching for < or > among the payoffs
                        # Fixing all other player's strategies
                        for m in range(numMatrices):  
                            for j in range(self.players[1].numStrats):
                                # if p1 has only one strategy lef
                                if len(self.payoffMatrix[0]) == 1: 
                                    multipleStrats1 = False
                                    break
                                # Comparing two payoffs
                                if self.payoffMatrix[m][pair[0]][j].getListNode(x).payoff < self.payoffMatrix[m][pair[1]][j].getListNode(x).payoff:
                                    lessThanFound[x] = True
                                elif self.payoffMatrix[m][pair[0]][j].getListNode(x).payoff > self.payoffMatrix[m][pair[1]][j].getListNode(x).payoff:
                                    greaterThanFound[x] = True
                                else: # equal payoffs found
                                    equalFound[x] = True
                                    break
                        
                        # Removing strategies based on the results
                        if lessThanFound[x] and not greaterThanFound[x] and not equalFound[x]: # remove strategy pair[0]
                            self.removeStrategy(x, pair[0])
                            oneStratEliminated = True
                            strategyIndices[x].pop()
                            stratRemoved[x] = True
                            for y in range(self.numPlayers):
                                if y != x:
                                    checked[y] = False
                        elif greaterThanFound[x] and not lessThanFound[x] and not equalFound[x]: # remove strategy pair[1]
                            self.removeStrategy(x, pair[1])
                            oneStratEliminated = True
                            strategyIndices[x].pop()
                            stratRemoved[x] = True
                            for y in range(self.numPlayers):
                                if y != x:
                                    checked[y] = False
                        else: # (not lessThanFound[x] and not greaterThanFound[x])(all equal) or (lessThanFound[x] and greaterThanFound[x])(no dominance)
                            stratRemoved[x] = False
                        
                        if stratRemoved[x]:
                            break
                elif x == 1:
                    for pair in pairs[x]:
                        greaterThanFound[1] = False
                        lessThanFound[1] = False
                        equalFound[1] = False
                        # Searching for < or > among the payoffs
                        # Fixing all other player's strategies
                        for m in range(numMatrices):
                            for i in range(self.players[0].numStrats):
                                if len(self.payoffMatrix[m][pair[0]]) == 1: # if p2 only has one strategy left
                                    multipleStrats2 = False
                                    break
                                # Comparing two payoffs
                                if self.payoffMatrix[m][i][pair[0]].getListNode(x).payoff < self.payoffMatrix[m][i][pair[1]].getListNode(x).payoff:
                                    lessThanFound[x] = True
                                elif self.payoffMatrix[m][i][pair[0]].getListNode(x).payoff > self.payoffMatrix[m][i][pair[1]].getListNode(x).payoff:
                                    greaterThanFound[x] = True
                                else: # equal payoffs were found
                                    equalFound[x] = True
                                    break
                        
                        # Removing strategies based on the results
                        if lessThanFound[x] and not greaterThanFound[x] and not equalFound[x]: # remove strategy pair[0]
                            self.removeStrategy(x, pair[0])
                            oneStratEliminated = True
                            strategyIndices[x].pop()
                            stratRemoved[x] = True
                            for y in range(self.numPlayers):
                                if y != x:
                                    checked[y] = False
                        elif greaterThanFound[x] and not lessThanFound[x] and not equalFound[x]: # remove strategy pair[1]
                            self.removeStrategy(x, pair[1])
                            oneStratEliminated = True
                            strategyIndices[x].pop()
                            stratRemoved[x] = True
                            for y in range(self.numPlayers):
                                if y != x:
                                    checked[y] = False
                        else: # (not lessThanFound[1] and not greaterThanFound[1]) or (lessThanFound[1] and greaterThanFound[1])
                            stratRemoved[x] = False
                        
                        if stratRemoved[x]:
                            break
                else: # x > 1
                    greaterThanFound[x] = False
                    lessThanFound[x] = False
                    equalFound[x] = False
                    for pair in pairs[x]:
                        greaterThanFound[x] = False
                        lessThanFound[x] = False
                        equalFound[x] = False
                        # Searching for < or > among the payoffs
                        # Fixing all other player's strategies
                        firstProfile1 = [0 for y in range(self.numPlayers)]
                        firstProfile2 = [0 for y  in range(self.numPlayers)]
                        firstProfile1[x] = pair[0] # start at the first array for the first strategy
                        firstProfile2[x] = pair[1] # start at the first array for the second strategy
                        m1 = self.toIndex(firstProfile1)
                        m2 = self.toIndex(firstProfile2)
                        product = 1
                        
                        # Getting the number of matrices to compare
                        numToCompare = 1
                        for y in range(2, self.numPlayers):
                            if y != x:
                                numToCompare *= self.players[y].numStrats
                                
                        numCompared = 0
                        while numCompared < numToCompare:
                            # Comparing
                            for i in range(self.players[0].numStrats):
                                for j in range(self.players[1].numStrats):
                                    if self.payoffMatrix[m1][i][j].getListNode(x).payoff < self.payoffMatrix[m2][i][j].getListNode(x).payoff:
                                        lessThanFound[x] = True
                                    elif self.payoffMatrix[m1][i][j].getListNode(x).payoff > self.payoffMatrix[m2][i][j].getListNode(x).payoff:
                                        greaterThanFound[x] = True
                                    else: # equal payoffs found
                                        equalFound[x] = True
                            numCompared += 1
                                    
                            # Move both profiles to the next matrix in the section
                            # obtaining the next profile in the sequence
                            if x == 2 and self.numPlayers > 3:
                                product = self.players[x].numStrats
                            else:
                                allBelowPlayerAtMaxStrat = True
                                m1Profile = self.toProfile(m1)
                                for y in range(2, x):
                                    if m1Profile[y] != self.players[y].numStrats - 1:
                                        allBelowPlayerAtMaxStrat = False
                                if m1Profile[x] == pair[0] and allBelowPlayerAtMaxStrat:
                                    productBelowPlayer = 1
                                    for y in range(2, x):
                                        productBelowPlayer *= self.players[y].numStrats
                                    product += productBelowPlayer * (self.players[x].numStrats - 1)
                                else:
                                    product = 1
                            m1 += product
                            if x == 2 and self.numPlayers > 3:
                                product = self.players[x].numStrats
                            else:
                                allBelowPlayerAtMaxStrat = True
                                m2Profile = self.toProfile(m2)
                                for y in range(2, x):
                                    if m2Profile[y] != self.players[y].numStrats - 1:
                                        allBelowPlayerAtMaxStrat = False
                                if m2Profile[x] == pair[1] and allBelowPlayerAtMaxStrat:
                                    productBelowPlayer = 1
                                    for y in range(2, x):
                                        productBelowPlayer *= self.players[y].numStrats
                                    product += productBelowPlayer * (self.players[x].numStrats - 1)
                                else:
                                    product = 1
                            m2 += product
                                                        
                        # Removing strategies based on the results
                        if lessThanFound[x] and not greaterThanFound[x] and not equalFound[x]: # remove strategy pair[0]
                            self.removeStrategy(x, pair[0])
                            oneStratEliminated = True
                            strategyIndices[x].pop()
                            stratRemoved[x] = True
                            for y in range(self.numPlayers):
                                if y != x:
                                    checked[y] = False
                        elif greaterThanFound[x] and not lessThanFound[x] and not equalFound[x]: # remove strategy pair[1]
                            self.removeStrategy(x, pair[1])
                            strategyIndices[x].pop()
                            stratRemoved[x] = True
                            for y in range(self.numPlayers):
                                if y != x:
                                    checked[y] = False
                        else: # (not lessThanFound[1] and not greaterThanFound[1]) or (lessThanFound[1] and greaterThanFound[1])
                            stratRemoved[x] = False
                        
                        if stratRemoved[x]:
                            break
            
            if self.players[x].numStrats == 1:
                multipleStrats[x] = False
            oneWithMultipleStratsAndNotChecked = False
            for y in range(self.numPlayers):
                if multipleStrats[y] and not checked[y]:
                    oneWithMultipleStratsAndNotChecked = True
                    break
            x += 1
        return
    
    def enterData(self, numPlayers = 2, numStrats = [2, 2], payoffs = [
        [[1, 5], [2, 6]],
        [[3, 7], [4, 8]]
    ]):        
        oldNumPlayers = self.numPlayers
        oldNumStrats = [self.players[x].numStrats for x in range(oldNumPlayers)]
        self.numPlayers = numPlayers
        
        if self.numPlayers <= oldNumPlayers:
            for x in range(self.numPlayers):
                self.players[x].numStrats = numStrats[x]
        else: # self.numPlayers > oldNumPlayers:
            for x in range(oldNumPlayers):
                self.players[x].numStrats = numStrats[x]
            for x in range(self.numPlayers - oldNumPlayers):
                self.players.append(Player(numStrats[oldNumPlayers + x]))
        
        # ensuring that the payoffs are a list of matrices
        if type(payoffs[0][0][0]).__name__ == "float":
            payoffs = [payoffs]
        
        self.payoffMatrix = []
        numMatrices = 1
        for x in range(2, numPlayers):
            numMatrices *= numStrats[x]
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
                    self.strategyNames.append(["L(" + str(x + 1) + ")", "R(" + str(x + 1) + ")"])
                else: 
                    self.strategyNames.append(["L(" + str(x + 1) + ")"] + ["C(" + str(x + 1) + ", " + str(s + 1) + ")" for s in range(self.players[x].numStrats)] + ["R(" + str(x + 1) + ")"])
        
    def isBestResponse(self, profile):
        """Checks whether p1Strat and p2Strat are best responses relative to each other

        Args:
            profile (int): the strategies to be checked
        """
        br = [True for x in range(self.numPlayers)]
        if self.numPlayers < 3:
            for i in chain(range(profile[0]), range(profile[0] + 1, self.players[0].numStrats)):
                if self.payoffMatrix[0][profile[0]][profile[1]].getListNode(0).payoff < self.payoffMatrix[0][i][profile[1]].getListNode(0).payoff:
                    br[0] = False
            
            for j in chain(range(profile[1]), range(profile[1] + 1, self.players[1].numStrats)):
                if self.payoffMatrix[0][profile[0]][profile[1]].getListNode(1).payoff < self.payoffMatrix[0][profile[0]][j].getListNode(1).payoff:
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
    
    def kToProfile(self, m):
        """Converts an index in a list of payoff arrays into the strategy profile that produces that index
        """
        rationality = 0
        previousValues = 0
        product = 1
        rationalityProfile = [-1, -1] + [0 for x in range(2, self.numPlayers)]
        
        product = 4 ** (self.numPlayers - 3)
        
        for x in range(self.numPlayers - 1, 1, -1):
            rationality = 0
            while product * rationality + previousValues < m and rationality != 4:
                rationality += 1
                
            if product * rationality + previousValues > m:
                rationality -= 1
                
            previousValues += product * rationality
            rationalityProfile[x] = rationality
            product = product / 4
            
        return rationalityProfile
    
    def maxStrat(self, x):
        """Returns the strategy that gives player x + 1's maximum payoff over all outcomes
        
        Args:
            x (int): the player index        
        """
        maxStrat = 0
        maxVal = -10000000
        curList = ListNode()
        
        if x == 0:
            for m in range(len(self.payoffMatrix)):
                for i in range(self.players[0].numStrats):
                    for j in range(self.players[1].numStrats):
                        curList = self.payoffMatrix[m][i][j]
                        if curList.getListNode(x).payoff > maxVal:
                            maxVal = curList.getListNode(x).payoff
                            maxStrat = i
        elif x == 1:
            for m in range(len(self.payoffMatrix)):
                for i in range(self.players[0].numStrats):
                    for j in range(self.players[1].numStrats):
                        curList = self.payoffMatrix[m][i][j]
                        if curList.getListNode(x).payoff > maxVal:
                            maxVal = curList.getListNode(x).payoff
                            maxStrat = j
        else: # x > 1
            for m in range(len(self.payoffMatrix)):
                for i in range(self.players[0].numStrats):
                    for j in range(self.players[1].numStrats):
                        curList = self.payoffMatrix[m][i][j]
                        if curList.getListNode(x).payoff > maxVal:
                            maxVal = curList.getListNode(x).payoff
                            maxStrat = self.toProfile(m)[x]
        return maxStrat
    
    def paretoOptimal(self, profile):
        """Checks if an outcome is Pareto optimal
        
        Args:
            profile (list): the strategy profile for the outcome in question
        """
        curList = ListNode()
        curProfile = self.payoffMatrix[self.toIndex(profile)][profile[0]][profile[1]]
        # (-->)
        onePlayerWorseOff = True
        # (<--)
        # onePlayerBetterOff = True
        # count = 0
        # (-->)
        betterOutcomes = []
        betterOffPlayers = []
        worseOff = []
        # (<--)
        worseOutcomes = []
        worseOffPlayers = []
        betterOff = []
        
        comparing = [0 for x in range(self.numPlayers)]
        for m in range(len(self.payoffMatrix)):
            comparing = self.toProfile(m)
            for i in range(self.players[0].numStrats):
                comparing[0] = i
                for j in range(self.players[1].numStrats):
                    comparing[1] = j
                    if comparing != profile:
                        foundOneBetter = False
                        foundOneWorse = False
                        x = 0
                        while (not foundOneBetter or not foundOneWorse) and x < self.numPlayers:
                            curList = self.payoffMatrix[m][i][j]
                            curProfile = self.payoffMatrix[self.toIndex(profile)][profile[0]][profile[1]]
                        
                            if curProfile.getListNode(x).payoff < curList.getListNode(x).payoff:
                                foundOneBetter = True
                                betterOffPlayers.append(x)
                                betterOutcomes.append(self.toProfile(m))
                                # first two are -1
                                betterOutcomes[len(betterOutcomes) - 1][0] = i
                                betterOutcomes[len(betterOutcomes) - 1][1] = j
                                worseOff.append(False)
                            elif curProfile.getListNode(x).payoff > curList.getListNode(x).payoff:
                                foundOneWorse = True
                                worseOffPlayers.append(x)
                                worseOutcomes.append(self.toProfile(m))
                                # first two are -1
                                worseOutcomes[len(worseOutcomes) - 1][0] = i
                                worseOutcomes[len(worseOutcomes) - 1][1] = j
                                betterOff.append(False)
                            x += 1
        
        # determine if at least one other player is worse off at each outcome found
        if len(betterOutcomes) > 0:
            if len(worseOutcomes) <= 0:
                return False
            
            n = 0
            while n < len(worseOff) and not worseOff[n]:
                for x in range(self.numPlayers):
                    if betterOffPlayers[n] != x:
                        curList = self.payoffMatrix[self.toIndex(betterOutcomes[n])][betterOutcomes[n][0]][betterOutcomes[n][1]]
                        curProfile = self.payoffMatrix[self.toIndex(profile)][profile[0]][profile[1]]

                        if curList.getListNode(x).payoff < curProfile.getListNode(x).payoff:
                            worseOff[n] = True
                n += 1
            n = 0
            while n < len(worseOff) and onePlayerWorseOff:
                if not worseOff[n]:
                    onePLayersWorseOff = False
                n += 1
            
            if onePlayerWorseOff:
                return True
            else:
                return False
        else:
            return True
    
    def print(self):
        """Prints the payoff matrix
        """
        for m in range(len(self.payoffMatrix)):
            for i in range(self.players[0].numStrats):
                for j in range(self.players[1].numStrats):
                    self.payoffMatrix[m][i][j].print() # print the linked list in self.payoffMatrix[m][i][j]
                    if j < self.players[1].numStrats - 1:
                        print("  ", end="")
                    else:
                        print()
            if m < len(self.payoffMatrix) - 1:
                print()
                
    def printKMatrix(self, probabilities = [0.25, 0.25, 0.25, 0.25]):
        self.rationalityProbabilities = probabilities
        curEntry = []
        temp = []
        inOutcomes = False
        self.kOutcomes = []
        self.outcomeProbabilities = []        
        self.computeKMatrix(probabilities)
        print()
        for m in range(len(self.kMatrix)):            
            for r1 in range(4):
                for r2 in range(4):
                    curEntry = self.kMatrix[m][r1][r2]
                    print("(", end="")
                    for x in range(self.numPlayers):
                        print(curEntry[x], end="")
                        if x < self.numPlayers - 1:
                            print(", ", end="")
                    print(")", end="")
                    if r2 < 3:
                        print(" ", end="")
                print()
            print()

    def printBestResponses(self):
        """Prints the payoff matrix
        """
        self.computeBestResponses()
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
    
    def probabilizeKChoices(self):
        self.computeKStrategies()    
        self.computeOutcomeProbabilities()

        choices = [0 for x in range(self.numPlayers)]
        for x in range(self.numPlayers):
            choices[x] = self.kStrategies[self.players[x].rationality][x]
            self.players[x].kChoice = choices[x]
        
        for n in range(len(self.kOutcomes)):
            print("P(", end="")
            for x in range(self.numPlayers):
                print(self.kOutcomes[n][x], end="")
                if x < self.numPlayers - 1:
                    print(", ", end="")
            print(") = " + str(self.outcomeProbabilities[n]))
        
        return

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
            self.removedRows.append(s)
            for m in range(len(self.payoffMatrix)):
                del self.payoffMatrix[m][s]
        elif player == 1: # x is player 2
            self.removedCols.append(s)
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
                self.removedMatrices.append(m - numDeleted)
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
    
    def resetStrategyNames(self):
        self.strategyNames = []
        
        if self.players[0].numStrats < 3:
            self.strategyNames.append(["U", "D"])
        else:
            middle = []
            if self.players[0].numStrats == 3:
                middle = ["M"]
            else: # [0].numStrats > 3
                middle = ["M" + str(i) for i in range(1, self.players[0].numStrats - 1)]
            self.strategyNames.append(["U"] + middle + ["D"])
        if self.players[1].numStrats < 3:
            self.strategyNames.append(["L", "R"])
        else:
            center = []
            if self.players[1].numStrats == 3:
                center = ["C"]
            else: # [1].numStrats > 3
                center = ["C" + str(j) for j in range(1, self.players[1].numStrats - 1)]
            self.strategyNames.append(["L"] + center + ["R"])
        if self.numPlayers > 2:
            for x in range(2, self.numPlayers):
                center = []
                if self.players[x].numStrats < 3:
                    center = []
                elif self.players[x].numStrats == 3:
                    center = ["C(" + str(x + 1) + ")"]
                else:
                    center = ["C(" + str(x + 1) + ", " + str(s) + ")" for s in range(1, self.players[x].numStrats - 1)]
                self.strategyNames.append(["L(" + str(x + 1) + ")"] + center + ["R(" + str(x + 1) + ")"])
        print("HERE:", self.strategyNames)
        return
    
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
    [
        [[1, 5], [2, 6]],
        [[3, 7], [4, 8]]
    ]
]

bos = [
    [
        [[2, 1], [0, 0]],
        [[0, 0], [1, 2]]
    ]
]

rps = [
    [
        [[0, 0], [-1, 1], [1, -1]],
        [[1, -1], [0, 0], [-1, 1]],
        [[-1, 1], [1, -1], [0, 0]]
    ]
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

iesds = [
    [
        [[13, 3], [1, 4], [7, 3]],
        [[4, 1], [3, 3], [6, 2]],
        [[-1, 9], [2, 8], [8, -1]]
    ]
]

iesds_3 = [
    [
        [[5, 2, 1], [3, 4, 1]],
        [[1, 6, 1], [7, 8, 1]]
    ],
    [
        [[9, 10, 2], [11, 12, 2]],
        [[13, 14, 2], [15, 16, 2]]
    ]
]

freeMoney = [
    [
        [[1, 0], [0, 0]],
        [[0, 0], [0, 0]]
    ]
]

krmodel = [
    [
        [[2, 12], [5, 6], [9, 0]],
        [[0, 24], [19, 5], [10, 10]],
        [[1, 3], [7, 5], [5, 25]],
    ]
]

# o1 = ListNode()
# o2 = ListNode()
# o1 = o1.load([10, 10])
# o2 = o2.load([20, 20])
# append_2 = [
#     [[10, 10], [20, 20]]
# ]

# G = SimGame(2)
# G.enterData(2, [3, 3], krmodel)
# G.print()
# print()
# G.printKMatrix(probabilities=[0.1, 0.4, 0.4, 0.1])

# o1 = ListNode()
# o2 = ListNode()
# o3 = ListNode()
# o4 = ListNode()
# o5 = ListNode()
# o6 = ListNode()
# o7 = ListNode()
# o8 = ListNode()
# o9 = ListNode()
# o1 = o1.load([1, 1, 1])
# o2 = o2.load([2, 2, 2])
# o3 = o3.load([3, 3, 3])
# o4 = o4.load([4, 4, 4])
# o5 = o5.load([5, 5, 5])
# o6 = o6.load([6, 6, 6])
# o7 = o7.load([7, 7, 7])
# o8 = o8.load([8, 8, 8])
# o9 = o9.load([9, 9, 9])

# append_3 = [
#     [o1, o2],
#     [o3, o4]
# ]

# append_3_player3 = [
#     [
#         [o2, o2, o3],
#         [o4, o5, o6], 
#         [o7, o8, o9]
#     ]
# ]

# second = [
#     [
#         [[1, 1, 1], [2, 2, 2], [3, 3, 3]],
#         [[4, 4, 4], [5, 5, 5], [6, 6, 6]],
#         [[7, 7, 7], [8, 8, 8], [9, 9, 9]]
#     ]
# ]

# H = SimGame(3)
# H.appendStrategy(2, second)
# H.print()

# o1 = ListNode()
# o2 = ListNode()
# o1 = o1.load([1, 1, 1, 1, 1])
# o2 = o2.load([2, 2, 2, 2, 2])
# o3 = ListNode()
# o4 = ListNode()
# o3 = o3.load([3, 3, 3, 3, 3])
# o4 = o4.load([4, 4, 4, 4, 4])
# o5 = ListNode()
# o6 = ListNode()
# o7 = ListNode()
# o8 = ListNode()
# o9 = ListNode()
# o10 = ListNode()
# o11 = ListNode()
# o12 = ListNode()
# o13 = ListNode()
# o14 = ListNode()
# o15 = ListNode()
# o16 = ListNode()
# o5 = o5.load([5, 5, 5, 5, 5])
# o6 = o5.load([6, 6, 6, 6, 6])
# o7 = o5.load([7, 7, 7, 7, 7])
# o8 = o5.load([8, 8, 8, 8, 8])
# o9 = o9.load([9, 9, 9, 9, 9])
# o10 = o10.load([10, 10, 10, 10, 10])
# o11 = o11.load([11, 11, 11, 11, 11])
# o12 = o12.load([12, 12, 12, 12, 12])
# o13 = o13.load([13, 13, 13, 13, 13])
# o14 = o14.load([14, 14, 14, 14, 14])
# o15 = o15.load([15, 15, 15, 15, 15])
# o16 = o16.load([16, 16, 16, 16, 16])

# append_4 = [
#     [
#         [o1, o2],
#         [o3, o4]
#     ],
#     [
#         [o5, o6],
#         [o7, o8]
#     ],
#     [
#         [o9, o10],
#         [o11, o12]
#     ]
# ]

# I = SimGame(4)
# I.enterData(4, [2, 2, 3, 3], arr_4players)
# I.appendStrategy(3, append_4)
# I.print()

# append_5 = [
#     [
#         [o1, o2],
#         [o3, o4]
#     ],
#     [
#         [o5, o6],
#         [o7, o8]
#     ],
#     [
#         [o9, o10],
#         [o11, o12]
#     ],
#     [
#         [o13, o14],
#         [o15, o16]
#     ]
# ]

# J = SimGame(5)
# J.enterData(5, [2, 2, 2, 2, 2], arr_5players)
# J.appendStrategy(2, append_5)
# J.print()