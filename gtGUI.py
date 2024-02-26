from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import nashpy as nash
import axelrod as axl
import warnings

# Function definitions
def changeBackgroundColor():
    top = Toplevel()
    top.title("Enter a Color")
    top.iconbitmap("knight.ico")
    top.geometry("190x30")
    
    colorLabel = Label(top, text="Enter a color:")
    colorEntry = Entry(top, width=10)
    colorEnter = Button(top, text="Enter", command=lambda: enterColor(colorEntry.get()))
    
    # Putting everything on the top window
    colorLabel.grid(row=0, column=0)
    colorEntry.grid(row=0, column=1)
    colorEnter.grid(row=0, column=2, padx=5)
    return

def clearPayoffMatrix():
    proceed = messagebox.askokcancel("Clear Payoffs?", "Are you sure you want to clear the payoff matrix? ")
    
    if (proceed == True):   
        numStrats1 = int(numStratsEntry1.get())
        numStrats2 = int(numStratsEntry2.get())
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
        
        root.geometry(f"{45 * numStrats2 + 600}x{25 * numStrats1 + 300}")
    return

def computeEquilibria(output):
    enterPayoffs()
    numStrats1 = int(numStratsEntry1.get())
    numStrats2 = int(numStratsEntry2.get())
    if output == 0: # Standard nashpy Output
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
        eqList= list(eqs)
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
        
        eqs = G.support_enumeration()
        pureEquilibria = []
        mixedEquilibria = []
        for e in eqs:
            if e[0][0] == 0.0 or e[0][0] == 1.0:
                pureEquilibria.append(e)
            else:
                mixedEquilibria.append(e)

        # Coloring the equilibria yellow
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
        
        # converting nashpy equilibria output to indices
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
        if type(eqSlaves[0]).__name__ == "Label":
            eqSlaves[0].grid_remove()
        
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
        
        pureEquilibria = []
        mixedEquilibria = []
        for e in eqs:
            if e[0][0] == 0.0 or e[0][0] == 1.0:
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
        for o in outcomes:
            if numInRow < numStrats2:
                row.append(o)
                numInRow += 1
                if numInRow == numStrats2:
                    newOutcomes.append(row)
                    numInRow = 0
                    row = []
        
        # Getting list of the strategy names
        payoffMatrixSlaves = payoffsFrame.grid_slaves()
        strategyNames = payoffMatrixSlaves[numStrats1 * numStrats2:]
        
        p1StrategyNames = strategyNames[:numStrats1]
        p1StrategyNames.reverse()
        p2StrategyNames = strategyNames[numStrats1:]
        p2StrategyNames.reverse()
        
        eqs = G.support_enumeration()
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
        
        # Creating the string to go in the label
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
        if type(eqSlaves[0]).__name__ == "Label":
            eqSlaves[0].grid_remove()
            
        equilibriaOutput = Label(equilibriaFrame, text=eqString, bd=1, relief=SUNKEN, anchor=E)    
        equilibriaOutput.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        root.geometry("750x425")
    else:
        print("Error: variable output has taken on an unexpected value")
    return

def enterColor(color):
    root.configure(bg=color)
    return
    
def enterFileName(fileName, payoffs):
    numStrats1 = int(numStratsEntry1.get())
    numStrats2 = int(numStratsEntry2.get())
    
    with open(fileName, 'w') as file:
        file.write(str(numStrats1) + " " + str(numStrats2) + "\n")
        
        for i, payoff in enumerate(payoffs):
            if i < numStrats1 * numStrats2 - 1:
                file.write(str(payoff[0]) + " " + str(payoff[1]) + " ")
            else:
                file.write(str(payoff[0]) + " " + str(payoff[1]))
            if i % numStrats2 - 1 == 0 and i < numStrats1 * numStrats2 - 1:
                file.write("\n")
    return

def enterPayoffs():
    numStrats1 = int(numStratsEntry1.get())
    numStrats2 = int(numStratsEntry2.get())
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
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
        
        root.geometry(f"{45 * numStrats2 + 600}x{25 * numStrats1 + 300}")
    return

