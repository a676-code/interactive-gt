# pysimultaneous.py
# Author: Andrew Lounsbury
# Date: 3/20/24
# Description: a class for handling simultaneous games with n players, n >= 2

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
            while(curNode != None and pos + 1 != index):
                pos = pos + 1
                curNode = curNode.next
 
            if curNode != None:
                return curNode
            else:
                print("Index not present")

    def insertAtBeginning(self, payoff, bestResponse):
        newNode = ListNode(payoff, bestResponse)
        if self.head is None:
            self.head = newNode
            return
        else:
            newNode.next = self.head
            self.head = newNode
            
    def insertAtIndex(self, data, index):
        newNode = ListNode(data)
        curNode = self.head
        pos = 0
        if pos == index:
            self.insertAtBeginning(data)
        else:
            while curNode != None and pos + 1 != index:
                pos = pos + 1
                curNode = curNode.next
 
            if curNode != None:
                newNode.next = curNode.next
                curNode.next = newNode
            else:
                print("Index not present")
        
    def pop(self):
        """Removes the last node from the linked list
        """
        if self.head is None:
            return
    
        curNode = self.head
        while(curNode.next.next):
            curNode = curNode.next
    
        curNode.next = None
                
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
            while(curNode != None and pos + 1 != index):
                pos = pos + 1
                curNode = curNode.next
 
            if curNode != None:
                curNode.next = curNode.next.next
            else:
                print("Index not present")
                
    def decapitate(self):
        """Removes the head ListNode
        """
        if self.head == None:
            return
        
        self.head = self.head.next
    
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
            self.strategyNames.append(["U"] + ["M" + str(i) for i in range(1, self.players[0].numStrats)] + ["D"])
        if self.players[1].numStrats < 3:
            self.strategyNames.append(["L", "R"])
        else:
            self.strategyNames.append(["L"] + ["C" + str(i) for i in range(self.players[0].numStrats)] + ["R"])
        for x in range(2, self.numPlayers):
            if self.players[x].numStrats < 3:
                self.strategyNames.append(["L(" + str(x) + ")", "R(" + str(x) + ")"])
            else: 
                self.strategyNames.append(["L(" + str(x) + ")"] + ["C(" + str(x) + ", " + str(i) + ")" for i in range(self.players[0].numStrats)] + ["R(" + str(x) + ")"])
        
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
            for i in range(3, self.numPlayers):
                numMatrices *= self.players[i].numStrats
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
    
    def enterPayoffs(self, payoffs = [
        [[1, 5], [2, 6]],
        [[3, 7], [4, 8]]
    ], numPlayers = 2, numStrats = [2, 2]):
        self.numPlayers = numPlayers
        for x in range(self.numPlayers):
            self.players[x].numStrats = numStrats[x]
        
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
        
    def isBestResponse(self, p1Strat, p2Strat):
        """Checks whether p1Strat and p2Strat are best responses relative to each other

        Args:
            p1Strat (int): p1's strategy
            p2Strat (int): p2's strategy
        """
        p1BR = True
        p2BR = True
        
        if self.numPlayers < 3:
            for i in range(self.players[0].numStrats):
                if self.payoffMatrix[p1Strat][p2Strat].getListNode(0).payoff < self.payoffMatrix[i][p2Strat].getListNode(0).payoff:
                    p1BR = False
            
            for j in range(self.players[1].numStrats):
                if self.payoffMatrix[p1Strat][p2Strat].getListNode(1).payoff < self.payoffMatrix[p1Strat][j].getListNode(1).payoff:
                    p2BR = False
            return (p1BR, p2BR)
        else:
            for m in range(len(self.payoffMatrix)):
                for i in range(self.players[0].numStrats):
                    if self.payoffMatrix[p1Strat][p2Strat].getListNode(0).payoff < self.payoffMatrix[i][p2Strat].getListNode(0).payoff:
                        p1BR = False
                
                for j in range(self.players[1].numStrats):
                    if self.payoffMatrix[p1Strat][p2Strat].getListNode(1).payoff < self.payoffMatrix[p1Strat][j].getNode[1].payoff:
                        p2BR = False
    
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
            numDeleted = 0
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
# G.enterPayoffs(arr_2players, 2, [2, 2])
# G.print()
# G.removeStrategy(0, 0)
# G.print()

# H = SimGame(3)
# H.enterPayoffs(arr_3players, 3, [2, 2, 2])
# H.removeStrategy(0, 1)
# H.print()

# I = SimGame(4)
# I.enterPayoffs(arr_4players, 4, [2, 2, 3, 3])
# I.removeStrategy(0, 1)
# I.print()

# J = SimGame(5)
# J.enterPayoffs(arr_5players, 5, [2, 2, 3, 3, 3])
# J.removeStrategy(0, 1)
# print("J:")
# J.print()