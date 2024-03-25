# interactivegt.py
# Author: Andrew W. Lounsbury
# Date: 3/24/24
# Description: Creates a GUI for analyzing 2-player games as well as a database of axelrod matches
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import nashpy as nash
import axelrod as axl
import numpy as np
import sqlite3
from itertools import combinations
import pysimultaneous
from pysimultaneous import SimGame

# Function definitions
def addAllPairs():
    """
    Inserts a match between every possible pair of strategies with a set number of turns. 
    """
    conn = sqlite3.connect('match.db')
    c = conn.cursor()

    options = [s() for s in axl.strategies]
    Combos = combinations(options, r=2)
    for i, pair in enumerate(Combos):
        print("Inserting pair " + str(i))
        c.execute("INSERT INTO matches VALUES (:strategy1, :strategy2, :numTurns, :output, :score1, :score2)",
            {
                'strategy1': str(pair[0]),
                'strategy2': str(pair[1]),
                'numTurns': dbTurnsEntry.get(),
                'output': str(dbPlayMatch(pair[0], pair[1], int(dbTurnsEntry.get()))[0]), 
                'score1': dbPlayMatch(pair[0], pair[1], int(dbTurnsEntry.get()))[1][0], 
                'score2':dbPlayMatch(pair[0], pair[1], int(dbTurnsEntry.get()))[1][1]
            }
        )
        print("Inserting output " + str(dbPlayMatch(pair[0], pair[1], int(dbTurnsEntry.get()))[0]))
    # Inserting pairs (s, s) for each strategy s
    for strategy in options:
        c.execute("INSERT INTO matches VALUES (:strategy1, :strategy2, :numTurns, :output, :score1, :score2)",
            {
                'strategy1': str(strategy),
                'strategy2': str(strategy),
                'numTurns': dbTurnsEntry.get(),
                'output': str(dbPlayMatch(strategy, strategy, int(dbTurnsEntry.get()))[0]), 
                'score1': dbPlayMatch(strategy, strategy, int(dbTurnsEntry.get()))[1][0], 
                'score2': dbPlayMatch(strategy, strategy, int(dbTurnsEntry.get()))[1][1]
            }
        )
        print("Inserting output " + str(dbPlayMatch(strategy, strategy, int(dbTurnsEntry.get()))[0]))
    
    conn.commit()
    conn.close()
    return

def addToDBClicked(value):
    dbOutput.set(value)

def addRecord():
    conn = sqlite3.connect('match.db')
    c = conn.cursor()
    
    # Converting the string strategies from the dropdown menus into the actual strategy objects
    p1 = ""
    p2 = ""
    clicked1NoSpaces = dbClicked1.get().replace(" ", "")
    clicked2NoSpaces = dbClicked2.get().replace(" ", "")
    counter = 0
    while type(p1).__name__ == "str" and counter < len(axl.strategies):
        if type(options[counter]).__name__ == clicked1NoSpaces:
            p1 = options[counter]
        counter += 1
    counter = 0
    while type(p2).__name__ == "str" and counter < len(axl.strategies):
        if type(options[counter]).__name__ == clicked2NoSpaces:
            p2 = options[counter]
        counter += 1
    
    # """
    c.execute("INSERT INTO matches VALUES (:strategy1, :strategy2, :numTurns, :output, :score1, :score2)",
        {
            'strategy1': dbClicked1.get(),
            'strategy2': dbClicked2.get(),
            'numTurns': dbTurnsEntry.get(),
            'output': str(dbPlayMatch(p1, p2, int(dbTurnsEntry.get()))[0]),
            'score1': dbPlayMatch(p1, p2, int(dbTurnsEntry.get()))[1][0],
            'score2': dbPlayMatch(p1, p2, int(dbTurnsEntry.get()))[1][1]
        }
    )
    # """
    
    conn.commit()
    conn.close()

def changeBackgroundColor():
    """
        Changes the background color of the window
    """
    topColor = Toplevel()
    topColor.title("Enter a Color")
    topColor.iconbitmap("knight.ico")
    topColor.geometry("190x30")
    
    colorLabel = Label(topColor, text="Enter a color:")
    colorEntry = Entry(topColor, width=10)
    colorEnter = Button(topColor, text="Enter", command=lambda: enterColor(colorEntry.get()))
    
    # Putting everything on the topColor window
    colorLabel.grid(row=0, column=0)
    colorEntry.grid(row=0, column=1)
    colorEnter.grid(row=0, column=2, padx=5)
    return

def clearDB():
    conn = sqlite3.connect('match.db')
    c = conn.cursor()
    
    clearDBWarning = messagebox.askyesno("Warning", "Are you sure you want to clear the matches database?")
    
    if clearDBWarning == True:
        c.execute("DELETE FROM matches")
    
    conn.commit()
    conn.close()
    
def clearPayoffs():
    """
        Fills the payoff matrix with zeros and default strategy names
    """
    proceed = messagebox.askokcancel("Clear Payoffs?", "Are you sure you want to clear the payoffs?")
    if (proceed == True):
        numStrats1 = int(numStratsEntries[0].get())
        numStrats2 = int(numStratsEntries[1].get())
        
        # clearing the table
        payoffMatrixSlaves = payoffsFrame.grid_slaves()
        payoffs = payoffMatrixSlaves[:numStrats1 * numStrats2]
        for payoff in payoffs:
            payoff.grid_remove()
        
        # refilling the table
        rows = []
        for i in range(numStrats1):
            cols = []
            for j in range(numStrats2):
                e = Entry(payoffsFrame, width=5)
                e.grid(row=i + 1, column=j + 1, sticky=NSEW)
                cols.append(e)
            rows.append(cols)
            
        # Clearing the equilibria
        equilibriaSlaves = equilibriaFrame.grid_slaves()
        eqLabel = equilibriaSlaves[0]
        if type(eqLabel).__name__ == "Label":
            eqLabel.grid_remove()
        
        entriesToSimGame()
        root.geometry(f"{45 * numStrats2 + 700}x{25 * numStrats1 + 490}")
    return
    
def clearPayoffMatrix():
    """
        Fills the payoff matrix with zeros and default strategy names
    """
    proceed = messagebox.askokcancel("Clear Payoffs?", "Are you sure you want to clear the payoff matrix?")
    if (proceed == True):
        numStrats1 = int(numStratsEntries[0].get())
        numStrats2 = int(numStratsEntries[1].get())
        
        # clearing the table
        payoffMatrixSlaves = payoffsFrame.grid_slaves()
        for slave in payoffMatrixSlaves:
            slave.grid_remove()
        
        # refilling the table
        for i in range(numStrats2):
            e = Entry(payoffsFrame, width=10)
            e.grid(row=0, column=i + 1, pady=5)
            
        for j in range(numStrats1):
            e = Entry(payoffsFrame, width=10)
            e.grid(row=j + 1, column=0, padx=5)

        rows = []
        for i in range(numStrats1):
            cols = []
            for j in range(numStrats2):
                e = Entry(payoffsFrame, width=5)
                e.grid(row=i + 1, column=j + 1, sticky=NSEW)
                cols.append(e)
            rows.append(cols)
            
        # Clearing the equilibria
        equilibriaSlaves = equilibriaFrame.grid_slaves()
        eqLabel = equilibriaSlaves[0]
        if type(eqLabel).__name__ == "Label":
            eqLabel.grid_remove()
        
        entriesToSimGame()
        root.geometry(f"{45 * numStrats2 + 700}x{25 * numStrats1 + 490}")
    return

def clearStrategies():
    """
    Clears p1 and p2's strategy names
    """
    resetStrategiesWarning = messagebox.askokcancel("Clear Strategy Names", "Are you sure you want to clear the strategy names?") 
    
    if resetStrategiesWarning == True:
        numStrats1 = int(numStratsEntries[0].get())
        numStrats2 = int(numStratsEntries[1].get())
        
        # clearing the strategies
        payoffMatrixSlaves = payoffsFrame.grid_slaves()
        strategies = payoffMatrixSlaves[numStrats1 * numStrats2:]
        for slave in strategies:
            slave.grid_remove()
        
        # refilling the table
        for i in range(numStrats2):
            e = Entry(payoffsFrame, width=10)
            e.grid(row=0, column=i + 1, pady=5)
            
        for j in range(numStrats1):
            e = Entry(payoffsFrame, width=10)
            e.grid(row=j + 1, column=0, padx=5)
            
        entriesToSimGame()
    else:
        return

def computeEquilibria(output):
    """
    Computes the equilibria of the current game and formats the output according to whether the output variable is 0 or 1, 
    """
    entriesToSimGame()
    proceed = enterPayoffs()
    if proceed == True:
        numStrats1 = int(numStratsEntries[0].get())
        numStrats2 = int(numStratsEntries[1].get())
        if output == 0: # Standard nashpy Output
            eqs = G.computeEquilibria()
            numEquilibria = len(list(eqs))
            if numEquilibria % 2 == 0:
                degenerateGameWarning = messagebox.showwarning(f"Even Number ({numEquilibria}) of Equilibria: Degenerate Game", f"An even number ({numEquilibria}) of equilibria was returned. This indicates that the game is degenerate. Consider using another algorithm to investigate.")

            eqList = [str(len(list(eqs))) + " equilibria returned\n"]
            for i, eq in enumerate(eqs):
                eqList.append(str(eq[0]) + ", " + str(eq[1]))
            eqList.reverse()
            
            pureEquilibria = []
            mixedEquilibria = []
            for e in eqs:
                print(e)
                if e[0] == 0.0 or e[0] == 1.0:
                    pureEquilibria.append(e)
                else:
                    mixedEquilibria.append(e)

            # Coloring the equilibria yellow ####################
            payoffMatrixSlaves = payoffsFrame.grid_slaves()
            outcomes = payoffMatrixSlaves[:numStrats1 * numStrats2]
            
            # Converting the list of outcomes to a list of lists
            newOutcomes = []
            row = []
            numInRow = 0
            for outcome in outcomes:
                if numInRow < numStrats2:
                    row.insert(0, outcome)
                    numInRow += 1
                    if numInRow == numStrats2:
                        newOutcomes.insert(0, row)
                        numInRow = 0
                        row = []
            
            # matching the indices to those of the payoff matrix and changing the color
            for i in range(numStrats1):
                for j in range(numStrats2):
                    if [i, j] in pureEquilibria:
                        newOutcomes[i][j].configure(bg="yellow")
                    else:
                        newOutcomes[i][j].configure(bg="white")
            
            # clearing the previous set of equilibria
            eqSlaves = equilibriaFrame.grid_slaves()
            if type(eqSlaves[0]).__name__ == "Listbox":
                eqSlaves[0].grid_remove()
            
            global eqOutputFrame
            eqOutputFrame = LabelFrame(equilibriaFrame)
    
            xscrollbar = Scrollbar(eqOutputFrame, orient=HORIZONTAL)
            yscrollbar = Scrollbar(eqOutputFrame, orient=VERTICAL)
            
            equilibriaOutputListBox = Listbox(eqOutputFrame, width=50, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, bg="black", fg="white")
            for eq in eqList:
                equilibriaOutputListBox.insert(0, eq)
            
            eqOutputFrame.grid(row=2, column=0, columnspan=2)
            equilibriaOutputListBox.grid(row=0, column=0, padx=10, sticky=NSEW)
            xscrollbar.grid(row=1, column=0, columnspan=2, sticky=EW)
            xscrollbar.config(command = equilibriaOutputListBox.xview)
            yscrollbar.grid(row=0, column=1, sticky=NS)
            yscrollbar.config(command = equilibriaOutputListBox.yview)
                        
            root.geometry("750x490")
            
        elif output == 1: # Named Strategies
            numPlayers = int(numPlayersEntry.get())
            eqs = G.computeEquilibria()
            numEquilibria = len(list(eqs))
            if numEquilibria % 2 == 0:
                warnings.warn(f"An even number ({numEquilibria}) of equilibria was returned. This indicates that the game is degenerate. Consider using another algorithm to investigate.", RuntimeWarning)
                degenerateGameWarning = messagebox.showwarning(f"Even Number ({numEquilibria}) of Equilibria: Degenerate Game", f"An even number ({numEquilibria}) of equilibria was returned. This indicates that the game is degenerate. Consider using another algorithm to investigate.")
                # resetting the generator
            newEqList = []
            for eq in eqs:
                newEq = []
                for strat in eq:
                    newEq.append(strat)
                newEqList.append(newEq)
            
            pureEquilibria = []
            mixedEquilibria = []
            for e in eqs:
                if e[0] == 0.0 or e[0] == 1.0:
                    pureEquilibria.append(e)
                else:
                    mixedEquilibria.append(e)

            # Coloring the equilibria yellow
            payoffMatrixSlaves = payoffsFrame.grid_slaves()
            outcomes = payoffMatrixSlaves[:numStrats1 * numStrats2]
            
            # converting the list of outcomes to a list of lists
            newOutcomes = []
            row = []
            numInRow = 0
            for outcome in outcomes:
                if numInRow < numStrats2:
                    row.append(outcome)
                    numInRow += 1
                    if numInRow == numStrats2:
                        newOutcomes.append(row)
                        numInRow = 0
                        row = []
            
            # FIXME: Can't finish this until we've implemented strategy names for players past player 2! 
            # Getting list of the strategy names
            payoffMatrixSlaves = payoffsFrame.grid_slaves()
            strategyNames = payoffMatrixSlaves[numStrats1 * numStrats2:]
            
            p1StrategyNames = strategyNames[:numStrats1]
            p1StrategyNames.reverse()
            p2StrategyNames = strategyNames[numStrats1:]
            p2StrategyNames.reverse()
            
            print("eqs:")
            for e in eqs:
                print(e)
            
            inp = input("Press Enter")
            
            # Collecting the named equilibria
            namedEquilibria = []
            stratIndices = []
            eqStratNames = []
            for eq in eqs:
                if type(eq[0]) != list():
                    oneFound = False
                    for x in range(numPlayers):
                        if eq[x] == 1.0:
                            stratIndices.append(x)
                namedEquilibria.append(tuple(...))               
            eqs = G.support_enumeration()
            eqList = [str(len(list(eqs))) + " equilibria returned\n"]
            for i, eq in enumerate(namedEquilibria):
                eqList.append("(" + str(eq[0]) + ", " + str(eq[1]) + ")")
            eqList.reverse()
            
            # Creating the string to go in the label
            eqString = str(len(list(eqs))) + " equilibria returned\n"
            for i, eq in enumerate(namedEquilibria):
                for j, strat in enumerate(eq):
                    if j == 0:
                        eqString = eqString + "(" + str(strat)
                    else:
                        eqString = eqString + str(strat)
                    if j < len(eq) - 1:
                        eqString = eqString + ", "
                    else:
                        eqString = eqString + ")"
                if i < len(namedEquilibria) - 1:
                    eqString = eqString + "\n"
            
            # Coloring the pure equilibria     
            payoffMatrixSlaves = payoffsFrame.grid_slaves()
            outcomes = payoffMatrixSlaves[:numStrats1 * numStrats2]
            
            # Converting the list of outcomes to a list of lists
            newOutcomes = []
            row = []
            numInRow = 0
            for outcome in outcomes:
                if numInRow < numStrats2:
                    row.insert(0, outcome)
                    numInRow += 1
                    if numInRow == numStrats2:
                        newOutcomes.insert(0, row)
                        numInRow = 0
                        row = []
            
            # Converting nashpy equilibria output to indices
            eqIndices = []
            for pe in pureEquilibria:
                # getting index of the 1's
                index1 = -1
                k = 0
                while index1 < 0:
                    if pe[0][k] == 1:
                        index1 = k
                    k += 1
                index2 = -1
                k = 0
                while index2 < 0:
                    if pe[1][k] == 1:
                        index2 = k
                    k += 1
                eqIndices.append([index1, index2])
            
            # matching the indices to those of the payoff matrix and changing the color
            for i in range(numStrats1):
                for j in range(numStrats2):
                    if [i, j] in eqIndices:
                        newOutcomes[i][j].configure(bg="yellow")
                    else:
                        newOutcomes[i][j].configure(bg="white")
                    
            # clearing the previous set of equilibria
            eqSlaves = equilibriaFrame.grid_slaves()
            if type(eqSlaves[0]).__name__ == "Listbox":
                eqSlaves[0].grid_remove()
            
            myFrame = LabelFrame(equilibriaFrame)
    
            xscrollbar = Scrollbar(myFrame, orient=HORIZONTAL)
            yscrollbar = Scrollbar(myFrame, orient=VERTICAL)
            
            equilibriaOutputListBox = Listbox(myFrame, width=50, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, bg="black", fg="white")
            for eq in eqList:
                equilibriaOutputListBox.insert(0, eq)
            
            myFrame.grid(row=2, column=0, columnspan=2)
            equilibriaOutputListBox.grid(row=0, column=0, padx=10, sticky=NSEW)
            xscrollbar.grid(row=1, column=0, columnspan=2, sticky=EW)
            xscrollbar.config(command = equilibriaOutputListBox.xview)
            yscrollbar.grid(row=0, column=1, sticky=NS)
            yscrollbar.config(command = equilibriaOutputListBox.yview)
            root.geometry("750x490")
        else:
            print("Error: variable output has taken on an unexpected value")
        return
    else:
        return

