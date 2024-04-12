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
from pysimultaneous import Player
from pprint import pprint
import warnings

# Function definitions
def addAllPairs(dbTurnsEntry, dbClicked1):
    """
    Inserts a match between every possible pair of strategies with a set number of turns. 
    """
    conn = sqlite3.connect('match.db')
    c = conn.cursor()
    
    strategy = dbClicked1.get()
    print("strategy: ", strategy)
    print("TYPE: ", type(strategy))
    options = [s() for s in axl.strategies]    
    for n, option in enumerate(options):
        match = dbPlayMatch(strategy, type(option).__name__, int(dbTurnsEntry.get()))
        print("Inserting pair " + str(n))
        c.execute("INSERT INTO matches VALUES (:strategy1, :strategy2, :numTurns, :output, :score1, :score2)",
            {
                'strategy1': strategy,
                'strategy2': type(option).__name__,
                'numTurns': dbTurnsEntry.get(),
                'output': match[0], 
                'score1': match[1][0], 
                'score2': match[1][1]
            }
        )
            
    conn.commit()
    conn.close()
    return

def addToDBClicked(dbOutput, value):
    dbOutput.set(value)

def addRecord(clicked1, clicked2, dbClicked1, dbClicked2, dbTurnsEntry):
    conn = sqlite3.connect('match.db')
    c = conn.cursor()
    
    # Converting the string strategies from the dropdown menus into the actual strategy objects
    p1 = ""
    p2 = ""
    clicked1NoSpaces = dbClicked1.get().replace(" ", "")
    clicked2NoSpaces = dbClicked2.get().replace(" ", "")
    counter = 0
    options = [s() for s in axl.strategies]
    while type(p1).__name__ == "str" and counter < len(axl.strategies):
        if type(options[counter]).__name__ == clicked1NoSpaces:
            p1 = options[counter]
        counter += 1
    counter = 0
    while type(p2).__name__ == "str" and counter < len(axl.strategies):
        if type(options[counter]).__name__ == clicked2NoSpaces:
            p2 = options[counter]
        counter += 1
    
    match = dbPlayMatch(p1, p2, int(dbTurnsEntry.get()))
    c.execute("INSERT INTO matches VALUES (:strategy1, :strategy2, :numTurns, :output, :score1, :score2)",
        {
            'strategy1': dbClicked1.get(),
            'strategy2': dbClicked2.get(),
            'numTurns': dbTurnsEntry.get(),
            'output': match[0],
            'score1': match[1][0],
            'score2': match[1][1]
        }
    )
    conn.commit()
    conn.close()

def changeBackgroundColor(rootFrame):
    """
        Changes the background color of the window
    """
    topColor = Toplevel()
    topColor.title("Enter a Color")
    topColor.iconbitmap("knight.ico")
    topColor.geometry("190x30")
    
    colorLabel = Label(topColor, text="Enter a color:")
    colorEntry = Entry(topColor, width=10)
    colorEnter = Button(topColor, text="Enter", command=lambda: enterColor(rootFrame, colorEntry.get()))
    
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
        
    clearDBInfo = messagebox.showinfo("Database Cleared", "The matches table has been cleared.")
    
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
        
        entriesToSimGame(G, dimensionsFrame, payoffsFrame)
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
        
        entriesToSimGame(G, dimensionsFrame, payoffsFrame)
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
            
        entriesToSimGame(G, dimensionsFrame, payoffsFrame)
    else:
        return

def computeEquilibria(G, root, dimensionsFrame, payoffsFrame, equilibriaFrame, output):
    """
    Computes the equilibria of the current game and formats the output according to whether the output variable is 0 or 1, 
    """
    entriesToSimGame(G, dimensionsFrame, payoffsFrame)
    # FIXME
    proceed = entriesToList(G, dimensionsFrame, payoffsFrame)
    if proceed == True:
        dimensionsSlaves = dimensionsFrame.grid_slaves()
        numStratsEntries = []
        for slave in dimensionsSlaves:
            if type(slave).__name__ == "Entry":
                numStratsEntries.append(slave)
        numPlayers = int(numStratsEntries[-1].get())
        numStratsEntries.pop() # last one will be the numPlayers entry
        numStratsEntries.reverse()
        numStrats = [int(e.get()) for e in numStratsEntries]
        
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
            outcomes = payoffMatrixSlaves[:numStrats[0] * numStrats[1]]
            
            # Converting the list of outcomes to a list of lists
            newOutcomes = []
            row = []
            numInRow = 0
            for outcome in outcomes:
                if numInRow < numStrats[1]:
                    row.insert(0, outcome)
                    numInRow += 1
                    if numInRow == numStrats[1]:
                        newOutcomes.insert(0, row)
                        numInRow = 0
                        row = []
            
            # matching the indices to those of the payoff matrix and changing the color
            for i in range(numStrats[0]):
                for j in range(numStrats[1]):
                    if [i, j] in pureEquilibria:
                        newOutcomes[i][j].configure(bg="yellow")
                    else:
                        newOutcomes[i][j].configure(bg="white")
            
            # clearing the previous set of equilibria
            eqSlaves = equilibriaFrame.grid_slaves()
            if type(eqSlaves[0]).__name__ == "Listbox":
                eqSlaves[0].grid_remove()
            
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
            outcomes = payoffMatrixSlaves[:numStrats[0] * numStrats[1]]
            
            # converting the list of outcomes to a list of lists
            newOutcomes = []
            row = []
            numInRow = 0
            for outcome in outcomes:
                if numInRow < numStrats[1]:
                    row.append(outcome)
                    numInRow += 1
                    if numInRow == numStrats[1]:
                        newOutcomes.append(row)
                        numInRow = 0
                        row = []
            
            # FIXME: Can't finish this until we've implemented strategy names for players past player 2! 
            # Getting list of the strategy names
            payoffMatrixSlaves = payoffsFrame.grid_slaves()
            strategyNames = payoffMatrixSlaves[numStrats[0] * numStrats[1]:]
            
            p1StrategyNames = strategyNames[:numStrats[0]]
            p1StrategyNames.reverse()
            p2StrategyNames = strategyNames[numStrats[0]:]
            p2StrategyNames.reverse()
            
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
                # FIXME
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
            outcomes = payoffMatrixSlaves[:numStrats[0] * numStrats[1]]
            
            # Converting the list of outcomes to a list of lists
            newOutcomes = []
            row = []
            numInRow = 0
            for outcome in outcomes:
                if numInRow < numStrats[1]:
                    row.insert(0, outcome)
                    numInRow += 1
                    if numInRow == numStrats[1]:
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
            for i in range(numStrats[0]):
                for j in range(numStrats[1]):
                    if [i, j] in eqIndices:
                        newOutcomes[i][j].configure(bg="yellow")
                    else:
                        newOutcomes[i][j].configure(bg="white")
                    
            # clearing the previous set of equilibria
            eqSlaves = equilibriaFrame.grid_slaves()
            if type(eqSlaves[0]).__name__ == "Listbox":
                eqSlaves[0].grid_remove()
            
            eqListBoxFrame = LabelFrame(equilibriaFrame)
    
            xscrollbar = Scrollbar(eqListBoxFrame, orient=HORIZONTAL)
            yscrollbar = Scrollbar(eqListBoxFrame, orient=VERTICAL)
            
            equilibriaOutputListBox = Listbox(eqListBoxFrame, width=50, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, bg="black", fg="white")
            for eq in eqList:
                equilibriaOutputListBox.insert(0, eq)
            
            eqListBoxFrame.grid(row=2, column=0, columnspan=2)
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

