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

def CaclImageBestSize(image, size):
    image_size = image.GetSize()
    width, height = 0, 0
    if (float(image_size[0]) / image_size[1]) > (float(size[0]) / size[1]):
        #如果图片本身的长宽比大于目标大小的长宽比，说明图片的宽度可以用来放大
        width = size[0]
        height = int(float(size[0]) *  image_size[1] / image_size[0])
    else:
        width = int(float(size[0]) *  image_size[0] / image_size[1])
        height = size[1]
    return (width, height)

def CaclImageBestScale(image, size):    
    new_size = CaclImageBestSize(image, size)
    result = float(new_size[0]) / image.GetSize()[0]
    if result > 1:
        result = 1
    return result