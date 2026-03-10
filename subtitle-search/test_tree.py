import sys
sys.path.append("/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules")
import DaVinciResolveScript as dvr_script
resolve = dvr_script.scriptapp("Resolve")
fusion = resolve.Fusion()
ui = fusion.UIManager
dispatcher = dvr_script.UIDispatcher(ui)

layout = ui.VGroup([
    ui.Tree({"ID": "MyTree", "Weight": 1})
])

win = dispatcher.AddWindow({"ID": "Win"}, layout)
tree = win.GetItems()["MyTree"]
tree.ColumnCount = 2
row = tree.NewItem()
row["Text"][0] = "1"
row["Text"][1] = "Click Me"
tree.AddTopLevelItem(row)

def OnItemClicked(ev):
    print("ItemClicked", ev)
    win.Hide()
    dispatcher.ExitLoop()

def OnItemDoubleClicked(ev):
    print("ItemDoubleClicked", ev)
    win.Hide()
    dispatcher.ExitLoop()

win.On.MyTree.ItemClicked = OnItemClicked
win.On.MyTree.ItemDoubleClicked = OnItemDoubleClicked

win.Show()
dispatcher.RunLoop()