def db(clicked1, clicked2):
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
    addRecordButton = Button(dbWindow, text="Add Record", command=lambda: addRecord(clicked1, clicked2, dbClicked1, dbClicked2, dbTurnsEntry))
    addAllPairsButton = Button(dbWindow, text="Add All Pairs for Player 1's Strategy", command=lambda: addAllPairs(dbTurnsEntry, dbClicked1))
    numRecordsButton = Button(dbWindow, text="Get Total Number of Records", command=lambda: getNumRecords(dbWindow))
    showRecordsButton = Button(dbWindow, text="Show Records", command=lambda: showRecords(dbWindow))
    exportButton = Button(dbWindow, text="Export to csv", command=export)
    searchRecordsButton = Button(dbWindow, text="Search Records", command=searchRecords)
    selectIDLabel = Label(dbWindow, text="Select ID: ")
    selectIDEntry = Entry(dbWindow, width=20)
    deleteRecordButton = Button(dbWindow, text="Delete Record", command=lambda: deleteRecord(selectIDEntry))
    updateRecordButton = Button(dbWindow, text="Update Record", command=lambda: updateRecord(selectIDEntry))
    resetRecordButton = Button(dbWindow, text="Reset Record", command=lambda: resetRecord(selectIDEntry))
    clearDBButton = Button(dbWindow, text="Clear DB", command=clearDB)
        
    # Putting everything in the top window
    dbStrategyLabel1.grid(row=0, column=0, padx=(5, 0), sticky=E)
    dbDropdown1.grid(row=0, column=1, padx=(0, 5), pady=5, sticky=W)
    dbStrategyLabel2.grid(row=1, column=0, padx=(5, 0), sticky=E)
    dbDropdown2.grid(row=1, column=1, padx=(0, 5),pady=(0,5), sticky=W)
    dbTurnsLabel.grid(row=2, column=0, padx=(5, 0), pady=(0,5), sticky=E)
    dbTurnsEntry.grid(row=2, column=1, pady=(0, 5), sticky=W)
    addRecordButton.grid(row=3, column=0, columnspan=2, padx=5, pady=(0, 5), ipadx=141)
    addAllPairsButton.grid(row=4, column=0, columnspan=2, padx=5, pady=(0, 5), ipadx=80)
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

def dbPlayMatch(p1Strat, p2Strat, t = 6):    
    """
    Runs an axelrod match between players of type p1 and p2 with t turns and returns a tuple of the match output and scores
    """
    p1Strat = p1Strat.replace(" ", "")
    p2Strat = p2Strat.replace(" ", "")
    p1 = ""
    p2 = ""
    # Getting the strategy object that corresponds to the string p1Strat
    counter = 0
    options = [s() for s in axl.strategies]
    while type(p1).__name__ == "str" and counter <= len(axl.strategies):
        try:
            if type(options[counter]).__name__ == p1Strat:
                p1 = options[counter]
        except IndexError:
            stratNotFoundError = messagebox.showerror("Error", "The strategy you entered for player 1 was not in axelrod's list of strategies. Perhaps you meant to capitalize the individual words?")
        counter += 1
    
    # Getting the strategy object that corresponds to the string p2Strat 
    counter = 0
    while type(p2).__name__ == "str" and counter <= len(axl.strategies):
        try:
            if type(options[counter]).__name__ == p2Strat:
                p2 = options[counter]
        except IndexError:
            stratNotFoundError = messagebox.showerror("Error", "The strategy you entered for player 2 was not in axelrod's list of strategies. Perhaps you meant to capitalize the individual words?")
        counter += 1
    match = axl.Match((p1, p2), turns = t)
    return (str(match.play()), match.final_score_per_turn())

def deleteRecord(selectIDEntry): 
    # Create a database or connect to one
    conn = sqlite3.connect('match.db')
    # Create cursor
    c = conn.cursor()
    
    id_ = selectIDEntry.get()
    try:
        c.execute("SELECT 1 FROM matches WHERE oid=" + id_)
        records = c.fetchall()
    except sqlite3.OperationalError:
            IDNotSelectedError = messagebox.showerror("Error", "You must enter an ID to delete a record.")
            return
    else:
        if len(records) == 0:
            recordDNEError = messagebox.showerror("Error", "A record with that ID does not exist in the matches table.")
        else:
            c.execute("DELETE FROM matches WHERE oid=" + id_)
            recordDeletedInfo = messagebox.showinfo("Record Deleted", f"Record with ID {id_} successfully deleted")     
        
        conn.commit()
        conn.close()
    return

def dimensionsClick(G, root, dimensionsFrame, payoffsFrame, oldNumPlayers):
    """
    Resizes the payoff matrix according to the numbers of strategies entered in by the user
    """
    dimensionsSlaves = dimensionsFrame.grid_slaves()
    numStratsLabels = []  
    numStratsEntries = []
    for slave in dimensionsSlaves:
        if type(slave).__name__ == "Label":
            numStratsLabels.append(slave)
        if type(slave).__name__ == "Entry":
            numStratsEntries.append(slave)
    numStratsLabels.pop()
    numStratsLabels.reverse()
    numPlayersEntry = numStratsEntries[-1]
    numStratsEntries.pop() # last one will be the numPlayers entry
    numStratsEntries.reverse()
    numStrats = [int(e.get()) for e in numStratsEntries]
    
    numPlayersError = -1
    numPlayers = int(numPlayersEntry.get())
    if numPlayers < 2:
        numPlayersError = messagebox.showerror("Error", "dimensionsClick: There must be at least 2 players.")
    
    if numPlayers < oldNumPlayers:
        for x in range(numPlayers, oldNumPlayers):
            numStratsLabels.grid_remove()
            numStratsEntries.grid_remove()
    
    if numPlayersError == -1:
        numStrats = []
        for x in range(numPlayers):
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
                        if oldNumPlayers < numPlayers:
                            for x in range(oldNumPlayers, numPlayers):
                                # Adding new players
                                p = Player(numStrats[x], 0)
                                G.players.append(p)
                                # Adding new strategyNames
                                if G.players[x].numStrats < 3:
                                    G.strategyNames.append(["L(" + str(x + 1) + ")", "R(" + str(x + 1) + ")"])
                                else: 
                                    G.strategyNames.append(["L(" + str(x + 1) + ")"] + ["C(" + str(x + 1) + ", " + str(s + 1) + ")" for s in range(G.players[x].numStrats)] + ["R(" + str(x + 1) + ")"])
                        
                        print("old:", oldNumPlayers)
                        print("nP:", numPlayers)
                        print("G:", G.numPlayers)
                        print("len players:", len(G.players))                 
                        # resetting the strategy names
                        gNumStrats = [G.players[x].numStrats for x in range(G.numPlayers)]
                        if numStrats != gNumStrats:
                            G.strategyNames = []
                            if G.players[0].numStrats < 3:
                                G.strategyNames.append(["U", "D"])
                            else:
                                if G.players[0].numStrats == 3:
                                    middle = ["M"]
                                else: # > 3
                                    middle = ["M" + str(i) for i in range(1, G.players[0].numStrats - 1)]
                                G.strategyNames.append(["U"] + middle + ["D"])
                            if G.players[1].numStrats < 3:
                                G.strategyNames.append(["L", "R"])
                            else:
                                if G.players[1].numStrats == 3:
                                    center = ["C"]
                                else: # > 3
                                    center = ["C" + str(j) for j in range(1, G.players[1].numStrats - 1)]
                                G.strategyNames.append(["L"] + center + ["R"])
                            if G.numPlayers > 2:
                                for x in range(2, G.numPlayers):
                                    if G.players[x].numStrats < 3:
                                        G.strategyNames.append(["L(" + str(x + 1) + ")", "R(" + str(x + 1) + ")"])
                                    else:
                                        G.strategyNames.append(["L(" + str(x + 1) + ")"] + ["C(" + str(x + 1) + ", " + str(s + 1) + ")" for s in range(G.players[x].numStrats)] + ["R(" + str(x + 1) + ")"])
                            
                        # Resetting the number of steps of IESDS that have been computed
                        numIESDSClicks = 0  
                        # clearing the table
                        payoffMatrixSlaves = payoffsFrame.grid_slaves()
                        for slave in payoffMatrixSlaves:
                            slave.grid_remove()
                        
                        numMatrices = 1
                        for x in range(2, numPlayers):
                            numMatrices *= numStrats[x]
                        
                        # refilling the table
                        namesToJoin = [[] for n in range(numMatrices)]
                        joinedNames = []
                        for m in range(numMatrices):
                            if numPlayers > 2:
                                player3OnEntry = Entry(payoffsFrame, width=20)
                                # FIXME
                                for x in range(2, G.numPlayers):
                                    namesToJoin[m].append(G.strategyNames[x][G.toProfile(m)[x]])
                                
                                print("nTJ[m]:", namesToJoin[m])
                                joinedNames.append(", ".join(namesToJoin[m]))
                                player3OnEntry.insert(0, joinedNames[m])                 
                                player3OnEntry.grid(row=0, column=numStrats[1] * m + 1, columnspan=2, pady=5, sticky=EW)
                            for j in range(numStrats[1]):
                                e = Entry(payoffsFrame, width=10)
                                e.insert(0, G.strategyNames[1][j])
                                e.grid(row=1, column=j + (numStrats[1] * m) + 1, pady=5)
                            
                        for i in range(numStrats[0]):
                            e = Entry(payoffsFrame, width=10)
                            e.insert(0, G.strategyNames[0][i])
                            e.grid(row=i + 2, column=0, padx=5)
                        
                        numMatrices = 1
                        for x in range(2, numPlayers):
                            numMatrices *= numStrats[x]

                        defaultPayoffs = [0.0 for x in range(numPlayers)]
                        stringFormatter = ''
                        for x in range(numPlayers):
                            stringFormatter += '%d'
                            if x < numPlayers - 1:
                                stringFormatter += ', '
                        
                        for m in range(numMatrices):
                            for i in range(numStrats[0]):
                                for j in range(numStrats[1]):
                                    e = Entry(payoffsFrame, width=10)
                                    if j < numStrats[1] - 1:
                                        e.grid(row=i + 1 + 1, column=j + 1 + (m * numStrats[1]), sticky=NSEW)
                                    else:
                                        e.grid(row=i + 1 + 1, column=j + 1 + (m * numStrats[1]), sticky=NSEW, padx=(0, 10))
                                    e.insert(END, stringFormatter % tuple(defaultPayoffs))

                        entriesToSimGame(G, dimensionsFrame, payoffsFrame)
                            
                        # Clearing the equilibria
                        try:
                            eqOutputFrame
                        except NameError:
                            print("eqOutputFrame not defined yet.")
                        else:
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
        else:
            return
    else:
        return
    return

