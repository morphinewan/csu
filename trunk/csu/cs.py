# -*- coding: utf-8 -*-
import os
import time
import wx,wx.aui
import wx.lib.scrolledpanel as scrolled
import wx.lib.imagebrowser as ib
import wx.lib.flatnotebook as fnb
import wx.combo
import threading
import lib.func as Common
import lib.cross_stitch as cs
from cs_definition import *

class MainFrame(wx.Frame):
    def __init__(
            self, parent, ID, title, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE
            ):
        
        wx.Frame.__init__(self, parent, ID, title, pos, size, style)        
        self.__mgr = wx.aui.AuiManager()
        self.__mgr.SetManagedWindow(self)
        #菜单
        mb = wx.MenuBar()
        
        file_menu = wx.Menu()
        file_menu.Append(ID_MenuItem_OpenFile, u"打开文件", u"导入图片文件")
        file_menu.AppendSeparator()
        file_menu.Append(ID_MenuItem_Exit, u"关闭", u"关闭并退出程序")        
        mb.Append(file_menu, u"文件")
        
        view_menu = wx.Menu()
        sub_menu = wx.Menu()
        menu_item = sub_menu.AppendCheckItem(ID_MenuItem_ShowOptionPanel, u"选项面板", u"打开或者关闭选项面板")
        menu_item = sub_menu.AppendCheckItem(ID_MenuItem_ShowLogPanel, u"日志面板", u"打开或者关闭日志面板")
        view_menu.AppendSubMenu(sub_menu, u"面板")
        mb.Append(view_menu, u"查看")
        
        self.SetMenuBar(mb)
        #Toolbar
        toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                         wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_HORZ_TEXT)
        toolbar.SetToolBitmapSize(wx.Size(16,16))
        toolbar.AddLabelTool(ID_ToolBar_OpenFile, u"打开文件", wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN))
        toolbar.AddLabelTool(ID_MenuItem_Exit, u"关闭", wx.ArtProvider_GetBitmap(wx.ART_QUIT))
        toolbar.Realize()
        self.__mgr.AddPane(toolbar, wx.aui.AuiPaneInfo().
                          Name("toolbar").Caption(u"文件").
                          ToolbarPane().Top().
                          LeftDockable(False).RightDockable(False))
        
        toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, (-1, -1), wx.TB_FLAT | wx.TB_HORIZONTAL | wx.NO_BORDER)
        toolbar.AddControl(wx.ToggleButton(toolbar, ID_ToolBar_ShowOptionPanel, u"选项面板"))
        toolbar.AddControl(wx.ToggleButton(toolbar, ID_ToolBar_ShowLogPanel, u"日志面板"))
        toolbar.Realize()
        self.__mgr.AddPane(toolbar, wx.aui.AuiPaneInfo().
                          Name("viewbar").Caption(u"查看").
                          ToolbarPane().Top().
                          LeftDockable(False).RightDockable(False).BestSize((150, 24)))
        
        toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                         wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_HORZ_TEXT)
        toolbar.AddControl(wx.StaticText(toolbar, -1, u"缩放"))
        choices = []
        for i in (10,25,50,75,100,150,200):
            choices.append("%d%%" % i)
        combo = wx.ComboBox(toolbar, ID_ToolBar_ZoomImage, value="100%",choices=choices)        
        toolbar.AddControl(combo)
        toolbar.Realize()
        combo.Enable(False)
        self.__mgr.AddPane(toolbar, wx.aui.AuiPaneInfo().
                          Name("picturebar").Caption(u"图片").
                          ToolbarPane().Top().
                          LeftDockable(False).RightDockable(False))
        #左部设置项目
        self.__option_panel = self.OptionPanel(self)
        self.__mgr.AddPane(self.__option_panel,
                          wx.aui.AuiPaneInfo().Name("option_panel").Caption(u"选项").Left()
                          .CloseButton(False).TopDockable(False).BottomDockable(False).MaximizeButton(True))
        
        #右部工作区
        self.__work_panel = self.WorkPanel(self)
        self.__mgr.AddPane(self.__work_panel,
                          wx.aui.AuiPaneInfo().Name("work_panel").CentrePane().MaximizeButton(True))
        
        #Log区
        self.__log_panel = self.LogPanel(self, size=(200, 150))
        self.__mgr.AddPane(self.__log_panel,
                          wx.aui.AuiPaneInfo().Name("log_panel").Caption(u"日志").Bottom()
                          .CloseButton(False).TopDockable(False).BottomDockable(True).MaximizeButton(True))
        
        
        self.__mgr.Update()
        #状态
        status_bar = self.CreateStatusBar(number = 1, name="statusbar")
        
        #窗口关闭
        self.Bind(wx.EVT_CLOSE, self.OnWindowClose)
    
        #绑定事件
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_MenuItem_Exit)
        self.Bind(wx.EVT_MENU, self.OnFileOpen, id=ID_MenuItem_OpenFile)
        self.Bind(wx.EVT_MENU, self.OnMenuClick, id=ID_MenuItem_ShowOptionPanel)
        self.Bind(wx.EVT_MENU, self.OnMenuClick, id=ID_MenuItem_ShowLogPanel)
        
        self.Bind(wx.EVT_TOOL, self.OnFileOpen, id=ID_ToolBar_OpenFile)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnMenuClick, id=ID_ToolBar_ShowOptionPanel)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnMenuClick, id=ID_ToolBar_ShowLogPanel)
        
        self.Bind(wx.EVT_TEXT_ENTER, self.OnImageZoom, id=ID_ToolBar_ZoomImage)
        self.Bind(wx.EVT_COMBOBOX, self.OnImageZoom, id=ID_ToolBar_ZoomImage)
        
        
        #定义待处理的图片数组
        self.__cs = []
        
        #加载系统配置信息
        global Application_Settings
        Application_Settings = Common.LoadFromDisk(Common.GetAppPath() + "\AppSetting.dat")
        
        #异步加载配置信息
        self.__log_panel.Log(u"异步读取绣线色彩映射表设定")
        self.__flossmap = cs.FlossMap()
        threading.Thread(target=self.__flossmap.Load, args=(self.__CallbackFlossMapLoad,)).start()
        #初始化界面
        self.__InitLayout()
        
    def OnImageZoom(self, event):
        '''
        缩放图片
        '''
        value = event.GetEventObject().GetValue()
        value = value.replace('%', '')
        try:
            value = float(value)
        except:
            value = 100
            event.GetEventObject().SetValue('100%')
        scale = value / 100        
