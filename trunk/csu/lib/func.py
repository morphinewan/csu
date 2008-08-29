# -*- coding: utf-8 -*-
import re
ImageTypes = (".jpg", ".jpeg", ".bmp",".gif", ".png")
def RGB2Hex(rgb):
    return "%02X%02X%02X" % rgb

def Hex2RGB(hex):
    return (int(hex[0:2], 16), int(hex[2:4], 16), int(hex[4:6], 16))

def IsFloat(s):
    pattern = '^[1-9]\d*\.\d*$|^0\.\d*[1-9]\d*$|^[1-9]\d*$'
    return re.search(pattern, s) != None

def IsInt(s):
    pattern = '^[1-9]\d*$'
    return re.search(pattern, s) != None