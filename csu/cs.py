# -*- coding: utf-8 -*-
import os
import time
import math
import wx,wx.aui
import wx.combo
import wx.lib.scrolledpanel as scrolled
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
        toolbar.SetToolBitmapSize(wx.Size(16,16))
        toolbar.AddControl(wx.StaticText(toolbar, -1, u"缩放"))
        choices = []
        for i in (10,25,50,75,100,150,200):
            choices.append("%d%%" % i)
        combo = wx.ComboBox(toolbar, ID_ToolBar_ZoomImage, value="100%",choices=choices)        
        toolbar.AddControl(combo)
        
        #添加spinbutton
        spinbutton = wx.SpinButton(toolbar, ID_ToolBar_ZoomImageSpin, style=wx.SP_VERTICAL)
        toolbar.AddControl(spinbutton)
        
        #添加自定义Button
        toolbar.AddControl(wx.Button(toolbar, ID_ToolBar_GeneratePreview, u"预览"))
        toolbar.Realize()
        
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
        self.__status_bar = self.CreateStatusBar(number = 1, name="statusbar")
        
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
        self.Bind(wx.EVT_BUTTON , self.OnGeneratePreview, id=ID_ToolBar_GeneratePreview)
        
        
        self.Bind(wx.EVT_TEXT_ENTER, self.OnImageZoom, id=ID_ToolBar_ZoomImage)
        self.Bind(wx.EVT_COMBOBOX, self.OnImageZoom, id=ID_ToolBar_ZoomImage)
        self.Bind(wx.EVT_SPIN_UP, self.OnImageZoomSpinUp, id=ID_ToolBar_ZoomImageSpin)
        self.Bind(wx.EVT_SPIN_DOWN, self.OnImageZoomSpinDown, id=ID_ToolBar_ZoomImageSpin)
        
        self.Bind(cs.EVT_UPDATE_CROSS_STITCH, self.OnCrossStitchUpdate)
        #定义待处理的图片数组
        self.__cs = []
        
        #加载系统配置信息
        global Application_Settings
        Application_Settings = Common.LoadFromDisk(Common.GetAppPath() + "/appsetting.dat")
        if not Application_Settings:
            Application_Settings = {}
        
        #异步加载配置信息
        self.__log_panel.Log(u"异步读取绣线色彩映射表设定")
        self.__flossmap = cs.FlossMap()
        threading.Thread(target=self.__flossmap.Load, args=(self.__CallbackFlossMapLoad,)).start()
        #初始化界面
        self.__InitLayout()
    
    def OnImageZoomSpinUp(self, event):
        value = self.FindWindowById(ID_ToolBar_ZoomImage).GetValue()
        value = value.replace('%', '')        
        try:
            value = int(value)            
        except:
            value = 100
        value += int(math.ceil(value * 0.5))            
        self.FindWindowById(ID_ToolBar_ZoomImage).SetValue('%d%%' % value)
        scale = float(value) / 100
        self.__work_panel.Scale(scale)
    
    def OnImageZoomSpinDown(self, event):
        value = self.FindWindowById(ID_ToolBar_ZoomImage).GetValue()
        value = value.replace('%', '')        
        try:
            value = int(value)            
        except:
            value = 100
        value -= int(math.ceil(value * 0.5))
        if value > 10:
            self.FindWindowById(ID_ToolBar_ZoomImage).SetValue('%d%%' % value)
            scale = float(value) / 100
            self.__work_panel.Scale(scale)
        
    def OnGeneratePreview(self, event):
        '''
        预览图片
        '''
        if self.__option_panel.ValidateData():
            self.FindWindowById(ID_ToolBar_ZoomImage).SetValue("100%")
            self.__EnableImageTool(0)
            threading.Thread(target=self.__cs[0].GeneratePreviewImage, args=(self.__option_panel.GetProperties(),)).start()
        
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
        self.__work_panel.Scale(scale)
        
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
                cs1 = cs.CrossStitch(path, self.__log_panel, self.__flossmap, self)
                self.__cs.append(cs1)
            Application_Settings["Default_Directory"] = Common.GetPathName(self.__cs[0].GetSourceImageFileName())
            #加载图像
            if self.__cs:
                self.__work_panel.Clear()
                self.FindWindowById(ID_ToolBar_ZoomImage).SetValue('100%')
                self.__EnableImageTool(1)
                self.__work_panel.ShowImage(self.__cs[0].GetSourceImage())
        dlg.Destroy()
    
    def __EnableImageTool(self, flg):
        self.FindWindowById(ID_ToolBar_ZoomImage).Enable(flg)
        self.FindWindowById(ID_ToolBar_ZoomImageSpin).Enable(flg)
        self.FindWindowById(ID_ToolBar_GeneratePreview).Enable(flg)
    
    def OnCrossStitchUpdate(self, event):
        if event.type ==  cs.EVENT_PREVIEW_GENERATED:
            self.__EnableImageTool(1)
            self.__status_bar.SetStatusText(u"预览图转换完成")
            self.__work_panel.ShowImage(self.__cs[0].GetPreviewImage())
        elif event.type == cs.EVENT_PREVIEW_GENERATING:
            per = float(event.pos) * 100 / (event.max - event.min)
            self.__status_bar.SetStatusText(u"进度%0.1f%%" % per, 0)
        
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
        Common.SaveToDisk(Application_Settings, Common.GetAppPath() + "/appsetting.dat")
        Common.SaveToDisk(self.__option_panel.GetProperties(), Common.GetAppPath() + "/options.dat")
        self.Destroy()
        
    def __InitLayout(self):
        self.__mgr.GetPane("option_panel").Show()
        item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowOptionPanel)
        item.Check(1)
        self.FindWindowById(ID_ToolBar_ShowOptionPanel).SetValue(1)
        
        self.__mgr.GetPane("log_panel").Show()
        item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowLogPanel)
        item.Check(1)
        self.FindWindowById(ID_ToolBar_ShowLogPanel).SetValue(1)
        self.__mgr.Update()
        
        self.__EnableImageTool(0)
        #设置图标        
        self.SetIcon(IMAGE_APP_ICON.GetIcon())
   
    def __CallbackFlossMapLoad(self):
        self.__log_panel.Log(u"异步读取绣线色彩映射表设定已经完成")
    
    class WorkPanel(wx.Panel):
        '''
        工作面板
        '''
        def __init__(self, parent):
            wx.Panel.__init__(self, parent, ID_Panel_Work)
            self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
            self.Bind(wx.EVT_SIZE, self.OnResize)
            self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
         
        def OnLeftDown(self, event):
            self.SetFocus()
            
        def OnMouseWheel(self, event):
            if self.FindWindowById(ID_Panel_Work_ImageReview):
                self.FindWindowById(ID_Panel_Work_ImageReview).GetEventHandler().ProcessEvent(event) 
        
        def OnResize(self, event):
            if self.FindWindowById(ID_Panel_Work_ImageReview):
                self.FindWindowById(ID_Panel_Work_ImageReview).SetSize(self.GetSize())
                self.SetFocus()
        
        def Clear(self):
            self.__cs = None
            self.__current_image = None
            self.DestroyChildren()
            
        def ShowImage(self, image):
            preview_panel = self.FindWindowById(ID_Panel_Work_ImageReview)
            if preview_panel:
                preview_panel.DestroyChildren()
            else:                           
                preview_panel = scrolled.ScrolledPanel(self, ID_Panel_Work_ImageReview, size=self.GetSize())
            sizer = wx.GridSizer(1, 1)
            sb = wx.StaticBitmap(preview_panel, -1, wx.BitmapFromImage(image), size=image.GetSize())
            sizer.Add(sb, flag=wx.ALIGN_CENTER | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
            preview_panel.SetSizer(sizer)
            preview_panel.SetAutoLayout(1)
            preview_panel.SetupScrolling()
            sb.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
            self.__current_image = image
            self.SetFocus()
            
#        def BoundCrossStitch(self, cs):
#            '''
#            绑定CS
#            '''
#            self.__cs = cs
#            self.ShowSourceImage()
#            
#            
#        def ShowSourceImage(self):
#            preview_panel = scrolled.ScrolledPanel(self, ID_Panel_Work_ImageReview, size=self.GetSize())
#            sizer = wx.GridSizer(1, 1)
#            sb = wx.StaticBitmap(preview_panel, -1, wx.BitmapFromImage(self.__cs.GetSourceImage()), size=self.__cs.GetSourceImage().GetSize())
#            sizer.Add(sb, flag=wx.ALIGN_CENTER | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
#            preview_panel.SetSizer(sizer)
#            preview_panel.SetAutoLayout(1)
#            preview_panel.SetupScrolling()
#            sb.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
#            self.__current_image = self.__cs.GetSourceImage()
#            self.SetFocus()
#            
#        def ShowPreviewImage(self, args):
#            '''
#            预览图片
#            '''
#            image_panel = self.FindWindowById(ID_Panel_Work_ImageReview)
#            image_panel.DestroyChildren()
#            self.__current_image = self.__cs.GetPreviewImage(args)
#            image = self.__current_image
#            sb = wx.StaticBitmap(image_panel, -1, wx.BitmapFromImage(image), size=image.GetSize())
#            image_panel.GetSizer().Add(sb, flag=wx.ALIGN_CENTER | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
#            image_panel.SetAutoLayout(1)
#            image_panel.SetupScrolling()
#            self.SetFocus()
#                
        def Scale(self, scale):
            '''
            图形缩放
            '''
            if self.__current_image:
                #修改图片大小
                image_panel = self.FindWindowById(ID_Panel_Work_ImageReview)
                image_panel.DestroyChildren()
                image = self.__current_image
                image = image.Scale(int(image.GetSize()[0] * scale), int(image.GetSize()[1] * scale))
                sb = wx.StaticBitmap(image_panel, -1, wx.BitmapFromImage(image), size=image.GetSize())
                image_panel.GetSizer().Add(sb, flag=wx.ALIGN_CENTER | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
                image_panel.SetAutoLayout(1)
                image_panel.SetupScrolling()               
            self.SetFocus()
                
            
    class OptionPanel(wx.Panel):
        '''
        选项面板
        '''
        def __init__(self, parent):
            wx.Panel.__init__(self, parent, ID_Panel_Option, size=(160, 400),
                                 style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER, name="option_panel")
            self.SetBackgroundColour(wx.Colour(red=255, green=255, blue=255))
            sizer = wx.GridBagSizer(vgap=1, hgap=1)
            
            props = Common.LoadFromDisk(Common.GetAppPath() + "/options.dat")
            if not props:
                props = {}
                props["PrintScale"] = 1.0
                props["PreviewScale"] = 0.1
                props["BgColour"] = "FFFFFF"
                props["MaxColourNum"] = 50
                props["MinFlossNum"] = 20
                props["MixColourDist"] = 15
                props["Width"] = 200
                props["Height"] = 0
                props["CT"] = 14
                props["CropSide"] = 1
                props["AntiNoise"] = 1
                props["AntiBgColour"] = 1
                props["OnlyPreview"] = 0
                props["ForTaobao"] = 0
                props["DisabledBgColour"] = 1
                
            input = wx.TextCtrl(self, ID_Option_PrintScale, str(props["PrintScale"]), style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"打印图片缩放比例")
            input.SetMaxLength(3)
            sizer.Add(label,pos=(0,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(0,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_PreviewScale, str(props["PreviewScale"]), style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"预览图片缩放比例")
            input.SetMaxLength(3)
            sizer.Add(label,pos=(1,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(1,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_BgColour, props["BgColour"], style=wx.TE_LEFT | wx.TE_READONLY, size=(45,20))
            label = wx.StaticText(self, -1, u"背景颜色")
            input.SetMaxLength(6)
            sizer.Add(label,pos=(2,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(2,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_MaxColourNum, str(props["MaxColourNum"]), style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"最高颜色数")
            input.SetMaxLength(3)
            sizer.Add(label,pos=(3,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(3,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_MinFlossNum, str(props["MinFlossNum"]), style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"最低颜色数")
            input.SetMaxLength(3)
            sizer.Add(label,pos=(4,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(4,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_MixColourDist, str(props["MixColourDist"]), style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"混合颜色距离")
            input.SetMaxLength(3)
            sizer.Add(label,pos=(5,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(5,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_Width, str(props["Width"]), style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"宽度")
            input.SetMaxLength(3)
            sizer.Add(label,pos=(6,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(6,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_Height, str(props["Height"]), style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"高度")
            input.SetMaxLength(3)
            sizer.Add(label,pos=(7,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(7,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            input = wx.TextCtrl(self, ID_Option_CT, str(props["CT"]), style=wx.TE_RIGHT, size=(45,20))
            label = wx.StaticText(self, -1, u"CT")
            input.SetMaxLength(2)
            sizer.Add(label,pos=(8,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(input,pos=(8,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            checkbox = wx.CheckBox(self, ID_Option_CropSide, "")
            checkbox.SetValue(props["CropSide"])
            label = wx.StaticText(self, -1, u"切除边缘空白")
            sizer.Add(label,pos=(9,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(checkbox, pos=(9, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            checkbox = wx.CheckBox(self, ID_Option_AntiNoise, "")
            checkbox.SetValue(props["AntiNoise"])
            label = wx.StaticText(self, -1, u"去除噪点")
            sizer.Add(label,pos=(10,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(checkbox, pos=(10, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            checkbox = wx.CheckBox(self, ID_Option_OnlyPreview, "")
            checkbox.SetValue(props["OnlyPreview"])
            label = wx.StaticText(self, -1, u"只输出预览图片")
            sizer.Add(label,pos=(11,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(checkbox, pos=(11, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            checkbox = wx.CheckBox(self, ID_Option_ForTaobao, "")
            checkbox.SetValue(props["ForTaobao"])
            label = wx.StaticText(self, -1, u"淘宝上传图片模式")
            sizer.Add(label,pos=(12,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(checkbox, pos=(12, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
                    
            checkbox = wx.CheckBox(self, ID_Option_AntiBgColour, "")
            checkbox.SetValue(props["AntiBgColour"])
            label = wx.StaticText(self, -1, u"去除背景颜色")
            sizer.Add(label,pos=(13,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
            sizer.Add(checkbox, pos=(13, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
            
            checkbox = wx.CheckBox(self, ID_Option_DisabledBgColour, "")
            checkbox.SetValue(props["DisabledBgColour"])
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
            event.Skip()
            
        def GetProperties(self):
            '''
            取得参数配置
            '''
            props = {}
            props["PrintScale"] = float(self.FindWindowById(ID_Option_PrintScale).GetValue())
            props["PreviewScale"] = float(self.FindWindowById(ID_Option_PreviewScale).GetValue())
            props["BgColour"] = self.FindWindowById(ID_Option_BgColour).GetValue()
            props["MaxColourNum"] = int(self.FindWindowById(ID_Option_MaxColourNum).GetValue())
            props["MinFlossNum"] = int(self.FindWindowById(ID_Option_MinFlossNum).GetValue())
            props["MixColourDist"] = int(self.FindWindowById(ID_Option_MixColourDist).GetValue())
            props["Width"] = self.FindWindowById(ID_Option_Width).GetValue()
            props["Height"] = self.FindWindowById(ID_Option_Height).GetValue()
            props["CT"] = int(self.FindWindowById(ID_Option_CT).GetValue())
            props["CropSide"] = int(self.FindWindowById(ID_Option_CropSide).GetValue())
            props["AntiNoise"] = int(self.FindWindowById(ID_Option_AntiNoise).GetValue())
            props["AntiBgColour"] = int(self.FindWindowById(ID_Option_AntiBgColour).GetValue())
            props["OnlyPreview"] = int(self.FindWindowById(ID_Option_OnlyPreview).GetValue())
            props["ForTaobao"] = int(self.FindWindowById(ID_Option_ForTaobao).GetValue())
            props["DisabledBgColour"] = int(self.FindWindowById(ID_Option_DisabledBgColour).GetValue())
            return props
        
        def ValidateData(self):
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
                if not Common.IsIntOrZero(obj.GetValue()):
                    self.__ShowError(u"请输入零或者其他任意正整数。")
                    obj.SetFocus()
                    obj.SetSelection(-1, -1)
                    return False
            return True
        
        def __ShowError(self, message):
            dlg = wx.MessageDialog(self, message, u"错误", style= wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        
        def __ShowInfo(self, message):
            dlg = wx.MessageDialog(self, message, u"信息", style= wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
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
            self.Bind(wx.EVT_SIZE, self.OnResize)
            
        def OnResize(self, event):
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