from tkinter import *

root = Tk()
root.geometry("300x100")

numStratsEntry1 = Entry(root, width=5)
numStratsEntry2 = Entry(root, width=5)
numStratsEntry1.insert(0, "2")
numStratsEntry2.insert(0, "2")

print("width: ")
print(root.winfo_reqwidth())

print("height: ")
print(root.winfo_reqheight())

def numStrats1Click():    
    numStrats1 = int(numStratsEntry1.get())
    numStrats2 = int(numStratsEntry2.get())
    rows = []
    for i in range(numStrats1):
        cols = []
        for j in range(2,numStrats2 + 2):
            e = Entry(width=10)
            e.grid(row=i, column=j, sticky=NSEW)
            e.insert(END, '%d.%d' % (i, j - 2))
            cols.append(e)
        rows.append(cols)
    root.geometry(f"{root.winfo_width()}x{25 * numStrats1}")
    
def numStrats2Click():
    numStrats1 = int(numStratsEntry1.get())
    numStrats2 = int(numStratsEntry2.get())
    rows = []
    for i in range(numStrats1):
        cols = []
        for j in range(2, numStrats2 + 2):
            e = Entry(width=10)
            e.grid(row=i, column=j, sticky=NSEW)
            e.insert(END, '%d.%d' % (i, j - 2))
            cols.append(e)
        rows.append(cols)
    root.geometry(f"{75 * numStrats2}x{root.winfo_height()}")

numStrats1Button = Button(root, text="Enter", command=numStrats1Click)
numStrats2Button = Button(root, text="Enter", command=numStrats2Click)
    
rows = []
for i in range(int(numStratsEntry1.get())):
    cols = []
    for j in range(2,int(numStratsEntry2.get()) + 2):
        e = Entry(width=10)
        e.grid(row=i, column=j, sticky=NSEW)
        e.insert(END, '%d.%d' % (i, j - 2))
        cols.append(e)
    rows.append(cols)

numStratsEntry1.grid(row=0, column=0)
numStratsEntry2.grid(row=1, column=0)
numStrats1Button.grid(row=0, column=1)
numStrats2Button.grid(row=1, column=1)

root.mainloop()