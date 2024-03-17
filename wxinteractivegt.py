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
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(wx.StaticText(self, label="Payoffs"))
        
class EquilibriaPanel(wx.Panel):
    def __init__(self, parent):
        super(EquilibriaPanel, self).__init__(parent)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(wx.StaticText(self, label="Equilibria"))
        
class IESDSPanel(wx.Panel):
    def __init__(self, parent):
        super(IESDSPanel, self).__init__(parent)
        
        # creating widgets
        labelList = ["Full Computation", "Computation in Steps"]
        radiobox = wx.RadioBox(self, choices = labelList, style=wx.RA_SPECIFY_ROWS)
        revertButton = wx.Button(self, label="Revert")
        iesdsButton = wx.Button(self, label="Eliminate Strictly Dominated Strategies")
        
        # putting the widgets in the sizer
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
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(wx.StaticText(self, label="axelrod"))
        
class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(parent=None, title="wxLinAlg")
        self.frame.Show()
        return True

app = MyApp()
app.MainLoop()