def dimensionsClickNoWarning(G, root, dimensionsFrame, payoffsFrame, equilibriaFrame):
    """
    Resizes the payoff matrix according to the numbers of strategies entered in by the user without prompting the user
    """
    dimensionsSlaves = dimensionsFrame.grid_slaves()
    dimensionsEntries = []
    for slave in dimensionsSlaves:
        if type(slave).__name__ == "Entry":
            dimensionsEntries.append(slave)
    numPlayers = int(dimensionsEntries[-1].get())
    dimensionsEntries.pop()
    dimensionsEntries.reverse()
    numStratsEntries = dimensionsEntries
    numStrats = [int(numStratsEntries[x].get()) for x in range(numPlayers)]

    negativeStratsError = -1
    zeroStratsError = -1
    oneByOneError = -1
    if numStrats[0] == 0 or numStrats[1] == 0:
        zeroStratsError = messagebox.showerror("Error", "A player may not have zero strategies.")
    
    if zeroStratsError == -1:
        if numStrats[0] == 1 or numStrats[1] == 1:
            oneByOneError = messagebox.showerror("Error", "A player may not have only one strategy.")
            return
        
        if oneByOneError == -1:
            if numStrats[0] < 0 or numStrats[1] < 0:
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
                for i in range(numStrats[1]):
                    e = Entry(payoffsFrame, width=10)
                    if i == 0:
                        e.insert(0, "L")
                    elif i > 0 and i < numStrats[1] - 1 and numStrats[1] == 3:
                        e.insert(0, "C")
                    elif i > 0 and i < numStrats[1] - 1 and numStrats[1] >= 3:
                        e.insert(0, "C" + str(i))
                    else:
                        e.insert(0, "R")
                    e.grid(row=0, column=i + 1, pady=5)
                    
                for j in range(numStrats[0]):
                    e = Entry(payoffsFrame, width=10)
                    if j == 0:
                        e.insert(0, "U")
                    elif j > 0 and j < numStrats[0] - 1 and numStrats[0] == 3:
                        e.insert(0, "M")
                    elif j > 0 and j < numStrats[0] - 1 and numStrats[0] > 3:
                        e.insert(0, "M" + str(j))
                    else:
                        e.insert(0, "D")
                    e.grid(row=j + 1, column=0, padx=5)

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
                equilibriaSlaves = equilibriaFrame.grid_slaves()
                eqLabel = equilibriaSlaves[0]
                if type(eqLabel).__name__ == "Label":
                    eqLabel.grid_remove()
                
                entriesToSimGame(G, dimensionsFrame, payoffsFrame)
                root.geometry(f"{45 * numStrats[1] + 700}x{25 * numStrats[0] + 490}")
                return
            else:
                return
        else:
            return
    return

