# -*- coding: utf-8 -*-
import os
import wx,wx.aui
import wx.lib.scrolledpanel as scrolled
import wx.lib.imagebrowser as ib
import lib.func as func

ID_OpenFile = wx.NewId()
ID_OpenFile_ToolBar = wx.NewId()
ID_Exit = wx.NewId()
ID_About = wx.NewId()

ID_PrintScale = wx.NewId()
ID_PreviewScale = wx.NewId()
ID_BgColour = wx.NewId()
ID_MaxColourNum = wx.NewId()
ID_MinFlossNum = wx.NewId()
ID_MixColourDist = wx.NewId()
ID_Width = wx.NewId()
ID_Height = wx.NewId()
ID_CT = wx.NewId()

ID_CropSide = wx.NewId()
ID_AntiNoise = wx.NewId()
ID_AntiBgColour = wx.NewId()
ID_OnlyPreview = wx.NewId()
ID_ForTaobao = wx.NewId()
ID_DisabledBgColour = wx.NewId()

ID_WorkPanel = wx.NewId()
ID_ImageReviewPanel = wx.NewId()
ID_ImageReview = wx.NewId()
class MainFrame(wx.Frame):
    def __init__(
            self, parent, ID, title, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE
            ):
        
        wx.Frame.__init__(self, parent, ID, title, pos, size, style)        
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        #菜单
        mb = wx.MenuBar()
        
        file_menu = wx.Menu()
        file_menu.Append(ID_OpenFile, u"打开文件")
        file_menu.AppendSeparator()
        file_menu.Append(ID_Exit, u"关闭")
        
        mb.Append(file_menu, u"文件")
        self.SetMenuBar(mb)
        #Toolbar
        toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                         wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_HORZ_TEXT)
        toolbar.SetToolBitmapSize(wx.Size(16,16))
        toolbar.AddLabelTool(ID_OpenFile_ToolBar, u"打开文件", wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN))
        toolbar.Realize()
        self._mgr.AddPane(toolbar, wx.aui.AuiPaneInfo().
                          Name("toolbar").Caption("Big Toolbar").
                          ToolbarPane().Top().
                          LeftDockable(False).RightDockable(False))
        #左部设置项目
        option_panel = scrolled.ScrolledPanel(self, -1, size=(160, 400),
                                 style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER, name="option_panel" )
        option_panel.SetBackgroundColour(wx.Colour(red=255, green=255, blue=255) )
        sizer = wx.GridBagSizer(vgap=1, hgap=1)
        
        input = wx.TextCtrl(option_panel, ID_PrintScale, "1.0", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"打印图片缩放比例")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(0,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(0,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_PreviewScale, "1.0", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"预览图片缩放比例")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(1,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(1,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_BgColour, "FFFFFF", style=wx.TE_LEFT | wx.TE_READONLY, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"背景颜色")
        input.SetMaxLength(6)
        sizer.Add(label,pos=(2,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(2,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_MaxColourNum, "50", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"最高颜色数")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(3,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(3,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_MinFlossNum, "20", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"最低颜色数")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(4,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(4,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_MixColourDist, "20", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"混合颜色距离")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(5,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(5,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_Width, "20", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"宽度")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(6,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(6,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_Height, "20", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"高度")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(7,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(7,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_CT, "20", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"CT")
        input.SetMaxLength(2)
        sizer.Add(label,pos=(8,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(8,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        checkbox = wx.CheckBox(option_panel, ID_CropSide, "")
        label = wx.StaticText(option_panel, -1, u"切除边缘空白")
        sizer.Add(label,pos=(9,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(9, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        checkbox = wx.CheckBox(option_panel, ID_AntiNoise, "")
        label = wx.StaticText(option_panel, -1, u"去除噪点")
        sizer.Add(label,pos=(10,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(10, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        checkbox = wx.CheckBox(option_panel, ID_OnlyPreview, "")
        label = wx.StaticText(option_panel, -1, u"只输出预览图片")
        sizer.Add(label,pos=(11,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(11, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        checkbox = wx.CheckBox(option_panel, ID_ForTaobao, "")
        label = wx.StaticText(option_panel, -1, u"淘宝上传图片模式")
        sizer.Add(label,pos=(12,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(12, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
                
        checkbox = wx.CheckBox(option_panel, ID_AntiBgColour, "")
        label = wx.StaticText(option_panel, -1, u"去除背景颜色")
        sizer.Add(label,pos=(13,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(13, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        checkbox = wx.CheckBox(option_panel, ID_DisabledBgColour, "")
        label = wx.StaticText(option_panel, -1, u"禁止输出背景颜色")
        sizer.Add(label,pos=(14,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(14, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
   
        option_panel.SetSizer(sizer)
        option_panel.SetupScrolling()

        self._mgr.AddPane(option_panel,
                          wx.aui.AuiPaneInfo().Name("option_panel").Caption(u"选项面板").Left()
                          .CloseButton(True).TopDockable(False).BottomDockable(False).MaximizeButton(True))
        
        #右部工作区
        work_panel = wx.Panel(self, ID_WorkPanel)
        self._mgr.AddPane(work_panel,
                          wx.aui.AuiPaneInfo().Name("work_panel").CentrePane().MaximizeButton(True))
        sizer = wx.BoxSizer(wx.VERTICAL)
        work_panel.SetSizer(sizer)
        self._mgr.Update()
        #窗口关闭
        self.Bind(wx.EVT_CLOSE, self.__CloseWindow)

    
        #绑定事件
        self.Bind(wx.EVT_MENU, self.__Exit, id=ID_Exit)
        self.Bind(wx.EVT_MENU, self.__OpenFile, id=ID_OpenFile)
        self.Bind(wx.EVT_TOOL, self.__OpenFile, id=ID_OpenFile_ToolBar)
        self.FindWindowById(ID_BgColour).Bind(wx.EVT_LEFT_DCLICK, self.__PickupColour)
        self.FindWindowById(ID_WorkPanel).Bind(wx.EVT_SIZE, self.__RereshWorkPanel)
        #定义待处理的图片数组
        self.__images = []
        
    def __RereshWorkPanel(self, event):
        '''
            工作面板改变大小
        '''
        panel = event.GetEventObject()
        obj = self.FindWindowById(ID_ImageReviewPanel)
        if obj:
            size = panel.GetVirtualSize()
            obj.SetSize(size)
            self.FindWindowById(ID_ImageReview).CentreOnParent(wx.BOTH)
            
        
    def __ValidateForm(self):
        #校验浮点数
        for id in (ID_PrintScale, ID_PreviewScale):
            obj = self.FindWindowById(id)
            if not func.IsFloat(obj.GetValue()):
                self.__ShowError(u"请输入正小数。")
                obj.SetFocus()
                obj.SetSelection(-1, -1)
                return False
        for id in (ID_MaxColourNum, ID_MinFlossNum, ID_MixColourDist, 
                   ID_Width, ID_Height, ID_CT):
            obj = self.FindWindowById(id)
            if not func.IsInt(obj.GetValue()):
                self.__ShowError(u"请输入正整数。")
                obj.SetFocus()
                obj.SetSelection(-1, -1)
                return False
        return True            
            
    def __OpenFile(self, event):
        wildcard = "All image files (*.bmp;*.gif;*.jpg;*.jpeg;*.png)|" \
                "*.bmp;*.gif;*.jpg;*.jpeg;*.png"
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.FD_PREVIEW | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            self.__images = []
            for path in dlg.GetPaths():
                self.__images.append(path)
        dlg.Destroy()
        #加载图像
        self.__LoadImage()
        
    def __PickupColour(self, event):
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            event.GetEventObject().SetValue(func.RGB2Hex(data.GetColour().Get()))
        dlg.Destroy()
            
    def __Exit(self, event):
        '''
        关闭按钮
        '''
        self.Close(True)

    def __CloseWindow(self, event):
        '''
        窗口关闭
        '''
        self.Destroy()
     
    def __ShowError(self, message):
        dlg = wx.MessageDialog(self, message, u"错误", style= wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        
    def __ShowInfo(self, message):
        dlg = wx.MessageDialog(self, message, u"信息", style= wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
    
    def __LoadImage(self, index = 0):
        '''
        读取图片
        '''
        if self.__images:
            
            work_panel = self.FindWindowById(ID_WorkPanel)
            work_panel.DestroyChildren()
            
            
            #图像预览用Panel做成
            size = work_panel.GetVirtualSize()
            panel1 = scrolled.ScrolledPanel(work_panel, ID_ImageReviewPanel, size=(size.GetWidth(),size.GetHeight()),
                                      style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
            img = wx.Image(self.__images[0])
            wx.StaticBitmap(panel1, ID_ImageReview, wx.BitmapFromImage(img)).CentreOnParent(wx.BOTH)
            panel1.Refresh()
            
            work_panel.GetSizer().Add(panel1, flag=wx.ALIGN_CENTER | wx.TOP)
            work_panel.Fit()
            
class Application(wx.App):
    def OnInit(self):
        win = MainFrame(None, -1, u"十字绣转换工具 morphinewan荣誉出品", size=(660, 550),
                  style = wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(win)
        win.Show(True)
        return True

def main():
    Application(0).MainLoop()
    
if __name__ == '__main__':
    main()