from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import nashpy as nash
import axelrod as axl
import warnings

# Function definitions
def computeEquilibria(output):
    numStrats1 = int(numStratsEntry1.get())
    numStrats2 = int(numStratsEntry2.get())
    if output == 0: # Standard nashpy Output
        eqs1 = G.support_enumeration()
        numEquilibria = len(list(eqs1))
        if numEquilibria % 2 == 0:
            warnings.warn(f"An even number ({numEquilibria}) of equilibria was returned. This indicates that the game is degenerate. Consider using another algorithm to investigate.", RuntimeWarning)
            degenerateGameWarning = messagebox.showwarning(f"Even Number ({numEquilibria}) of Equilibria: Degenerate Game", f"An even number ({numEquilibria}) of equilibria was returned. This indicates that the game is degenerate. Consider using another algorithm to investigate.")
            # resetting the generator
            eqs1 = G.support_enumeration()
        else:
            # resetting the generator
            eqs1 = G.support_enumeration()
        eqList= list(eqs1)
        newList = []
        for eq in eqList:
            newEq = []
            for strat in eq:
                newEq.append(strat.tolist())
            newList.append(newEq)

        eqString = ""
        for i, eq in enumerate(newList):
            for j, strat in enumerate(eq):
                eqString = eqString + str(strat)
                if j < len(eq) - 1:
                    eqString = eqString + ", "
            if i < len(newList) - 1:
                eqString = eqString + "\n"
        
        eqs2 = G.support_enumeration()
        pureEquilibria = []
        mixedEquilibria = []
        for e in eqs2:
            if e[0][0] == 0.0 or e[0][0] == 1.0:
                pureEquilibria.append(e)
            else:
                mixedEquilibria.append(e)
        print(pureEquilibria)
        print(mixedEquilibria)
        
        equilibriaOutput = Label(equilibriaFrame, text=eqString, bd=1, relief=SUNKEN, anchor=E) 
        equilibriaOutput.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        root.geometry("750x425")
    elif output == 1: # Named Strategies
        eqs = G.support_enumeration()
        numEquilibria = len(list(eqs))
        if numEquilibria % 2 == 0:
            warnings.warn(f"An even number ({numEquilibria}) of equilibria was returned. This indicates that the game is degenerate. Consider using another algorithm to investigate.", RuntimeWarning)
            degenerateGameWarning = messagebox.showwarning(f"Even Number ({numEquilibria}) of Equilibria: Degenerate Game", f"An even number ({numEquilibria}) of equilibria was returned. This indicates that the game is degenerate. Consider using another algorithm to investigate.")
            # resetting the generator
            eqs = G.support_enumeration()
        else:
            # resetting the generator
            eqs = G.support_enumeration()
            
        payoffMatrixSlaves = payoffMatrixFrame.grid_slaves()
        strategyNames = payoffMatrixSlaves[numStrats1 * numStrats2:]
        
        p1StrategyNames = strategyNames[:numStrats1]
        p1StrategyNames.reverse()
        p2StrategyNames = strategyNames[numStrats1:]
        p2StrategyNames.reverse()
        
        namedEquilibria = []
        for eq in eqs:
            mixed = False
            if eq[0][0] != 1.0 and eq[0][0] != 0.0:
                mixed = True
            
            if not mixed:
                oneFound = False
                i = 0
                while not oneFound:
                    if eq[0][i] == 1.0:
                        oneFound = True
                        p1Strat = i
                    i += 1
                if not oneFound:
                    mixed = True
                oneFound = False
                i = 0
                while not oneFound:
                    if eq[1][i] == 1.0:
                        oneFound = True
                        p2Strat = i
                    i += 1
                namedEquilibria.append((p1StrategyNames[p1Strat].get(), p2StrategyNames[p2Strat].get()))
            else:
                namedEquilibria.append(list(eq))
            
        eqString = ""
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
            
        equilibriaOutput = Label(equilibriaFrame, text=eqString, bd=1, relief=SUNKEN, anchor=E)    
        equilibriaOutput.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        root.geometry("750x425")
    else:
        print("Error: variable output has taken on an unexpected value")
    return
    
def enterPayoffs():
    numStrats1 = int(numStratsEntry1.get())
    numStrats2 = int(numStratsEntry2.get())
    payoffMatrixSlaves = payoffMatrixFrame.grid_slaves()
    outcomes = payoffMatrixSlaves[:numStrats1 * numStrats2]
    payoffs = [tuple(map(int, o.get().split(", "))) for o in outcomes]
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
    
    global G
    G = nash.Game(p1Matrix, p2Matrix)
    return

