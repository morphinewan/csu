# -*- coding: utf-8 -*-
import os
import time
import math
import wx,wx.aui
import wx.grid
import wx.combo
import wx.lib.scrolledpanel as scrolled
import threading
import lib.func as Common
import lib.cross_stitch as cs
from cs_definition import *

class MainFrame(wx.MDIParentFrame):
    def __init__(
            self, parent, ID, title
            ):
        
        wx.MDIParentFrame.__init__(self, parent, ID, title, size=(800, 600))   
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
        menu_item = sub_menu.AppendCheckItem(ID_MenuItem_ShowFlossPanel, u"绣线统计面板", u"打开或者关闭绣线统计面板")
        view_menu.AppendSubMenu(sub_menu, u"面板")
        mb.Append(view_menu, u"查看")
               
        self.SetMenuBar(mb)
        
        #Toolbar
        toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                         wx.TB_FLAT | wx.TB_NODIVIDER)
        toolbar.SetToolBitmapSize(wx.Size(16,16))
        toolbar.AddLabelTool(ID_ToolBar_OpenFile, u"打开文件", wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN), shortHelp=u"打开文件", longHelp=u"选取制作十字绣的图片源文件")
        toolbar.AddLabelTool(ID_MenuItem_Exit, u"关闭", wx.ArtProvider_GetBitmap(wx.ART_QUIT), shortHelp=u"关闭", longHelp=u"关闭本应用程序")
        
        toolbar.AddSeparator()
        
        toolbar.AddControl(wx.ToggleButton(toolbar, ID_ToolBar_ShowOptionPanel, u"选项面板"))
        toolbar.AddControl(wx.ToggleButton(toolbar, ID_ToolBar_ShowLogPanel, u"日志面板"))
        toolbar.AddControl(wx.ToggleButton(toolbar, ID_ToolBar_ShowFlossPanel, u"绣线统计面板"))
        
        toolbar.AddSeparator()
        toolbar.AddControl(wx.BitmapButton(toolbar, ID_ToolBar_ShowImageFormat1, bitmap=TOOLBAR_ICON_01.GetBitmap()))
        toolbar.AddControl(wx.BitmapButton(toolbar, ID_ToolBar_ShowImageFormat2, bitmap=TOOLBAR_ICON_02.GetBitmap()))
        toolbar.AddControl(wx.BitmapButton(toolbar, ID_ToolBar_ShowImageFormat3, bitmap=TOOLBAR_ICON_03.GetBitmap()))
        toolbar.AddSeparator()
        
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
        self.SetToolBar(toolbar)
        
        #左部设置项目
        self.__option_panel = OptionFrame(self, ID_Panel_Option, u"选项")        
        #Log区
        self.__log_panel = LogFrame(self, ID_Panel_Log, u"日志")        
        #绣线区
        self.__floss_panel = FlossFrame(self, ID_Panel_Floss, u"绣线统计")
        #状态
        self.__status_bar = self.CreateStatusBar(number = 1, name="statusbar")
        
        #窗口关闭
        self.Bind(wx.EVT_CLOSE, self.OnWindowClose)
    
        #绑定事件
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_MenuItem_Exit)
        self.Bind(wx.EVT_MENU, self.OnFileOpen, id=ID_MenuItem_OpenFile)
        self.Bind(wx.EVT_MENU, self.OnMenuClick, id=ID_MenuItem_ShowOptionPanel)
        self.Bind(wx.EVT_MENU, self.OnMenuClick, id=ID_MenuItem_ShowLogPanel)
        self.Bind(wx.EVT_MENU, self.OnMenuClick, id=ID_MenuItem_ShowFlossPanel)
     
        self.Bind(wx.EVT_TOOL, self.OnFileOpen, id=ID_ToolBar_OpenFile)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnMenuClick, id=ID_ToolBar_ShowOptionPanel)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnMenuClick, id=ID_ToolBar_ShowLogPanel)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnMenuClick, id=ID_ToolBar_ShowFlossPanel)
        self.Bind(wx.EVT_BUTTON , self.OnGeneratePreview, id=ID_ToolBar_GeneratePreview)
        self.Bind(wx.EVT_BUTTON, self.OnViewChange, id=ID_ToolBar_ShowImageFormat1)
        self.Bind(wx.EVT_BUTTON, self.OnViewChange, id=ID_ToolBar_ShowImageFormat2)
        self.Bind(wx.EVT_BUTTON, self.OnViewChange, id=ID_ToolBar_ShowImageFormat3)
        
        self.Bind(wx.EVT_TEXT_ENTER, self.OnImageZoom, id=ID_ToolBar_ZoomImage)
        self.Bind(wx.EVT_COMBOBOX, self.OnImageZoom, id=ID_ToolBar_ZoomImage)
        self.Bind(wx.EVT_SPIN_UP, self.OnImageZoomSpinUp, id=ID_ToolBar_ZoomImageSpin)
        self.Bind(wx.EVT_SPIN_DOWN, self.OnImageZoomSpinDown, id=ID_ToolBar_ZoomImageSpin)
        
        self.Bind(cs.EVT_PI_GENERATE_START, self.OnPreviewImageGenerateStart)
        self.Bind(cs.EVT_PI_GENERATE_END, self.OnPreviewImageGenerateEnd)
        self.Bind(cs.EVT_PI_RESIZED, self.OnPreviewImageResized)
        
        self.Bind(cs.EVT_PI_COLOURTABLE_CHANGE_START, self.OnCSProcessStartEvent)
        self.Bind(cs.EVT_PI_COLOURTABLE_CHANGE_END, self.OnCSProcessEndEvent)
        self.Bind(cs.EVT_PI_COLOURTABLE_CHANGING, self.OnCSProcessingEvent)
        
        self.Bind(cs.EVT_PI_COLOUR_DIST_MIX_START, self.OnCSProcessStartEvent)
        self.Bind(cs.EVT_PI_COLOUR_DIST_MIXING, self.OnCSProcessingEvent)
        self.Bind(cs.EVT_PI_COLOUR_DIST_MIX_END, self.OnCSProcessEndEvent)
        
        self.Bind(cs.EVT_PI_MAX_COLOUR_NUM_REDUCE_START, self.OnCSProcessStartEvent)
        self.Bind(cs.EVT_PI_MAX_COLOUR_NUM_REDUCING, self.OnCSProcessingEvent)
        self.Bind(cs.EVT_PI_MAX_COLOUR_NUM_REDUCE_END, self.OnCSProcessEndEvent)
        
        self.Bind(cs.EVT_PI_MIN_FLOSS_NUM_REDUCE_START, self.OnCSProcessStartEvent)
        self.Bind(cs.EVT_PI_MIN_FLOSS_NUM_REDUCING, self.OnCSProcessingEvent)
        self.Bind(cs.EVT_PI_MIN_FLOSS_NUM_REDUCE_END, self.OnCSProcessEndEvent)
        
        self.Bind(cs.EVT_PI_CROPSIDE_START, self.OnCSProcessStartEvent)
        self.Bind(cs.EVT_PI_CROPSIDING, self.OnCSProcessingEvent)
        self.Bind(cs.EVT_PI_CROPSIDE_END, self.OnCSProcessEndEvent)
        
        self.Bind(cs.EVT_PI_ANTINOISE_START, self.OnCSProcessStartEvent)
        self.Bind(cs.EVT_PI_ANTINOISING, self.OnCSProcessingEvent)
        self.Bind(cs.EVT_PI_ANTINOISE_END, self.OnCSProcessEndEvent)
        
        self.Bind(cs.EVT_PI_ANTIBGCOLOUR_START, self.OnCSProcessStartEvent)
        self.Bind(cs.EVT_ANTIBGCOLOURING, self.OnCSProcessingEvent)
        self.Bind(cs.EVT_PI_ANTIBGCOLOUR_END, self.OnCSProcessEndEvent)
        
        self.Bind(cs.EVT_PI_STITCHCONVASGENERATE_START, self.OnCSProcessStartEvent)
        self.Bind(cs.EVT_STITCHCONVASGENERATING, self.OnCSProcessingEvent)
        self.Bind(cs.EVT_PI_STITCHCONVASGENERATE_END, self.OnCSProcessEndEvent)
        
        self.Bind(cs.EVT_PI_PRINTCONVASGENERATE_START, self.OnCSProcessStartEvent)
        self.Bind(cs.EVT_PRINTCONVASGENERATING, self.OnCSProcessingEvent)
        self.Bind(cs.EVT_PI_PRINTCONVASGENERATE_END, self.OnCSProcessEndEvent)
        
        self.Bind(cs.EVT_PI_CROSSSTITCHSAVE_START, self.OnCSProcessStartEvent)
        self.Bind(cs.EVT_CROSSSTITCHSAVING, self.OnCSProcessingEvent)
        self.Bind(cs.EVT_PI_CROSSSTITCHSAVE_END, self.OnCSProcessEndEvent)
        
        self.Bind(EVT_WORK_FRAME_MOUSE_MOVE_EVENT, self.OnWorkFrameMouseMove)
        self.Bind(EVT_WORK_FRAME_CLOSE_EVENT, self.OnWorkFrameCloseEvent)
        
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        #定义待处理的图片数组
        self.__cs = []
        
        #加载系统配置信息
        global Application_Settings
        Application_Settings = Common.LoadFromDisk(Common.GetAppPath() + "/appsetting.dat")
        if not Application_Settings:
            Application_Settings = {}
        
        #异步加载配置信息
        self.__log_panel.Log(u"异步加载绣线色彩映射表设定")
        self.__flossmap = cs.FlossMap(self)
        threading.Thread(target=self.__flossmap.Load).start()
        #绑定加载完成的事件
        self.Bind(cs.EVT_FLOSSMAP_LOADED, self.OnFlossMapLoaded)
        
        #初始化界面
        self.__InitLayout()
        
    def OnCSProcessStartEvent(self, event):
        #取得事件ID
        event_type = event.GetEventType()
        log_content = ""
        title = ""
        if event_type == cs.EVT_PI_CROPSIDE_START.typeId:
            log_content = u"裁剪图片四周多余无用的空格开始"
            title = u"裁剪图片四周多余无用的空格"
        elif event_type == cs.EVT_PI_COLOURTABLE_CHANGE_START.typeId:
            log_content = u"更换预览图调色板为绣图专用DMC颜色开始"
            title = u"更换预览图调色板为绣图专用DMC颜色"
        elif event_type == cs.EVT_PI_COLOUR_DIST_MIX_START.typeId:
            log_content = u"合并颜色相近绣线开始，目前颜色数总共%d色" % event.total
            title = u"合并颜色相近绣线"
        elif event_type == cs.EVT_PI_MAX_COLOUR_NUM_REDUCE_START.typeId:
            log_content = u"限定颜色数最高为%d色处理开始，目前颜色数总共%d色" % (event.param, event.total)
            title = u"限定颜色数最高为%d色" % event.param
        elif event_type == cs.EVT_PI_MIN_FLOSS_NUM_REDUCE_START.typeId:
            log_content = u"剔除使用量少于%d格的线条开始，目前颜色数总共%d色" % (event.param, event.total)
            title = u"剔除使用量少于%d格的线条" % event.param
        elif event_type == cs.EVT_PI_ANTINOISE_START.typeId:
            log_content = u"去除图片中的噪点开始"
            title = u"去除图片中的噪点"
        elif event_type == cs.EVT_PI_ANTIBGCOLOUR_START.typeId:
            log_content = u"去除接近背景色的像素开始"
            title = u"去除接近背景色的像素"
        elif event_type == cs.EVT_PI_STITCHCONVASGENERATE_START.typeId:
            log_content = u"生成绣图预览模式1开始"
            title = u"生成绣图预览模式1"
        elif event_type == cs.EVT_PI_PRINTCONVASGENERATE_START.typeId:
            log_content = u"生成绣图预览模式2开始"
            title = u"生成绣图预览模式2"
        elif event_type == cs.EVT_PI_CROSSSTITCHSAVE_START.typeId:
            log_content = u"保存绣图开始"
            title = u"保存绣图"
        self.__log_panel.Log(log_content)
        self.__prodlg = wx.ProgressDialog(u"进度条",
                           title,
                           maximum=100,
                           parent=self,
                           style = wx.PD_APP_MODAL
                            | wx.PD_AUTO_HIDE
                            | wx.PD_SMOOTH 
                            )
        
    def OnCSProcessingEvent(self, event):
        #取得事件ID
        event_type = event.GetEventType()
        if event_type in (cs.EVT_PI_CROPSIDING.typeId,
                          cs.EVT_PI_COLOUR_DIST_MIXING.typeId,
                          cs.EVT_PI_MAX_COLOUR_NUM_REDUCING.typeId,
                          cs.EVT_PI_MIN_FLOSS_NUM_REDUCING.typeId,
                          cs.EVT_PI_ANTINOISING.typeId,
                          cs.EVT_ANTIBGCOLOURING.typeId,
                          cs.EVT_STITCHCONVASGENERATING.typeId,
                          cs.EVT_PRINTCONVASGENERATING.typeId,
                          cs.EVT_CROSSSTITCHSAVING.typeId,
                          ):
            self.__prodlg.Update(event.count * 100 / event.total)
        elif event_type == cs.EVT_PI_COLOURTABLE_CHANGING.typeId:
            self.__prodlg.Update(event.pos * 100 / (event.max - event.min))
    
    def OnCSProcessEndEvent(self, event):
        event_type = event.GetEventType()
        log_content = ""
        if event_type == cs.EVT_PI_CROPSIDE_END.typeId:
            log_content = u"裁剪图片四周多余无用的空格结束"
        elif event_type == cs.EVT_PI_COLOURTABLE_CHANGE_END.typeId:
            log_content = u"更换预览图调色板为绣图专用DMC颜色结束"
        elif event_type == cs.EVT_PI_COLOUR_DIST_MIX_END.typeId:
            log_content =  u"合并颜色相近绣线结束，目前颜色数总共%d色" % event.total
        elif event_type == cs.EVT_PI_MAX_COLOUR_NUM_REDUCE_END.typeId:
            log_content =  u"限定颜色数最高为%d色处理结束，目前颜色数总共%d色" % (event.param, event.total)
        elif event_type == cs.EVT_PI_MIN_FLOSS_NUM_REDUCE_END.typeId:
            log_content =  u"剔除使用量少于%d格的线条结束，目前颜色数总共%d色" % (event.param, event.total)
        elif event_type == cs.EVT_PI_ANTINOISE_END.typeId:
            log_content =  u"去除图片中的噪点结束"
        elif event_type == cs.EVT_PI_ANTIBGCOLOUR_END.typeId:    
            log_content =  u"去除接近背景色的像素结束"
        elif event_type == cs.EVT_PI_STITCHCONVASGENERATE_END.typeId:    
            log_content =  u"生成绣图预览模式1结束"
        elif event_type == cs.EVT_PI_PRINTCONVASGENERATE_END.typeId:    
            log_content =  u"生成绣图预览模式2结束"
        elif event_type == cs.EVT_PI_CROSSSTITCHSAVE_END.typeId:    
            log_content =  u"保存绣图结束"
            Common.ShowInfo(self, log_content)
        self.__log_panel.Log(log_content)
        if self.__prodlg:
            self.__prodlg.Destroy()
            
    def OnPreviewImageResized(self, event):
        self.__log_panel.Log((u"调整分辨率大小为(%d, %d)" % (event.width, event.height)))
    
    def OnPreviewImageGenerateEnd(self, event):
        self.__EnableImageTool(1)
        self.__log_panel.Log((u"预览图转换完成"))
        scale = self.__work_frame.ShowImage(self.__cs[0].GetPreviewImage(), 1)
        self.FindWindowById(ID_ToolBar_ZoomImage).SetValue("%d%%" % (scale*100))
        #显示绣线面板
        self.__floss_panel.ShowFlossInfo(self.__cs[0].GetFlossSummary(), self.__cs[0].GetFlossMaskList())
        self.__work_frame.Show()
    
    def OnPreviewImageGenerateStart(self, event):
        self.__EnableImageTool(0)
        self.__work_frame.Hide()
        self.__log_panel.Log((u"预览图转换开始"))
    
    def OnFlossMapLoaded(self, event):
        self.__log_panel.Log(u"异步加载绣线色彩映射表设定已经完成")
    
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
        self.__work_frame.Scale(scale)
    
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
            self.__work_frame.Scale(scale)
        
    def OnGeneratePreview(self, event):
        '''
        预览图片
        '''
        if self.__option_panel.ValidateData():
            self.FindWindowById(ID_ToolBar_ZoomImage).SetValue("100%")
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
        self.__work_frame.Scale(scale)
        
    def OnMenuClick(self, event):
        '''
        菜单相应事件
        '''
        if event.GetId() == ID_MenuItem_ShowOptionPanel:
            item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowOptionPanel)           
            self.FindWindowById(ID_ToolBar_ShowOptionPanel).SetValue(item.IsChecked())
            self.__option_panel.Show(show=item.IsChecked())
        elif event.GetId() == ID_ToolBar_ShowOptionPanel:
            item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowOptionPanel)
            item.Check(self.FindWindowById(ID_ToolBar_ShowOptionPanel).GetValue())
            self.__option_panel.Show(show=item.IsChecked())
        elif event.GetId() == ID_MenuItem_ShowLogPanel:
            item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowLogPanel)           
            self.FindWindowById(ID_ToolBar_ShowLogPanel).SetValue(item.IsChecked())
            self.__log_panel.Show(show=item.IsChecked())
        elif event.GetId() == ID_ToolBar_ShowLogPanel:
            item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowLogPanel)
            item.Check(self.FindWindowById(ID_ToolBar_ShowLogPanel).GetValue())
            self.__log_panel.Show(show=item.IsChecked())
        elif event.GetId() == ID_MenuItem_ShowFlossPanel:
            item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowFlossPanel)           
            self.FindWindowById(ID_ToolBar_ShowFlossPanel).SetValue(item.IsChecked())
            self.__floss_panel.Show(show=item.IsChecked())
        elif event.GetId() == ID_ToolBar_ShowFlossPanel:
            item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowFlossPanel)
            item.Check(self.FindWindowById(ID_ToolBar_ShowFlossPanel).GetValue())
            self.__floss_panel.Show(show=item.IsChecked())
        
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
                cs1 = cs.CrossStitch(path, self.__flossmap, self)
                self.__cs.append(cs1)
            Application_Settings["Default_Directory"] = Common.GetPathName(self.__cs[0].GetSourceImageFileName())
            #加载图像
            if self.__cs:
                pos = (100, 95)               
                self.__work_frame = WorkFrame(self, -1, u"图片工作区")
                self.FindWindowById(ID_ToolBar_ZoomImage).SetValue('100%')
                self.__EnableImageTool(1)
                scale = self.__work_frame.ShowImage(self.__cs[0].GetSourceImage(), 1)                
                self.FindWindowById(ID_ToolBar_ZoomImage).SetValue("%d%%" % (scale*100))
                self.__work_frame.Maximize()
                self.__work_frame.Show()
        dlg.Destroy()
    
    def OnWorkFrameMouseMove(self, event):
        self.__status_bar.SetStatusText(u"光标位置:%d,%d  颜色:%s" % (event.pos[0], event.pos[1], event.rgb))
        
    def OnWorkFrameCloseEvent(self, event):
        self.__EnableImageTool(0)
        self.__log_panel.Clear()
        self.__floss_panel.Clear()
    
    def OnInitFlossMap(self, event):
        '''
         初始化颜色映射表
        '''
