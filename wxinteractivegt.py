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
        
        numStratsLabel1 = wx.StaticText(self, label="Number of strategies for player 1: ")
        # numStratsEntry1 = wx.TextEntry()
        numStratsLabel2 = wx.StaticText(self, label="Number of strategies for player 2: ")
        # numStratsEntry2 = wx.TextEntry()
        
        numStratsSizer = wx.GridBagSizer(2, 2)
        numStratsSizer.Add(numStratsLabel1, pos=(0, 0), flag=wx.EXPAND)
        # numStratsSizer.Add(numStratsEntry1, pos=(0, 1), flag=wx.EXPAND)
        numStratsSizer.Add(numStratsLabel2, pos=(1, 0), flag=wx.EXPAND)
        # numStratsSizer.Add(numStratsEntry2, pos=(1, 1), flag=wx.EXPAND)
        
        numStratsSizer.AddGrowableRow(0)
        numStratsSizer.AddGrowableRow(1)
        numStratsSizer.AddGrowableCol(0)
        # numStratsSizer.AddGrowableCol(1)
        
        self.SetSizer(numStratsSizer)
        
class PayoffsPanel(wx.Panel):
    def __init__(self, parent):
        super(PayoffsPanel, self).__init__(parent)
        
        label = wx.StaticText(self, label="2")
        
class EquilibriaPanel(wx.Panel):
    def __init__(self, parent):
        super(EquilibriaPanel, self).__init__(parent)
        
        label = wx.StaticText(self, label="3")
        
class IESDSPanel(wx.Panel):
    def __init__(self, parent):
        super(IESDSPanel, self).__init__(parent)
        
        label = wx.StaticText(self, label="4")
        
class AxelrodPanel(wx.Panel):
    def __init__(self, parent):
        super(AxelrodPanel, self).__init__(parent)
        
        label = wx.StaticText(self, label="5")
        
class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(parent=None, title="wxLinAlg")
        self.frame.Show()
        return True

app = MyApp()
app.MainLoop()