def numStratsClick():
    proceed = messagebox.askokcancel("Clear Payoffs?", "This will clear the payoff matrix. Do you want to proceed?")
    
    if (proceed == True):   
        numStrats1 = int(numStratsEntry1.get())
        numStrats2 = int(numStratsEntry2.get())
        
        # clearing the table
        L = payoffMatrixFrame.grid_slaves()
        for l in L:
            l.grid_remove()
        
        # refilling the table
        for i in range(numStrats2):
            e = Entry(payoffMatrixFrame, width=10)
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
            e = Entry(payoffMatrixFrame, width=10)
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
                e = Entry(payoffMatrixFrame, width=5)
                e.grid(row=i + 1, column=j + 1, sticky=NSEW)
                e.insert(END, '%d, %d' % (0, 0))
                cols.append(e)
            rows.append(cols)
        
        root.geometry(f"{45 * numStrats2 + 600}x{25 * numStrats1 + 300}")

def startMatch(p1, p2, t = 6):    
    p1 = ""
    p2 = ""
    clicked1NoSpaces = clicked1.get().replace(" ", "")
    clicked2NoSpaces = clicked2.get().replace(" ", "")
    counter1 = 0
    while type(p1).__name__ == "str" and counter1 <= len(axl.strategies):
        try:
            if type(options[counter1]).__name__ == clicked1NoSpaces:
                p1 = options[counter1]
        except IndexError:
            stratNotFoundError = messagebox.showerror("Error", "The strategy you entered for player 1 was not in axelrod's list of strategies. Perhaps you meant to capitalize the individual words?")
        counter1 += 1
    counter2 = 0
    while type(p2).__name__ == "str" and counter2 <= len(axl.strategies):
        try:
            if type(options[counter2]).__name__ == clicked2NoSpaces:
                p2 = options[counter2]
                
                match = axl.Match((p1, p2), turns = t)
                axelrodOutput1 = Label(axelrodFrame, text=str(match.play()), relief=SUNKEN, anchor=E)
                axelrodOutput2 = Label(axelrodFrame, text=str(match.final_score_per_turn()), relief=SUNKEN, anchor=E)
                axelrodOutput1.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
                axelrodOutput2.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
        except IndexError:
            stratNotFoundError = messagebox.showerror("Error", "The strategy you entered for player 2 was not in axelrod's list of strategies. Perhaps you meant to capitalize the individual words?")
        counter2 += 1

    if axelrodOutput1.winfo_reqwidth() > axelrodOutput2.winfo_reqwidth():
        root.geometry(f"{axelrodOutput1.winfo_reqwidth() + 400}x425")
    else:
        root.geometry(f"700x{axelrodOutput2.winfo_reqwidth() + 200}")
    return

def startTournament():
    players = [s() for s in axl.demo_strategies]
    tournament = axl.Tournament(players=players, turns=10, repetitions=5)
    results = tournament.play() 
    
    axelrodOutput1.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
    axelrodOutput2.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
    return

# Defining the root window
root = Tk()
root.title("Interactive GT")
root.geometry("700x425")
root.iconbitmap("knight.ico")

# numStrats Frame
numStratsFrame = LabelFrame(root, text="Numbers of Strategies", padx=10, pady=10)

numStratsLabel1 = Label(numStratsFrame, text="Number of strategies for player 1: ")
numStratsLabel2 = Label(numStratsFrame, text="Number of strategies for player 2: ")
numStratsEntry1 = Entry(numStratsFrame, width=5)
numStratsEntry2 = Entry(numStratsFrame, width=5)
numStratsEntry1.insert(0, "2")
numStratsEntry2.insert(0, "2")
numStratsButton = Button(numStratsFrame, text="Enter", command=numStratsClick)

# Payoffs Frame
payoffsFrame = LabelFrame(root, text="Payoffs", padx=10, pady=10)
payoffMatrixFrame = LabelFrame(payoffsFrame, padx=10, pady=10)

# Adding strategy names
p2strat1Name = Entry(payoffMatrixFrame, width=10)
p2strat2Name = Entry(payoffMatrixFrame, width=10)
p1strat1Name = Entry(payoffMatrixFrame, width=10)
p1strat2Name = Entry(payoffMatrixFrame, width=10)
p2strat1Name.insert(0, "L")
p2strat2Name.insert(0, "R")
p1strat1Name.insert(0, "U")
p1strat2Name.insert(0, "D")
p2strat1Name.grid(row=0, column=1, pady=5)
p2strat2Name.grid(row=0, column=2, pady=5)
p1strat1Name.grid(row=1, column=0, padx=5)
p1strat2Name.grid(row=2, column=0, padx=5)