#        self.__flossmap.Initialize()
#        self.__flossmap.SaveData()
        pass
    
    def __EnableImageTool(self, flg):
        '''
        控制图片相关工具的可用性
        '''
        if not flg:
            self.FindWindowById(ID_ToolBar_ZoomImage).SetValue("100%")
        self.FindWindowById(ID_ToolBar_ZoomImage).Enable(flg)
        self.FindWindowById(ID_ToolBar_ZoomImageSpin).Enable(flg)
        self.FindWindowById(ID_ToolBar_GeneratePreview).Enable(flg)
        self.FindWindowById(ID_ToolBar_ShowImageFormat1).Enable(flg)
        self.FindWindowById(ID_ToolBar_ShowImageFormat2).Enable(flg)
        self.FindWindowById(ID_ToolBar_ShowImageFormat3).Enable(flg)
        
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
    
    def OnViewChange(self, event):
        scale = None
        if event.GetId() == ID_ToolBar_ShowImageFormat1:
            scale = self.__work_frame.ShowImage(self.__cs[0].GetPreviewImage(), 1)                
        elif event.GetId() == ID_ToolBar_ShowImageFormat2:
            scale = self.__work_frame.ShowImage(self.__cs[0].GetStitchConvas(), 1)
        elif event.GetId() == ID_ToolBar_ShowImageFormat3:
            scale = self.__work_frame.ShowImage(self.__cs[0].GetPrintConvas(), 1)
        if scale:
            self.FindWindowById(ID_ToolBar_ZoomImage).SetValue("%d%%" % (scale*100))
    
    def OnKeyDown(self, event):
        print "mother key down %s" % event.GetKeyCode()
