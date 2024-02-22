from tkinter import *
import nashpy as nash
import axelrod as axl

# Function definitions
def computeEquilibria():
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
            e.insert(END, '%d,%d' % (i, j))
            cols.append(e)
        rows.append(cols)
    
    root.geometry(f"{45 * numStrats2 + 400}x{25 * numStrats1 + 150}")
    
def savePayoffs():
    return

root = Tk()
root.title("Interactive GT")
root.geometry("550x250")
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
        e.insert(END, '%d,%d' % (i, j))
        cols.append(e)
    rows.append(cols)
    
savePayoffsButton = Button(payoffsFrame, text="Save Payoffs", command=savePayoffs)

# Equilibria Frame
equilibriaFrame = LabelFrame(root, text="Equilibria", padx=10, pady=10)

equilibriaButton = Button(equilibriaFrame, text="Compute Equilibria", command=computeEquilibria)

# Putting everything on the screen
numStratsFrame.grid(row=0, column=0, padx=10, pady=10)
numStratsLabel1.grid(row=0, column=0)
numStratsLabel2.grid(row=1, column=0)
numStratsEntry1.grid(row=0, column=1)
numStratsEntry2.grid(row=1, column=1)
numStratsButton.grid(row=0, column=2, padx=5, pady=5)

payoffsFrame.grid(row=0, column=1, padx=10, pady=10)

payoffMatrixFrame.grid(row=0, column=0, padx=10, pady=10)
savePayoffsButton.grid(row=1, column=0, padx=5, pady=5)

equilibriaFrame.grid(row=0, column=2, padx=10, pady=10)
equilibriaButton.pack(padx=10, pady=10)

root.mainloop()