def containsDigit(string):
    """
        Checks if string contains a digit
    """
    return any(char.isdigit() for char in string)

def db():
    global dbWindow
    dbWindow = Toplevel()
    dbWindow.title("Match DB")
    dbWindow.geometry("400x400")
    dbWindow.iconbitmap("knight.ico")
    
    # Create a database or connect to one
    conn = sqlite3.connect('match.db')
    # Create cursor
    c = conn.cursor()
    
    c.execute("""CREATE TABLE IF NOT EXISTS matches (
        strategy1 text,
        strategy2 text,
        numTurns integer,
        output text,
        score1 float,
        score2 float
        )""")
    
    # Creating fields
    global dbTurnsEntry
    global dbClicked1
    global dbClicked2
    global dbDropdown1
    global selectIDEntry
    
    dbStrategyLabel1 = Label(dbWindow, text="Choose a strategy for player 1: ")
    dbStrategyLabel2 = Label(dbWindow, text="Choose a strategy for player 2: ")
    options = [s() for s in axl.strategies]
    dbClicked1 = StringVar()
    dbClicked1.set(options[0])
    dbClicked2 = StringVar()
    dbClicked2.set(options[0])
    dbDropdown1 = ttk.Combobox(dbWindow, textvariable=dbClicked1, values=options)
    dbDropdown2 = ttk.Combobox(dbWindow, textvariable=dbClicked2, values=options)
    dbTurnsLabel = Label(dbWindow, text="Number of turns: ")
    dbTurnsEntry = Entry(dbWindow, width=5)
    dbTurnsEntry.insert(0, "6")
    addRecordButton = Button(dbWindow, text="Add Record", command=addRecord)
    addAllPairsButton = Button(dbWindow, text="Add All Pairs for a Given Number of Turns", command=addAllPairs)
    numRecordsButton = Button(dbWindow, text="Get Total Number of Records", command=getNumRecords)
    showRecordsButton = Button(dbWindow, text="Show Records", command=showRecords)
    exportButton = Button(dbWindow, text="Export to csv", command=exportGetFileName)
    searchRecordsButton = Button(dbWindow, text="Search Records", command=searchRecords)
    selectIDLabel = Label(dbWindow, text="Select ID: ")
    selectIDEntry = Entry(dbWindow, width=20)
    deleteRecordButton = Button(dbWindow, text="Delete Record", command=deleteRecord)
    updateRecordButton = Button(dbWindow, text="Update Record", command=updateRecord)
    resetRecordButton = Button(dbWindow, text="Reset Record", command=resetRecord)
    clearDBButton = Button(dbWindow, text="Clear DB", command=clearDB)
        
    # Putting everything in the top window
    dbStrategyLabel1.grid(row=0, column=0, padx=(5, 0), sticky=E)
    dbDropdown1.grid(row=0, column=1, padx=(0, 5), pady=5, sticky=W)
    dbStrategyLabel2.grid(row=1, column=0, padx=(5, 0), sticky=E)
    dbDropdown2.grid(row=1, column=1, padx=(0, 5),pady=(0,5), sticky=W)
    dbTurnsLabel.grid(row=2, column=0, padx=(5, 0), pady=(0,5), sticky=E)
    dbTurnsEntry.grid(row=2, column=1, pady=(0, 5), sticky=W)
    addRecordButton.grid(row=3, column=0, columnspan=2, padx=5, pady=(0, 5), ipadx=141)
    addAllPairsButton.grid(row=4, column=0, columnspan=2, padx=5, pady=(0, 5), ipadx=62)
    numRecordsButton.grid(row=5, column=0, columnspan=2, padx=5, pady=(0, 5), ipadx=96)
    showRecordsButton.grid(row=6, column=0, columnspan=2, padx=5, pady=(0, 5), ipadx=135)
    exportButton.grid(row=7, column=0, columnspan=2, padx=5, pady=(0, 5), ipadx=137)
    searchRecordsButton.grid(row=8, column=0, columnspan=2, padx=5, pady=(0, 5), ipadx=132)
    selectIDLabel.grid(row=9, column=0, pady=(0, 5), sticky=E)
    selectIDEntry.grid(row=9, column=1, pady=(0, 5), sticky=W)
    deleteRecordButton.grid(row=10, column=0, columnspan=2, padx=5, pady=(0, 5), ipadx=135)
    updateRecordButton.grid(row=11, column=0, columnspan=2, padx=5, pady=(0, 5), ipadx=132)
    resetRecordButton.grid(row=12, column=0, columnspan=2, padx=5, pady=(0, 5), ipadx=136)
    clearDBButton.grid(row=13, column=0, columnspan=2, padx=5, pady=(0, 5), ipadx=148)
    
    # Commit changes
    conn.commit()
    # Close Connection
    conn.close()
    return

def dbPlayMatch(p1, p2, t = 6):    
    """
    Runs an axelrod match between players of type p1 and p2 with t turns and returns a tuple of the match output and scores
    """    
    p1 = ""
    p2 = ""
    clicked1NoSpaces = clicked1.get().replace(" ", "")
    clicked2NoSpaces = clicked2.get().replace(" ", "")
    counter= 0
    while type(p1).__name__ == "str" and counter <= len(axl.strategies):
        try:
            if type(options[counter]).__name__ == clicked1NoSpaces:
                p1 = options[counter]
        except IndexError:
            stratNotFoundError = messagebox.showerror("Error", "The strategy you entered for player 1 was not in axelrod's list of strategies. Perhaps you meant to capitalize the individual words?")
        counter += 1  
    
    counter = 0
    while type(p2).__name__ == "str" and counter <= len(axl.strategies):
        try:
            if type(options[counter]).__name__ == clicked2NoSpaces:
                p2 = options[counter]
                
                match = axl.Match((p1, p2), turns = t)
        except IndexError:
            stratNotFoundError = messagebox.showerror("Error", "The strategy you entered for player 2 was not in axelrod's list of strategies. Perhaps you meant to capitalize the individual words?")
        counter += 1
    return (str(match.play()), match.final_score_per_turn())

def deleteRecord():
    # Create a database or connect to one
    conn = sqlite3.connect('match.db')
    # Create cursor
    c = conn.cursor()
    try:
        c.execute("DELETE FROM matches WHERE oid=" + selectIDEntry.get())
    except sqlite3.OperationalError:
        IDNotSelectedError = messagebox.showerror("Error", "You must enter an ID to delete a record.")            
    
    conn.commit()
    conn.close()
    return

def dimensionsClick():
    """
    Resizes the payoff matrix according to the numbers of strategies entered in by the user
    """
    entriesToSimGame()
    numStrats = []
    for x in range(G.numPlayers):
        numStrats.append(int(numStratsEntries[x].get()))
    negativeStratsError = -1
    zeroStratsError = -1
    oneByOneError = -1
    if numStrats[0] == 0 or numStrats[1] == 0:
        zeroStratsError = messagebox.showerror("Error", "dimensionsClick: A player may not have zero strategies.")
    
    if zeroStratsError == -1:
        if numStrats[0] == 1 or numStrats[1] == 1:
            oneByOneError = messagebox.showerror("Error", "dimensionsClick: A player may not have only one strategy.")
            return
        
        if oneByOneError == -1:
            if numStrats[0] < 0 or numStrats[1] < 0:
                negativeStratsError = messagebox.showerror("Error", "dimensionsClick: A player may not have a negative number of strategies.")
                return
            if negativeStratsError == -1:
                proceed = messagebox.askokcancel("Clear Payoffs?", "This will reset the payoff matrix. Do you want to proceed?")
                if (proceed == True):
                    # Resetting the number of steps of IESDS that have been computed
                    numIESDSClicks = 0  
                    # clearing the table
                    payoffMatrixSlaves = payoffsFrame.grid_slaves()
                    for slave in payoffMatrixSlaves:
                        slave.grid_remove()
                    
                    # refilling the table
                    for j in range(numStrats[1]):
                        e = Entry(payoffsFrame, width=10)
                        if j == 0:
                            e.insert(0, "L")
                        elif j > 0 and j < numStrats[1] - 1 and numStrats[1] == 3:
                            e.insert(0, "C")
                        elif j > 0 and j < numStrats[1] - 1 and numStrats[1] >= 3:
                            e.insert(0, "C" + str(i))
                        else:
                            e.insert(0, "R")
                        e.grid(row=0, column=j + 1, pady=5)
                        
                    for i in range(numStrats[0]):
                        e = Entry(payoffsFrame, width=10)
                        if i == 0:
                            e.insert(0, "U")
                        elif i > 0 and i < numStrats[0] - 1 and numStrats[0] == 3:
                            e.insert(0, "M")
                        elif i > 0 and i < numStrats[0] - 1 and numStrats[0] > 3:
                            e.insert(0, "M" + str(j))
                        else:
                            e.insert(0, "D")
                        e.grid(row=i + 1, column=0, padx=5)

                    rows = []
                    for i in range(numStrats[0]):
                        cols = []
                        for j in range(numStrats[1]):
                            e = Entry(payoffsFrame, width=5)
                            e.grid(row=i + 1, column=j + 1, sticky=NSEW)
                            e.insert(END, '%d, %d' % (0, 0))
                            cols.append(e)
                        rows.append(cols)
                        
                    # Clearing the equilibria
                    eqOutputSlaves = eqOutputFrame.grid_slaves()
                    scrollbar1 = eqOutputSlaves[0]
                    scrollbar2 = eqOutputSlaves[1]
                    eqListBox = eqOutputSlaves[2]
                    scrollbar1.grid_remove()
                    scrollbar2.grid_remove()
                    eqListBox.grid_remove()
                    eqOutputFrame.grid_remove()
                    
                    root.geometry(f"{45 * numStrats[1] + 700}x{25 * numStrats[0] + 490}")
                    return proceed
                else:
                    return
            else:
                return
        else:
            return
    return

def dimensionsClickNoWarning():
    """
    Resizes the payoff matrix according to the numbers of strategies entered in by the user without prompting the user
    """
    numStrats1 = int(numStratsEntries[0].get())
    numStrats2 = int(numStratsEntries[1].get())
    negativeStratsError = -1
    zeroStratsError = -1
    oneByOneError = -1
    if numStrats1 == 0 or numStrats2 == 0:
        zeroStratsError = messagebox.showerror("Error", "A player may not have zero strategies.")
    
    if zeroStratsError == -1:
        if numStrats1 == 1 or numStrats2 == 1:
            oneByOneError = messagebox.showerror("Error", "A player may not have only one strategy.")
            return
        
        if oneByOneError == -1:
            if numStrats1 < 0 or numStrats2 < 0:
                negativeStratsError = messagebox.showerror("Error", "A player may not have a negative number of strategies.")
                return
            if negativeStratsError == -1:
                # Resetting the number of steps of IESDS that have been computed
                numIESDSClicks = 0   
                # clearing the table
                payoffMatrixSlaves = payoffsFrame.grid_slaves()
                for slave in payoffMatrixSlaves:
                    slave.grid_remove()
                
                # refilling the table
                for i in range(numStrats2):
                    e = Entry(payoffsFrame, width=10)
                    if i == 0:
                        e.insert(0, "L")
                    elif i > 0 and i < numStrats2 - 1 and numStrats2 == 3:
                        e.insert(0, "C")
                    elif i > 0 and i < numStrats2 - 1 and numStrats2 >= 3:
                        e.insert(0, "C" + str(i))
                    else:
                        e.insert(0, "R")
                    e.grid(row=0, column=i + 1, pady=5)
                    
                for j in range(numStrats1):
                    e = Entry(payoffsFrame, width=10)
                    if j == 0:
                        e.insert(0, "U")
                    elif j > 0 and j < numStrats1 - 1 and numStrats1 == 3:
                        e.insert(0, "M")
                    elif j > 0 and j < numStrats1 - 1 and numStrats1 > 3:
                        e.insert(0, "M" + str(j))
                    else:
                        e.insert(0, "D")
                    e.grid(row=j + 1, column=0, padx=5)

                rows = []
                for i in range(numStrats1):
                    cols = []
                    for j in range(numStrats2):
                        e = Entry(payoffsFrame, width=5)
                        e.grid(row=i + 1, column=j + 1, sticky=NSEW)
                        e.insert(END, '%d, %d' % (0, 0))
                        cols.append(e)
                    rows.append(cols)
                    
                # Clearing the equilibria
                equilibriaSlaves = equilibriaFrame.grid_slaves()
                eqLabel = equilibriaSlaves[0]
                if type(eqLabel).__name__ == "Label":
                    eqLabel.grid_remove()
                
                root.geometry(f"{45 * numStrats2 + 700}x{25 * numStrats1 + 490}")
                return
            else:
                return
        else:
            return
    return

