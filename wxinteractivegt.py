import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(500, 400))
        
        root = MyPanel(self)
        numStratsPanel = NumStratsPanel(root)
        payoffsPanel = PayoffsPanel(root)
        equilibriaPanel = EquilibriaPanel(root)
        iesdsPanel = IESDSPanel(root)
        axelrodPanel = AxelrodPanel(root)
        
        rootSizer = wx.GridBagSizer(1, 2)
        rootSizer.Add(numStratsPanel, pos=(0, 0), flag=wx.EXPAND)
        rootSizer.Add(payoffsPanel, pos=(0, 1), flag=wx.EXPAND)
        rootSizer.Add(equilibriaPanel, pos=(1, 0), flag=wx.EXPAND)
        rootSizer.Add(iesdsPanel, pos=(1, 1), flag=wx.EXPAND)
        rootSizer.Add(axelrodPanel, pos=(2, 1), flag=wx.EXPAND)
        
        rootSizer.AddGrowableRow(0)
        rootSizer.AddGrowableRow(1)
        rootSizer.AddGrowableRow(2)
        rootSizer.AddGrowableCol(0)
        rootSizer.AddGrowableCol(1)
        
        root.SetSizer(rootSizer)
        
class MyPanel(wx.Panel):
    def __init__(self, parent):
        super(MyPanel, self).__init__(parent)
        
class NumStratsPanel(wx.Panel):
    def __init__(self, parent):
        super(NumStratsPanel, self).__init__(parent)

        # creating widgets
        numStratsLabel1 = wx.StaticText(self, label="Number of strategies for player 1: ")
        numStratsTextCtrl1 = wx.TextCtrl(self)
        numStratsLabel2 = wx.StaticText(self, label="Number of strategies for player 2: ")
        numStratsTextCtrl2 = wx.TextCtrl(self)
        enterButton = wx.Button(self, label="Enter", size=(50, 25))
        
        # putting the widgets in the sizer
        numStratsSizer = wx.GridBagSizer(3, 3)
        numStratsSizer.Add(wx.StaticText(self, label="Numbers of Strategies"), pos=(0, 0), flag=wx.ALIGN_LEFT)
        numStratsSizer.Add(numStratsLabel1, pos=(1, 0))
        numStratsSizer.Add(numStratsTextCtrl1, pos=(1, 1))
        numStratsSizer.Add(numStratsLabel2, pos=(2, 0))
        numStratsSizer.Add(numStratsTextCtrl2, pos=(2, 1))
        numStratsSizer.Add(enterButton, pos=(1, 2))
        
        numStratsSizer.AddGrowableRow(0)
        numStratsSizer.AddGrowableRow(1)
        numStratsSizer.AddGrowableRow(2)
        numStratsSizer.AddGrowableCol(0)
        numStratsSizer.AddGrowableCol(1)
        numStratsSizer.AddGrowableCol(2)
        
        self.SetSizer(numStratsSizer)
        
class PayoffsPanel(wx.Panel):
    def __init__(self, parent):
        super(PayoffsPanel, self).__init__(parent)
        
        numStrats1 = 2
        numStrats2 = 2
        
        payoffsSizer = wx.GridBagSizer(2, 1)
        payoffsSizer.Add(wx.StaticText(self, label="Payoffs"), pos=(0, 0))
        for i in range(1, numStrats1 + 1):
            for j in range(numStrats2):
                payoffsSizer.Add(wx.TextCtrl(self), pos=(i, j))
            
        for i in range(numStrats1 + 1):
            payoffsSizer.AddGrowableRow(i)
        for j in range(numStrats2):
            payoffsSizer.AddGrowableCol(j)
        
        self.SetSizer(payoffsSizer)
    
class EquilibriaPanel(wx.Panel):
    def __init__(self, parent):
        super(EquilibriaPanel, self).__init__(parent)
        
        # Creating widgets
        labelList = ["Standard nashpy Output", "Named Strategies"]
        radiobox = wx.RadioBox(self, choices = labelList, style=wx.RA_SPECIFY_ROWS)
        equilibriaButton = wx.Button(self, label="Compute Equilibria")
        output = wx.TextCtrl(self, size=(200, 100), style=wx.TE_MULTILINE)
        
        # Putting the widgets in the sizer
        equilibriaSizer = wx.GridBagSizer(3, 2)
        equilibriaSizer.Add(wx.StaticText(self, label="Equilibria"), pos=(0, 0))
        equilibriaSizer.Add(radiobox, pos=(1, 0))
        equilibriaSizer.Add(equilibriaButton, pos=(1, 1))
        equilibriaSizer.Add(output, pos=(2, 0))
        
        equilibriaSizer.AddGrowableRow(0)
        equilibriaSizer.AddGrowableRow(1)
        equilibriaSizer.AddGrowableRow(2)
        equilibriaSizer.AddGrowableCol(0)
        equilibriaSizer.AddGrowableCol(1)
        
        self.SetSizer(equilibriaSizer)
        
