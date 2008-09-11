# -*- coding: utf-8 -*-
import re
import os,sys
import cPickle as pickle
import wx
import math

def RGB2Hex(rgb):
    return "%02X%02X%02X" % rgb

def Hex2RGB(hex):
    return (int(hex[0:2], 16), int(hex[2:4], 16), int(hex[4:6], 16))

def Hex2Colour(hex):
    rgb = Hex2RGB(hex)
    return wx.Colour(rgb[0], rgb[1], rgb[2])

def Colour2Hex(colour):
    return RGB2Hex(Colour2RGB(colour))

def Colour2RGB(colour):
    return (colour.Red(), colour.Green(), colour.Blue())

def IsFloat(s):
    pattern = '^[1-9]\d*\.\d*$|^0\.\d*[1-9]\d*$|^[1-9]\d*$'
    return re.search(pattern, s) != None

def IsInt(s):
    pattern = '^[1-9]\d*$'
    return re.search(pattern, s) != None

def IsIntOrZero(s):
    pattern = '^[1-9]\d*$|^0$'
    return re.search(pattern, s) != None

def GetPathName(s):
    '''
    返回路径
    '''
    if os.path.isdir(s):
        return s
    elif os.path.isfile(s):
        return os.path.split(s)[0]
    else:
        return None
    
def GetAppPath():
    return GetPathName(sys.argv[0])
    
def SaveToDisk(obj, filename):
    '''
    把对象保存到硬盘
    '''
    f = open(filename, 'wb')
    try:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    finally:
        f.close()

def LoadFromDisk(filename):
    '''
    从硬盘加载对象
    '''
    if os.path.exists(filename) and os.path.isfile(filename):
        f = open(filename, 'rb')
        try:
            result = pickle.load(f)
        finally:
            f.close()
    else:
        result = None
    return result

def GetRGBDistance(rgb1, rgb2):
    return math.sqrt((rgb1[0] - rgb2[0])**2 + (rgb1[1] - rgb2[1])**2 + (rgb1[2] - rgb2[2])**2)

def ShowError(parent, message):
        dlg = wx.MessageDialog(parent, message, u"错误", style= wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
    
def ShowInfo(parent, message):
    dlg = wx.MessageDialog(parent, message, u"信息", style= wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()
    
def ShowAlert(parent, message):
    dlg = wx.MessageDialog(parent, message, u"警告", style= wx.OK | wx.ICON_EXCLAMATION)
    dlg.ShowModal()
    dlg.Destroy()
    
def GetOutputFileName(path, outputPath, suffix = None):
    '''
    从目标文件名得到存储路径中的文件名
    '''
    fileName = os.path.split(path)[1]
    extensionName =  os.path.splitext(path)[1]
    fileName = fileName[:len(fileName) - len(extensionName)]
    if suffix:
        result = "%s\\%s(%s).jpg" %(outputPath, fileName, suffix)
    else:
        result = "%s\\%s.jpg" %(outputPath, fileName)
    return result