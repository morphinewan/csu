# -*- coding: utf-8 -*-
import sys,os
import wx
import func as Common

class FlossMap():
    '''
    颜色映射表
    '''       
    def __init__(self):
        self.__savedFlg = True
        self.__fl = None
    
    def Load(self, callback = None):
        '''
        加载flossmap
        '''
        if not self.__fl:
            self.__fl = self.__LoadMap()
            if callback:
                callback()
    
    def __LoadMap(self):
        '''
        加载颜色映射表
        程序中使用的都是RGB形式，保存为Hex形式
        '''
        path = os.path.realpath(os.path.split(sys.argv[0])[0] + '/FlossMap.txt')
        if not os.path.exists(path):
            f = open(path, 'w')
            f.close()        
        fo = open(path)
        try:
            lines = fo.readlines()
        finally:
            fo.close()
        result = {}
        for i in range(0, len(lines)):
            values = lines[i].split('=')
            if not result.has_key(values[0]):
                result[Common.Hex2RGB(values[0])] = Common.Hex2RGB(values[1])
        return result
    
    def AppendData(self, key, value):
        '''
        增加映射关系
        '''
        self.__fl[key] = value
        #一旦增加过键值对，则标志为未保存状态
        self.__savedFlg = False
    
    def SaveData(self):
        '''
        保存数据
        '''
        if not self.__savedFlg:
            result = ''
            for k, v in self.__fl.iteritems():
                result += Common.RGB2Hex(k) + "=" + Common.RGB2Hex(v) + "\n"            
            fo = open('FlossMap.txt', 'w')
            try:
                fo.write(result)
            finally:
                fo.close()
                
    
    def GetValue(self, key):
        '''
        检索映射颜色
        '''
        if self.__fl.has_key(key):
            return self.__fl[key]
        else:
            return None

class CrossStitch():
    '''
    十字绣对象
    '''
    def __init__(self, filename):
        #定义原图
        self.__sip = filename
        self.__si = wx.Image(self.__sip)
        
    def GetSourceImage(self):
        '''
        获取原图
        '''
        return self.__si
    
    def GetSourceImageFileName(self):
        '''
        获取原图文件名
        '''
        return self.__sip
    
    def Destroy(self):
        '''
        注销对象
        '''
        self.__si.Destroy()
        del self.__si
        del self.__sip
        
    def GetPreviewImage(self):
        pass
        
class Logger():
    '''
    Log记录器, 抽象类
    '''
    def Log(self, content):
        pass
    
    def Clear(self):
        pass