def eliminateStrictlyDominatedStrategies(G, dimensionsFrame, payoffsFrame, steps):
    """
    Compares all payoffs of all pairs of strategies for both players and eliminates strategies that are strictly dominated.    
    """
    global numIESDSClicks
    try:
        numIESDSClicks
    except NameError:
        numIESDSClicks = 0
    dimensionsSlaves = dimensionsFrame.grid_slaves()
    dimensionsEntries = []
    for slave in dimensionsSlaves:
        if type(slave).__name__ == "Entry":
            dimensionsEntries.append(slave)
        
    numPlayers = int(dimensionsEntries[-1].get())
    dimensionsEntries.pop()
    dimensionsEntries.reverse()
    numStratsEntries = dimensionsEntries
    
    # saving the original game in case the user wants to revert back to it
    if steps == 0 or numIESDSClicks == 0:
        entriesToSimGame(G, dimensionsFrame, payoffsFrame)
        global originalGame
        global originalNumStrats
        originalGame = payoffsFrame.grid_slaves()
        originalNumStrats = []
        for x in range(numPlayers):
            originalNumStrats.append(int(numStratsEntries[x].get()))
    
    numStrats = [int(e.get()) for e in numStratsEntries]
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    outcomes = payoffMatrixSlaves[:numStrats[0] * numStrats[1]]
    outcomes.reverse()
    strategyNames = payoffMatrixSlaves[numStrats[0] * numStrats[1]:]
    p1StrategyNameEntries = strategyNames[:numStrats[0]]
    p1StrategyNameEntries.reverse()
    p2StrategyNameEntries = strategyNames[numStrats[1]:]
    p2StrategyNameEntries.reverse()
    groupedOutcomes = [outcomes[i:i + numStrats[1]] for i in range(0, len(outcomes), numStrats[1])]
    
    newGroupedOutcomes = []
    for outcome in groupedOutcomes:
        row = []
        for i in range(numStrats[1]):
            row.append(outcome[i])
        newGroupedOutcomes.append(row)
    
    outcomesListList = []
    for outcome in newGroupedOutcomes:
        outcomesListList.append(outcome)

    strategies = payoffMatrixSlaves[numStrats[0] * numStrats[1]:]
    strategies.reverse()
    # strategyIndices[x] is the set of indices (0, 1, 2,...,numStrats[x] - 1) for the x-th player
    # strategyIndices[x][k] is the k-th strategy index for the x-th player
    strategyIndices = [[k for k in range(numStrats[x])] for x in range(numPlayers)]
    
    if steps == 0: # perform full IESDS computation with one click
        G.eliminateStrictlyDominatedStrategies_full()
        simGameToEntries(G, dimensionsFrame, payoffsFrame)
        
        
        """
        # pairs[x] contains numPlayers-long tuples of strategy indices
        # pairs[x][0] and pairs[x][1] are the strategies being compared
        pairs = [combinations(strategyIndices[x], r=2) for x in range(numPlayers)]
        numCombos = [sum(1 for pair in pairs[x]) for x in range(numPlayers)]
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
            
            for x in range(numPlayers):
                # recomputing the pairs that need to be checked because the number of strategies may have changed
                strategyIndices = [[k for k in range(numStrats[x])] for x in range(numPlayers)]
                pairs = [combinations(strategyIndices[x], r=2) for x in range(numPlayers)]
                numCombos = [sum(1 for pair in pairs[x]) for x in range(numPlayers)]
                pairs = [combinations(strategyIndices[x], r=2) for x in range(numPlayers)]
                if x == 0:
                    # eliminating strategies for player 1 #####################################################################
                    for pair in pairs[x]:
                        greaterThanFound1 = False
                        lessThanFound1 = False
                        equalFound1 = False
                        # searching for < or > among the payoffs
                        for j in range(numStrats[1]):
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
                            numStrats[0] -= 1
                            numStratsEntries[0].delete(0, END)
                            numStratsEntries[0].insert(0, numStrats[0])
                            p1StrategyNameEntries[pair[0]].grid_remove()
                            for j in range(numStrats[1]):
                                outcomesListList[pair[0]][j].grid_remove()
                                outcomesListList[pair[0]].pop(j)
                            strategyIndices[0].pop()
                            stratRemoved1 = True
                        elif greaterThanFound1 and not lessThanFound1 and not equalFound1: # remove strategy pair[1]
                            numStrats[0] -= 1
                            numStratsEntries[0].delete(0, END)
                            numStratsEntries[0].insert(0, numStrats[0])
                            p1StrategyNameEntries[pair[1]].grid_remove()
                            numDeleted = 0
                            for j in range(numStrats[1]):
                                j -= numDeleted
                                outcomesListList[pair[1]][j].grid_remove()
                                outcomesListList[pair[1]].pop(j)
                                numDeleted += 1
                            strategyIndices[0].pop()
                            stratRemoved1 = True
                        else: # (not lessThanFound1 and not greaterThanFound1)(all equal) or (lessThanFound1 and greaterThanFound1)(no dominance)
                            stratRemoved1 = False
                        
                        if stratRemoved1:
                            break
                elif x == 1:
                    # eliminating strategies for player 2 ######################################################################
                    for pair in pairs[x]:
                        greaterThanFound2 = False
                        lessThanFound2 = False
                        equalFound2 = False
                        # searching for < or > among the payoffs
                        for i in range(numStrats[0]):
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
                            numStrats[1] -= 1
                            numStratsEntries[1].delete(0, END)
                            numStratsEntries[1].insert(0, numStrats[1])
                            p2StrategyNameEntries[pair[0]].grid_remove()
                            for i in range(numStrats[0]):
                                outcomesListList[i][pair[0]].grid_remove()
                                outcomesListList[i].pop(pair[0])
                            strategyIndices[1].pop()
                            stratRemoved2 = True
                        elif greaterThanFound2 and not lessThanFound2 and not equalFound2: # remove strategy pair[1]
                            numStrats[1] -= 1
                            numStratsEntries[1].delete(0, END)
                            numStratsEntries[1].insert(0, numStrats[1])
                            p2StrategyNameEntries[pair[1]].grid_remove()
                            for i in range(numStrats[0]):
                                outcomesListList[i][pair[1]].grid_remove()
                                outcomesListList[i].pop(pair[1])
                            strategyIndices[1].pop()
                            stratRemoved2 = True
                        else: # (not lessThanFound2 and not greaterThanFound2) or (lessThanFound2 and greaterThanFound2)
                            stratRemoved2 = False
                        
                        if stratRemoved2:
                            break
                    if not stratRemoved1 and not stratRemoved2:
                        break
                else: # x > 1
                    # FIXME
                    for pair in pairs[x]:
                        greaterThanFound2 = False
                        lessThanFound2 = False
                        equalFound2 = False
                        # searching for < or > among the payoffs
                        
                        # Removing strategies based on the results
                    return
                    """
    elif steps == 1: # perform IESDS computation step by step
        numIESDSClicks += 1
        pairs[0] = combinations(strategyIndices[0], r=2) # pairs of p1's strategies to compare; indices
        pairs[1] = combinations(strategyIndices[1], r=2) # pairs of p2's strategies to compare; indices
        numCombos1 = sum(1 for pair in pairs[0])
        numCombos2 = sum(1 for pair in pairs[1])
        oneStratEliminated = False
        
        if numIESDSClicks == 1:
            # eliminating strategies for player 1
            for pair in pairs[0]:
                greaterThanFound1 = False
                lessThanFound1 = False
                equalFound1 = False
                # searching for < or > among the payoffs
                for j in range(numStrats[1]):
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
                    numStrats[0] -= 1
                    numStratsEntries[0].delete(0, END)
                    numStratsEntries[0].insert(0, numStrats[0])
                    p1StrategyNameEntries[pair[0]].grid_remove()
                    for j in range(numStrats[1]):
                        outcomesListList[pair[0]][j].grid_remove()
                        outcomesListList[pair[0]].pop(j)
                if greaterThanFound1 and not lessThanFound1 and not equalFound1: # remove strategy pair[1]
                    # one strat found
                    oneStratEliminated = True
                    numStrats[0] -= 1
                    numStratsEntries[0].delete(0, END)
                    numStratsEntries[0].insert(0, numStrats[0])
                    p1StrategyNameEntries[pair[1]].grid_remove()
                    numDeleted = 0
                    for j in range(numStrats[1]):
                        j -= numDeleted
                        outcomesListList[pair[1]][j].grid_remove()
                        outcomesListList[pair[1]].pop(j)
                        numDeleted += 1
            if not oneStratEliminated:
                # eliminating strategies for player 2
                for pair in pairs[1]:
                    greaterThanFound2 = False
                    lessThanFound2 = False
                    equalFound2 = False
                    # searching for < or > among the payoffs
                    for i in range(numStrats[0]):
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
                        numStrats[1] -= 1
                        numStratsEntries[1].delete(0, END)
                        numStratsEntries[1].insert(0, numStrats[1])
                        p2StrategyNameEntries[pair[0]].grid_remove()
                        for i in range(numStrats[0]):
                            outcomesListList[i][pair[0]].grid_remove()
                            outcomesListList[i].pop(pair[0])
                    if greaterThanFound2 and not lessThanFound2 and not equalFound2: # remove strategy pair[1]
                        oneStratEliminated = True
                        numIESDSClicks = 2 # if we start by eliminating a strat for p2, check p1 next (numIESDSClicks will be incremented to 3 \cong 1 mod 2)
                        numStrats[1] -= 1
                        numStratsEntries[1].delete(0, END)
                        numStratsEntries[1].insert(0, numStrats[1])
                        p2StrategyNameEntries[pair[1]].grid_remove()
                        for i in range(numStrats[0]):
                            outcomesListList[i][pair[1]].grid_remove()
                            outcomesListList[i].pop(pair[1])
        else: # numIESDSClicks > 1
            if numIESDSClicks % 2 == 1: # check player 1's strategies
                # eliminating strategies for player 1
                for pair in pairs[0]:
                    greaterThanFound1 = False
                    lessThanFound1 = False
                    equalFound1 = False
                    # searching for < or > among the payoffs
                    for j in range(numStrats[1]):
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
                        numStrats[0] -= 1
                        numStratsEntries[0].delete(0, END)
                        numStratsEntries[0].insert(0, numStrats[0])
                        p1StrategyNameEntries[pair[0]].grid_remove()
                        for j in range(numStrats[1]):
                            outcomesListList[pair[0]][j].grid_remove()
                            outcomesListList[pair[0]].pop(j)
                    if greaterThanFound1 and not lessThanFound1 and not equalFound1: # remove strategy pair[1]
                        numStrats[0] -= 1
                        numStratsEntries[0].delete(0, END)
                        numStratsEntries[0].insert(0, numStrats[0])
                        p1StrategyNameEntries[pair[1]].grid_remove()
                        numDeleted = 0
                        for j in range(numStrats[1]):
                            j -= numDeleted
                            outcomesListList[pair[1]][j].grid_remove()
                            outcomesListList[pair[1]].pop(j)
                            numDeleted += 1
            else: # numIESDSClicks % 2 == 0; check player 2's strategies
                # eliminating strategies for player 2
                for pair in pairs[1]:
                    greaterThanFound2 = False
                    lessThanFound2 = False
                    equalFound2 = False
                    # searching for < or > among the payoffs
                    for i in range(numStrats[0]):
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
                        numStrats[1] -= 1
                        numStratsEntries[1].delete(0, END)
                        numStratsEntries[1].insert(0, numStrats[1])
                        p2StrategyNameEntries[pair[0]].grid_remove()
                        for i in range(numStrats[0]):
                            outcomesListList[i][pair[0]].grid_remove()
                            outcomesListList[i].pop(pair[0])
                    if greaterThanFound2 and not lessThanFound2 and not equalFound2: # remove strategy pair[1]
                        numStrats[1] -= 1
                        numStratsEntries[1].delete(0, END)
                        numStratsEntries[1].insert(0, numStrats[1])
                        p2StrategyNameEntries[pair[1]].grid_remove()
                        for i in range(numStrats[0]):
                            outcomesListList[i][pair[1]].grid_remove()
                            outcomesListList[i].pop(pair[1])
    else:
        print(f"Unexpected value {steps} for variable\"steps\"")
        stepsError = messagebox.showError("Error", f"Unexpected value {steps} for variable\"steps\"")
    return