# https://www.activestate.com/resources/quick-reads/how-to-display-data-in-a-table-using-tkinter/
rows = []
for i in range(int(numStratsEntry1.get())):
    cols = []
    for j in range(int(numStratsEntry2.get())):
        e = Entry(payoffMatrixFrame, width=5)
        e.grid(row=i + 1, column=j + 1, sticky=NSEW)
        e.insert(END, '%d, %d' % (0, 0))
        cols.append(e)
    rows.append(cols)
    
enterPayoffsButton = Button(payoffsFrame, text="Enter", command=enterPayoffs)

L = payoffMatrixFrame.grid_slaves()
L.pop()
L.pop()
L.pop()
L.pop()
payoffs = [tuple(map(int, l.get().split(", "))) for l in L]
payoffs.reverse()
numStrats1 = int(numStratsEntry1.get())
numStrats2 = int(numStratsEntry2.get())

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
    
global G
G = nash.Game(p1Matrix, p2Matrix)

# Equilibria Frame
equilibriaFrame = LabelFrame(root, text="Equilibria" , padx=10, pady=10)

output = IntVar()
output.set("0")

def clicked(value):
    output.set(value)

Radiobutton(equilibriaFrame, text="Standard nashpy Output", variable=output, value=0, command=lambda: clicked(output.get())).grid(row=0, column=0, sticky=W)
Radiobutton(equilibriaFrame, text="Named Strategies", variable=output, value=1, command=lambda: clicked(output.get())).grid(row=1, column=0, sticky=W)

equilibriaButton = Button(equilibriaFrame, text="Compute Equilibria", command=lambda: computeEquilibria(output.get()))

# Axelrod Frame
axelrodFrame = LabelFrame(root, text="axelrod" , padx=10, pady=10)
strategyLabel1 = Label(axelrodFrame, text="Enter a strategy for player 1: ")
strategyLabel2 = Label(axelrodFrame, text="Enter a strategy for player 2: ")
options = [s() for s in axl.strategies]
clicked1 = StringVar()
clicked1.set(options[0])
clicked2 = StringVar()
clicked2.set(options[0])
dropdown1 = ttk.Combobox(axelrodFrame, textvariable=clicked1, values=options)
dropdown2 = ttk.Combobox(axelrodFrame, textvariable=clicked2, values=options)
turnsLabel = Label(axelrodFrame, text="Enter the number of turns: ")
turnsEntry = Entry(axelrodFrame, width=5)
turnsEntry.insert(0, "6")

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

matchButton = Button(axelrodFrame, text="Start Match", command=lambda: startMatch(p1, p2, int(turnsEntry.get())))
tournamentButton = Button(axelrodFrame, text="Start Tournament", command=startTournament)
axelrodOutput1 = Label(axelrodFrame, text="MATCHES HERE", relief=SUNKEN, bd=1, anchor=E)
axelrodOutput2 = Label(axelrodFrame, text="MATCHES HERE", relief=SUNKEN, bd=1, anchor=E)

# Putting everything on the screen
numStratsFrame.grid(row=0, column=0, padx=10, pady=10)
numStratsLabel1.grid(row=0, column=0)
numStratsLabel2.grid(row=1, column=0)
numStratsEntry1.grid(row=0, column=1)
numStratsEntry2.grid(row=1, column=1)
numStratsButton.grid(row=1, column=2, padx=5, pady=5)

payoffsFrame.grid(row=0, column=1, padx=10, pady=10)
payoffMatrixFrame.grid(row=0, column=0, padx=10, pady=10)
enterPayoffsButton.grid(row=1, column=0, padx=5, pady=5)

equilibriaFrame.grid(row=1, column=0, padx=10, pady=10)
equilibriaButton.grid(row=1, column=1, padx=10, pady=10)

axelrodFrame.grid(row=1, column=1, padx=10, pady=10)
strategyLabel1.grid(row=0, column=0)
dropdown1.grid(row=0, column=1)
strategyLabel2.grid(row=1, column=0)
dropdown2.grid(row=1, column=1)
turnsLabel.grid(row=2, column=0, sticky=W)
turnsEntry.grid(row=2, column=1, sticky=W)
matchButton.grid(row=3,column=0)
tournamentButton.grid(row=3,column=1)

root.mainloop()