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
import interactivegt_n_players_functions
from interactivegt_n_players_functions import *

# Creating our SimGame object
# global G
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

# FIXME: The scrollbars are in the right place, but instead of becoming usable when the contents of the frame get bigger, the frame simply stretches, leaving the scrollbars grayed out. 
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
numPlayersButton = Button(dimensionsFrame, text="Enter numPlayers", command=numPlayersClick)
dimensionsButton = Button(dimensionsFrame, text="Enter Dimensions", command=dimensionsClick)

# payoffsFrame < payoffsCanvas < mainPayoffsFrame < rootFrame < ...
# Payoffs Frame
def onScroll(event):
    payoffsCanvas.configure(scrollregion=payoffsCanvas.bbox("all"), width=100 * numStrats2, height=40 * numStrats1)

mainPayoffsFrame = LabelFrame(rootFrame, text="Payoffs", padx=10, pady=10)
payoffsCanvas = Canvas(mainPayoffsFrame)
# payoffsCanvas.pack(side=LEFT, fill=BOTH, expand=1)
yPayoffsScrollbar = Scrollbar(mainPayoffsFrame, orient="vertical", command=payoffsCanvas.yview)
xPayoffsScrollbar = Scrollbar(mainPayoffsFrame, orient="horizontal", command=payoffsCanvas.xview)
payoffsCanvas.configure(xscrollcommand=xPayoffsScrollbar.set, yscrollcommand=yPayoffsScrollbar.set)
payoffsCanvas.bind('<Configure>', onScroll)
payoffsFrame = Frame(payoffsCanvas, padx=10, pady=10)
payoffsCanvas.create_window((0, 0), window=payoffsFrame, anchor="nw")

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
revertButton = Button(iesdsFrame, text="Revert", command=lambda: revert(dimensionsFrame))
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

numPlayersButton.grid(row=3, column=0, padx=(0, 5), pady=5)
dimensionsButton.grid(row=3, column=1, padx=(0, 5), pady=5, sticky=W)

# payoffsFrame.grid(row=0, column=1, padx=10, pady=10, sticky=W)
mainPayoffsFrame.grid(row=0, column=1)
# payoffsVScrollbar.pack(side=RIGHT, fill=Y)
# payoffsHScrollbar.pack(side=BOTTOM, fill=X)
xPayoffsScrollbar.grid(row=1, column=0, sticky=EW)
yPayoffsScrollbar.grid(row=0, column=1, sticky=NS)

payoffsCanvas.grid(row=0, column=0)
payoffsFrame.pack(side=TOP)


iesdsFrame.grid(row=1, column=1, padx=10, pady=10, sticky=W)
revertButton.grid(row=0, column=1)
iesdsButton.grid(row=2, column=0, columnspan=2)

equilibriaFrame.grid(row=1, column=0, padx=10, pady=10)
equilibriaButton.grid(row=1, column=1, padx=10, pady=10)

axelrodFrame.grid(row=2, column=1, padx=10, pady=10, sticky=W)
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