def eliminateStrictlyDominatedStrategies(steps):
    """
    Compares all payoffs of all pairs of strategies for both players and eliminates strategies that are strictly dominated.    
    """
    entriesToSimGame()
    # saving the original game in case the user wants to revert back to it
    global numIESDSClicks
    global originalGame
    global originalNumStrats1
    global originalNumStrats2
    if steps == 0 or numIESDSClicks == 0:
        originalGame = payoffsFrame.grid_slaves()
        originalNumStrats1 = int(numStratsEntries[0].get())
        originalNumStrats2 = int(numStratsEntries[1].get())
    
    numStrats1 = int(numStratsEntries[0].get())
    numStrats2 = int(numStratsEntries[1].get())
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    outcomes = payoffMatrixSlaves[:numStrats1 * numStrats2]
    outcomes.reverse()
    strategyNames = payoffMatrixSlaves[numStrats1 * numStrats2:]
    p1StrategyNameEntries = strategyNames[:numStrats1]
    p1StrategyNameEntries.reverse()
    p2StrategyNameEntries = strategyNames[numStrats2:]
    p2StrategyNameEntries.reverse()
    groupedOutcomes = [outcomes[i:i + numStrats2] for i in range(0, len(outcomes), numStrats2)]
    
    newGroupedOutcomes = []
    for outcome in groupedOutcomes:
        row = []
        for i in range(numStrats2):
            row.append(outcome[i])
        newGroupedOutcomes.append(row)
    
    outcomesListList= []
    for outcome in newGroupedOutcomes:
        outcomesListList.append(outcome)

    strategies = payoffMatrixSlaves[numStrats1 * numStrats2:]
    strategies.reverse()
    p1Strategies = [i for i in range(numStrats1)] # = [0, 1, 2,...]
    p2Strategies = [i for i in range(numStrats2)] # = [0, 1, 2,...]
    
    if steps == 0: # perform full IESDS computation with one click
        pairs1 = combinations(p1Strategies, r=2) # pairs of p1's strategies to compare; indices
        pairs2 = combinations(p2Strategies, r=2) # pairs of p2's strategies to compare; indices
        numCombos1 = sum(1 for pair in pairs1)
        numCombos2 = sum(1 for pair in pairs2)
        pairs1 = combinations(p1Strategies, r=2) # pairs of p1's strategies to compare; indices
        pairs2 = combinations(p2Strategies, r=2) # pairs of p2's strategies to compare; indices
        greaterThanFound1 = False
        lessThanFound1 = False
        equalFound1 = False
        greaterThanFound2 = False
        lessThanFound2 = False
        equalFound2 = False
        multipleStrats1 = True
        multipleStrats2 = True
        stratRemoved1 = True
        stratRemoved2 = True  
        # stop when you can't eliminate a strategy for either player or when only one strategy is left for each player
        while (multipleStrats1 and multipleStrats2) and (stratRemoved1 or stratRemoved2):
            stratRemoved1 = False
            stratRemoved2 = False
            
            # recomputing the pairs that need to be checked because the number of strategies may have changed
            pairs1 = combinations(p1Strategies, r=2) # pairs of p1's strategies to compare; indices
            pairs2 = combinations(p2Strategies, r=2) # pairs of p2's strategies to compare; indices
            numCombos1 = sum(1 for pair in pairs1)
            numCombos2 = sum(1 for pair in pairs2)
            pairs1 = combinations(p1Strategies, r=2) # pairs of p1's strategies to compare; indices
            pairs2 = combinations(p2Strategies, r=2) # pairs of p2's strategies to compare; indices
            # eliminating strategies for player 1 #####################################################################
            for pair in pairs1:
                greaterThanFound1 = False
                lessThanFound1 = False
                equalFound1 = False
                # searching for < or > among the payoffs
                for j in range(numStrats2):
                    if len(outcomesListList) == 1: # if p1 has only one strategy left
                        multipleStrats1 = False
                        break
                    if int(outcomesListList[pair[0]][j].get().split(", ")[0]) < int(outcomesListList[pair[1]][j].get().split(", ")[0]):
                        lessThanFound1 = True
                    elif int(outcomesListList[pair[0]][j].get().split(", ")[0]) > int(outcomesListList[pair[1]][j].get().split(", ")[0]):
                        greaterThanFound1 = True
                    else: # equal payoffs found
                        equalFound1 = True
                        break
                
                # Removing strategies based on the results
                if lessThanFound1 and not greaterThanFound1 and not equalFound1: # remove strategy pair[0]
                    numStrats1 -= 1
                    numStratsEntries[0].delete(0, END)
                    numStratsEntries[0].insert(0, numStrats1)
                    p1StrategyNameEntries[pair[0]].grid_remove()
                    for j in range(numStrats2):
                        outcomesListList[pair[0]][j].grid_remove()
                        outcomesListList[pair[0]].pop(j)
                    p1Strategies.pop()
                    stratRemoved1 = True
                elif greaterThanFound1 and not lessThanFound1 and not equalFound1: # remove strategy pair[1]
                    numStrats1 -= 1
                    numStratsEntries[0].delete(0, END)
                    numStratsEntries[0].insert(0, numStrats1)
                    p1StrategyNameEntries[pair[1]].grid_remove()
                    numDeleted = 0
                    for j in range(numStrats2):
                        j -= numDeleted
                        outcomesListList[pair[1]][j].grid_remove()
                        outcomesListList[pair[1]].pop(j)
                        numDeleted += 1
                    p1Strategies.pop()
                    stratRemoved1 = True
                else: # (not lessThanFound1 and not greaterThanFound1)(all equal) or (lessThanFound1 and greaterThanFound1)(no dominance)
                    stratRemoved1 = False
                
                if stratRemoved1:
                    break
                    
            # eliminating strategies for player 2 ######################################################################
            for pair in pairs2:
                greaterThanFound2 = False
                lessThanFound2 = False
                equalFound2 = False
                # searching for < or > among the payoffs
                for i in range(numStrats1):
                    if len(outcomesListList[pair[0]]) == 1: # if p2 only has one strategy left
                        multipleStrats2 = False
                        break
                    if int(outcomesListList[i][pair[0]].get().split(", ")[1]) < int(outcomesListList[i][pair[1]].get().split(", ")[1]):
                        lessThanFound2 = True
                    elif int(outcomesListList[i][pair[0]].get().split(", ")[1]) > int(outcomesListList[i][pair[1]].get().split(", ")[1]):
                        greaterThanFound2 = True
                    else: # equal payoffs were found
                        equalFound2 = True
                        break
                
                # Removing strategies based on the results
                if lessThanFound2 and not greaterThanFound2 and not equalFound2: # remove strategy pair[0]
                    numStrats2 -= 1
                    numStratsEntries[1].delete(0, END)
                    numStratsEntries[1].insert(0, numStrats2)
                    p2StrategyNameEntries[pair[0]].grid_remove()
                    for i in range(numStrats1):
                        outcomesListList[i][pair[0]].grid_remove()
                        outcomesListList[i].pop(pair[0])
                    p2Strategies.pop()
                    stratRemoved2 = True
                elif greaterThanFound2 and not lessThanFound2 and not equalFound2: # remove strategy pair[1]
                    numStrats2 -= 1
                    numStratsEntries[1].delete(0, END)
                    numStratsEntries[1].insert(0, numStrats2)
                    p2StrategyNameEntries[pair[1]].grid_remove()
                    for i in range(numStrats1):
                        outcomesListList[i][pair[1]].grid_remove()
                        outcomesListList[i].pop(pair[1])
                    p2Strategies.pop()
                    stratRemoved2 = True
                else: # (not lessThanFound2 and not greaterThanFound2) or (lessThanFound2 and greaterThanFound2)
                    stratRemoved2 = False
                
                if stratRemoved2:
                    break
            if not stratRemoved1 and not stratRemoved2:
                break
    elif steps == 1: # perform IESDS computation step by step
        numIESDSClicks += 1
        pairs1 = combinations(p1Strategies, r=2) # pairs of p1's strategies to compare; indices
        pairs2 = combinations(p2Strategies, r=2) # pairs of p2's strategies to compare; indices
        numCombos1 = sum(1 for pair in pairs1)
        numCombos2 = sum(1 for pair in pairs2)
        pairs1 = combinations(p1Strategies, r=2) # pairs of p1's strategies to compare; indices
        pairs2 = combinations(p2Strategies, r=2) # pairs of p2's strategies to compare; indices
        oneStratEliminated = False
        
        if numIESDSClicks == 1:
            # eliminating strategies for player 1
            for pair in pairs1:
                greaterThanFound1 = False
                lessThanFound1 = False
                equalFound1 = False
                # searching for < or > among the payoffs
                for j in range(numStrats2):
                    if int(outcomesListList[pair[0]][j].get().split(", ")[0]) < int(outcomesListList[pair[1]][j].get().split(", ")[0]):
                        lessThanFound1 = True
                    elif int(outcomesListList[pair[0]][j].get().split(", ")[0]) > int(outcomesListList[pair[1]][j].get().split(", ")[0]):
                        greaterThanFound1 = True
                    else: # equal payoffs were found
                        equalFound1 = True
                        break
                    if lessThanFound1 and greaterThanFound1: # neither is strictly dominated
                        break
                if lessThanFound1 and not greaterThanFound1 and not equalFound1: # remove strategy pair[0]
                    oneStratEliminated = True
                    numStrats1 -= 1
                    numStratsEntries[0].delete(0, END)
                    numStratsEntries[0].insert(0, numStrats1)
                    p1StrategyNameEntries[pair[0]].grid_remove()
                    for j in range(numStrats2):
                        outcomesListList[pair[0]][j].grid_remove()
                        outcomesListList[pair[0]].pop(j)
                if greaterThanFound1 and not lessThanFound1 and not equalFound1: # remove strategy pair[1]
                    # one strat found
                    oneStratEliminated = True
                    numStrats1 -= 1
                    numStratsEntries[0].delete(0, END)
                    numStratsEntries[0].insert(0, numStrats1)
                    p1StrategyNameEntries[pair[1]].grid_remove()
                    numDeleted = 0
                    for j in range(numStrats2):
                        j -= numDeleted
                        outcomesListList[pair[1]][j].grid_remove()
                        outcomesListList[pair[1]].pop(j)
                        numDeleted += 1
            if not oneStratEliminated:
                # eliminating strategies for player 2
                for pair in pairs2:
                    greaterThanFound2 = False
                    lessThanFound2 = False
                    equalFound2 = False
                    # searching for < or > among the payoffs
                    for i in range(numStrats1):
                        if len(outcomesListList[pair[0]]) == 0 or len(outcomesListList[pair[1]]) == 0:
                            break
                        if int(outcomesListList[i][pair[0]].get().split(", ")[1]) < int(outcomesListList[i][pair[1]].get().split(", ")[1]):
                            lessThanFound2 = True
                        elif int(outcomesListList[i][pair[0]].get().split(", ")[1]) > int(outcomesListList[i][pair[1]].get().split(", ")[1]):
                            greaterThanFound2 = True
                        else: # equal payoffs were found
                            equalFound2 = True
                            break
                        if lessThanFound2 and greaterThanFound2: # neither is strictly dominated
                            break
                    if lessThanFound2 and not greaterThanFound2 and not equalFound2: # remove strategy pair[0]
                        oneStratEliminated = True
                        numIESDSClicks = 3 # if we start by eliminating a strat for p2, check p1 next
                        numStrats2 -= 1
                        numStratsEntries[1].delete(0, END)
                        numStratsEntries[1].insert(0, numStrats2)
                        p2StrategyNameEntries[pair[0]].grid_remove()
                        for i in range(numStrats1):
                            outcomesListList[i][pair[0]].grid_remove()
                            outcomesListList[i].pop(pair[0])
                    if greaterThanFound2 and not lessThanFound2 and not equalFound2: # remove strategy pair[1]
                        oneStratEliminated = True
                        numIESDSClicks = 2 # if we start by eliminating a strat for p2, check p1 next (numIESDSClicks will be incremented to 3 \cong 1 mod 2)
                        numStrats2 -= 1
                        numStratsEntries[1].delete(0, END)
                        numStratsEntries[1].insert(0, numStrats2)
                        p2StrategyNameEntries[pair[1]].grid_remove()
                        for i in range(numStrats1):
                            outcomesListList[i][pair[1]].grid_remove()
                            outcomesListList[i].pop(pair[1])
        else: # numIESDSClicks > 1
            if numIESDSClicks % 2 == 1: # check player 1's strategies
                # eliminating strategies for player 1
                for pair in pairs1:
                    greaterThanFound1 = False
                    lessThanFound1 = False
                    equalFound1 = False
                    # searching for < or > among the payoffs
                    for j in range(numStrats2):
                        if int(outcomesListList[pair[0]][j].get().split(", ")[0]) < int(outcomesListList[pair[1]][j].get().split(", ")[0]):
                            lessThanFound1 = True
                        elif int(outcomesListList[pair[0]][j].get().split(", ")[0]) > int(outcomesListList[pair[1]][j].get().split(", ")[0]):
                            greaterThanFound1 = True
                        else: # equal payoffs were found
                            equalFound1 = True
                            break
                        if lessThanFound1 and greaterThanFound1: # neither is strictly dominated
                            break
                    if lessThanFound1 and not greaterThanFound1 and not equalFound1: # remove strategy pair[0]
                        numStrats1 -= 1
                        numStratsEntries[0].delete(0, END)
                        numStratsEntries[0].insert(0, numStrats1)
                        p1StrategyNameEntries[pair[0]].grid_remove()
                        for j in range(numStrats2):
                            outcomesListList[pair[0]][j].grid_remove()
                            outcomesListList[pair[0]].pop(j)
                    if greaterThanFound1 and not lessThanFound1 and not equalFound1: # remove strategy pair[1]
                        numStrats1 -= 1
                        numStratsEntries[0].delete(0, END)
                        numStratsEntries[0].insert(0, numStrats1)
                        p1StrategyNameEntries[pair[1]].grid_remove()
                        numDeleted = 0
                        for j in range(numStrats2):
                            j -= numDeleted
                            outcomesListList[pair[1]][j].grid_remove()
                            outcomesListList[pair[1]].pop(j)
                            numDeleted += 1
            else: # numIESDSClicks % 2 == 0; check player 2's strategies
                # eliminating strategies for player 2
                for pair in pairs2:
                    greaterThanFound2 = False
                    lessThanFound2 = False
                    equalFound2 = False
                    # searching for < or > among the payoffs
                    for i in range(numStrats1):
                        if len(outcomesListList[pair[0]]) == 0 or len(outcomesListList[pair[1]]) == 0:
                            break
                        if int(outcomesListList[i][pair[0]].get().split(", ")[1]) < int(outcomesListList[i][pair[1]].get().split(", ")[1]):
                            lessThanFound2 = True
                        elif int(outcomesListList[i][pair[0]].get().split(", ")[1]) > int(outcomesListList[i][pair[1]].get().split(", ")[1]):
                            greaterThanFound2 = True
                        else: # equal payoffs were found
                            equalFound2 = True
                            break
                        if lessThanFound2 and greaterThanFound2: # neither is strictly dominated
                            break
                    if lessThanFound2 and not greaterThanFound2 and not equalFound2: # remove strategy pair[0]
                        numStrats2 -= 1
                        numStratsEntries[1].delete(0, END)
                        numStratsEntries[1].insert(0, numStrats2)
                        p2StrategyNameEntries[pair[0]].grid_remove()
                        for i in range(numStrats1):
                            outcomesListList[i][pair[0]].grid_remove()
                            outcomesListList[i].pop(pair[0])
                    if greaterThanFound2 and not lessThanFound2 and not equalFound2: # remove strategy pair[1]
                        numStrats2 -= 1
                        numStratsEntries[1].delete(0, END)
                        numStratsEntries[1].insert(0, numStrats2)
                        p2StrategyNameEntries[pair[1]].grid_remove()
                        for i in range(numStrats1):
                            outcomesListList[i][pair[1]].grid_remove()
                            outcomesListList[i].pop(pair[1])
    else:
        print(f"Unexpected value {steps} for variable\"steps\"")
        stepsError = messagebox.showError("Error", f"Unexpected value {steps} for variable\"steps\"")
    return

