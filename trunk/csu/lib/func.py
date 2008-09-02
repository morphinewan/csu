# -*- coding: utf-8 -*-
import re
import os,sys
import cPickle as pickle
import wx

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
    f = open(filename, 'w')
    pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    f.close()

def LoadFromDisk(filename):
    '''
    从硬盘加载对象
    '''
    if os.path.exists(filename) and os.path.isfile(filename):
        f = open(filename, 'r')
        result = pickle.load(f)
        f.close()
    else:
        result = None
    return result