def openFile():
    root.filename = filedialog.askopenfilename(initialdir=".", title="Select a File", filetypes=(("Text files", "*.txt"),))
    
    with open(root.filename, 'r') as file:
        numStrats = file.readline().split(" ")
        numStratsEntry1.delete(0, 'end')
        numStratsEntry2.delete(0, 'end')
        numStratsEntry1.insert(0, numStrats[0])
        numStratsEntry2.insert(0, numStrats[1])
        numStratsClick()
        
        line_index = 0
        for line in file:
            payoffLine = line.split(" ")
            if payoffLine[-1] == "\n":
                payoffLine.pop()
            if "\n" in payoffLine[-1]:
                payoffLine[-1] = payoffLine[-1][:len(payoffLine[-1]) - 1]
            
            groupedPayoffs = [payoffLine[i:i + 2] for i in range(0, len(payoffLine), 2)]
            stringPayoffs = [str(p[0]) + ", " + str(p[1]) for p in groupedPayoffs]
            
            payoffMatrixSlaves = payoffsFrame.grid_slaves()
            payoffs = payoffMatrixSlaves[:numStrats1 * numStrats2]
            payoffs.reverse()
            row = payoffs[line_index:line_index + numStrats2]
            
            for p in row:
                p.delete(0, 'end')
            for j, payoff in enumerate(row):
                if j < numStrats2:
                    payoff.insert(0, stringPayoffs[j])
            line_index += 2
    return

def saveAs():
    numStrats1 = int(numStratsEntry1.get())
    numStrats2 = int(numStratsEntry2.get())
    
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    outcomes = payoffMatrixSlaves[:numStrats1 * numStrats2]
    payoffs = [outcome.get() for outcome in outcomes]
    payoffs.reverse()
    payoffs = [[payoff[0], payoff[3]] for payoff in payoffs]
    
    # Prompting the user for a file name
    top = Toplevel()
    top.title("Enter a File Name")
    top.iconbitmap("knight.ico")
    top.geometry("210x30")

    fileNameLabel = Label(top, text="Enter a File Name: ")
    fileNameEntry = Entry(top, width=10)
    fileNameButton = Button(top, text="Enter", command=lambda: [enterFileName(fileNameEntry.get(), payoffs), top.destroy()])
    
    # Putting everything in the top window
    fileNameLabel.grid(row=0, column=0)
    fileNameEntry.grid(row=0, column=1)
    fileNameButton.grid(row=0, column=2)
    return

def saveAsLatex():
    numStrats1 = int(numStratsEntry1.get())
    numStrats2 = int(numStratsEntry2.get())
    
    payoffMatrixSlaves = payoffsFrame.grid_slaves()
    outcomes = payoffMatrixSlaves[:numStrats1 * numStrats2]
    payoffs = [outcome.get() for outcome in outcomes] # = [[4, 4], [3, 3], [2, 2], [1, 1]]
    payoffs.reverse()
    payoffs = [[payoff[0], payoff[3]] for payoff in payoffs]
        
    file = open('test.txt', 'w')
    for i, payoff in enumerate(payoffs):
        if i < numStrats1 * numStrats2 - 1:
            file.write(str(payoff[0]) + " " + str(payoff[1]) + " ")
        else:
            file.write(str(payoff[0]) + " " + str(payoff[1]))
        if i % numStrats2 - 1 == 0 and i < numStrats1 * numStrats2 - 1:
            file.write("\n")
    file.close()
    return

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
                axelrodOutput1.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
                axelrodOutput2.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
        except IndexError:
            stratNotFoundError = messagebox.showerror("Error", "The strategy you entered for player 2 was not in axelrod's list of strategies. Perhaps you meant to capitalize the individual words?")
        counter2 += 1

    if axelrodOutput1.winfo_reqwidth() > axelrodOutput2.winfo_reqwidth():
        root.geometry(f"{axelrodOutput1.winfo_reqwidth() + 400}x425")
    else:
        root.geometry(f"700x{axelrodOutput2.winfo_reqwidth() + 200}")
    return