#        print event.GetKeyCode()
        if event.GetModifiers() == wx.MOD_CONTROL and event.GetKeyCode() in (65, 79):
            #打开文件 ctrl + a  or ctrl + o
            self.OnFileOpen(None)
        elif event.GetModifiers() == wx.MOD_CONTROL and event.GetKeyCode() in (81, 90):
            #退出系统 ctrl + q or ctrl + z
            self.OnExit(None)
        elif event.GetKeyCode() == wx.WXK_F1:
            item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowOptionPanel)           
            item.Check(not item.IsChecked())
            self.FindWindowById(ID_ToolBar_ShowOptionPanel).SetValue(item.IsChecked())
            self.__option_panel.Show(show=item.IsChecked())
        elif event.GetKeyCode() == wx.WXK_F2:
            item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowLogPanel)           
            item.Check(not item.IsChecked())
            self.FindWindowById(ID_ToolBar_ShowLogPanel).SetValue(item.IsChecked())
            self.__log_panel.Show(show=item.IsChecked())
        elif event.GetKeyCode() == wx.WXK_F3:
            item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowFlossPanel)           
            item.Check(not item.IsChecked())
            self.FindWindowById(ID_ToolBar_ShowFlossPanel).SetValue(item.IsChecked())
            self.__floss_panel.Show(show=item.IsChecked())
        if self.__cs:
            scale = None
            if event.GetKeyCode() == wx.WXK_F5:
                scale = self.__work_frame.ShowImage(self.__cs[0].GetPreviewImage(), 1)
            elif event.GetKeyCode() == wx.WXK_F6:
                scale = self.__work_frame.ShowImage(self.__cs[0].GetStitchConvas(), 1)
            elif event.GetKeyCode() == wx.WXK_F7:
                scale = self.__work_frame.ShowImage(self.__cs[0].GetPrintConvas(), 1)
            if scale:
                self.FindWindowById(ID_ToolBar_ZoomImage).SetValue("%d%%" % (scale*100))
            if event.GetKeyCode() == wx.WXK_F9:
                #预览
                self.OnGeneratePreview(None)
            elif event.GetKeyCode() == wx.WXK_F10:
                #保存功能
                pass
            
    
    def OnDebug(self, event):
        for k, v in cs.COLOR_TABLE.iteritems():
            print k, v
     
    def __InitLayout(self):
        self.__option_panel.Hide()
        item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowOptionPanel)
        item.Check(0)
        self.FindWindowById(ID_ToolBar_ShowOptionPanel).SetValue(0)
        
        self.__log_panel.Hide()
        item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowLogPanel)
        item.Check(0)
        self.FindWindowById(ID_ToolBar_ShowLogPanel).SetValue(0)
        
        self.__floss_panel.Hide()
        item = self.GetMenuBar().GetMenus()[1][0].FindItemById(ID_MenuItem_ShowFlossPanel)
        item.Check(0)
        self.FindWindowById(ID_ToolBar_ShowFlossPanel).SetValue(0)
        
        self.__EnableImageTool(0)
        #设置图标        
        self.SetIcon(IMAGE_APP_ICON.GetIcon())
        