def enterColor(rootFrame, color):
    """
        Makes the root window have a certain color
    """
    try:
        rootFrame.config(bg=color)
    except TclError:
        colorNotFound = messagebox.showerror(f"Error", f"Unknown color name \"{color}\". Try entering in a different color.")
    return

def entriesToSimGame(G, dimensionsFrame, payoffsFrame):
    """Enters the information in the text entries into the SimGame object
    """
    oldNumStrats = [G.players[x].numStrats for x in range(G.numPlayers)]
    
    # Getting the numbers of strategies
    numStrats = []
    dimensionsSlaves = dimensionsFrame.grid_slaves()
    for slave in dimensionsSlaves:
        if type(slave).__name__ == "Entry":
            numStrats.append(int(slave.get()))
    numPlayers = numStrats[-1]
    numStrats.pop() # last one will be the entry for numPlayers
    numStrats.reverse()
    
    oldNumPlayers = G.numPlayers
    # Entering the number of players
    G.numPlayers = numPlayers
    # Adding new players if necessary
    if G.numPlayers > oldNumPlayers:
        for x in range(oldNumPlayers, G.numPlayers):
            G.players.append(Player(numStrats[x], 0))
    elif G.numPlayers < oldNumPlayers:
        G.players = G.players[:G.numPlayers]
    
    # Getting the entries from the payoffs frame
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    
    numOutcomes = 1
    for x in range(numPlayers):
        numOutcomes *= numStrats[x]
    
    numOutcomes = 1
    for x in range(numPlayers):
        numOutcomes *= numStrats[x]
    
    print("numOutcomes:", numOutcomes)
    
    outcomes = payoffMatrixSlaves[:numOutcomes]
    outcomes.reverse()
    outcomesGet = [outcome.get() for outcome in outcomes]
    
    for outcome in outcomesGet:
        print("outcome:", outcome)
    
    strategyNames = payoffMatrixSlaves[numOutcomes:]
    p1StrategyNameEntries = strategyNames[:numStrats[0]]
    p1StrategyNameEntries.reverse()
    p2StrategyNameEntries = strategyNames[numStrats[1]:]
    p2StrategyNameEntries.reverse()
    
    for x in range(numPlayers):
        G.players[x].numStrats = numStrats[x]
    
    # Grouping the outcomes
    matrixGroupedOutcomes = [outcomesGet[n:n + numStrats[0] * numStrats[1]] for n in range(0, numOutcomes, numStrats[0] * numStrats[1])]  
    groupedOutcomes = [[matrix[n:n + numStrats[1]] for n in range(0, numStrats[0] * numStrats[1], numStrats[1])] for matrix in matrixGroupedOutcomes]
    
    # FIXME: is this garbage? 
    # FIXME: I think this is garbage :/
    newGroupedOutcomes = []
    for outcome in groupedOutcomes:
        row = []
        for i in range(numStrats[0]):
            row.append(outcome[i])
        newGroupedOutcomes.append(row)
    outcomesListList= []
    for outcome in newGroupedOutcomes:
        outcomesListList.append(outcome)
        
    print("oLL:")
    print(outcomesListList)
    
    # Converting from a list of list of entries to a list of list of floats
    newListList = [] 
    for matrix in outcomesListList:
        newMatrix = []
        for row in matrix:
            tempRow = []
            newRow = []
            for outcome in row:
                newOutcome = []
                for payoff in outcome.split(", "):
                    newOutcome.append(float(payoff))
                newRow.append(newOutcome)
            newMatrix.append(newRow)
        newListList.append(newMatrix)
    
    # Entering the payoffs
    G.enterData(numPlayers, numStrats, newListList)

    # FIXME: Finish for games with >= 3 players
    # Entering the strategy names
    G.strategyNames[0] = [entry.get() for entry in p1StrategyNameEntries]
    G.strategyNames[1] = [entry.get() for entry in p2StrategyNameEntries]
    
    print("new G:")
    G.print()
    return

def entriesToList(G, dimensionsFrame, payoffsFrame):
    """
    Enters the payoffs from the Entries into a list
    """
    dimensionsSlaves = dimensionsFrame.grid_slaves()
    dimensionsEntries = []
    for slave in dimensionsSlaves:
        if type(slave).__name__ == "Entry":
            dimensionsEntries.append(slave)
        
    numPlayers = int(dimensionsEntries[-1].get())

    dimensionsEntries.pop()
    dimensionsEntries.reverse()
    numStratsEntries = dimensionsEntries
    numStrats = []
    for x in range(numPlayers):
        numStrats.append(int(numStratsEntries[x].get()))
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    outcomes = payoffMatrixSlaves[:numStrats[0] * numStrats[1]]
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
        if numInRow < numStrats[1]:
            row.append(p)
            numInRow += 1
            if numInRow == numStrats[1]:
                newPayoffs.append(row)
                numInRow = 0
                row = []

    G.enterData(numPlayers, numStrats, newPayoffs)
    return True

def equilibriaOutputStyleClicked(eqOutput, value):
    eqOutput.set(value)
    
def export():
    fileSave = filedialog.asksaveasfile(defaultextension = ".csv", mode='w', initialdir=".", title="Save As", filetypes=(("CSV files", "*.csv"),))
    if fileSave:
        # Create a database or connect to one
        conn = sqlite3.connect('match.db')
        # Create cursor
        c = conn.cursor()
        
        c.execute("""SELECT *, oid FROM matches""")
        records = c.fetchall()
        
        # Commit changes
        conn.commit()
        # Close Connection
        conn.close()
        
        with open(fileSave.name, 'w') as file:
            for i, record in enumerate(records):
                file.write(
                    str(record[0]) + "," + 
                    str(record[1])+ "," + 
                    str(record[2]) + ",\"" + 
                    str(record[3]) + "\"," + 
                    str(record[4]) + "," + 
                    str(record[5]) + "," + 
                    str(record[6]))
                if i < len(records) - 1:
                    file.write("\n")

def exportSearch():
    file = filedialog.asksaveasfile(defaultextension = ".csv", mode='w', initialdir=".", title="Save As", filetypes=(("CSV files", "*.csv"),))
    if file:
        # Create a database or connect to one
        conn = sqlite3.connect('match.db')
        # Create cursor
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
        
        # Commit changes
        conn.commit()
        # Close Connection
        conn.close()
        
        with open(fileName, 'w') as file:
            for i, record in enumerate(records):
                file.write(
                    str(record[0]) + "," + 
                    str(record[1])+ "," + 
                    str(record[2]) + ",\"" + 
                    str(record[3]) + "\"," + 
                    str(record[4]) + "," + 
                    str(record[5]) + "," +
                    str(record[6]))
                if i < len(records) - 1:
                    file.write("\n")

def getNumRecords(dbWindow):
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