def enterColor(color):
    """
        Makes the root window have a certain color
    """
    try:
        root.configure(bg=color)
    except TclError:
        colorNotFound = messagebox.showerror(f"Error", f"Unknown color name \"{color}\". Try entering in a different color.")
    return

def entriesToSimGame():
    """Enters the information in the text entries into the SimGame object
    """
    # Getting the number of players
    numPlayers = int(numPlayersEntry.get())
    
    # Getting the numbers of strategies
    numStrats = []
    dimensionsSlaves = dimensionsFrame.grid_slaves()
    for slave in dimensionsSlaves:
        if type(slave).__name__ == "Entry":
            numStrats.append(int(slave.get()))
    numStrats.pop() # last one will be the entry for numPlayers
    numStrats.reverse()
    
    # Getting the entries from the payoffs frame
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    outcomes = payoffMatrixSlaves[:numStrats1 * numStrats2]
    outcomes.reverse()
    strategyNames = payoffMatrixSlaves[numStrats1 * numStrats2:]
    p1StrategyNameEntries = strategyNames[:numStrats1]
    p1StrategyNameEntries.reverse()
    p2StrategyNameEntries = strategyNames[numStrats2:]
    p2StrategyNameEntries.reverse()
    
    # Grouping the outcomes
    groupedOutcomes = [outcomes[i:i + numStrats2] for i in range(0, len(outcomes), numStrats2)]
    newGroupedOutcomes = []
    for outcome in groupedOutcomes:
        row = []
        for i in range(numStrats2):
            row.append(outcome[i])
        newGroupedOutcomes.append(row)
    outcomesListList= []
    for outcome in newGroupedOutcomes:
        outcomesListList.append(outcome)
    
    # Converting from a list of list of entries to a list of list of integers
    newListList = []
    for row in outcomesListList:
        newRow = []
        for item in row:
            newRow.append(item.get().split(", "))
            for l in newRow:
                for el in l:
                    el = float(el)
        newListList.append(newRow)
    # Entering the payoffs
    G.enterPayoffs(newListList, numPlayers, numStrats)
    
    # FIXME: Finish for games with >= 3 players
    # Entering the strategy names
    G.strategyNames[0] = [entry.get() for entry in p1StrategyNameEntries]
    G.strategyNames[1] = [entry.get() for entry in p2StrategyNameEntries]
    return

def enterPayoffs():
    """
    Enters the payoffs from the Entries into a list
    """
    numPlayers = int(numPlayersEntry.get())
    numStrats1 = int(numStratsEntries[0].get())
    numStrats2 = int(numStratsEntries[1].get())
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    outcomes = payoffMatrixSlaves[:numStrats1 * numStrats2]
    # input validation
    for outcome in outcomes:
        if "," not in outcome.get():
            invalidPayoffError = messagebox.showerror("Error", f"Invalid payoff \"{outcome.get()}\". Payoffs must be two numbers separated by commas.")
            return False
    
    payoffs = [list(map(float, outcome.get().split(","))) for outcome in outcomes]
    payoffs.reverse()
    
    # converting the list of payoffs to a list of lists
    newPayoffs = []
    row = []
    numInRow = 0
    for p in payoffs:
        if numInRow < numStrats2:
            row.append(p)
            numInRow += 1
            if numInRow == numStrats2:
                newPayoffs.append(row)
                numInRow = 0
                row = []
    
    global G
    G.enterPayoffs(newPayoffs, numPlayers, [numStrats1, numStrats2])
    return True

def equilibriaOutputStyleClicked(value):
    eqOutput.set(value)
    
def export(fileName, records):
    # input validation
    if ".csv" not in fileName and "." in fileName:
        wrongExtensionError = messagebox.showerror("Error", f"The file name \"{fileName}\" contains the wrong file extension. The extension should be \".csv\".")
        return
    elif ".csv" not in fileName and "." not in fileName:
        fileName = fileName + ".csv"
    
    with open(fileName, 'w') as file:
        for i, record in enumerate(records):
            file.write(
                "\"" + str(record[0]) + "\",\"" + 
                str(record[1])+ "\",\"" + 
                str(record[2]) + "\",\"" + 
                str(record[3]) + "\",\"" + 
                str(record[4]) + "\",\"" + 
                str(record[5]) + "\",\"" + 
                str(record[6]) + "\"")
            if i < len(records) - 1:
                file.write("\n")
        
def exportGetFileName():
     # Create a database or connect to one
    conn = sqlite3.connect('match.db')
    # Create cursor
    c = conn.cursor()
    
    c.execute("""SELECT *, oid FROM matches""")
    records = c.fetchall()
    
    top = Toplevel()
    top.title("Export to csv")
    top.iconbitmap("knight.ico")
    top.geometry("250x30")
    
    fileNameLabel = Label(top, text="Enter a File Name: ")
    fileNameEntry = Entry(top, width=15)
    fileNameButton = Button(top, text="Enter", command=lambda: export(fileNameEntry.get(), records))
    
    # Putting everything in the top window
    fileNameLabel.grid(row=0, column=0)
    fileNameEntry.grid(row=0, column=1)
    fileNameButton.grid(row=0, column=2)
    
    # Commit changes
    conn.commit()
    # Close Connection
    conn.close()
    return

def exportSearchGetFileName(records):
    top = Toplevel()
    top.title("Export to csv")
    top.iconbitmap("knight.ico")
    top.geometry("250x30")
    
    fileNameLabel = Label(top, text="Enter a File Name: ")
    fileNameEntry = Entry(top, width=15)
    fileNameButton = Button(top, text="Enter", command=lambda: export(fileNameEntry.get(), records))
    
    # Putting everything in the top window
    fileNameLabel.grid(row=0, column=0)
    fileNameEntry.grid(row=0, column=1)
    fileNameButton.grid(row=0, column=2)
    return

def getNumRecords():
    # Create a database or connect to one
    conn = sqlite3.connect('match.db')
    # Create cursor
    c = conn.cursor()
    
    c.execute("""SELECT COUNT(*) FROM matches""")
    numRecords = c.fetchone()[0]
    
    myFrame = LabelFrame(dbWindow)
    
    xscrollbar = Scrollbar(myFrame, orient=HORIZONTAL)
    yscrollbar = Scrollbar(myFrame, orient=VERTICAL)
    
    showRecordsListBox = Listbox(myFrame, width=50, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, bg="black", fg="white")
    showRecordsListBox.insert(0, f"There are {numRecords} records in the matches table.")
    
    myFrame.grid(row=14, column=0, columnspan=2)
    showRecordsListBox.grid(row=0, column=0, padx=10, sticky=NSEW)
    xscrollbar.grid(row=1, column=0, columnspan=2, sticky=EW)
    xscrollbar.config(command = showRecordsListBox.xview)
    yscrollbar.grid(row=0, column=1, sticky=NS)
    yscrollbar.config(command = showRecordsListBox.yview)
    
    # Commit changes
    conn.commit()
    # Close Connection
    conn.close()
    return

def iesdsStepsClicked(value):
    iesdsSteps.set(value)

def openFile():
    """
        opens a file and reads the data from it into a list
    """
    root.filename = filedialog.askopenfilename(initialdir=".", title="Select a File", filetypes=(("Text files", "*.txt"),))
    
    if root.filename != '':
        with open(root.filename, 'r') as file:
            # Entering the numbers of strategies
            numStrats = file.readline().rstrip().split(" ")
            proceed = messagebox.askokcancel("Clear Payoffs?", "This will reset the payoff matrix. Do you want to proceed?")
            if proceed == True:
                # Resetting the number of IESDS steps that have been computed
                numIESDSClicks = 0
                
                numStratsEntries[0].delete(0, 'end')
                numStratsEntries[1].delete(0, 'end')
                numStratsEntries[0].insert(0, numStrats[0])
                numStratsEntries[1].insert(0, numStrats[1])
                dimensionsClickNoWarning()
                numStrats1 = int(numStratsEntries[0].get())
                numStrats2 = int(numStratsEntries[1].get())
                
                # Entering the strategy names
                p1StrategyNames = file.readline().rstrip().split(" ")
                p2StrategyNames = file.readline().rstrip().split(" ")
                payoffMatrixSlaves = payoffsFrame.grid_slaves()
                strategyNames = payoffMatrixSlaves[numStrats1 * numStrats2:]
                p1StrategyNameEntries = strategyNames[:numStrats1]
                p1StrategyNameEntries.reverse()
                p2StrategyNameEntries = strategyNames[numStrats2:]
                p2StrategyNameEntries.reverse()
                
                for i, entry in enumerate(p1StrategyNameEntries):
                    entry.delete(0, 'end')
                    entry.insert(0, p1StrategyNames[i])
                for i, entry in enumerate(p2StrategyNameEntries):
                    entry.delete(0, 'end')
                    entry.insert(0, p2StrategyNames[i])
                
                payoffs = payoffMatrixSlaves[:numStrats1 * numStrats2]
                payoffs.reverse()
                groupedOutcomes = [payoffs[i:i + numStrats2] for i in range(0, len(payoffs), numStrats2)]
                
                # clearing the payoff matrix
                for row in groupedOutcomes:
                    for payoff in row:
                        payoff.delete(0, 'end')
                
                # filling the payoff matrix with the values from the file
                for line_index, line in enumerate(file):
                    payoffLine = line.split(" ")
                    if payoffLine[-1] == "\n":
                        payoffLine.pop()
                    if "\n" in payoffLine[-1]:
                        payoffLine[-1] = payoffLine[-1][:len(payoffLine[-1]) - 1]
                    
                    groupedPayoffs = [payoffLine[i:i + 2] for i in range(0, len(payoffLine), 2)]
                    stringPayoffs = [str(p[0]) + ", " + str(p[1]) for p in groupedPayoffs]
                        
                    # entering the new values into the payoff matrix
                    row = groupedOutcomes[line_index]
                    for i, payoff in enumerate(row):
                        payoff.insert(0, stringPayoffs[i])
    return