class OptionFrame(wx.Frame):
    '''
    选项面板
    '''
    def __init__(self, parent, ID, title):
        style = wx.RESIZE_BORDER | wx.MINIMIZE_BOX | wx.FRAME_TOOL_WINDOW | wx.CAPTION | wx.CLIP_CHILDREN | wx.STAY_ON_TOP
        size = (160, 400)
        pos = (10, 100)
        wx.Frame.__init__(self, parent, ID, title, pos=pos, size=size, style=style)    
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
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        
    def OnKeyDown(self, event):
        self.Parent.ProcessEvent(event)
        
    def OnColourPickup(self, event):
        '''
        选择颜色
        '''
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        dlg.GetColourData().SetColour(Common.Hex2Colour(event.GetEventObject().GetValue()))
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData().GetColour().Get()                
            event.GetEventObject().SetValue(Common.RGB2Hex(data))
        dlg.Destroy()
        
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
                Common.ShowError(self, u"请输入正小数。")
                obj.SetFocus()
                obj.SetSelection(-1, -1)
                return False
        for id in (ID_Option_MaxColourNum, ID_Option_MinFlossNum, ID_Option_MixColourDist, 
                   ID_Option_Width, ID_Option_Height, ID_Option_CT):
            obj = self.FindWindowById(id)
            if not Common.IsIntOrZero(obj.GetValue()):
                Common.ShowError(self, u"请输入零或者其他任意正整数。")
                obj.SetFocus()
                obj.SetSelection(-1, -1)
                return False
        return True
        