def iesdsStepsClicked(iesdsSteps, value):
    iesdsSteps.set(value)

def numPlayersClick(G, dimensionsFrame, numPlayersButton, dimensionsButton, oldNumPlayerss):
    dimensionsSlaves = dimensionsFrame.grid_slaves()
    dimensionsLabels = []
    dimensionsEntries = []
    for slave in dimensionsSlaves:
        if type(slave).__name__ == "Label":
            dimensionsLabels.append(slave)
        if type(slave).__name__ == "Entry":
            dimensionsEntries.append(slave)
    numPlayers = int(dimensionsEntries[-1].get())
    
    numPlayersError = -1
    if numPlayers < 2:
        numPlayersError = messagebox.showerror("Error", "dimensionsClick: There must be at least 2 players.")
        return
    else:
        dimensionsLabels.pop()
        dimensionsLabels.reverse()
        dimensionsEntries.pop()
        dimensionsEntries.reverse()
        numStratsLabels = dimensionsLabels
        numStratsEntries = dimensionsEntries
        
        oldNumPlayers = G.numPlayers
        print("HERE ONP:", oldNumPlayers)
        G.numPlayers = numPlayers
        if numPlayers > oldNumPlayers:
            print("GREATER")
            for x in range(numPlayers - oldNumPlayers):
                l = Label(dimensionsFrame, text=f"Number of strategies for player {oldNumPlayers + x + 1}: ")
                l.grid(row=oldNumPlayers + x + 1, column=0, sticky=E)
                e = Entry(dimensionsFrame, width=5)
                e.grid(row=oldNumPlayers + x + 1, column=1, sticky=W)
                e.insert(0, 2)
            numPlayersButton.grid(row=numPlayers + 2, column=0)
            dimensionsButton.grid(row=numPlayers + 2, column=1)
        elif numPlayers < oldNumPlayers:
            print("HERE")
            for x in range(numPlayers, oldNumPlayers):
                print("removing:", x)
                numStratsLabels[x].grid_remove()
                numStratsEntries[x].grid_remove()
        return

def openFile(G, root, dimensionsFrame, payoffsFrame, equilibriaFrame):
    """
        opens a file and reads the data from it into a list
    """
    root.filename = filedialog.askopenfilename(initialdir=".", title="Select a File", filetypes=(("Text files", "*.txt"),))
    
    if root.filename != '':
        with open(root.filename, 'r') as file:
            # Entering the number of players
            numPlayers = int(file.readline().rstrip())
            # Entering the numbers of strategies
            numStrats = file.readline().rstrip().split(" ")
            proceed = messagebox.askokcancel("Clear Payoffs?", "This will reset the payoff matrix. Do you want to proceed?")
            if proceed == True:
                # Resetting the number of IESDS steps that have been computed
                numIESDSClicks = 0
                
                dimensionsSlaves = dimensionsFrame.grid_slaves()
                dimensionsLabels = []
                dimensionsEntries = []
                for slave in dimensionsSlaves:
                    if type(slave).__name__ == "Label":
                        dimensionsLabels.append(slave)
                    elif type(slave).__name__ == "Entry":
                        dimensionsEntries.append(slave)
                
                dimensionsLabels.pop()
                dimensionsLabels.reverse()
                numStratsLabels = dimensionsLabels

                oldNumPlayers = int(dimensionsEntries[-1].get())
                dimensionsEntries[-1].delete(0, 'end')
                dimensionsEntries[-1].insert(0, numPlayers)
                dimensionsEntries.pop()
                dimensionsEntries.reverse()
                numStratsEntries = dimensionsEntries
                
                for x in range(numPlayers):
                    numStratsEntries[x].delete(0, 'end')
                    numStratsEntries[x].insert(0, int(numStrats[x]))
                dimensionsClickNoWarning(G, root, dimensionsFrame, payoffsFrame, equilibriaFrame)
                numStrats = []
                for x in range(numPlayers):
                    numStrats.append(int(numStratsEntries[x].get()))
                
                # Entering the strategy names
                strategyNames = []
                for x in range(numPlayers):
                    strategyNames.append(file.readline().rstrip().split(" "))
                payoffMatrixSlaves = payoffsFrame.grid_slaves()
                strategyNamesEntries = payoffMatrixSlaves[numStrats[0] * numStrats[1]:]
                p1StrategyNameEntries = strategyNamesEntries[:numStrats[0]]
                p1StrategyNameEntries.reverse()
                p2StrategyNameEntries = strategyNamesEntries[numStrats[1]:]
                p2StrategyNameEntries.reverse()
                
                for i, entry in enumerate(p1StrategyNameEntries):
                    entry.delete(0, 'end')
                    entry.insert(0, strategyNames[0][i])
                for j, entry in enumerate(p2StrategyNameEntries):
                    entry.delete(0, 'end')
                    entry.insert(0, strategyNames[1][j])
                
                payoffs = payoffMatrixSlaves[:numStrats[0] * numStrats[1]]
                payoffs.reverse()
                groupedOutcomes = [payoffs[i:i + numStrats[1]] for i in range(0, len(payoffs), numStrats[1])]
                
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

                    # Removing extra numStrats labels and entries from the dimensionsFrame
                    if numPlayers < oldNumPlayers:
                        for x in range(oldNumPlayers - numPlayers):
                            numStratsLabels[-1].grid_remove()
                            numStratsEntries[-1].grid_remove()
    return

def playMatch(root, axelrodFrame, turnsEntry, clicked1, clicked2, p1, p2, output, t = 6):
    """
    Runs an axelrod match between players of type p1 and p2 with t turns
    """
    if output == 0: # Add to Database    
        p1 = ""
        p2 = ""
        clicked1NoSpaces = clicked1.get().replace(" ", "")
        clicked2NoSpaces = clicked2.get().replace(" ", "")
        counter = 0
        options = [s() for s in axl.strategies]
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
                'output': str(dbPlayMatch(clicked1, clicked2, p1, p2, int(turnsEntry.get()))[0]),
                'score1': dbPlayMatch(clicked1, clicked2, p1, p2, int(turnsEntry.get()))[1][0],
                'score2': dbPlayMatch(clicked1, clicked2, p1, p2, int(turnsEntry.get()))[1][1]
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
        options = [s() for s in axl.strategies]
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
        
        entriesToSimGame(G, dimensionsFrame, payoffsFrame)
        root.geometry(f"{45 * numStrats2 + 700}x{25 * numStrats1 + 490}")
    return

def resetRecord(selectIDEntry):
    """
    Resets or recomputes the values that should be in a record according to the given inputs. 
    """
    conn = sqlite3.connect('match.db')
    c = conn.cursor()
    
    recordID = selectIDEntry.get()
    try:
        c.execute("SELECT *, oid FROM matches where oid=" + recordID)
    except sqlite3.OperationalError:
        IDNotSelectedError = messagebox.showerror("Error", "You must enter an ID to reset a record.")
        return
    else:
        record = c.fetchall()[0]
        match = dbPlayMatch(record[0], record[1], int(record[2]))
        c.execute("""UPDATE matches SET
                strategy1 = :strategy1, 
                strategy2 = :strategy2, 
                numTurns = :numTurns, 
                output = :output,
                score1 = :score1,
                score2 = :score2
                WHERE oid = :oid""",
                {
                    'strategy1': record[0], 
                    'strategy2': record[1], 
                    'numTurns': record[2],
                    'output': match[0],
                    'score1': match[1][0],
                    'score2': match[1][1],
                    'oid': recordID
                })    
        recordResetInfo = messagebox.showinfo("Record Reset", f"The record with ID {recordID} was successfully reset.")
        
        conn.commit()
        conn.close()
        return

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
            
        entriesToSimGame(G, dimensionsFrame, payoffsFrame)
    else:
        return
    