def playMatch(p1, p2, output, t = 6):
    """
    Runs an axelrod match between players of type p1 and p2 with t turns
    """
    if output == 0: # Add to Database    
        p1 = ""
        p2 = ""
        clicked1NoSpaces = clicked1.get().replace(" ", "")
        clicked2NoSpaces = clicked2.get().replace(" ", "")
        counter = 0
        while type(p1).__name__ == "str" and counter <= len(axl.strategies):
            try:
                if type(options[counter]).__name__ == clicked1NoSpaces:
                    p1 = options[counter]
            except IndexError:
                stratNotFoundError = messagebox.showerror("Error", "The strategy you entered for player 1 was not in axelrod's list of strategies. Perhaps you meant to capitalize the individual words?")
            counter += 1
        counter = 0
        while type(p2).__name__ == "str" and counter <= len(axl.strategies):
            try:
                if type(options[counter]).__name__ == clicked2NoSpaces:
                    p2 = options[counter]
                    
                    match = axl.Match((p1, p2), turns = t)
                    axelrodOutput1 = Label(axelrodFrame, text=str(match.play()), bg="black", fg="white", relief=SUNKEN, anchor=E)
                    axelrodOutput2 = Label(axelrodFrame, text=str(match.final_score_per_turn()), bg="black", fg="white", relief=SUNKEN, anchor=E)
                    axelrodOutput1.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
                    axelrodOutput2.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
            except IndexError:
                stratNotFoundError = messagebox.showerror("Error", "The strategy you entered for player 2 was not in axelrod's list of strategies. Perhaps you meant to capitalize the individual words?")
            counter += 1

        if axelrodOutput1.winfo_reqwidth() > axelrodOutput2.winfo_reqwidth():
            root.geometry(f"{axelrodOutput1.winfo_reqwidth() + 400}x495")
        else:
            root.geometry(f"700x{axelrodOutput2.winfo_reqwidth() + 200}")
        
        conn = sqlite3.connect('match.db')
        c = conn.cursor()
        
        # Converting the string strategies from the dropdown menus into the actual strategy objects
        p1 = ""
        p2 = ""
        clicked1NoSpaces = clicked1.get().replace(" ", "")
        clicked2NoSpaces = clicked2.get().replace(" ", "")
        counter = 0
        while type(p1).__name__ == "str" and counter < len(axl.strategies):
            if type(options[counter]).__name__ == clicked1NoSpaces:
                p1 = options[counter]
            counter += 1
        counter = 0
        while type(p2).__name__ == "str" and counter < len(axl.strategies):
            if type(options[counter]).__name__ == clicked2NoSpaces:
                p2 = options[counter]
            counter += 1

        c.execute("INSERT INTO matches VALUES (:strategy1, :strategy2, :numTurns, :output, :score1, :score2)",
            {
                'strategy1': clicked1.get(),
                'strategy2': clicked2.get(),
                'numTurns': turnsEntry.get(),
                'output': str(dbPlayMatch(p1, p2, int(turnsEntry.get()))[0]),
                'score1': dbPlayMatch(p1, p2, int(turnsEntry.get()))[1][0],
                'score2': dbPlayMatch(p1, p2, int(turnsEntry.get()))[1][1]
            }
        )
        
        conn.commit()
        conn.close()
            
    elif output == 1: # Don't Add to Database
        p1 = ""
        p2 = ""
        clicked1NoSpaces = clicked1.get().replace(" ", "")
        clicked2NoSpaces = clicked2.get().replace(" ", "")
        counter = 0
        while type(p1).__name__ == "str" and counter <= len(axl.strategies):
            try:
                if type(options[counter]).__name__ == clicked1NoSpaces:
                    p1 = options[counter]
            except IndexError:
                stratNotFoundError = messagebox.showerror("Error", f"The strategy you entered for player 1 \"{clicked1.get()}\" was not in axelrod's list of strategies. Perhaps you meant to capitalize the individual words?")
            counter += 1
        counter = 0
        while type(p2).__name__ == "str" and counter <= len(axl.strategies):
            try:
                if type(options[counter]).__name__ == clicked2NoSpaces:
                    p2 = options[counter]
                    
                    match = axl.Match((p1, p2), turns = t)
                    axelrodOutput1 = Label(axelrodFrame, text=str(match.play()), bg="black", fg="white", relief=SUNKEN, anchor=E, )
                    axelrodOutput2 = Label(axelrodFrame, text=str(match.final_score_per_turn()), bg="black", fg="white", relief=SUNKEN, anchor=E, )
                    axelrodOutput1.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
                    axelrodOutput2.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
                    if axelrodOutput1.winfo_reqwidth() > axelrodOutput2.winfo_reqwidth():
                        root.geometry(f"{axelrodOutput1.winfo_reqwidth() + 400}x425")
                    else:
                        root.geometry(f"700x{axelrodOutput2.winfo_reqwidth() + 200}")
            except IndexError:
                stratNotFoundError = messagebox.showerror("Error", f"The strategy you entered for player 2 \"{clicked2.get()}\" was not in axelrod's list of strategies. Perhaps you meant to capitalize the individual words?")
            counter += 1
    return

def removeStrategy():
    """Removes a single strategy
    """
    global playerEntry
    global stratEntry
    
    # prompt the user for a player index and a strategy name
    topRemoveStrat = Toplevel()
    topRemoveStrat.geometry("220x80")
    playerLabel = Label(topRemoveStrat, text="Enter a player (number):")
    playerEntry = Entry(topRemoveStrat, width=10)
    stratLabel = Label(topRemoveStrat, text="Enter a strategy name:")
    stratEntry = Entry(topRemoveStrat, width=10)
    submitButton = Button(topRemoveStrat, text="Submit", command=submitRemoveStrategy)
    
    # putting everything in the topRemoveStrat window
    playerLabel.grid(row=0, column=0)
    playerEntry.grid(row=0, column=1)
    stratLabel.grid(row=1, column=0)
    stratEntry.grid(row=1, column=1)
    submitButton.grid(row=2, column=1)
    
    return

def resetPayoffMatrix():
    """
        Fills the payoff matrix with zeros and default strategy names
    """
    proceed = messagebox.askokcancel("Clear Payoffs?", "Are you sure you want to reset the payoff matrix?")
    if (proceed == True):
        numStrats1 = int(numStratsEntries[0].get())
        numStrats2 = int(numStratsEntries[1].get())
        
        # clearing the table
        payoffMatrixSlaves = payoffsFrame.grid_slaves()
        for slave in payoffMatrixSlaves:
            slave.grid_remove()
        
        # refilling the table
        for i in range(numStrats2):
            e = Entry(payoffsFrame, width=10)
            if i == 0:
                e.insert(0, "L")
            elif i > 0 and i < numStrats2 - 1 and numStrats2 == 3:
                e.insert(0, "C")
            elif i > 0 and i < numStrats2 - 1 and numStrats2 >= 3:
                e.insert(0, "C" + str(i))
            else:
                e.insert(0, "R")
            e.grid(row=0, column=i + 1, pady=5)
            
        for j in range(numStrats1):
            e = Entry(payoffsFrame, width=10)
            if j == 0:
                e.insert(0, "U")
            elif j > 0 and j < numStrats1 - 1 and numStrats1 == 3:
                e.insert(0, "M")
            elif j > 0 and j < numStrats1 - 1 and numStrats1 > 3:
                e.insert(0, "M" + str(j))
            else:
                e.insert(0, "D")
            e.grid(row=j + 1, column=0, padx=5)

        rows = []
        for i in range(numStrats1):
            cols = []
            for j in range(numStrats2):
                e = Entry(payoffsFrame, width=5)
                e.grid(row=i + 1, column=j + 1, sticky=NSEW)
                e.insert(END, '%d, %d' % (0, 0))
                cols.append(e)
            rows.append(cols)
            
        # Clearing the equilibria
        equilibriaSlaves = equilibriaFrame.grid_slaves()
        eqLabel = equilibriaSlaves[0]
        if type(eqLabel).__name__ == "Label":
            eqLabel.grid_remove()
        
        entriesToSimGame()
        root.geometry(f"{45 * numStrats2 + 700}x{25 * numStrats1 + 490}")
    return

def resetRecord():
    """
    Resets or recomputes the values that should be in a record according to the given inputs. 
    """
    conn = sqlite3.connect('match.db')
    c = conn.cursor()
    
    # Check if an ID was actually selected
    recordID  = selectIDEntry.get()
    if recordID == "":
        emptyRecordIDError = messagebox.showerror("Error", "You must enter an ID to reset a record.")
        conn.commit()
        conn.close()
        return
    
    c.execute("""UPDATE matches SET
              strategy1 = :strategy1, 
              strategy2 = :strategy2, 
              numTurns = :numTurns, 
              output = :output,
              score1 = :score1,
              score2 = :score2
              WHERE oid = :oid""",
              {
                  'strategy1': dbClicked1.get(), 
                  'strategy2': dbClicked2.get(), 
                  'numTurns': dbTurnsEntry.get(),
                  'output': dbPlayMatch(dbClicked1.get(), dbClicked2.get(), int(dbTurnsEntry.get()))[0],
                  'score1': dbPlayMatch(dbClicked1.get(), dbClicked2.get(), int(dbTurnsEntry.get()))[1][0],
                  'score2': dbPlayMatch(dbClicked1.get(), dbClicked2.get(), int(dbTurnsEntry.get()))[1][1],
                  'oid': recordID
              })    
    
    conn.commit()
    conn.close()

def resetStrategies():
    """
    Resets p1's strategy names to U M1 M2 ... D and p2's strategy names to L C1 C2 ... R
    """
    resetStrategiesWarning = messagebox.askokcancel("Clear Strategy Names", "Are you sure you want to reset the strategy names?") 
    
    if resetStrategiesWarning == True:
        numStrats1 = int(numStratsEntries[0].get())
        numStrats2 = int(numStratsEntries[1].get())
        
        # clearing the strategies
        payoffMatrixSlaves = payoffsFrame.grid_slaves()
        strategies = payoffMatrixSlaves[numStrats1 * numStrats2:]
        for slave in strategies:
            slave.grid_remove()
        
        # refilling the table
        for i in range(numStrats2):
            e = Entry(payoffsFrame, width=10)
            if i == 0:
                e.insert(0, "L")
            elif i > 0 and i < numStrats2 - 1 and numStrats2 == 3:
                e.insert(0, "C")
            elif i > 0 and i < numStrats2 - 1 and numStrats2 >= 3:
                e.insert(0, "C" + str(i))
            else:
                e.insert(0, "R")
            e.grid(row=0, column=i + 1, pady=5)
            
        for j in range(numStrats1):
            e = Entry(payoffsFrame, width=10)
            if j == 0:
                e.insert(0, "U")
            elif j > 0 and j < numStrats1 - 1 and numStrats1 == 3:
                e.insert(0, "M")
            elif j > 0 and j < numStrats1 - 1 and numStrats1 > 3:
                e.insert(0, "M" + str(j))
            else:
                e.insert(0, "D")
            e.grid(row=j + 1, column=0, padx=5)
            
        entriesToSimGame()
    else:
        return
    
def revert():
    """
        Reverts back to the original game after computing IESDS
    """
    global numIESDSClicks
    numIESDSClicks = 0
    numStrats1 = int(numStratsEntries[0].get())
    numStrats2 = int(numStratsEntries[1].get())
    try:
        outcomes = originalGame[:originalNumStrats1 * originalNumStrats2] # entries
    except NameError:
        notYetIESDSError = messagebox.showerror("Error", "The IESDS algorithm has not run yet. There's nothing to revert back to.")
    else:
        outcomes.reverse()
        strategyNames = originalGame[originalNumStrats1 * originalNumStrats2:]
        p1StrategyNameEntries = strategyNames[:originalNumStrats1]
        p1StrategyNameEntries.reverse()
        p1StrategyNames = [entry.get() for entry in p1StrategyNameEntries]
        p2StrategyNameEntries = strategyNames[originalNumStrats2:]
        p2StrategyNameEntries.reverse()
        p2StrategyNames = [entry.get() for entry in p2StrategyNameEntries]
        groupedOutcomes = [outcomes[i:i + originalNumStrats2] for i in range(0, len(outcomes), originalNumStrats2)] # entries
        
        newGroupedOutcomes = [] # entries
        for outcome in groupedOutcomes:
            row = []
            for i in range(originalNumStrats2):
                row.append(outcome[i])
            newGroupedOutcomes.append(row)
        
        outcomesListList= [] # entries
        for outcome in newGroupedOutcomes:
            outcomesListList.append(outcome)
            
        newOutcomesListList = []
        for row in outcomesListList:
            newRow = []
            for outcome in row:
                newRow.append(outcome.get().split(", "))
            newOutcomesListList.append(newRow)
        
        for row in newOutcomesListList:
            for outcome in row:
                try:
                    outcome[1]
                except IndexError:
                    missingOutcomeError = messagebox.showerror("Error", f"You cannot revert twice.")
                    return
            
        curGame = payoffsFrame.grid_slaves()
        curOutcomes = curGame[:numStrats1 * numStrats2]
        curOutcomes.reverse()
        curStrategyNames = curGame[numStrats1 * numStrats2:]
        curP1StrategyNameEntries = curStrategyNames[:numStrats1]
        curP1StrategyNameEntries.reverse()
        curP1StrategyNames = [entry.get() for entry in curP1StrategyNameEntries]
        curP2StrategyNameEntries = strategyNames[numStrats2:]
        curP2StrategyNameEntries.reverse()
        curP2StrategyNames = [entry.get() for entry in curP2StrategyNameEntries]
        curGroupedOutcomes = [curOutcomes[i:i + numStrats2] for i in range(0, len(curOutcomes), numStrats2)]
        
        # clearing the current payoff matrix
        for slave in curGame:
            slave.delete(0, 'end')
            slave.grid_remove()
        
        # refilling the table
        for i in range(originalNumStrats1):
            e = Entry(payoffsFrame, width=10)
            e.insert(0, p1StrategyNames[i])
            e.grid(row=0, column=i + 1, pady=5)
        for j in range(originalNumStrats2):
            e = Entry(payoffsFrame, width=10)
            e.insert(0, p2StrategyNames[j])
            e.grid(row=j + 1, column=0, padx=5)
        
        # inserting the original payoffs
        rows = []
        for i in range(originalNumStrats1):
            cols = []
            for j in range(originalNumStrats2):
                e = Entry(payoffsFrame, width=5)
                e.grid(row=i + 1, column=j + 1, sticky=NSEW)
                e.insert(END, '%d, %d' % (int(newOutcomesListList[i][j][0]), int(newOutcomesListList[i][j][1])))
                cols.append(e)
            rows.append(cols)
        
        # setting the numbers of strategies back to the originals
        numStratsFrameSlaves = numStratsFrame.grid_slaves()
        numStratsFrameSlaves[2].delete(0, END)
        numStratsFrameSlaves[2].insert(0, originalNumStrats1)
        numStratsFrameSlaves[1].delete(0, END)
        numStratsFrameSlaves[1].insert(0, originalNumStrats2)

        # entering the "new" payoffs into the system
        enterPayoffs()
        return

def saveAs():
    """
    Save the data of the current payoff matrix in a txt file
    """
    numStrats1 = int(numStratsEntries[0].get())
    numStrats2 = int(numStratsEntries[1].get())
    
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    outcomeEntries = payoffMatrixSlaves[:numStrats1 * numStrats2]
    outcomes = [entry.get() for entry in outcomeEntries]
    outcomes.reverse()
    
    payoffs = [outcome.split(", ") for outcome in outcomes]
    
    groupedPayoffs = [payoffs[i:i + numStrats2] for i in range(0, len(payoffs), numStrats2)]
    
    # Prompting the user for a file name    
    file = filedialog.asksaveasfile(defaultextension = ".txt", mode='w', initialdir=".", title="Save As", filetypes=(("Text files", "*.txt"),))
    if file:
        numStrats1 = int(numStratsEntries[0].get())
        numStrats2 = int(numStratsEntries[1].get())
        
        # Getting list of the strategy names
        payoffMatrixSlaves = payoffsFrame.grid_slaves()
        strategyNames = payoffMatrixSlaves[numStrats1 * numStrats2:]
        
        p1StrategyNames = strategyNames[:numStrats1]
        p1StrategyNames = [name.get() for name in p1StrategyNames]
        p1StrategyNames.reverse()
        p1StrategyNamesString = " ".join(p1StrategyNames)
        p1StrategyNamesString = p1StrategyNamesString + "\n"
        p2StrategyNames = strategyNames[numStrats2:]
        p2StrategyNames = [name.get() for name in p2StrategyNames]
        p2StrategyNames.reverse()
        p2StrategyNamesString = " ".join(p2StrategyNames)
        p2StrategyNamesString = p2StrategyNamesString + "\n"
        
        file.write(str(numStrats1) + " " + str(numStrats2) + "\n")
        file.write(p1StrategyNamesString)
        file.write(p2StrategyNamesString)
        for i, group in enumerate(groupedPayoffs):
            for j, payoff in enumerate(group):
                if j < numStrats2 - 1:
                    file.write(str(payoff[0]) + " " + str(payoff[1]) + " ")
                else:
                    file.write(str(payoff[0]) + " " + str(payoff[1]))
            if i < len(groupedPayoffs) - 1:
                file.write("\n")
    return