# def startTournament(t = 10, r = 5):
#     players = [s() for s in axl.demo_strategies]
#     tournament = axl.Tournament(players=players, turns=t, repetitions=r)
#     results = tournament.play() 
#     print("results:", results)
    
#     axelrodOutput1 = Label(axelrodFrame, text=results, relief=SUNKEN, bd=1, anchor=E)
#     axelrodOutput2 = Label(axelrodFrame, text=results, relief=SUNKEN, bd=1, anchor=E)
    
#     axelrodOutput1.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
#     axelrodOutput2.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky=EW)
#     return

# Defining the root window
root = Tk()
root.title("Interactive GT")
root.geometry("700x425")
root.iconbitmap("knight.ico")

# Menu bar
menubar = Menu(root)
root.config(menu=menubar)
# Create a menu item
file_menu = Menu(menubar)
menubar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open File", command=openFile)
file_menu.add_command(label="Save As...", command=saveAs)
file_menu.add_command(label="Save as LaTeX", command=saveAsLatex)

edit_menu = Menu(menubar)
menubar.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Clear Payoff Matrix", command=clearPayoffMatrix)

option_menu = Menu(menubar)
menubar.add_cascade(label="Options", menu=option_menu)
option_menu.add_command(label="Change Background Color", command=changeBackgroundColor)

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

# https://www.activestate.com/resources/quick-reads/how-to-display-data-in-a-table-using-tkinter/
rows = []
for i in range(int(numStratsEntry1.get())):
    cols = []
    for j in range(int(numStratsEntry2.get())):
        e = Entry(payoffsFrame, width=5)
        e.grid(row=i + 1, column=j + 1, sticky=NSEW)
        e.insert(END, '%d, %d' % (0, 0))
        cols.append(e)
    rows.append(cols)

payoffMatrixSlaves= payoffsFrame.grid_slaves()
payoffMatrixSlaves.pop()
payoffMatrixSlaves.pop()
payoffMatrixSlaves.pop()
payoffMatrixSlaves.pop()
payoffs = [tuple(map(int, slave.get().split(", "))) for slave in payoffMatrixSlaves]
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
# repetitionsLabel = Label(axelrodFrame, text="Enter the number of repetitions: ")
# repetitionsEntry = Entry(axelrodFrame, width=5)
# repetitionsEntry.insert(0, "10")

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
# tournamentButton = Button(axelrodFrame, text="Start Tournament", command=startTournament(int(turnsEntry.get())))

# Putting everything in the root window
numStratsFrame.grid(row=0, column=0, padx=10, pady=10)
numStratsLabel1.grid(row=0, column=0)
numStratsLabel2.grid(row=1, column=0)
numStratsEntry1.grid(row=0, column=1)
numStratsEntry2.grid(row=1, column=1)
numStratsButton.grid(row=1, column=2, padx=5, pady=5)

payoffsFrame.grid(row=0, column=1, padx=10, pady=10)

equilibriaFrame.grid(row=1, column=0, padx=10, pady=10)
equilibriaButton.grid(row=1, column=1, padx=10, pady=10)

axelrodFrame.grid(row=1, column=1, padx=10, pady=10)
strategyLabel1.grid(row=0, column=0, sticky=W)
dropdown1.grid(row=0, column=1, sticky=W)
strategyLabel2.grid(row=1, column=0, sticky=W)
dropdown2.grid(row=1, column=1, sticky=W)
turnsLabel.grid(row=2, column=0, sticky=W)
turnsEntry.grid(row=2, column=1, sticky=W)
# repetitionsLabel.grid(row=3, column=0, sticky=W)
# repetitionsEntry.grid(row=3, column=1, sticky=W)
matchButton.grid(row=4,column=1, sticky=W)
# tournamentButton.grid(row=4,column=1)

root.mainloop()