def revert(G, dimensionsFrame, payoffsFrame):
    """
        Reverts back to the original game after computing IESDS
    """
    # getting numStratsEntries
    dimensionsSlaves = dimensionsFrame.grid_slaves()
    dimensionsEntries = []
    for slave in dimensionsSlaves:
        if type(slave).__name__ == "Entry":
            dimensionsEntries.append(slave)
    numPlayers = int(dimensionsEntries[-1].get())
    dimensionsEntries.pop()
    dimensionsEntries.reverse()
    numStratsEntries = dimensionsEntries
    
    numIESDSClicks = 0
    numStrats = []
    for x in range(numPlayers):
        numStrats.append(int(numStratsEntries[x].get()))
    try:
        outcomes = originalGame[:originalNumStrats[0] * originalNumStrats[1]] # entries
    except NameError:
        notYetIESDSError = messagebox.showerror("Error", "The IESDS algorithm has not run yet. There's nothing to revert back to.")
    else:
        outcomes.reverse()
        strategyNames = originalGame[originalNumStrats[0] * originalNumStrats[1]:]
        p1StrategyNameEntries = strategyNames[:originalNumStrats[0]]
        p1StrategyNameEntries.reverse()
        p1StrategyNames = [entry.get() for entry in p1StrategyNameEntries]
        p2StrategyNameEntries = strategyNames[originalNumStrats[1]:]
        p2StrategyNameEntries.reverse()
        p2StrategyNames = [entry.get() for entry in p2StrategyNameEntries]
        groupedOutcomes = [outcomes[i:i + originalNumStrats[1]] for i in range(0, len(outcomes), originalNumStrats[1])] # entries
        
        newGroupedOutcomes = [] # entries
        for outcome in groupedOutcomes:
            row = []
            for i in range(originalNumStrats[1]):
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
        curOutcomes = curGame[:numStrats[0] * numStrats[1]]
        curOutcomes.reverse()
        curStrategyNames = curGame[numStrats[0] * numStrats[1]:]
        curP1StrategyNameEntries = curStrategyNames[:numStrats[0]]
        curP1StrategyNameEntries.reverse()
        curP1StrategyNames = [entry.get() for entry in curP1StrategyNameEntries]
        curP2StrategyNameEntries = strategyNames[numStrats[1]:]
        curP2StrategyNameEntries.reverse()
        curP2StrategyNames = [entry.get() for entry in curP2StrategyNameEntries]
        curGroupedOutcomes = [curOutcomes[i:i + numStrats[1]] for i in range(0, len(curOutcomes), numStrats[1])]
        
        # clearing the current payoff matrix
        for slave in curGame:
            slave.delete(0, 'end')
            slave.grid_remove()
        
        # refilling the table
        for i in range(originalNumStrats[0]):
            e = Entry(payoffsFrame, width=10)
            e.insert(0, p1StrategyNames[i])
            e.grid(row=0, column=i + 1, pady=5)
        for j in range(originalNumStrats[1]):
            e = Entry(payoffsFrame, width=10)
            e.insert(0, p2StrategyNames[j])
            e.grid(row=j + 1, column=0, padx=5)
        
        # inserting the original payoffs
        rows = []
        for i in range(originalNumStrats[0]):
            cols = []
            for j in range(originalNumStrats[1]):
                e = Entry(payoffsFrame, width=5)
                e.grid(row=i + 1, column=j + 1, sticky=NSEW)
                e.insert(END, '%d, %d' % (int(newOutcomesListList[i][j][0]), int(newOutcomesListList[i][j][1])))
                cols.append(e)
            rows.append(cols)
        
        # setting the numbers of strategies back to the originals
        dimensionsSlaves = dimensionsFrame.grid_slaves()
        dimensionsEntries = []
        for slave in dimensionsSlaves:
            if type(slave).__name__ == "Entry":
                dimensionsEntries.append(slave)
        dimensionsEntries.pop()
        dimensionsEntries.reverse()
        numStratsEntries = dimensionsEntries
        for x in range(numPlayers):
            numStratsEntries[x].delete(0, END)
            numStratsEntries[x].insert(0, originalNumStrats[x])

        # entering the "new" payoffs into the system
        entriesToList(G, dimensionsFrame, payoffsFrame)
        return

"""
def saveAs(dimensionsFrame, payoffsFrame):
    # 
    Save the data of the current payoff matrix in a txt file
    # 
    # Getting the numbers of strategies
    numStrats = []
    dimensionsSlaves = dimensionsFrame.grid_slaves()
    for slave in dimensionsSlaves:
        if type(slave).__name__ == "Entry":
            numStrats.append(int(slave.get()))
    numPlayers = numStrats[-1]
    numStrats.pop() # last one will be the entry for numPlayers
    numStrats.reverse()
    
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    outcomeEntries = payoffMatrixSlaves[:numStrats[0] * numStrats[1]]
    outcomes = [entry.get() for entry in outcomeEntries]
    outcomes.reverse()
    
    payoffs = [outcome.split(", ") for outcome in outcomes]
    groupedPayoffs = [payoffs[i:i + numStrats[1]] for i in range(0, len(payoffs), numStrats[1])]
    
    # Prompting the user for a file name    
    file = filedialog.asksaveasfile(defaultextension = ".txt", mode='w', initialdir=".", title="Save As", filetypes=(("Text files", "*.txt"),))
    if file:
        # Getting the number of matrices
        numMatrices = 1
        for x in range(2, numPlayers):
            numMatrices *= numStrats[x]
        
        # Getting list of the strategy names
        payoffMatrixSlaves = payoffsFrame.grid_slaves()
        strategyNames = payoffMatrixSlaves[numStrats[0] * numStrats[1] * numMatrices:]
        
        p1StrategyNames = strategyNames[:numStrats[0]]
        p1StrategyNames = [name.get() for name in p1StrategyNames]
        p1StrategyNames.reverse()
        p1StrategyNamesString = " ".join(p1StrategyNames)
        p1StrategyNamesString = p1StrategyNamesString + "\n"
        p2StrategyNames = strategyNames[numStrats[1]:]
        p2StrategyNames = [name.get() for name in p2StrategyNames]
        p2StrategyNames.reverse()
        p2StrategyNamesString = " ".join(p2StrategyNames)
        p2StrategyNamesString = p2StrategyNamesString + "\n"
        
        file.write(str(numStrats[0]) + " " + str(numStrats[1]) + "\n")
        file.write(p1StrategyNamesString)
        file.write(p2StrategyNamesString)
        for i, group in enumerate(groupedPayoffs):
            for j, payoff in enumerate(group):
                if j < numStrats[1] - 1:
                    file.write(str(payoff[0]) + " " + str(payoff[1]) + " ")
                else:
                    file.write(str(payoff[0]) + " " + str(payoff[1]))
            if i < len(groupedPayoffs) - 1:
                file.write("\n")
    return
"""

def saveAs(G, dimensionsFrame, payoffsFrame):
    entriesToSimGame(G, dimensionsFrame, payoffsFrame)
    G.saveToFile("three_players.txt")

def saveRecord(topUpdate, selectIDEntry, updateClicked1, updateClicked2, numTurnsEntry, outputEntry, score1Entry, score2Entry):
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
    recordSavedInfo = messagebox.showinfo("Record Saved", "Record successfully saved")
    return
    
def searchRecords():    
    topSearch = Toplevel()
    topSearch.title("Search Records")
    topSearch.iconbitmap("knight.ico")
    topSearch.geometry("400x180")
    
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
    
    submitButton = Button(topSearch, text="Submit", command=lambda: submitQuery(topSearch, searchClicked1, searchClicked2, numTurnsSearchEntry, outputSearchEntry, score1SearchEntry, score2SearchEntry, IDEntry))
    submitButton.grid(row=7, column=0, columnspan=2)
    return

def showRecords(dbWindow):
    # Create a database or connect to one
    conn = sqlite3.connect('match.db')
    
    # Create cursor
    c = conn.cursor()
    
    c.execute("SELECT *, oid FROM matches")
    records = c.fetchall()
    numRecords = len(records)
    
    proceed = True
    if numRecords >= 100000:
        proceed = messagebox.askyesno("Warning", f"The number of records retrieved from the database was {numRecords}. This may take some time. Do you want to proceed?")
    if proceed:
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