def saveAsLatex():
    """
        Saves the current payoff matrix in the format of a buildable LaTeX array
    """
    numStrats1 = int(numStratsEntries[0].get())
    numStrats2 = int(numStratsEntries[1].get())
    
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    outcomes = payoffMatrixSlaves[:numStrats1 * numStrats2]
    payoffs = [outcome.get() for outcome in outcomes]
    payoffs.reverse()
    payoffs = [[payoff[0], payoff[3]] for payoff in payoffs]
    groupedPayoffs = [payoffs[i:i + numStrats2] for i in range(0, len(payoffs), numStrats2)]
    
    # Prompting the user for a file name
    top = Toplevel()
    top.title("Save as LaTeX")
    top.iconbitmap("knight.ico")
    top.geometry("250x30")

    fileNameLabel = Label(top, text="Enter a File Name: ")
    fileNameEntry = Entry(top, width=15)
    fileNameButton = Button(top, text="Enter", command=lambda: [writeToFileLatex(fileNameEntry.get(), groupedPayoffs), top.destroy()])
    
    # Putting everything in the top window
    fileNameLabel.grid(row=0, column=0)
    fileNameEntry.grid(row=0, column=1)
    fileNameButton.grid(row=0, column=2)
    return

def saveRecord():
    """
    Saves an updated record into the database
    """
    conn = sqlite3.connect('match.db')
    c = conn.cursor()
    
    record_id = selectIDEntry.get()
    c.execute("""UPDATE matches SET 
              strategy1 = :strategy1, 
              strategy2 = :strategy2, 
              numTurns = :numTurns, 
              output = :output,
              score1 = :score1,
              score2 = :score2
              WHERE oid = :oid""",
              {
                  'strategy1': updateClicked1.get(), 
                  'strategy2': updateClicked2.get(), 
                  'numTurns': numTurnsEntry.get(),
                  'output': outputEntry.get(),
                  'score1': score1Entry.get(),
                  'score2': score2Entry.get(),
                  'oid': record_id 
              })
    
    conn.commit()
    conn.close()
    topUpdate.destroy()
    
def searchRecords():
    global topSearch
    
    topSearch = Toplevel()
    topSearch.title("Search Records")
    topSearch.iconbitmap("knight.ico")
    topSearch.geometry("400x180")
    
    global searchClicked1
    global searchClicked2
    global numTurnsSearchEntry
    global outputSearchEntry
    global score1SearchEntry
    global score2SearchEntry
    global IDEntry
    
    options = [s() for s in axl.strategies]
    searchClicked1 = StringVar()
    searchClicked2 = StringVar()
    
    # Labels and input fields
    strategy1SearchLabel = Label(topSearch, text="Strategy 1: ")
    strategy1SearchDropdown = ttk.Combobox(topSearch, textvariable=searchClicked1, values=options)
    strategy2SearchLabel = Label(topSearch, text="Strategy 2: ")
    strategy2SearchDropdown = ttk.Combobox(topSearch, textvariable=searchClicked2, values=options)
    numTurnsSearchLabel = Label(topSearch, text="Number of turns: ")
    numTurnsSearchEntry = Entry(topSearch, width=5)
    outputSearchLabel = Label(topSearch, text="Output: ")
    outputSearchEntry = Entry(topSearch, width=45)
    score1SearchLabel = Label(topSearch, text="Score 1: ")
    score1SearchEntry = Entry(topSearch, width=20)
    score2SearchLabel = Label(topSearch, text="Score 2: ")
    score2SearchEntry = Entry(topSearch, width=20)
    IDLabel = Label(topSearch, text="ID: ")
    IDEntry = Entry(topSearch, width=20)
    
    # Putting everything in the topSearch window
    strategy1SearchLabel.grid(row=0, column=0, sticky=E)
    strategy1SearchDropdown.grid(row=0, column=1, sticky=W)
    strategy2SearchLabel.grid(row=1, column=0, sticky=E)
    strategy2SearchDropdown.grid(row=1, column=1, sticky=W)
    numTurnsSearchLabel.grid(row=2, column=0, padx=(10, 0), sticky=E)
    numTurnsSearchEntry.grid(row=2, column=1, sticky=W)
    outputSearchLabel.grid(row=3, column=0, sticky=E)
    outputSearchEntry.grid(row=3, column=1, sticky=W)
    score1SearchLabel.grid(row=4, column=0, sticky=E)
    score1SearchEntry.grid(row=4, column=1, sticky=W)
    score2SearchLabel.grid(row=5, column=0, sticky=E)
    score2SearchEntry.grid(row=5, column=1, sticky=W, pady=(0,5))
    IDLabel.grid(row=6, column=0, sticky=E)
    IDEntry.grid(row=6, column=1, sticky=W)
    
    submitButton = Button(topSearch, text="Submit", command=submitQuery)
    submitButton.grid(row=7, column=0, columnspan=2)
    
    return

def showRecords():
    # Create a database or connect to one
    conn = sqlite3.connect('match.db')
    
    # Create cursor
    c = conn.cursor()
    
    c.execute("SELECT *, oid FROM matches")
    records = c.fetchall()
    numRecords = len(records)

    recordsList = []
    recordsList.append(f"{numRecords} records retrieved from the matches table\n")
    for record in records:
        recordsList.append(
            str(record[0]) + " " + str(record[1]) + " " + str(record[2]) + " " + str(record[3]) + " " + str(record[4]) + " " + str(record[5]) + " " + str(record[6])
        )
    recordsList.reverse()
    
    myFrame = LabelFrame(dbWindow)
    
    xscrollbar = Scrollbar(myFrame, orient=HORIZONTAL)
    yscrollbar = Scrollbar(myFrame, orient=VERTICAL)
    
    showRecordsListBox = Listbox(myFrame, width=50, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, bg="black", fg="white")
    for record in recordsList:
        showRecordsListBox.insert(0, record)
    
    myFrame.grid(row=14, column=0, columnspan=2)
    showRecordsListBox.grid(row=0, column=0, padx=10, sticky=NSEW)
    xscrollbar.grid(row=1, column=0, columnspan=2, sticky=EW)
    xscrollbar.config(command = showRecordsListBox.xview)
    yscrollbar.grid(row=0, column=1, sticky=NS)
    yscrollbar.config(command = showRecordsListBox.yview)
    
    # Commit changes
    conn.commit()
    # Close Connection
    conn.close()
    
    return

def simGameToEntries():
    """Loads the data from the SimGame object into the entries.
    """
    oldNumStrats1 = int(numStratsEntry1.get())
    oldNumStrats2 = int(numStratsEntry2.get())
    
    # Getting G.numPlayers
    oldNumPlayers = numPlayersEntry.get()
    numPlayersEntry.delete(0, END)
    numPlayersEntry.insert(G.numPlayers)
    
    # Handle cases where G.numPlayers is different from what's on the screen
    if oldNumPlayers <= G.numPlayers:
        # Need to add more numStrat labels and entries
        for x in range(oldNumPlayers, G.numPlayers):
            l = Label(dimensionsFrame, text=f"Number of strategies for player {x}: ")
            l.grid(row=x, column=0)
            e = Entry(dimensionsFrame, width=5)
            e.grid(row=x, column=1)
    else:
        # FIXME: Removing the extra numStrats labels and entries
        # FIXME: Can't test this without being able to load a 3-player game into interactiveGT! 
        dimensionsSlaves = dimensionsFrame.grid_slaves()
        slavesToDelete = []
        for slave in dimensionsSlaves:
            if type(slave).__name__ == "Label" or type(slave).__name__ == "Entry":
                slavesToDelete.append(slave)
        if type(slavestoDelete[-2]).__name__ == "Label":
            print("-2:", slavestoDelete[-2]["text"])
        if type(slavestoDelete[-1]).__name__ == "Label":
            print("-1:", slavestoDelete[-1]["text"])
    
    # Getting numStrats
    dimensionsSlaves = dimensionsFrame.grid_slaves()
    numStratsEntries = []
    for slave in dimensionsSlaves:
        if type(slave).__name__ == "Entry":
            numStratsEntries.append(slave)
    numStratsEntries.pop() # last one will be the numPlayers entry
    numStratsEntries.reverse()
    
    for x in range(G.numPlayers):
        numStratsEntries[x].delete(0, END)
        numStratsEntries[x].insert(G.players[x].numStrats)
        
    # FIXME: handle cases where entries need to be added or deleted
    # Getting payoffs
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    outcomes = payoffMatrixSlaves[:oldNumStrats1 * oldNumStrats2]
    groupedOutcomes = [outcomes[i:i + numStrats2] for i in range(0, len(outcomes), numStrats2)] # entries
    strategyNames = payoffMatrixSlaves[oldNumStrats1 * oldNumStrats2:]
    
    newGroupedOutcomes = []
    for outcome in groupedOutcomes:
        row = []
        for i in range(oldNumStrats2):
            row.append(outcome[i])
        newGroupedOutcomes.append(row)
    
    outcomesListList= []
    for outcome in newGroupedOutcomes:
        outcomesListList.append(outcome)
    
    # FIXME: handle cases where entries need to be added or deleted
    # Getting strategy names
    p1StrategyNames = strategyNames[:oldNumStrats1]
    p1StrategyNames = [name.get() for name in p1StrategyNames]
    p1StrategyNames.reverse()
    p2StrategyNames = strategyNames[oldNumStrats2:]
    p2StrategyNames = [name.get() for name in p2StrategyNames]
    p2StrategyNames.reverse()
    return

"""def startTournament(t = 10, r = 5):
    players = [s() for s in axl.demo_strategies]
    tournament = axl.Tournament(players=players, turns=t, repetitions=r)
    results = tournament.play()
    print("results:", results)
    
    axelrodOutput1 = Label(axelrodFrame, text=results, relief=SUNKEN, bd=1, anchor=E)
    axelrodOutput2 = Label(axelrodFrame, text=results, relief=SUNKEN, bd=1, anchor=E)
    
    axelrodOutput1.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
    axelrodOutput2.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
    return"""
    
def submitRemoveStrategy():
    """Removes the strategy for the player entered in function removeStrategy
    """
    entriesToSimGame()
    
    numStrats1 = int(numStratsEntries[0].get())
    numStrats2 = int(numStratsEntries[1].get())

    # get the index that corresponds to the given strategy name
    player = int(playerEntry.get()) - 1
    stratName = stratEntry.get()
    
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    outcomes = payoffMatrixSlaves[:numStrats1 * numStrats2]
    groupedOutcomes = [outcomes[i:i + numStrats2] for i in range(0, len(outcomes), numStrats2)] # entries
    strategyNames = payoffMatrixSlaves[numStrats1 * numStrats2:]
    
    p1StrategyNames = strategyNames[:numStrats1]
    p1StrategyNames = [name.get() for name in p1StrategyNames]
    p1StrategyNames.reverse()
    p2StrategyNames = strategyNames[numStrats2:]
    p2StrategyNames = [name.get() for name in p2StrategyNames]
    p2StrategyNames.reverse()
    
    newGroupedOutcomes = []
    for outcome in groupedOutcomes:
        row = []
        for i in range(numStrats2):
            row.append(outcome[i])
        newGroupedOutcomes.append(row)
    
    outcomesListList= []
    for outcome in newGroupedOutcomes:
        outcomesListList.append(outcome)
    
    stratIndex = -1
    if player == 0:
        for i, name in enumerate(p1StrategyNames):
            if name == stratName:
                stratIndex = i
    
        for j in range(numStrats2):
            outcomesListList[stratIndex][j].grid_remove()
            
        G.removeStrategy(player, stratIndex)
        
    elif player == 1:
        for j, name in enumerate(p2StrategyNames):
            if name == stratName:
                stratIndex = j
        
        for i in range(numStrats1):
            outcomesListList[i][stratIndex].grid_remove()
            
        G.removeStrategy(player, stratIndex)
    else:
        # FIXME
        return
    
    return
    
def submitQuery():
    """
    Submits the user's query when searching the match database
    """
    conn = sqlite3.connect('match.db')
    c = conn.cursor()
    
    # Building the query that we'll search with
    tupleSize = 0
    searchQuery = "SELECT *, oid FROM matches"
    whereAdded = False
    if searchClicked1.get() != "":
        if not whereAdded:
            searchQuery = searchQuery + " WHERE "
            whereAdded = True
        searchQuery = searchQuery + "strategy1='" + searchClicked1.get() + "'"
        searchQuery = searchQuery + " OR strategy2='" + searchClicked1.get() + "'"
    if searchClicked2.get() != "":
        if not whereAdded:
            searchQuery = searchQuery + " WHERE "
            whereAdded = True
        else:
            searchQuery = searchQuery + " AND "
        searchQuery = searchQuery + "strategy2='" + searchClicked2.get() + "'"
        searchQuery = searchQuery + "or strategy1='" + searchClicked2.get() + "'"
    if searchClicked1.get() != "" and searchClicked2.get() != "":
        searchQuery = searchQuery + " OR strategy1='" + searchClicked2.get() + "' AND strategy2='" + searchClicked1.get() + "'"
    if numTurnsSearchEntry.get() != "":
        if not whereAdded:
            searchQuery = searchQuery + " WHERE "
            whereAdded = True
        else: 
            searchQuery = searchQuery + " AND "
        searchQuery = searchQuery + "numTurns=" + numTurnsSearchEntry.get()
    if outputSearchEntry.get() != "":
        if not whereAdded:
            searchQuery = searchQuery + " WHERE "
            whereAdded = True
        else:
            searchQuery = searchQuery + " AND "
        searchQuery = searchQuery + "output='" + outputSearchEntry.get() + "'"
    if score1SearchEntry.get() != "":
        if not whereAdded:
            searchQuery = searchQuery + " WHERE "
            whereAdded = True
        else:
            searchQuery = searchQuery + " AND "
        searchQuery = searchQuery + "score1='" + score1SearchEntry.get() + "'"
    if score2SearchEntry.get() != "":
        if not whereAdded:
            searchQuery = searchQuery + " WHERE "
            whereAdded = True
        else:
            searchQuery = searchQuery + " AND "
        searchQuery = searchQuery + "score2='" + score2SearchEntry.get() + "'"
        tupleSize += 1
    if IDEntry.get() != "":
        if not whereAdded:
            searchQuery = searchQuery + " WHERE "
            whereAdded = True
        else:
            searchQuery = searchQuery + " AND "
        searchQuery = searchQuery + "oid='" + IDEntry.get() + "'"
    
    c.execute(searchQuery)
    
    records = c.fetchall()
    
    numRecords = len(records)
    
    proceed = True
    if numRecords >= 100000:
        proceed = messagebox.askyesno("Warning", f"The number of records retrieved from the database was {numRecords}. This may take some time. Do you want to proceed?")
    
    if proceed == True:
        recordsList = []
        if numRecords == 1:
            recordsList.append(f"{numRecords} record retrieved from the matches table\n")
        else: 
            recordsList.append(f"{numRecords} records retrieved from the matches table\n")
        for record in records:
            recordsList.append(str(record[0]) + " " + str(record[1]) + " " + str(record[2]) + " " + str(record[3]) + " " + str(record[4]) + " " + str(record[5]) + " " + str(record[6]))
        recordsList.reverse()
        
        searchResultsFrame = LabelFrame(topSearch)
        
        xscrollbar = Scrollbar(searchResultsFrame, orient=HORIZONTAL)
        yscrollbar = Scrollbar(searchResultsFrame, orient=VERTICAL)
        
        showRecordsListBox = Listbox(searchResultsFrame, width=50, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, bg="black", fg="white")
        for record in recordsList:
            showRecordsListBox.insert(0, record)
            
        exportSearchButton = Button(topSearch, text="Export to csv", command=lambda: exportSearchGetFileName(records))
        
        searchResultsFrame.grid(row=11, column=0, columnspan=2)
        showRecordsListBox.grid(row=0, column=0, padx=10, sticky=NSEW)
        xscrollbar.grid(row=1, column=0, columnspan=2, sticky=EW)
        xscrollbar.config(command = showRecordsListBox.xview)
        yscrollbar.grid(row=0, column=1, sticky=NS)
        yscrollbar.config(command = showRecordsListBox.yview)
        
        exportSearchButton.grid(row=12, column=0, columnspan=2)
        
        topSearch.geometry("400x400")
        
        conn.commit()
        conn.close()
    else:
        conn.commit()
        conn.close()
    return

