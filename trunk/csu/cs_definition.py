# -*- coding: utf-8 -*-
import wx
#系统设置
Application_Settings = {}

#菜单ID
ID_MenuItem_OpenFile = wx.NewId()
ID_MenuItem_Exit = wx.NewId()
ID_MenuItem_About = wx.NewId()
ID_MenuItem_ShowOptionPanel = wx.NewId()
ID_MenuItem_ShowLogPanel = wx.NewId()
#工具栏
ID_ToolBar_ShowOptionPanel = wx.NewId()
ID_ToolBar_ShowLogPanel = wx.NewId()
ID_ToolBar_OpenFile = wx.NewId()

ID_ToolBar_ZoomImage = wx.NewId()
ID_ToolBar_ZoomImageSpin = wx.NewId()
ID_ToolBar_GeneratePreview = wx.NewId()

#参数区
ID_Panel_Option = wx.NewId()
ID_Option_PrintScale = wx.NewId()
ID_Option_PreviewScale = wx.NewId()
ID_Option_BgColour = wx.NewId()
ID_Option_MaxColourNum = wx.NewId()
ID_Option_MinFlossNum = wx.NewId()
ID_Option_MixColourDist = wx.NewId()
ID_Option_Width = wx.NewId()
ID_Option_Height = wx.NewId()
ID_Option_CT = wx.NewId()
ID_Option_CropSide = wx.NewId()
ID_Option_AntiNoise = wx.NewId()
ID_Option_AntiBgColour = wx.NewId()
ID_Option_OnlyPreview = wx.NewId()
ID_Option_ForTaobao = wx.NewId()
ID_Option_DisabledBgColour = wx.NewId()

#图片区ID
ID_Panel_Work = wx.NewId()
ID_Panel_Work_ImageReview = wx.NewId()

#Log区
ID_Panel_Log = wx.NewId()

#绣线区
ID_Panel_Floss = wx.NewId()

from wx.lib.embeddedimage import PyEmbeddedImage

IMAGE_APP_ICON = PyEmbeddedImage(
    "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")