class LogFrame(wx.Frame):
    '''
    日志面板
    '''
    def __init__(self, parent, ID, title):
        style = wx.RESIZE_BORDER | wx.MINIMIZE_BOX | wx.FRAME_TOOL_WINDOW | wx.CAPTION | wx.CLIP_CHILDREN | wx.STAY_ON_TOP
        size = (wx.DisplaySize()[0] -20, 300)
        pos = (10, wx.DisplaySize()[1] - 310)
        wx.Frame.__init__(self, parent, ID, title, pos=pos, size=size, style=style)
        self.panel = scrolled.ScrolledPanel(self, -1, size=self.GetSize())
        sizer = wx.GridSizer(1, 1)      
        self.log = wx.TextCtrl(self.panel, -1,
                    "",
                   size=self.GetSize(), style=wx.TE_MULTILINE|wx.TE_READONLY)
        sizer = wx.GridSizer(1, 1)
        sizer.AddF(self.log, wx.SizerFlags().Expand())
        self.panel.SetSizer(sizer)
        self.panel.SetAutoLayout(1)
        self.panel.SetupScrolling()
        sizer = wx.GridSizer(1, 1)
        sizer.AddF(self.panel, wx.SizerFlags().Expand())
        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        
    def OnKeyDown(self, event):
        self.Parent.ProcessEvent(event)
           
    def Log(self, content):
        self.__lastpos = self.log.GetLastPosition()
        self.log.AppendText("%s %s\n" % (time.strftime('%Y-%m-%d %X', time.localtime()), content))
    
    def Replace(self, content):
        '''
        替换最后一条记录
        '''
        content = "%s %s\n" % (time.strftime('%Y-%m-%d %X', time.localtime()), content)           
        self.log.Replace(self.__lastpos, self.log.GetLastPosition(), content)
        
    def Clear(self):
        self.log.ChangeValue("")
    