def updateRecord():
    """
    Allows the user to manually update a record in the matches table
    """    
    conn = sqlite3.connect('match.db')
    c = conn.cursor()
    
    recordID = selectIDEntry.get()
    try:
        c.execute("SELECT * FROM matches WHERE oid=" + recordID)
    except sqlite3.OperationalError:
        IDNotSelectedError = messagebox.showerror("Error", "You must enter an ID to update a record.")
        
        conn.commit()
        conn.close()
        return
    
    global topUpdate
    topUpdate = Toplevel()
    topUpdate.title("Update a Record")
    topUpdate.iconbitmap("knight.ico")
    topUpdate.geometry("400x170")
        
    records = c.fetchall()
    
    global updateClicked1
    global updateClicked2
    global numTurnsEntry
    global outputEntry
    global score1Entry
    global score2Entry
    
    options = [s() for s in axl.strategies]
    updateClicked1 = StringVar()
    updateClicked1.set(options[0])
    updateClicked2 = StringVar()
    updateClicked2.set(options[0])
    
    # Labels and input fields
    strategy1Label = Label(topUpdate, text="Strategy 1: ")
    strategy1Dropdown = ttk.Combobox(topUpdate, textvariable=updateClicked1, values=options)
    strategy2Label = Label(topUpdate, text="Strategy 2: ")
    strategy2Dropdown = ttk.Combobox(topUpdate, textvariable=updateClicked2, values=options)
    numTurnsLabel = Label(topUpdate, text="Number of turns: ")
    numTurnsEntry = Entry(topUpdate, width=5)
    outputLabel = Label(topUpdate, text="Output: ")
    outputEntry = Entry(topUpdate, width=45)
    score1Label = Label(topUpdate, text="Score 1: ")
    score1Entry = Entry(topUpdate, width=20)
    score2Label = Label(topUpdate, text="Score 2: ")
    score2Entry = Entry(topUpdate, width=20)
    
    # Putting everything in the topUpdate window
    strategy1Label.grid(row=0, column=0, sticky=E)
    strategy1Dropdown.grid(row=0, column=1, sticky=W)
    strategy2Label.grid(row=1, column=0, sticky=E)
    strategy2Dropdown.grid(row=1, column=1, sticky=W)
    numTurnsLabel.grid(row=2, column=0, padx=(10, 0), sticky=E)
    numTurnsEntry.grid(row=2, column=1, sticky=W)
    outputLabel.grid(row=3, column=0, sticky=E)
    outputEntry.grid(row=3, column=1, sticky=W)
    score1Label.grid(row=4, column=0, sticky=E)
    score1Entry.grid(row=4, column=1, sticky=W)
    score2Label.grid(row=5, column=0, sticky=E)
    score2Entry.grid(row=5, column=1, sticky=W, pady=(0,5))
    
    # Loop through results
    for record in records:
        updateClicked1.set(record[0])
        updateClicked2.set(record[1])
        numTurnsEntry.insert(0, record[2])
        outputEntry.insert(0, record[3])
        score1Entry.insert(0, record[4])
        score2Entry.insert(0, record[5])
        
    saveButton = Button(topUpdate, text="Save Record", command=saveRecord)
    saveButton.grid(row=6, column=0, columnspan=2)
    
    conn.commit()
    conn.close()
    
    return

def writeToFile(fileName, groupedPayoffs):
    """
        Writes the data of the current game into the fileName file
    """
    # input validation
    if ".txt" not in fileName and "." in fileName:
        wrongExtensionError = messagebox.showerror("Error", f"The file name \"{fileName}\" contains the wrong file extension. The extension should be \".txt\".")
        return
    elif ".txt" not in fileName and "." not in fileName:
        fileName = fileName + ".txt"
        
    numPeriods = 0
    for char in fileName:
        if char == '.':
            numPeriods += 1
    if numPeriods != 1:
        multiplePeriodsError = messagebox.showerror("Error", f"The file name \"{fileName}\" contains multiple periods.")
        return
    
    numStrats1 = int(numStratsEntries[0].get())
    numStrats2 = int(numStratsEntries[1].get())
    
    # Getting list of the strategy names
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    strategyNames = payoffMatrixSlaves[numStrats1 * numStrats2:]
    
    p1StrategyNames = strategyNames[:numStrats1]
    p1StrategyNames = [name.get() for name in p1StrategyNames]
    p1StrategyNames.reverse()
    p1StrategyNamesString = " ".join(p1StrategyNames)
    p1StrategyNamesString = p1StrategyNamesString + "\n"
    p2StrategyNames = strategyNames[numStrats2:]
    p2StrategyNames = [name.get() for name in p2StrategyNames]
    p2StrategyNames.reverse()
    p2StrategyNamesString = " ".join(p2StrategyNames)
    p2StrategyNamesString = p2StrategyNamesString + "\n"
    
    # writing to file
    with open(fileName, 'w') as file:
        file.write(str(numStrats1) + " " + str(numStrats2) + "\n")
        file.write(p1StrategyNamesString)
        file.write(p2StrategyNamesString)
        for i, group in enumerate(groupedPayoffs):
            for j, payoff in enumerate(group):
                if j < numStrats2 - 1:
                    file.write(str(payoff[0]) + " " + str(payoff[1]) + " ")
                else:
                    file.write(str(payoff[0]) + " " + str(payoff[1]))
            if i < len(groupedPayoffs) - 1:
                file.write("\n")
    return

def writeToFileLatex(fileName, groupedPayoffs):
    """
        Writes the data of the current game into the fileName file in the format of a buildable LaTeX array
    """
    LETTERS = ["a", "b", "c", "d", "e", "f","g", "h","i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",]
    GREEK_LETTERS = [
        "alpha",
        "beta",
        "gamma",
        "delta",
        "epsilon",
        "zeta",
        "eta",
        "theta",
        "iota",
        "kappa",
        "lambda",
        "mu", 
        "nu",
        "xi",
        # "omicron",
        "pi",
        "rho",
        "sigma",
        "tau",
        "upsilon",
        "phi",
        "chi",
        "psi",
        "omega"
    ]
    CAPITAL_GREEK_LETTERS = [
        # "Alpha",
        # "Beta",
        "Gamma",
        "Delta",
        # "Epsilon",
        # "Zeta",
        # "Eta", 
        "Theta",
        # "Iota",
        # "Kappa",
        "Lambda",
        # "Mu", 
        # "Nu",
        "Xi",
        # "Omicron",
        "Pi",
        # "Rho",
        "Sigma",
        # "Tau",
        # "Upsilon"
        "Phi",
        "Chi",
        "Psi",
        "Omega"
    ]
    
    numStrats1 = int(numStratsEntries[0].get())
    numStrats2 = int(numStratsEntries[1].get())
    
    # Getting list of the strategy names
    """
    We want to accept all names of the forms: 
      X+, 
      X+n+, 
      X+_n+, 
      g, 
      gn+, and 
      g_n, 
    where X+ is a string of characters, g is the English name of a greek letter, and n+ is a string of digits, and reject all others. So, we want to reject things like spaces, n+, n+X+, X+_ and any name with multiple underscores
    """
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    strategyNameEntries = payoffMatrixSlaves[numStrats1 * numStrats2:]
    
    # P1 ###########################################################
    p1StrategyNameEntries = strategyNameEntries[:numStrats1]
    p1StrategyNameEntries.reverse()
    p1StrategyNames = [name.get() for name in p1StrategyNameEntries]
    
    # Input validation; checking for invalid names and cancelling if rejects are found
    for i, name in enumerate(p1StrategyNames):
        if name[0].isalpha(): # starts with a letter
            numUnderscores = 0
            for char in name:
                if char == "_":
                    numUnderscores += 1
                    if numUnderscores > 1:
                        # ERROR: multiple underscores
                        multipleUnderscoresError = messagebox.showerror("Error", f"Invalid strategy name \"{name}\". Strategy names may not contain multiple underscores.")
                        return
                    
            if " " in name:
                # ERROR: spaces
                spacesError = messagebox.showerror("Error", f"Invalid strategy name \"{name}\". Strategy names may not contain spaces.")
                
            if name[-1] == "_":
                # ERRROR: ending underscore
                endingUnderscoreError = messagebox.showerror("Error", f"Invalid strategy name \"{name}\". Strategy names may not end with an underscore.")
            
            # Getting the last index of the first alphabetical string in the name
            # num = 0
            # breakWhile = False
            # while num < len(name) and not name[num].isdigit():
            #     for g in GREEK_LETTERS:
            #         if g in name[num + 1:len(name) - 1]:
            #             lastIndexOfFirstString = num
            #             breakWhile = True
            #             break
            #     if breakWhile == True:
            #         break
            #     if name[num].isdigit() or num == len(name) - 1:
            #         lastIndexOfFirstString = num
            #     num += 1
            
            # adding a slash to greek letters
            if name in GREEK_LETTERS or name in CAPITAL_GREEK_LETTERS:
                p1StrategyNames[i] = "\\" + name
            
            if name[-1].isdigit():
                # Getting the position of the last alphabetical character in the name
                lastAlphaPos = -1
                j = len(name) - 1
                while j > 0 and lastAlphaPos == -1:
                    if name[j].isalpha():
                        lastAlphaPos = j
                    j -= 1
                # inserting an underscore at that position
                if "_" not in name:
                    p1StrategyNames[i] = name[:lastAlphaPos + 1] + "_" + name[lastAlphaPos + 1:]
            
            if name[:lastAlphaPos + 1] in GREEK_LETTERS or name[:lastAlphaPos + 1] in CAPITAL_GREEK_LETTERS:
                p1StrategyNames[i] = "\\" + p1StrategyNames[i]
        else:
            # ERROR: n+, n+X, _X+
            digitsAndUnderscoresError = messagebox.showerror("Error", f"Invalid strategy name \"{name}\". Strategy names may not begin with digits or underscores.")
            return
    # P2 ###########################################################
    p2StrategyNamesEntries = strategyNameEntries[numStrats1:]
    p2StrategyNamesEntries.reverse()
    p2StrategyNames = [name.get() for name in p2StrategyNamesEntries]
    
    # Input validation; checking for invalid names and cancelling if rejects are found
    for i, name in enumerate(p2StrategyNames):
        if name[0].isalpha(): # starts with a letter
            numUnderscores = 0
            for char in name:
                if char == "_":
                    numUnderscores += 1
                    if numUnderscores > 1:
                        # ERROR: multiple underscores
                        multipleUnderscoresError = messagebox.showerror("Error", f"Invalid strategy name \"{name}\". Strategy names may not contain multiple underscores.")
                        return
                    
            if " " in name:
                # ERROR: spaces
                spacesError = messagebox.showerror("Error", f"Invalid strategy name \"{name}\". Strategy names may not contain spaces.")
                
            if name[-1] == "_":
                # ERRROR: ending underscore
                endingUnderscoreError = messagebox.showerror("Error", f"Invalid strategy name \"{name}\". Strategy names may not end with an underscore.")
            
            if name in GREEK_LETTERS or name in CAPITAL_GREEK_LETTERS:
                    p2StrategyNames[i] = "\\" + name
                    
            if name[-1].isdigit():
                # Getting the position of the last alphabetical character in the name
                lastAlphaPos = -1
                j = len(name) - 1
                while j > 0 and lastAlphaPos == -1:
                    if name[j].isalpha():
                        lastAlphaPos = j
                    j -= 1
                # inserting an underscore at that position
                if "_" not in name:
                    p2StrategyNames[i] = name[:lastAlphaPos + 1] + "_" + name[lastAlphaPos + 1:]
            
            if name[:lastAlphaPos + 1] in GREEK_LETTERS or name[:lastAlphaPos + 1] in CAPITAL_GREEK_LETTERS:
                p2StrategyNames[i] = "\\" + p2StrategyNames[i]
        else:
            # ERROR: n+, n+X, _X+
            digitsAndUnderscoresError = messagebox.showerror("Error", f"Invalid strategy name \"{name}\". Strategy names may not begin with digits or underscores.")
            return
    
    with open(fileName, 'w') as file:
        file.write("\documentclass[12pt]{article}\n\n")
        file.write("\\begin{document}\n")
        file.write("\[\n")
        file.write("\t\\begin{array}{|c||")
        
    with open(fileName, 'r') as file:
        lines = file.readlines()
    
    for i in range(numStrats2):
        lines[-1] = lines[-1] + "c|"
    lines[-1] = lines[-1] + "}\n"
        
    with open(fileName, "w") as file:
        file.writelines(lines)        
        file.write("\t\t\hline\n")
        # writing p2's strategy names
        nameString = " & ".join(p2StrategyNames)
        nameString = "& " + nameString + " "
        file.write("\t\t" + nameString + "\\\\ \hline\hline\n")
        
        # getting payoffs
        payoffMatrixSlaves = payoffsFrame.grid_slaves()
        for i in range(numStrats1 + numStrats2):
            payoffMatrixSlaves.pop()
        payoffs = [tuple(map(int, slave.get().split(", "))) for slave in payoffMatrixSlaves]
        payoffs.reverse()
        numStrats1 = int(numStratsEntries[0].get())
        numStrats2 = int(numStratsEntries[1].get())

        # converting the list of payoffs to a list of lists
        newPayoffs = []
        row = []
        numInRow = 0
        for p in payoffs:
            if numInRow < numStrats2:
                row.append(p)
                numInRow += 1
                if numInRow == numStrats2:
                    newPayoffs.append(row)
                    numInRow = 0
                    row = []
                    
        p1Matrix = []
        p2Matrix = []
        for i in range(numStrats1):
            row1 = []
            row2 = []
            for j in range(numStrats2):
                row1.append(newPayoffs[i][j][0])
                row2.append(newPayoffs[i][j][1])
            p1Matrix.append(row1)
            p2Matrix.append(row2)
            
        # updating G
        G = nash.Game(p1Matrix, p2Matrix)
        
        zeros1 = [0 for i in range(numStrats1)]
        zeros2 = [0 for i in range(numStrats2)]
        for i, group in enumerate(groupedPayoffs):
            zeros1[i] = 1
            array1 = np.array(zeros1)
            file.write("\t\t" + p1StrategyNames[i] + " & ")
            for j, payoff in enumerate(group):
                zeros2[j] = 1
                array2 = np.array(zeros2)
                result = G.is_best_response(array1, array2)
                if j < numStrats2 - 1:
                    if result[0] == True and result[1] == False:# p1 best response
                        file.write("(" + str(payoff[0]) + "), " + str(payoff[1]) + " & ")
                    elif result[0] == False and result[1] == True:# p2 best response
                        file.write(str(payoff[0]) + ", (" + str(payoff[1]) + ") & ")
                    elif result[0] == True and result[1] == True:# both best reponses
                        file.write("(" + str(payoff[0]) + "), (" + str(payoff[1]) + ") & ")
                    else: # not
                        file.write(str(payoff[0]) + ", " + str(payoff[1]) + " & ")
                else:
                    if result[0] == True and result[1] == False:# p1 best response
                        file.write("(" + str(payoff[0]) + "), " + str(payoff[1]) + " \\\\ \hline")
                    elif result[0] == False and result[1] == True:# p2 best response
                        file.write(str(payoff[0]) + ", (" + str(payoff[1]) + ") \\\\ \hline")
                    elif result[0] == True and result[1] == True:# both best reponses
                        file.write("(" + str(payoff[0]) + "), (" + str(payoff[1]) + ") \\\\ \hline")
                    else: # not
                        file.write(str(payoff[0]) + ", " + str(payoff[1]) + " \\\\ \hline")
                zeros2 = [0 for i in range(numStrats2)]
            file.write("\n")
            zeros1 = [0 for i in range(numStrats1)]
        
        file.write("\t\end{array}\n")
        file.write("\]\n")
        file.write("\end{document}")
    return

