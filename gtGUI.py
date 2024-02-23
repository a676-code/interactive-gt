from tkinter import *
import nashpy as nash
import axelrod as axl

# Function definitions
def computeEquilibria():
    eqs = G.support_enumeration()
    output = Label(equilibriaFrame, text=list(eqs), bd=1, relief=SUNKEN, anchor=E)
    output.pack(padx=5, pady=5)
    root.geometry("575x500")
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
    
    root.geometry(f"{45 * numStrats2 + 400}x{25 * numStrats1 + 250}")
    
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
    print(G)
    return

root = Tk()
root.title("Interactive GT")
root.geometry("550x500")
root.iconbitmap("knight.ico")

# numStrats Frame
numStratsFrame = LabelFrame(root, text="Numbers of Strategies", padx=10, pady=10)

numStratsLabel1 = Label(numStratsFrame, text="Num Strats 1")
numStratsLabel2 = Label(numStratsFrame, text="Num Strats 2")
numStratsEntry1 = Entry(numStratsFrame, width=5)
numStratsEntry2 = Entry(numStratsFrame, width=5)
numStratsEntry1.insert(0, "2")
numStratsEntry2.insert(0, "2")
numStratsButton = Button(numStratsFrame, text="Enter", command=numStratsClick)
warning = Label(numStratsFrame, text="Warning: pressing Enter will clear all payoffs")

# Payoffs Frame
payoffsFrame = LabelFrame(root, text="Payoffs", padx=10, pady=10)
payoffMatrixFrame = LabelFrame(payoffsFrame, text="Payoff Matrix", padx=10, pady=10)

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
    
enterPayoffsButton = Button(payoffsFrame, text="Enter Payoffs", command=enterPayoffs)

# Equilibria Frame
equilibriaFrame = LabelFrame(root, text="Equilibria", padx=10, pady=10)

equilibriaButton = Button(equilibriaFrame, text="Compute Equilibria", command=computeEquilibria)

output = Label(equilibriaFrame, text="EQUILIBRIA HERE", bd=1, relief=SUNKEN, anchor=E)

# Axelrod Frame
axelrodFrame = LabelFrame(root, text="axelrod", padx=10, pady=10)
btn = Button(axelrodFrame, text="Placeholder")

# Putting everything on the screen
numStratsFrame.grid(row=0, column=0, padx=10, pady=10)
numStratsLabel1.grid(row=0, column=0)
numStratsLabel2.grid(row=1, column=0)
numStratsEntry1.grid(row=0, column=1)
numStratsEntry2.grid(row=1, column=1)
numStratsButton.grid(row=0, column=2, padx=5, pady=5)
warning.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

payoffsFrame.grid(row=0, column=1, padx=10, pady=10)
payoffMatrixFrame.grid(row=0, column=0, padx=10, pady=10)
enterPayoffsButton.grid(row=1, column=0, padx=5, pady=5)

equilibriaFrame.grid(row=1, column=0, padx=10, pady=10)
equilibriaButton.pack(padx=10, pady=10)

axelrodFrame.grid(row=1, column=1, padx=10, pady=10)
btn.pack(padx=10, pady=10)

root.mainloop()