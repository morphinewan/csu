# -*- coding: utf-8 -*-
import os
import wx,wx.aui
import wx.lib.scrolledpanel as scrolled
import wx.lib.imagebrowser as ib
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
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
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
        menu_item.Check(1)
        view_menu.AppendSubMenu(sub_menu, u"面板")
        mb.Append(view_menu, u"查看")
        
        self.Bind(wx.EVT_MENU, self.__MenuClick, id=ID_MenuItem_ShowOptionPanel)
        
        self.SetMenuBar(mb)
        #Toolbar
        toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                         wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_HORZ_TEXT)
        toolbar.SetToolBitmapSize(wx.Size(16,16))
        toolbar.AddLabelTool(ID_ToolBar_OpenFile, u"打开文件", wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN))
        toolbar.AddLabelTool(ID_MenuItem_Exit, u"关闭", wx.ArtProvider_GetBitmap(wx.ART_QUIT))
        toolbar.Realize()
        self._mgr.AddPane(toolbar, wx.aui.AuiPaneInfo().
                          Name("toolbar").Caption(u"文件").
                          ToolbarPane().Top().
                          LeftDockable(False).RightDockable(False))
        
        toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                         wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_HORZ_TEXT)
        toolbar.SetToolBitmapSize(wx.Size(16,16))
        toolbar.AddLabelTool(ID_ToolBar_ShowOptionPanel, u"隐藏选项面板", wx.ArtProvider_GetBitmap(wx.ART_FOLDER))
        toolbar.Realize()
        self._mgr.AddPane(toolbar, wx.aui.AuiPaneInfo().
                          Name("viewbar").Caption(u"查看").
                          ToolbarPane().Top().
                          LeftDockable(False).RightDockable(False))
        
        toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                         wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_HORZ_TEXT)
        toolbar.AddControl(wx.StaticText(toolbar, -1, u"缩放"))
        choices = []
        for i in range(10, 210, 10):
            choices.append("%d%%" % i)
        combo = wx.ComboBox(toolbar, ID_ToolBar_ZoomImage, value="100%",choices=choices)        
        toolbar.AddControl(combo)
        toolbar.Realize()
        combo.Enable(False)
        self._mgr.AddPane(toolbar, wx.aui.AuiPaneInfo().
                          Name("picturebar").Caption(u"图片").
                          ToolbarPane().Top().
                          LeftDockable(False).RightDockable(False))
        #左部设置项目
        option_panel = wx.Panel(self, ID_Panel_Option, size=(160, 400),
                                 style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER, name="option_panel" )
        option_panel.SetBackgroundColour(wx.Colour(red=255, green=255, blue=255) )
        sizer = wx.GridBagSizer(vgap=1, hgap=1)
        
        input = wx.TextCtrl(option_panel, ID_Option_PrintScale, "1.0", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"打印图片缩放比例")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(0,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(0,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_Option_PreviewScale, "1.0", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"预览图片缩放比例")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(1,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(1,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_Option_BgColour, "FFFFFF", style=wx.TE_LEFT | wx.TE_READONLY, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"背景颜色")
        input.SetMaxLength(6)
        sizer.Add(label,pos=(2,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(2,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_Option_MaxColourNum, "50", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"最高颜色数")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(3,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(3,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_Option_MinFlossNum, "20", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"最低颜色数")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(4,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(4,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_Option_MixColourDist, "20", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"混合颜色距离")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(5,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(5,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_Option_Width, "20", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"宽度")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(6,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(6,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_Option_Height, "20", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"高度")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(7,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(7,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_Option_CT, "20", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"CT")
        input.SetMaxLength(2)
        sizer.Add(label,pos=(8,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(8,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        checkbox = wx.CheckBox(option_panel, ID_Option_CropSide, "")
        label = wx.StaticText(option_panel, -1, u"切除边缘空白")
        sizer.Add(label,pos=(9,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(9, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        checkbox = wx.CheckBox(option_panel, ID_Option_AntiNoise, "")
        label = wx.StaticText(option_panel, -1, u"去除噪点")
        sizer.Add(label,pos=(10,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(10, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        checkbox = wx.CheckBox(option_panel, ID_Option_OnlyPreview, "")
        label = wx.StaticText(option_panel, -1, u"只输出预览图片")
        sizer.Add(label,pos=(11,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(11, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        checkbox = wx.CheckBox(option_panel, ID_Option_ForTaobao, "")
        label = wx.StaticText(option_panel, -1, u"淘宝上传图片模式")
        sizer.Add(label,pos=(12,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(12, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
                
        checkbox = wx.CheckBox(option_panel, ID_Option_AntiBgColour, "")
        label = wx.StaticText(option_panel, -1, u"去除背景颜色")
        sizer.Add(label,pos=(13,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(13, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        checkbox = wx.CheckBox(option_panel, ID_Option_DisabledBgColour, "")
        label = wx.StaticText(option_panel, -1, u"禁止输出背景颜色")
        sizer.Add(label,pos=(14,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(14, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
   
        option_panel.SetSizer(sizer)

        self._mgr.AddPane(option_panel,
                          wx.aui.AuiPaneInfo().Name("option_panel").Caption(u"选项").Left()
                          .CloseButton(False).TopDockable(False).BottomDockable(False).MaximizeButton(True))
        
        #右部工作区
        work_panel = wx.Panel(self, ID_Panel_Work)
        self._mgr.AddPane(work_panel,
                          wx.aui.AuiPaneInfo().Name("work_panel").CentrePane().MaximizeButton(True))
        
        self._mgr.Update()
        
        #Log区
        log_panel = wx.Panel(self, )
        
        #状态
        status_bar = self.CreateStatusBar(number = 1, name="statusbar")
        
        #窗口关闭
        self.Bind(wx.EVT_CLOSE, self.__CloseWindow)
    
        #绑定事件
        self.Bind(wx.EVT_MENU, self.__Exit, id=ID_MenuItem_Exit)
        self.Bind(wx.EVT_MENU, self.__OpenFile, id=ID_MenuItem_OpenFile)
        self.Bind(wx.EVT_TOOL, self.__OpenFile, id=ID_ToolBar_OpenFile)
        self.Bind(wx.EVT_TOOL, self.__MenuClick, id=ID_ToolBar_ShowOptionPanel)
        self.Bind(wx.EVT_TEXT_ENTER, self.__ZoomImage, id=ID_ToolBar_ZoomImage)
        self.Bind(wx.EVT_COMBOBOX, self.__ZoomImage, id=ID_ToolBar_ZoomImage)
        self.FindWindowById(ID_Option_BgColour).Bind(wx.EVT_LEFT_DCLICK, self.__PickupColour)
        self.FindWindowById(ID_Panel_Work).Bind(wx.EVT_SIZE, self.__RereshWorkPanel)
        #定义待处理的图片数组
        self.__images = []
        
        #加载系统配置信息
        global Application_Settings
        Application_Settings = Common.LoadFromDisk(Common.GetAppPath() + "\AppSetting.dat")
        
        #异步加载配置信息
        self.FindWindowByName("statusbar").SetStatusText(u"异步读取绣线色彩映射表设定", 0)
        self.__flossmap = cs.FlossMap()
        threading.Thread(target=self.__flossmap.Load, args=(self.__FlossMapLoadCallback,)).start()
        
    def __FlossMapLoadCallback(self):
        self.FindWindowByName("statusbar").SetStatusText(u"异步读取绣线色彩映射表设定已经完成", 0)
        
    def __ZoomImage(self, event):
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
        self.__LoadImage(scale=scale)
        if self.FindWindowById(ID_Panel_Work_ImageReview):
            self.FindWindowById(ID_Panel_Work_ImageReview).SetFocus()
        
    def __MenuClick(self, event):
        '''
        菜单相应事件
        '''
        print event.GetId()
        if event.GetId() == ID_MenuItem_ShowOptionPanel:
            item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowOptionPanel)
            self._mgr.GetPane("option_panel").Show(show=item.IsChecked())
            self._mgr.Update()
        elif event.GetId() == ID_ToolBar_ShowOptionPanel:
            item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowOptionPanel)
            item.Check(not item.IsChecked())
            self._mgr.GetPane("option_panel").Show(show=item.IsChecked())
            self._mgr.Update()
            if item.IsChecked():
                event.GetEventObject().FindById(ID_ToolBar_ShowOptionPanel).SetLabel(u"隐藏选项面板")
            else:
                event.GetEventObject().FindById(ID_ToolBar_ShowOptionPanel).SetLabel(u"显示选项面板")
            event.GetEventObject().Realize()
            self._mgr.Update()
    def __RereshWorkPanel(self, event):
        '''
            工作面板改变大小
        '''
        if self.FindWindowById(ID_Panel_Work_ImageReview) and self.FindWindowById(ID_Panel_Work):
            self.FindWindowById(ID_Panel_Work_ImageReview).SetSize(self.FindWindowById(ID_Panel_Work).GetSize())
        
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
            
    def __OpenFile(self, event):
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
            self.__images = []
            for path in dlg.GetPaths():
                self.__images.append(path)
            Application_Settings["Default_Directory"] = Common.GetPathName(self.__images[0])
        dlg.Destroy()
        #加载图像
        self.__LoadImage()
        
    def __PickupColour(self, event):
        '''
        选择颜色
        '''
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            event.GetEventObject().SetValue(Common.RGB2Hex(data.GetColour().Get()))
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
        #保存系统设置
        Common.SaveToDisk(Application_Settings, Common.GetAppPath() + "\AppSetting.dat")
        self.Destroy()
     
    def __ShowError(self, message):
        dlg = wx.MessageDialog(self, message, u"错误", style= wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        
    def __ShowInfo(self, message):
        dlg = wx.MessageDialog(self, message, u"信息", style= wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
    
    def __LoadImage(self, index = 0, scale = None):
        '''
        读取图片
        '''
        if self.__images:
            self.FindWindowById(ID_ToolBar_ZoomImage).SetValue('100%')
            self.FindWindowById(ID_ToolBar_ZoomImage).Enable(True)
            self.__ShowImage(wx.Image(self.__images[index]), scale)
            
    def __ShowImage(self, img, scale = None):
        '''
        将图片显示在工作区
        '''
        work_panel = self.FindWindowById(ID_Panel_Work)
        work_panel.DestroyChildren()
        panel1 = scrolled.ScrolledPanel(work_panel, ID_Panel_Work_ImageReview, size=work_panel.GetSize(),
                             style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER, name="panel1" )
        sizer = wx.GridSizer(1, 1)
        if scale:
            img = img.Scale(int(img.GetSize()[0] * scale), int(img.GetSize()[1] * scale))
        sb = wx.StaticBitmap(panel1, -1, wx.BitmapFromImage(img), size=img.GetSize())
        sb.Bind(wx.EVT_LEFT_DOWN, self.__FocusImage)
        sizer.Add(sb, flag=wx.ALIGN_CENTER | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
        panel1.SetSizer(sizer)
        panel1.SetAutoLayout(1)
        panel1.SetupScrolling()
        self.FindWindowById(ID_Panel_Work_ImageReview).SetFocus()
    
    def __FocusImage(self, event):
        '''
        点击图片后聚焦到工作区，以相应鼠标滚轮事件
        '''
        self.FindWindowById(ID_Panel_Work).SetFocus()
   
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