###################################################################
# Creating our SimGame object
global G
G = SimGame(2)

# Defining the root window
root = Tk()
root.title("Interactive GT")
root.geometry("700x490")
root.iconbitmap("knight.ico")

# Initializing the number of IESDS steps computed to 0
numIESDSClicks = 0

# Menu bar
menubar = Menu(root)
root.config(menu=menubar)
# Create a menu item
file_menu = Menu(menubar)
menubar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open File", command=openFile)
file_menu.add_separator()
file_menu.add_command(label="Save As...", command=saveAs)
file_menu.add_command(label="Save as LaTeX", command=saveAsLatex)

edit_menu = Menu(menubar)
menubar.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Enter Values into SimGame Object", command=entriesToSimGame)
edit_menu.add_command(label="Load Values from SimGame Object", command=simGameToEntries)
edit_menu.add_separator()
edit_menu.add_command(label="Remove a Strategy", command=removeStrategy)
edit_menu.add_separator()
edit_menu.add_command(label="Clear Payoffs", command=clearPayoffs)
edit_menu.add_command(label="Clear Payoff Matrix", command=clearPayoffMatrix)
edit_menu.add_command(label="Clear Strategy Names", command=clearStrategies)
edit_menu.add_separator()
edit_menu.add_command(label="Reset Payoff Matrix", command=resetPayoffMatrix)
edit_menu.add_command(label="Reset Strategy Names", command=resetStrategies)

option_menu = Menu(menubar)
menubar.add_cascade(label="Options", menu=option_menu)
option_menu.add_command(label="Change Background Color", command=changeBackgroundColor)

# rootFrame < rootCanvas < mainFrame < root
mainFrame = Frame(root)
rootCanvas = Canvas(mainFrame) # canvas in root
rootFrame = Frame(rootCanvas) # frame in canvas
xRootScrollbar = Scrollbar(mainFrame, orient="horizontal", command=rootCanvas.xview) # scrollbar in root
yRootScrollbar = Scrollbar(mainFrame, orient="vertical", command=rootCanvas.yview)   # scrollbar in root
rootCanvas.configure(xscrollcommand = xRootScrollbar.set, yscrollcommand = yRootScrollbar.set)
xRootScrollbar.pack(side=BOTTOM, fill=X)
yRootScrollbar.pack(side=RIGHT, fill=Y)
rootCanvas.pack(side=TOP)
rootCanvas.create_window((0, 0), window=rootFrame, anchor = "nw")
rootFrame.bind("<Configure>", lambda e: rootCanvas.configure(scrollregion=rootCanvas.bbox("all"), width=root.winfo_width() - 25, height=root.winfo_height() - 25))

# Dimensions Frame
dimensionsFrame = LabelFrame(rootFrame, text="Dimensions")
# numPlayers
numPlayersLabel = Label(dimensionsFrame, text="Number of players: ")
numPlayersEntry = Entry(dimensionsFrame, width=5)
numPlayersEntry.insert(0, "2")
# numStrats
numStratsLabels = [Label(dimensionsFrame, text=f"Number of strategies for player {x + 1}:", anchor=E) for x in range(G.numPlayers)]
numStratsEntries = [Entry(dimensionsFrame, width=5) for x in range(G.numPlayers)]
for x in range(G.numPlayers):
    numStratsEntries[x].insert(0, "2")
dimensionsButton = Button(dimensionsFrame, text="Enter", command=dimensionsClick)

# Payoffs Frame
payoffsFrame = LabelFrame(rootFrame, text="Payoffs", padx=10, pady=10)

# Adding strategy names
p2strat1Name = Entry(payoffsFrame, width=10)
p2strat2Name = Entry(payoffsFrame, width=10)
p1strat1Name = Entry(payoffsFrame, width=10)
p1strat2Name = Entry(payoffsFrame, width=10)
p2strat1Name.insert(0, "L")
p2strat2Name.insert(0, "R")
p1strat1Name.insert(0, "U")
p1strat2Name.insert(0, "D")
p2strat1Name.grid(row=0, column=1, pady=5)
p2strat2Name.grid(row=0, column=2, pady=5)
p1strat1Name.grid(row=1, column=0, padx=5)
p1strat2Name.grid(row=2, column=0, padx=5)

# Putting the payoffs in the frame
# https://www.activestate.com/resources/quick-reads/how-to-display-data-in-a-table-using-tkinter/
rows = []
for i in range(int(numStratsEntries[0].get())):
    cols = []
    for j in range(int(numStratsEntries[1].get())):
        e = Entry(payoffsFrame, width=5)
        e.grid(row=i + 1, column=j + 1, sticky=NSEW)
        e.insert(END, '%d, %d' % (0, 0))
        cols.append(e)
    rows.append(cols)

payoffMatrixSlaves = payoffsFrame.grid_slaves()
# removing the strategy names from payoffMatrixSlaves
payoffMatrixSlaves.pop()
payoffMatrixSlaves.pop()
payoffMatrixSlaves.pop()
payoffMatrixSlaves.pop()
payoffs = [list(map(int, slave.get().split(", "))) for slave in payoffMatrixSlaves]
payoffs.reverse()
numStrats1 = int(numStratsEntries[0].get())
numStrats2 = int(numStratsEntries[1].get())

# converting the list of payoffs to a list of lists
newPayoffs = []
row = []
numInRow = 0
for p in payoffs:
    if numInRow < numStrats2:
        row.append(p)
        numInRow += 1
        if numInRow == numStrats2:
            newPayoffs.append(row)
            numInRow = 0
            row = []

G.enterPayoffs(newPayoffs, 2, [2, 2])

# Eliminate Strictly Dominated Strategies Frame
iesdsFrame = LabelFrame(rootFrame, text="IESDS", padx=10, pady=10)

iesdsSteps = IntVar()
iesdsSteps.set("0")

Radiobutton(iesdsFrame, text="Full Computation", variable=iesdsSteps, value=0, command=lambda: iesdsStepsClicked(iesdsSteps.get())).grid(row=0, column=0, sticky=W)
revertButton = Button(iesdsFrame, text="Revert", command=revert)
Radiobutton(iesdsFrame, text="Computation in Steps", variable=iesdsSteps, value=1, command=lambda: iesdsStepsClicked(iesdsSteps.get())).grid(row=1, column=0, sticky=W)
iesdsButton = Button(iesdsFrame, text="Eliminate Strictly Dominated Strategies", command=lambda: eliminateStrictlyDominatedStrategies(iesdsSteps.get()))

# Equilibria Frame
equilibriaFrame = LabelFrame(rootFrame, text="Equilibria" , padx=10, pady=10)

eqOutput = IntVar()
eqOutput.set("0")

Radiobutton(equilibriaFrame, text="Standard nashpy Output", variable=eqOutput, value=0, command=lambda: equilibriaOutputStyleClicked(eqOutput.get())).grid(row=0, column=0, sticky=W)
Radiobutton(equilibriaFrame, text="Named Strategies", variable=eqOutput, value=1, command=lambda: equilibriaOutputStyleClicked(eqOutput.get())).grid(row=1, column=0, sticky=W)

equilibriaButton = Button(equilibriaFrame, text="Compute Equilibria", command=lambda: computeEquilibria(eqOutput.get()))

# Axelrod Frame
axelrodFrame = LabelFrame(rootFrame, text="axelrod" , padx=10, pady=10)
strategyLabel1 = Label(axelrodFrame, text="Choose a strategy for player 1: ")
strategyLabel2 = Label(axelrodFrame, text="Choose a strategy for player 2: ")
options = [s() for s in axl.strategies]
clicked1 = StringVar()
clicked1.set(options[0])
clicked2 = StringVar()
clicked2.set(options[0])
dropdown1 = ttk.Combobox(axelrodFrame, textvariable=clicked1, values=options)
dropdown2 = ttk.Combobox(axelrodFrame, textvariable=clicked2, values=options)
turnsLabel = Label(axelrodFrame, text="Number of turns: ")
turnsEntry = Entry(axelrodFrame, width=5)
turnsEntry.insert(0, "6")
# repetitionsLabel = Label(axelrodFrame, text="Enter the number of repetitions: ")
# repetitionsEntry = Entry(axelrodFrame, width=5)
# repetitionsEntry.insert(0, "10")

dbOutput = IntVar()
dbOutput.set("0")

Radiobutton(axelrodFrame, text="Add to Database", variable=dbOutput, value=0, command=lambda: addToDBClicked(dbOutput.get())).grid(row=3, column=0, sticky=W)
Radiobutton(axelrodFrame, text="Don't Add to Database", variable=dbOutput, value=1, command=lambda: addToDBClicked(dbOutput.get())).grid(row=4, column=0, sticky=W)

# Converting the string strategies from the dropdown menus into the actual strategy objects
p1 = ""
p2 = ""
clicked1NoSpaces = clicked1.get().replace(" ", "")
clicked2NoSpaces = clicked2.get().replace(" ", "")
counter = 0
while type(p1).__name__ == "str":
    if type(options[counter]).__name__ == clicked1NoSpaces:
        p1 = options[counter]
    counter += 1
counter = 0
while type(p2).__name__ == "str":
    if type(options[counter]).__name__ == clicked2NoSpaces:
        p2 = options[counter]
    counter += 1

matchButton = Button(axelrodFrame, text="Play Match", command=lambda: playMatch(p1, p2, dbOutput.get(), int(turnsEntry.get())))
# tournamentButton = Button(axelrodFrame, text="Start Tournament", command=startTournament(int(turnsEntry.get())))
dbButton = Button(axelrodFrame, text="View Database", command=db)

# Putting everything in the root window
mainFrame.pack(fill=BOTH, expand=1)

dimensionsFrame.grid(row=0, column=0, padx=10, pady=10)
numPlayersLabel.grid(row=0, column=0, padx=(10, 0), sticky=E)
numPlayersEntry.grid(row=0, column=1, padx=(0, 5), sticky=W)

row = 1
col = -1
for x in range(G.numPlayers):
    col = 0
    numStratsLabels[x].grid(row=row, column=col, sticky=E)
    col = 1
    numStratsEntries[x].grid(row=row, column=col, sticky=W)
    row += 1

dimensionsButton.grid(row=3, column=1, padx=(0, 5), pady=5, sticky=W)

payoffsFrame.grid(row=0, column=1, padx=10, pady=10)

iesdsFrame.grid(row=1, column=1, padx=10, pady=10)
revertButton.grid(row=0, column=1)
iesdsButton.grid(row=2, column=0, columnspan=2)

equilibriaFrame.grid(row=1, column=0, padx=10, pady=10)
equilibriaButton.grid(row=1, column=1, padx=10, pady=10)

axelrodFrame.grid(row=2, column=1, padx=10, pady=10)
strategyLabel1.grid(row=0, column=0, sticky=W)
dropdown1.grid(row=0, column=1, sticky=W)
strategyLabel2.grid(row=1, column=0, sticky=W)
dropdown2.grid(row=1, column=1, sticky=W)
turnsLabel.grid(row=2, column=0, sticky=W)
turnsEntry.grid(row=2, column=1, sticky=W)
# repetitionsLabel.grid(row=3, column=0, sticky=W)
# repetitionsEntry.grid(row=3, column=1, sticky=W)
matchButton.grid(row=3,column=1, pady=5, sticky=W)
# tournamentButton.grid(row=4,column=1)
dbButton.grid(row=4, column=1, pady=5, sticky=W)

root.mainloop()