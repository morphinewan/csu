# -*- coding: utf-8 -*-
import os, sys
import math
import tkMessageBox
import re
ImageTypes = (".jpg", ".jpeg", ".bmp",".gif", ".png")

def IsValidPath(path):
    '''
    测试路径是否存在
    '''
    return os.path.isdir(path) and os.path.exists(path)

def GetAllImageFile(path):
    '''
        根据路径，获取路径下所有图片文件
    '''
    result = []
    #如果路径是文件的话，则取该文件所在的路径进行迭代
    if os.path.isfile(path):
        path = os.path.split(path)[0]
    for path,subPaths,files in os.walk(path):
        if not path.endswith('\output'):
            for fileName in files:
                fullPath = path + "\\" + fileName
                pair = os.path.splitext(fullPath)
                if pair[1] is not None:
                    if pair[1].lower() in ImageTypes:
                        result.append(fullPath)
    return result

def MakeOutputPath(target):
    '''
    建立输出目录
    '''
    p = os.path.split(target)
    outputPath = p[0] + "\\" + "output"
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    else:
        if not os.path.isdir(outputPath):
                raise Exception(u"输出目标不是目录。")
    return outputPath

def GetOutputFileName(path, outputPath, suffix = None, extation = None):
    '''
    从目标文件名得到存储路径中的文件名
    '''
    if not os.path.isfile(path):
        return None
    fileName = os.path.split(path)[1]
    extensionName =  os.path.splitext(path)[1]
    fileName = fileName[:len(fileName) - len(extensionName)]
    result = outputPath + "\\" + fileName
    if suffix:
        result += '(' + suffix + ')'
    if extation:
        result += extation
    else:
        result += extensionName
    return result

def GetFileName(path):
    '''
    获得文件名
    '''
    if not os.path.isfile(path):
        return None
    fileName = os.path.split(path)[1]
    return fileName

def RGB2Hex(rgb):
    return "%02X%02X%02X" % rgb

def Hex2RGB(hex):
    return (int(hex[0:2], 16), int(hex[2:4], 16), int(hex[4:6], 16))

def GetRGBDistance(rgb1, rgb2):
    return math.sqrt((rgb1[0] - rgb2[0])**2 + (rgb1[1] - rgb2[1])**2 + (rgb1[2] - rgb2[2])**2)

def Log(content):
    print content

def IsFloat(s):
    pattern = '^[1-9]\d*\.\d*|0\.\d*[1-9]\d*|[1-9]\d*$'
    return re.search(pattern, s) != None
def IsInt(s):
    pattern = '^[1-9]\d*$'
    return re.search(pattern, s) != None

def ShowError(message, title = None):
    tkMessageBox.showerror(title or Message["MF201"], message)

def ShowInfo(message, title = None):
    tkMessageBox.showinfo(title or Message["MF214"], message)
Message = {
           #主窗口字符串定义
           "MF001" : u"十字绣转换程序 morphinewan荣誉出品",   #主窗口标题
#           "MF002" : u"选择目录：",   #主窗口Label
           "MF003" : u"最高颜色数",   #主窗口Label
           "MF004" : u"最低颜色数",   #主窗口Label
           "MF005" : u"背景颜色：",   #主窗口Label
           "MF006" : u"切边",   #主窗口Label
           "MF007" : u"去除噪点",   #主窗口Label
           "MF008" : u"去除背景色",   #主窗口Label
           "MF009" : u"只输出预览图",   #主窗口Label
           "MF010" : u"生成淘宝上传专用预览图片",   #主窗口Label
           "MF011" : u"禁止输出背景色",   #主窗口Label
           "MF012" : u"打印图片缩放比例",   #主窗口Label
           "MF013" : u"预览图片缩放比例",   #主窗口Label
           "MF014" : u"宽度",   #主窗口Label
           "MF015" : u"高度",   #主窗口Label
           "MF016" : u"ct",   #主窗口Label
           "MF017" : u"混合颜色距离",   #主窗口Label
           
           "MF101" : u"浏览...",   #主窗口Button
           "MF102" : u"转换",   #主窗口Button
           "MF103" : u"关闭",   #主窗口Button
           "MF104" : u"批量转换",   #主窗口Button
           
           "MF201" : u"错误",   #系统字符串
           "MF202" : u"%s输入值无效。",   #系统字符串
           "MF203" : u"图片目前有%d种颜色。",   #系统字符串
           "MF204" : u"文件%s开始转换......",   #系统字符串
           "MF205" : u"调整分辨率大小为(%d, %d)。",   #系统字符串
           "MF206" : u"更换图片调色板为绣图专用DMC颜色。",   #系统字符串
           "MF207" : u"减少绣线颜色数量到最多%d种。",   #系统字符串
           "MF208" : u"绣线使用量不足%d格子的颜色合并到其他颜色中。",   #系统字符串
           "MF209" : u"裁剪图片四周多余无用的空格。",   #系统字符串
           "MF210" : u"去除图片中的噪点。",   #系统字符串
           "MF211" : u"去除接近背景色的像素。",   #系统字符串
           "MF212" : u"输出预览图。",   #系统字符串
           "MF213" : u"所有图片转换完毕。",   #系统字符串
           "MF214" : u"信息",   #系统字符串
           "MF215" : u"加载系统配置中，请稍候。",   #系统字符串
           "MF216" : u"输出用线统计。",   #系统字符串
           "MF217" : u"使用线量大于定义的符号数。",   #系统字符串
           "MF218" : u"输出带标识的正式绣图。",   #系统字符串
           "MF219" : u"输出符号对照表。",   #系统字符串
           "MF220" : u"文件%s转换完毕。",   #系统字符串
           "MF221" : u"加载系统配置完毕，您可以开始操作。",   #系统字符串
           "MF222" : u"合并颜色相近像素。",   #系统字符串
           
           "MF301" : u"绣线颜色表%s存在错误。",   #系统字符串
           "MF302" : u"请选择需要处理的文件路径。",   #系统字符串
           
           "MF401" : u"打开文件...",  #菜单项
           "MF402" : u"打开目录...",  #菜单项
           "MF403" : u"退出",  #菜单项
           "MF404" : u"文件",  #菜单项
           "MF405" : u"帮助",  #菜单项
           "MF406" : u"关于...",  #菜单项
           }

def main():
    print GetRGBDistance((227,216,201),(176,160,124))

if __name__ == '__main__':
    main()
    