class IESDSPanel(wx.Panel):
    def __init__(self, parent):
        super(IESDSPanel, self).__init__(parent)
        
        # Creating widgets
        labelList = ["Full Computation", "Computation in Steps"]
        radiobox = wx.RadioBox(self, choices = labelList, style=wx.RA_SPECIFY_ROWS)
        revertButton = wx.Button(self, label="Revert")
        iesdsButton = wx.Button(self, label="Eliminate Strictly Dominated Strategies")
        
        # Putting the widgets in the sizer
        iesdsSizer = wx.GridBagSizer(3, 2)
        iesdsSizer.Add(wx.StaticText(self, label="IESDS"), pos=(0, 0), flag=wx.ALIGN_LEFT)
        iesdsSizer.Add(radiobox, pos=(1, 0))
        iesdsSizer.Add(revertButton, pos=(1, 1))
        iesdsSizer.Add(iesdsButton, pos=(2, 0))
        
        iesdsSizer.AddGrowableRow(0)
        iesdsSizer.AddGrowableRow(1)
        iesdsSizer.AddGrowableRow(2)
        iesdsSizer.AddGrowableCol(0)
        iesdsSizer.AddGrowableCol(1)
        
        self.SetSizer(iesdsSizer)
        
        
class AxelrodPanel(wx.Panel):
    def __init__(self, parent):
        super(AxelrodPanel, self).__init__(parent)
        
        strategies = ["Alternator", "Tit For Tat"]
        
        # Creating widgets
        stratText1 = wx.StaticText(self, label="Enter a strategy for player 1; ")
        strat1Combobox = wx.ComboBox(self, choices=strategies)
        stratText2 = wx.StaticText(self, label="Enter a strategy for player 2: ")
        strat2Combobox = wx.ComboBox(self, choices=strategies)
        numTurnsText = wx.StaticText(self, label="Enter the number of turns: ")
        numTurnsTextCtrl = wx.TextCtrl(self)
        labelList = ["Add to Database", "Don't Add to Database"]
        radioButton1 = wx.RadioButton(self, label="Add to Database", style=wx.RB_GROUP)
        playMatchButton = wx.Button(self, label="Play Match")
        radioButton2 = wx.RadioButton(self, label="Don't Add to Database")
        viewDatabaseButton = wx.Button(self, label="View Database")
        matchTextCtrl = wx.TextCtrl(self)
        scoreTextCtrl = wx.TextCtrl(self)
        
        # Putting the widgets in the sizer
        axelrodSizer = wx.GridBagSizer(7, 2)
        axelrodSizer.Add(wx.StaticText(self, label="axelrod"), pos=(0, 0))
        axelrodSizer.Add(stratText1, pos=(1, 0))
        axelrodSizer.Add(strat1Combobox, pos=(1, 1))
        axelrodSizer.Add(stratText2, pos=(2, 0))
        axelrodSizer.Add(strat2Combobox, pos=(2, 1))
        axelrodSizer.Add(numTurnsText, pos=(3, 0))
        axelrodSizer.Add(numTurnsTextCtrl, pos=(3, 1))
        axelrodSizer.Add(radioButton1, pos=(4, 0))
        axelrodSizer.Add(playMatchButton, pos=(4, 1))
        axelrodSizer.Add(radioButton2, pos=(5, 0))
        axelrodSizer.Add(viewDatabaseButton, pos=(5, 1))
        axelrodSizer.Add(matchTextCtrl, pos=(6, 1))
        axelrodSizer.Add(scoreTextCtrl, pos=(7, 1))
        
        axelrodSizer.AddGrowableRow(0)
        axelrodSizer.AddGrowableRow(1)
        axelrodSizer.AddGrowableRow(2)
        axelrodSizer.AddGrowableRow(3)
        axelrodSizer.AddGrowableRow(4)
        axelrodSizer.AddGrowableRow(5)
        axelrodSizer.AddGrowableRow(6)
        axelrodSizer.AddGrowableCol(0)
        axelrodSizer.AddGrowableCol(1)
        
        self.SetSizer(axelrodSizer)
        
class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(parent=None, title="wxLinAlg")
        self.frame.Show()
        return True

app = MyApp()
app.MainLoop()