class FlossFrame(wx.Frame):
    def __init__(self, parent, ID, title, pos=wx.DefaultPosition,
            size=(300, 600), style=wx.MINIMIZE_BOX | wx.FRAME_TOOL_WINDOW | wx.CAPTION | wx.CLIP_CHILDREN | wx.STAY_ON_TOP
            ):
        position = (wx.DisplaySize()[0] - 320, 100)
        wx.Frame.__init__(self, parent, ID, title, pos=position, size=size, style=style)
        self.floss_table = wx.grid.Grid(self, -1, size=self.GetSize())
        self.floss_table.CreateGrid(0, 4, wx.grid.Grid.wxGridSelectRows)
        self.floss_table.EnableGridLines(1)
        self.floss_table.EnableEditing(0)
        self.floss_table.SetRowLabelSize(0)        
        self.floss_table.SetColLabelValue(0, u"线号")
        self.floss_table.SetColLabelValue(1, u"说明")
        self.floss_table.SetColLabelValue(2, u"颜色")
        self.floss_table.SetColLabelValue(3, u"格子数")
        sizer = wx.GridSizer(1, 1)
        sizer.Add(self.floss_table, flag=wx.ALIGN_CENTER | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        
        self.floss_table.EnableEditing(0)
        self.floss_table.EnableDragCell(0)
        self.floss_table.EnableDragColSize(0)
        self.floss_table.EnableDragColMove(0)
        self.floss_table.EnableDragRowSize(0)
        
        #窗口关闭
        self.Bind(wx.EVT_CLOSE, self.OnWindowClose)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        
#        self.floss_table.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnPopupMenu)
        
    def OnPopupMenu(self, event):
        '''
        右键菜单
        '''
        if not hasattr(self, "POPUP_MENU_ID_1"):
            self.POPUP_MENU_ID_1 = wx.NewId()
            self.POPUP_MENU_ID_2 = wx.NewId()
            
            self.Bind(wx.EVT_MENU, self.OnRemoveColor, id=self.POPUP_MENU_ID_1)
        menu = wx.Menu()       
        menu.Append(self.POPUP_MENU_ID_1, u"删除该颜色")
        menu.Append(self.POPUP_MENU_ID_2, u"替换颜色")
        self.PopupMenu(menu)
        menu.Destroy()
        
    def OnKeyDown(self, event):
        self.Parent.ProcessEvent(event)
    
    def OnRemoveColor(self, event):
        print "remove"
    
    def OnWindowClose(self, event):
        wx.PostEvent(self.Parent, WorkFrameCloseEvent())
        self.Destroy()
    
    def Clear(self):
        self.floss_table.ClearGrid()
        if self.floss_table.GetNumberRows():
            self.floss_table.DeleteRows(0, self.floss_table.GetNumberRows())
    
    def ShowFlossInfo(self, fs, masklist):
        self.floss_table.ClearGrid()
        if self.floss_table.GetNumberRows():
            self.floss_table.DeleteRows(0, self.floss_table.GetNumberRows())
        self.floss_table.AppendRows(len(fs))
        i = 0        
        for floss in fs:
            f = cs.COLOR_TABLE[floss[0]]
            self.floss_table.SetCellValue(i, 0, f.id)
            self.floss_table.SetCellAlignment(i, 0, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
            self.floss_table.SetCellValue(i, 1, f.description)
            self.floss_table.SetCellAlignment(i, 1, wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
            mask = masklist[(f.rgb[0], f.rgb[1], f.rgb[2],)]
            self.floss_table.SetCellRenderer(i, 2, self.GridCellMaskRenderer(mask[0]))
            self.floss_table.SetCellBackgroundColour(i, 2, f.rgb)
            self.floss_table.SetCellAlignment(i, 2, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.floss_table.SetCellValue(i, 3, str(floss[1]))
            self.floss_table.SetCellAlignment(i, 3, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
            i += 1
        self.floss_table.AutoSize()
        
    class GridCellMaskRenderer(wx.grid.PyGridCellRenderer):
        def __init__(self, mask):
            wx.grid.PyGridCellRenderer.__init__(self)
            self.mask = mask
        
        def Draw(self, grid, attr, dc, rect, row, col, isSelected):
            dc_temp = wx.MemoryDC(wx.BitmapFromImage(self.mask))
            dc.SetBrush(wx.Brush((255, 255, 255)))
            dc.DrawRectangle(rect.x, rect.y, rect.GetWidth(), rect.GetHeight())
            x = rect.x + (rect.GetWidth() - self.mask.GetSize()[0]) / 2
            y = rect.y + (rect.GetHeight() - self.mask.GetSize()[1]) / 2
            dc.Blit(x, y, self.mask.GetSize()[0], self.mask.GetSize()[1], dc_temp, 0, 0)
            
class WorkFrame(wx.MDIChildFrame):
    def __init__(self, parent, ID, title):        
        wx.MDIChildFrame.__init__(self, parent, ID, title)
#        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        #窗口关闭
        self.Bind(wx.EVT_CLOSE, self.OnWindowClose)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
#        #设置图标
#        self.SetIcon(IMAGE_APP_CHILD_ICON.GetIcon())
        
    def OnKeyDown(self, event):
        print "child key down %s" % event.GetKeyCode()
        self.Parent.ProcessEvent(event)
        
    def OnWindowClose(self, event):
        if not self.Parent.IsShown():
            self.Parent.Show()
        wx.PostEvent(self.Parent, WorkFrameCloseEvent())
        self.Destroy()
         
    def OnSetFocus(self, event):
        if self.FindWindowById(ID_Frame_Work_ImageReview):
            self.FindWindowById(ID_Frame_Work_ImageReview).Bind(wx.EVT_MOTION, self.OnMouseMove)
    
    def OnMouseWheel(self, event):
        obj = self.FindWindowById(ID_Frame_Work_ImageReviewPanel)
        pos = obj.GetViewStart()
        [x, y] = pos
        if event.GetWheelRotation() > 0:
            if event.m_controlDown:
                x -= 1
            else:
                y -= 1
        else:
            if event.m_controlDown:
                x += 1
            else:
                y += 1        
        obj.Scroll(x, y)
        
    def OnMouseMove(self, event):
        rgb = None
        image = self.FindWindowById(ID_Frame_Work_ImageReview)
        x, y = event.GetX(), event.GetY()
        if image:
            image = image.GetBitmap().ConvertToImage()
            rgb = Common.RGB2Hex((image.GetRed(x, y), image.GetGreen(x, y), image.GetBlue(x, y)))
        wx.PostEvent(self.Parent, WorkFrameMouseMoveEvent(pos=(x, y), rgb=rgb))
    
    def Clear(self):
        self.__cs = None
        self.__current_image = None
        self.DestroyChildren()
            
    def ShowImage(self, image, fill=False):
        if image:
            preview_panel = self.FindWindowById(ID_Frame_Work_ImageReviewPanel)
            if preview_panel:
                preview_panel.DestroyChildren()
            else:                           
                preview_panel = scrolled.ScrolledPanel(self, ID_Frame_Work_ImageReviewPanel, size=self.GetSize())
            sizer = wx.GridSizer(1, 1)
            self.__current_image = image
            scale = 1.0
            if fill:
                if (float(image.GetSize()[0]) / image.GetSize()[1]) > \
                    (float(self.GetSize()[0]) / self.GetSize()[1]):
                    scale = float(self.GetSize()[0]) / image.GetSize()[0]
                else:
                    scale = float(self.GetSize()[1]) / image.GetSize()[1]      
                image = image.Scale(int(image.GetSize()[0] * scale), int(image.GetSize()[1] * scale))
            sb = wx.StaticBitmap(preview_panel, ID_Frame_Work_ImageReview, wx.BitmapFromImage(image), size=image.GetSize())
            sizer.Add(sb, flag=wx.ALIGN_CENTER | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
            preview_panel.SetSizer(sizer)
            preview_panel.SetAutoLayout(1)
            preview_panel.SetupScrolling()
            return scale
            
    def FitBestSize(self):
        if self.__current_image:
            image = self.__current_image 
            #自适应图片大小
            if wx.DisplaySize()[0] - 200 > image.GetSize()[0]:
                width = image.GetSize()[0] + 50
            else:
                width = wx.DisplaySize()[0] - 200
            if wx.DisplaySize()[1]-150 > image.GetSize()[1]:
                height = image.GetSize()[1] + 50
            else:
                height = wx.DisplaySize()[1]-150
            self.SetSize((width, height))
        
    def Scale(self, scale):
        '''
        图形缩放
        '''
        if self.__current_image:
            #修改图片大小
            image_panel = self.FindWindowById(ID_Frame_Work_ImageReviewPanel)
            image_panel.DestroyChildren()
            image = self.__current_image
            image = image.Scale(int(image.GetSize()[0] * scale), int(image.GetSize()[1] * scale))
            sb = wx.StaticBitmap(image_panel, ID_Frame_Work_ImageReview, wx.BitmapFromImage(image), size=image.GetSize())
            image_panel.GetSizer().Add(sb, flag=wx.ALIGN_CENTER | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
            image_panel.SetAutoLayout(1)
            image_panel.SetupScrolling()
            self.SetFocus()
            
class Application(wx.App):
    def OnInit(self):
        win = MainFrame(None, -1, u"十字绣转换工具 morphinewan荣誉出品")
        self.SetTopWindow(win)
        win.Show(True)
        return True

def main():
    Application(0).MainLoop()
    
if __name__ == '__main__':
    main()
