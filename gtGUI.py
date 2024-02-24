from tkinter import *
from tkinter import ttk
import nashpy as nash
import axelrod as axl

# Function definitions
def computeEquilibria():
    eqs1 = G.support_enumeration()
    eqs2 = G.support_enumeration()
    pureEquilibria = []
    mixedEqulibria = []
    for e in eqs1:
        if e[0][0] == 0.0 or e[0][0] == 1.0:
            pureEquilibria.append(e)
        else:
            mixedEqulibria.append(e)
    print(pureEquilibria)
    print(mixedEqulibria)
        
    equilibriaOutput = Label(equilibriaFrame, text=list(eqs2), bd=1, relief=SUNKEN, anchor=E)    
    equilibriaOutput.pack(padx=5, pady=5)
    root.geometry("750x425")
    return
    
def enterPayoffs():
    L = payoffMatrixFrame.grid_slaves()
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
    return

def numStratsClick():
    # clearing the table
    L = payoffMatrixFrame.grid_slaves()
    for l in L:
        l.grid_remove()
    
    # refilling the table
    numStrats1 = int(numStratsEntry1.get())
    numStrats2 = int(numStratsEntry2.get())
    rows = []
    for i in range(numStrats1):
        cols = []
        for j in range(numStrats2):
            e = Entry(payoffMatrixFrame, width=5)
            e.grid(row=i, column=j, sticky=NSEW)
            e.insert(END, '%d, %d' % (0, 0))
            cols.append(e)
        rows.append(cols)
    
    root.geometry(f"{45 * numStrats2 + 600}x{25 * numStrats1 + 300}")

def startMatch(p1, p2):    
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
    
    match = axl.Match((p1, p2), turns = 6)
    axelrodOutput1 = Label(axelrodFrame, text=str(match.play()), relief=SUNKEN, anchor=E)
    axelrodOutput2 = Label(axelrodFrame, text=str(match.final_score_per_turn()), relief=SUNKEN, anchor=E)
    axelrodOutput1.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
    axelrodOutput2.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
    return

def startTournament():
    players = [s() for s in axl.demo_strategies]
    tournament = axl.Tournament(players=players, turns=10, repetitions=5)
    results = tournament.play() 
    
    axelrodOutput1.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
    axelrodOutput2.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
    return

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
warning = Label(numStratsFrame, text="Warning: pressing Enter will clear all payoffs")

# Payoffs Frame
payoffsFrame = LabelFrame(root, text="Payoffs", padx=10, pady=10)
payoffMatrixFrame = LabelFrame(payoffsFrame, text="Payoff Matrix" , padx=10, pady=10)

# https://www.activestate.com/resources/quick-reads/how-to-display-data-in-a-table-using-tkinter/
rows = []
for i in range(int(numStratsEntry1.get())):
    cols = []
    for j in range(int(numStratsEntry2.get())):
        e = Entry(payoffMatrixFrame, width=5)
        e.grid(row=i, column=j, sticky=NSEW)
        e.insert(END, '%d, %d' % (0, 0))
        cols.append(e)
    rows.append(cols)
    
enterPayoffsButton = Button(payoffsFrame, text="Enter", command=enterPayoffs)

L = payoffMatrixFrame.grid_slaves()
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

equilibriaButton = Button(equilibriaFrame, text="Compute Equilibria", command=computeEquilibria)
equilibriaOutput = Label(equilibriaFrame, text="EQUILIBRIA HERE", relief=SUNKEN, anchor=E)

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
turnsEntry = Label(axelrodFrame, width=5)

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

matchButton = Button(axelrodFrame, text="Start Match", command=lambda: startMatch(p1, p2))
tournamentButton = Button(axelrodFrame, text="Start Tournament", command=startTournament)
axelrodOutput1 = Label(axelrodFrame, text="MATCHES HERE", relief=SUNKEN, bd=1, anchor=E)
axelrodOutput2 = Label(axelrodFrame, text="MATCHES HERE", relief=SUNKEN, bd=1, anchor=E)

# Putting everything on the screen
numStratsFrame.grid(row=0, column=0, padx=10, pady=10)
numStratsLabel1.grid(row=0, column=0)
numStratsLabel2.grid(row=1, column=0)
numStratsEntry1.grid(row=0, column=1)
numStratsEntry2.grid(row=1, column=1)
numStratsButton.grid(row=2, column=2, padx=5, pady=5)
warning.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

payoffsFrame.grid(row=0, column=1, padx=10, pady=10)
payoffMatrixFrame.grid(row=0, column=0, padx=10, pady=10)
enterPayoffsButton.grid(row=1, column=0, padx=5, pady=5)

equilibriaFrame.grid(row=1, column=0, padx=10, pady=10)
equilibriaButton.pack(padx=10, pady=10)

axelrodFrame.grid(row=1, column=1, padx=10, pady=10)
strategyLabel1.grid(row=0, column=0)
dropdown1.grid(row=0, column=1)
strategyLabel2.grid(row=1, column=0)
dropdown2.grid(row=1, column=1)
turnsLabel.grid(row=2, column=0)
turnsEntry.grid(row=2, column=1)
matchButton.grid(row=3,column=0)
tournamentButton.grid(row=3,column=1)

root.mainloop()