def simGameToEntries(G, dimensionsFrame, payoffsFrame):
    """Loads the data from the SimGame object into the entries.
    """
    G.print()
    # Getting numStrats
    dimensionsSlaves = dimensionsFrame.grid_slaves()
    numStratsEntries = []
    for slave in dimensionsSlaves:
        if type(slave).__name__ == "Entry":
            numStratsEntries.append(slave)
    numPlayersEntry = numStratsEntries[-1]
    numPlayers = int(numPlayersEntry.get())
    numStratsEntries.pop() # last one will be the numPlayers entry
    numStratsEntries.reverse()
    
    oldNumStrats = [int(numStratsEntries[x].get()) for x in range(numPlayers)]
    
    # Getting G.numPlayers
    oldNumPlayers = numPlayers
    numPlayersEntry.delete(0, END)
    numPlayersEntry.insert(0, G.numPlayers)
    
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
        numStratsEntries[x].insert(0, G.players[x].numStrats)
    
    numStrats = [int(numStratsEntries[x].get()) for x in range(numPlayers)]
    
    # When entries need to be deleted
    # Getting payoffs
    numOutcomes = 1
    for x in range(numPlayers):
        numOutcomes *= oldNumStrats[x]
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    outcomes = payoffMatrixSlaves[:numOutcomes]
    outcomes.reverse()
    outcomesGet = [outcome.get() for outcome in outcomes]
    # Grouping them into rows
    matrixGroupedOutcomes = [outcomes[n:n + oldNumStrats[0] * oldNumStrats[1]] for n in range(0, numOutcomes, oldNumStrats[0] * oldNumStrats[1])]
    groupedOutcomes = [[matrix[n:n + oldNumStrats[1]] for n in range(0, oldNumStrats[0] * oldNumStrats[1], oldNumStrats[1])] for matrix in matrixGroupedOutcomes]
    
    strategyNames = payoffMatrixSlaves[numOutcomes:]
    strategyNames.reverse()
    
    numMatrices = 1
    for x in range(2, numPlayers):
        numMatrices *= oldNumStrats[x]
        
    groupedStrategyNames = []
    if numPlayers < 3:
        groupedStrategyNames.append(strategyNames[:oldNumStrats[1]])
        groupedStrategyNames.append(strategyNames[oldNumStrats[1]:])
    else:
        groupedStrategyNames.append(strategyNames[:numMatrices])
        groupedStrategyNames.append(strategyNames[numMatrices:numMatrices + oldNumStrats[1]])
        groupedStrategyNames.append(strategyNames[numMatrices + oldNumStrats[1]:])  
    groupedStrategyNames.reverse()

    # Deleting extra matrices
    for m in G.removedMatrices:
        for i in range(oldNumStrats[0]):
            for j in range(oldNumStrats[1]):
                groupedOutcomes[m][i][j].grid_remove()
        del groupedOutcomes[m]
        
    numMatrices = 1
    for x in range(2, numPlayers):
        numMatrices *= numStrats[x]
    
    # Deleting rows and columns in the matrices we're keeping according to what's in removedRow and removedCols
    # Remove the same row from every array in the front-end payoff matrix
    for m in range(numMatrices):
        for r in G.removedRows:
            for j in range(oldNumStrats[1]):
                groupedOutcomes[m][r][j].grid_remove()
            del groupedOutcomes[m][r]
    # Remove the same column from every array in the front-end payoff matrix
    for m in range(numMatrices):
        for c in G.removedCols:
            for i in range(oldNumStrats[0] - len(G.removedRows)):
                groupedOutcomes[m][i][c].grid_remove()
                del groupedOutcomes[m][i][c]
    outcomesToRegrid = groupedOutcomes
    
    # removing and deleting strategy names
    for r in G.removedRows:
        groupedStrategyNames[0][r].grid_remove()
        del groupedStrategyNames[0][r]
    for c in G.removedCols:
        groupedStrategyNames[1][c].grid_remove()
        del groupedStrategyNames[1][c]
    if numPlayers >= 3:
        allPast2Have1Strat = True
        for x in range(2, numPlayers):
            if numStrats[x] > 1:
                allPast2Have1Strat = False
        if allPast2Have1Strat:
            for m in range(numMatrices):
                groupedStrategyNames[2][m].grid_remove()
                del groupedStrategyNames[2][m]
    stratNamesToRegrid = groupedStrategyNames
    
    # Clearing the table
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    for slave in payoffMatrixSlaves:
        slave.grid_remove()
    
    # Offsets for gridding
    if numPlayers >= 3:
        if allPast2Have1Strat:
            offset1 = 1
            offset2 = 0
        else:
            offset1 = 2
            offset2 = 1
    else:
        offset1 = 1
        offset2 = 0
    # Regridding the strategy names
    for p, player in enumerate(stratNamesToRegrid):
        for n, name in enumerate(player):
            if p == 0:
                name.grid(row=n + offset1, column=0)
            elif p == 1:
                name.grid(row=offset2, column=n + 1)
            else: # p == 2
                name.grid(row=0, column=n + 1)
    
    # Regridding the remaining entries
    for m in range(len(outcomesToRegrid)):
        for i in range(len(outcomesToRegrid[0])):
            for j in range(len(outcomesToRegrid[0][0])):
                outcomesToRegrid[m][i][j].grid(row=i + 1, column=j + m * numStrats[1] + 1, sticky=NSEW)
        
    # FIXME: When entries need to be added
    
    # Getting strategy names
    p1StrategyNames = strategyNames[:oldNumStrats[0]]
    p1StrategyNames = [name.get() for name in p1StrategyNames]
    p1StrategyNames.reverse()
    p2StrategyNames = strategyNames[oldNumStrats[1]:]
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
    entriesToSimGame(G, dimensionsFrame, payoffsFrame)
    
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
    
def submitQuery(topSearch, searchClicked1, searchClicked2, numTurnsSearchEntry, outputSearchEntry, score1SearchEntry, score2SearchEntry, IDEntry):
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
            
        exportSearchButton = Button(topSearch, text="Export to csv", command=export)
        
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

def updateRecord(selectIDEntry):
    """
    Allows the user to manually update a record in the matches table
    """    
    conn = sqlite3.connect('match.db')
    c = conn.cursor()
    
    recordID = selectIDEntry.get()
    try:
        c.execute("SELECT 1 FROM matches where oid=" + recordID)
    except sqlite3.OperationalError:
        IDNotSelectedError = messagebox.showerror("Error", "You must enter an ID to update a record.")
        return
    else:
        records = c.fetchall()
        if len(records) == 0:
            recordDNEError = messagebox.showerror("Error", "A record with that ID does not exist in the matches table.")
        else:
            # Update the record
            topUpdate = Toplevel()
            topUpdate.title("Update a Record")
            topUpdate.iconbitmap("knight.ico")
            topUpdate.geometry("400x170")
                
            records = c.fetchall()
            
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
                
            saveButton = Button(topUpdate, text="Save Record", command=lambda: saveRecord(topUpdate, selectIDEntry, updateClicked1, updateClicked2, numTurnsEntry, outputEntry, score1Entry, score2Entry))
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

def saveAsLatex():
    """
        Saves the current payoff matrix in the format of a buildable LaTeX array
    """    
    file = filedialog.asksaveasfile(defaultextension = ".tex", mode='w', initialdir=".", title="Save As", filetypes=(("LaTeX files", "*.tex"),))
    if file:
        numStrats1 = int(numStratsEntries[0].get())
        numStrats2 = int(numStratsEntries[1].get())
        
        payoffMatrixSlaves = payoffsFrame.grid_slaves()
        outcomes = payoffMatrixSlaves[:numStrats1 * numStrats2]
        payoffs = [outcome.get() for outcome in outcomes]
        payoffs.reverse()
        payoffs = [[payoff[0], payoff[3]] for payoff in payoffs]
        groupedPayoffs = [payoffs[i:i + numStrats2] for i in range(0, len(payoffs), numStrats2)]
        
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
        for j, name in enumerate(p2StrategyNames):
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
                        p2StrategyNames[j] = "\\" + name
                        
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
                        p2StrategyNames[j] = "\\" + p2StrategyNames[j]
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