#        self.__work_panel.AppendImage(self.__cs[0].GetSourceImage(), u"原图", scale)
        
    def OnMenuClick(self, event):
        '''
        菜单相应事件
        '''
        if event.GetId() == ID_MenuItem_ShowOptionPanel:
            item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowOptionPanel)           
            self.FindWindowById(ID_ToolBar_ShowOptionPanel).SetValue(item.IsChecked())
            self.__mgr.GetPane("option_panel").Show(show=item.IsChecked())
            self.__mgr.Update()
        elif event.GetId() == ID_ToolBar_ShowOptionPanel:
            item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowOptionPanel)
            item.Check(self.FindWindowById(ID_ToolBar_ShowOptionPanel).GetValue())
            self.__mgr.GetPane("option_panel").Show(show=item.IsChecked())
            self.__mgr.Update() 
        elif event.GetId() == ID_MenuItem_ShowLogPanel:
            item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowLogPanel)           
            self.FindWindowById(ID_ToolBar_ShowLogPanel).SetValue(item.IsChecked())
            self.__mgr.GetPane("log_panel").Show(show=item.IsChecked())
            self.__mgr.Update()
        elif event.GetId() == ID_ToolBar_ShowLogPanel:
            item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowLogPanel)
            item.Check(self.FindWindowById(ID_ToolBar_ShowLogPanel).GetValue())
            self.__mgr.GetPane("log_panel").Show(show=item.IsChecked())
            self.__mgr.Update()
        
    def OnFileOpen(self, event):
        '''
        打开文件
        '''
        wildcard = "All image files (*.bmp;*.gif;*.jpg;*.jpeg;*.png)|" \
                "*.bmp;*.gif;*.jpg;*.jpeg;*.png"
        dd = os.getcwd()
        global Application_Settings
        if Application_Settings.has_key("Default_Directory"):
            dd = Application_Settings["Default_Directory"]
        dlg = wx.FileDialog(
            self, message=u"选择文件",
            defaultDir=dd,
            wildcard=wildcard,
            style=wx.OPEN | wx.FD_PREVIEW | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            self.__cs = []
            for path in dlg.GetPaths():
                self.__cs.append(cs.CrossStitch(path))
            Application_Settings["Default_Directory"] = Common.GetPathName(self.__cs[0].GetSourceImageFileName())
            #加载图像
            if self.__cs:
                self.__work_panel.Clear()
                self.FindWindowById(ID_ToolBar_ZoomImage).SetValue('100%')
                self.FindWindowById(ID_ToolBar_ZoomImage).Enable(True)
                self.__work_panel.BoundCrossStitch(self.__cs[0])
        dlg.Destroy()
        
        
            
    def OnExit(self, event):
        '''
        关闭按钮
        '''
        self.Close(True)

    def OnWindowClose(self, event):
        '''
        窗口关闭
        '''
        #保存系统设置
        Common.SaveToDisk(Application_Settings, Common.GetAppPath() + "\AppSetting.dat")
        self.Destroy()
        
    def __InitLayout(self):
        self.__mgr.GetPane("option_panel").Show()
        item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowOptionPanel)
        item.Check(1)
        self.FindWindowById(ID_ToolBar_ShowOptionPanel).SetValue(1)
        
        self.__mgr.GetPane("log_panel").Hide()
        item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowLogPanel)
        item.Check(0)
        self.FindWindowById(ID_ToolBar_ShowLogPanel).SetValue(0)
        self.__mgr.Update()
        
        #设置图标        
        self.SetIcon(wx.Icon("%s/favicon.ico" % Common.GetAppPath(), wx.BITMAP_TYPE_ICO))
        
    def __ShowError(self, message):
        dlg = wx.MessageDialog(self, message, u"错误", style= wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        
    def __ShowInfo(self, message):
        dlg = wx.MessageDialog(self, message, u"信息", style= wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
   
    def __CallbackFlossMapLoad(self):
        self.__log_panel.Log(u"异步读取绣线色彩映射表设定已经完成")
    
    def __ValidateForm(self):
        #校验浮点数
        for id in (ID_Option_PrintScale, ID_Option_PreviewScale):
            obj = self.FindWindowById(id)
            if not Common.IsFloat(obj.GetValue()):
                self.__ShowError(u"请输入正小数。")
                obj.SetFocus()
                obj.SetSelection(-1, -1)
                return False
        for id in (ID_Option_MaxColourNum, ID_Option_MinFlossNum, ID_Option_MixColourDist, 
                   ID_Option_Width, ID_Option_Height, ID_Option_CT):
            obj = self.FindWindowById(id)
            if not Common.IsInt(obj.GetValue()):
                self.__ShowError(u"请输入正整数。")
                obj.SetFocus()
                obj.SetSelection(-1, -1)
                return False
        return True
    
    class WorkPanel(wx.Panel):
        '''
        工作面板
        '''
        def __init__(self, parent):
            wx.Panel.__init__(self, parent, ID_Panel_Work)
            self.__nb = fnb.FlatNotebook(self, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_NO_NAV_BUTTONS \
                                         | fnb.FNB_FF2 | fnb.FNB_HIDE_ON_SINGLE_TAB)
            self.__nb.Hide()
            sizer = wx.BoxSizer()
            sizer.Add(self.__nb, 0, wx.EXPAND)
            self.SetSizer(sizer)
            self.Bind(wx.EVT_SIZE, self.OnResize)
            self.__cs = None
            
        def OnResize(self, event):
            '''
                工作面板改变大小
            '''
            self.__nb.SetSize(self.GetSize())
          
        def Clear(self):
            self.__nb.DeleteAllPages()
            if self.__cs:
                self.__cs.Destroy()
            del self.__cs
            
        def BoundCrossStitch(self, cs):
            '''
            绑定CS
            '''
            self.__cs = cs
            self.__AppendImage(self.__cs.GetSourceImage(), u"原图")
            
        def __AppendImage(self, img, name, scale=None):
            preview_panel = scrolled.ScrolledPanel(self, ID_Panel_Work_ImageReview, size=self.GetSize(),
                                 style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
            sizer = wx.GridSizer(1, 1)
            if scale:
                img = img.Scale(int(img.GetSize()[0] * scale), int(img.GetSize()[1] * scale))
            sb = wx.StaticBitmap(preview_panel, -1, wx.BitmapFromImage(img), size=img.GetSize())
            sb.Bind(wx.EVT_LEFT_DOWN, self.OnImageFocus)
            sb.SetFocus()
            sizer.Add(sb, flag=wx.ALIGN_CENTER | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
            preview_panel.SetSizer(sizer)
            preview_panel.SetAutoLayout(1)
            preview_panel.SetupScrolling()

            self.__nb.AddPage(preview_panel, name, select=True)
            self.__nb.Show()
                
        def OnImageFocus(self, event):
            '''
            点击图片后聚焦到工作区，以相应鼠标滚轮事件
            '''
            event.GetEventObject().SetFocus()
        
        def HasPage(self):
            '''
            是否有图片显示
            '''
            return self.__nb.GetPageCount > 0
            
    class OptionPanel(wx.Panel):
        '''
        选项面板
        '''
        def __init__(self, parent):
            wx.Panel.__init__(self, parent, ID_Panel_Option, size=(160, 400),
                                 style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER, name="option_panel")
            self.SetBackgroundColour(wx.Colour(red=255, green=255, blue=255))
            sizer = wx.GridBagSizer(vgap=1, hgap=1)
            
            input = wx.TextCtrl(self, ID_Option_PrintScale, "1.0", style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"打印图片缩放比例")
            input.SetMaxLength(3)
            sizer.Add(label,pos=(0,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(0,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_PreviewScale, "1.0", style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"预览图片缩放比例")
            input.SetMaxLength(3)
            sizer.Add(label,pos=(1,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(1,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_BgColour, "FFFFFF", style=wx.TE_LEFT | wx.TE_READONLY, size=(45,20))
            label = wx.StaticText(self, -1, u"背景颜色")
            input.SetMaxLength(6)
            sizer.Add(label,pos=(2,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(2,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_MaxColourNum, "50", style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"最高颜色数")
            input.SetMaxLength(3)
            sizer.Add(label,pos=(3,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(3,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_MinFlossNum, "20", style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"最低颜色数")
            input.SetMaxLength(3)
            sizer.Add(label,pos=(4,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(4,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_MixColourDist, "20", style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"混合颜色距离")
            input.SetMaxLength(3)
            sizer.Add(label,pos=(5,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(5,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_Width, "20", style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"宽度")
            input.SetMaxLength(3)
            sizer.Add(label,pos=(6,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(6,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_Height, "20", style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"高度")
            input.SetMaxLength(3)
            sizer.Add(label,pos=(7,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(7,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_CT, "20", style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"CT")
            input.SetMaxLength(2)
            sizer.Add(label,pos=(8,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(8,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            checkbox = wx.CheckBox(self, ID_Option_CropSide, "")
            label = wx.StaticText(self, -1, u"切除边缘空白")
            sizer.Add(label,pos=(9,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(checkbox, pos=(9, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            checkbox = wx.CheckBox(self, ID_Option_AntiNoise, "")
            label = wx.StaticText(self, -1, u"去除噪点")
            sizer.Add(label,pos=(10,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(checkbox, pos=(10, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            checkbox = wx.CheckBox(self, ID_Option_OnlyPreview, "")
            label = wx.StaticText(self, -1, u"只输出预览图片")
            sizer.Add(label,pos=(11,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(checkbox, pos=(11, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            checkbox = wx.CheckBox(self, ID_Option_ForTaobao, "")
            label = wx.StaticText(self, -1, u"淘宝上传图片模式")
            sizer.Add(label,pos=(12,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(checkbox, pos=(12, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
                    
            checkbox = wx.CheckBox(self, ID_Option_AntiBgColour, "")
            label = wx.StaticText(self, -1, u"去除背景颜色")
            sizer.Add(label,pos=(13,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(checkbox, pos=(13, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            checkbox = wx.CheckBox(self, ID_Option_DisabledBgColour, "")
            label = wx.StaticText(self, -1, u"禁止输出背景颜色")
            sizer.Add(label,pos=(14,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(checkbox, pos=(14, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
       
            self.SetSizer(sizer)
            
            self.FindWindowById(ID_Option_BgColour).Bind(wx.EVT_LEFT_DCLICK, self.OnColourPickup)
            
        def OnColourPickup(self, event):
            '''
            选择颜色
            '''
            dlg = wx.ColourDialog(self)
            dlg.GetColourData().SetChooseFull(True)
            dlg.GetColourData().SetColour(Common.Hex2Colour(event.GetEventObject().GetValue()))
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.GetColourData()
                event.GetEventObject().SetValue(Common.RGB2Hex(data.GetColour().Get()))
            dlg.Destroy()
            
    class LogPanel(wx.Panel, cs.Logger):
        '''
        日志面板
        '''
        def __init__(self, parent, size=(-1, -1)):
            wx.Panel.__init__(self, parent, ID_Panel_Log, size=size)          
            self.log = wx.TextCtrl(self, -1,
                        "",
                       size=self.GetSize(), style=wx.TE_MULTILINE|wx.TE_READONLY)    
            bsizer = wx.BoxSizer(wx.VERTICAL)
            bsizer.Add(self.log, 0, wx.GROW|wx.ALL)
            self.SetSizer(bsizer)
            self.SetAutoLayout(True)
            self.Bind(wx.EVT_SIZE, self.__OnResize)
            
        def __OnResize(self, event):
            self.log.SetSize(self.GetSize())
        
        def Log(self, content):
            self.log.AppendText("%s %s\n" % (time.strftime('%Y-%m-%d %X', time.localtime()), content))
        
        def Clear(self):
            self.log.ChangeValue("")
            
class Application(wx.App):
    def OnInit(self):
        win = MainFrame(None, -1, u"十字绣转换工具 morphinewan荣誉出品", size=(800, 600),
                  style = wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(win)
        win.CenterOnScreen(1)
        win.Show(True)
        return True

def main():
    Application(0).MainLoop()
    
if __name__ == '__main__':
    main()