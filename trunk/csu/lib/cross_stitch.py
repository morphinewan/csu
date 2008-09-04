# -*- coding: utf-8 -*-
import sys,os
import wx
import wx.lib.newevent
import time
import func as Common

(UpdateCrossStitchEvent, EVT_UPDATE_CROSS_STITCH) = wx.lib.newevent.NewEvent()

EVENT_PREVIEW_GENERATING = 1
EVENT_PREVIEW_GENERATED = 2

class Floss():
    '''
    绣线
    '''
    def __init__(self, id, description, rgb):
        self.id = id
        self.description = description
        self.rgb = rgb
    
    def __str__(self):
        return "Floss Object\nId: %s\nDescription: %s\nRGB: %s" % (self.id, self.description, self.rgb)
    
    def CalcDistance(self, rgb):
        '''
        计算颜色之间的距离
        '''
        return Common.GetRGBDistance(rgb, self.rgb)  
    
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
            if not self.__fl:
                self.__fl = {}
            if callback:
                callback()
    
    def __LoadMap(self):
        '''
         加载颜色映射表
                程序中使用的都是RGB形式，保存为Hex形式
        '''
        return Common.LoadFromDisk(Common.GetAppPath() + "/flossmap.dat")
    
    def SaveData(self):
        Common.SaveToDisk(self.__fl, Common.GetAppPath() + "/flossmap.dat")
    
    def AppendData(self, key, value):
        '''
        增加映射关系
        '''
        self.__fl[key] = value
        #一旦增加过键值对，则标志为未保存状态
        self.__savedFlg = False                
    
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
    def __init__(self, filename, logger, flossmap, sender):
        #定义原图
        self.__sourceimage = (filename, wx.Image(filename))
        #定义预览图
        self.__previewimage = None
        #定义日志记录器
        self.__logger = logger
        #颜色映射表
        self.__flossmap = flossmap
        self.__sender = sender
        
    def GetSourceImage(self):
        '''
        获取原图
        '''
        return self.__sourceimage[1]
    
    def GetSourceImageFileName(self):
        '''
        获取原图文件名
        '''
        return self.__sourceimage[0]
    
    def Destroy(self):
        '''
        注销对象
        '''
        self.__sourceimage[1].Destroy()
        del self.__sourceimage
        
        if self.__previewimage:
            self.__previewimage.Destroy()
            del self.__previewimage
            
    def GeneratePreviewImage(self, dic_args):
        '''
        #生成预览图片
        '''
        self.__previewimage = self.__GeneratePreviewImage(dic_args)
        #完成事件
        evt = UpdateCrossStitchEvent(type=EVENT_PREVIEW_GENERATED)
        wx.PostEvent(self.__sender, evt)
        
    def GetPreviewImage(self):
        '''
        取得预览图
        '''
        #如果传递参数，则重新做成预览图       
        if self.__previewimage:
            return self.__previewimage
        else:
            return None
    
      
    def __GeneratePreviewImage(self, dic_args):
        '''
        根据参数作成预览图
        '''
        self.__logger.Clear()
        im = self.__sourceimage[1]
        #计算绣图像素级大小
        (w, h) = self.__GetStitchSize(im.GetSize(), dic_args)
        #把原图片按照格子数重新Resize
        self.__logger.Log(u"调整分辨率大小为(%d, %d)" % (w, h))
        new_im = im.Scale(w, h)
        self.__logger.Log(u"更换图片调色板为绣图专用DMC颜色")
        new_im = self.__ChangeColorTable(new_im)
        
        return new_im
    
    def __GetStitchSize(self, size, dic_args):
        #没有设置输出大小，默认为宽度200格
        width = 200
        height = 200
        p_size = (dic_args["Width"], dic_args["Height"])
        if p_size[0].count("cm") > 0:
            #厘米为长度的场合,折算一下，厘米折算成英寸
            p_size[0] = p_size[0].replace("cm", "")
            p_size[0] = "%0.2finches" % (float(p_size[0]) / 2.45)
        if p_size[1].count("cm") > 0:
            #厘米为长度的场合,折算一下，厘米折算成英寸
            p_size[1] = p_size[1].replace("cm", "")
            p_size[1] = "%0.2finches" % (float(p_size[1]) / 2.45)
        ct = dic_args["CT"]
        if p_size[0].count("inches") > 0:
            #英寸为长度的场合,折算一下，英寸折算成格子
            p_size[0] = p_size[0].replace("inches", "")
            p_size[0] = math.ceil(float(p_size[0]) * ct)
        if p_size[1].count("inches") > 0:
            #英寸为长度的场合,折算一下，厘米折算成格子
            p_size[1] = p_size[1].replace("inches", "")
            p_size[1] = math.ceil(float(p_size[1]) * ct)
        #如果宽度有效
        if p_size[0] != '0' and p_size[1] == '0':
            width = int(p_size[0])
            height = width * size[1] // size[0]
        #如果高度有效
        elif p_size[0] == '0' and p_size[1] != '0':
            height = int(p_size[1])
            width = height * size[0] // size[1]
        #如果宽度高度都有效，则看长宽比
        elif p_size[0] != '0' and p_size[1] != '0':
            if float(p_size[0]) / float(p_size[1]) > float(size[0]) / float(size[1]):
                width = int(p_size[0])
                height = width * size[1] // size[0]
            else:
                height = int(p_size[1])
                width = height * size[0] // size[1]
        else:
            height = 200 * size[1] // size[0]
        
        return (width, height)

    def __ChangeColorTable(self, im):
        '''
        将图片的颜色表替换成绣图专用颜色
        '''
        min = 0
        max = im.GetWidth() * im.GetHeight() - 1
        pos = 0
        #逐个分析各个像素的颜色，找到颜色表内对应最接近的颜色替代
        for x in range(im.GetWidth()):
            for y in range(im.GetHeight()):
                rgb = self.__GetMinDistanceColor(im.GetRed(x, y), im.GetGreen(x, y), im.GetBlue(x, y))
                im.SetRGB(x, y, rgb[0], rgb[1], rgb[2])
                evt = UpdateCrossStitchEvent(type=EVENT_PREVIEW_GENERATING, min=min, max=max, pos=pos)
                wx.PostEvent(self.__sender, evt)
                pos += 1
        #保存颜色映射表
        self.__flossmap.SaveData()
        return im
    
    def __GetMinDistanceColor(self, red, green, blue):
        '''
        求颜色表中距离目标颜色最短的颜色
        '''
        if self.__flossmap.GetValue((red, green, blue)):
            #如果在颜色映射表里面已经存在，则直接返回该颜色
            return self.__flossmap.GetValue((red, green, blue))
        else:
            min = [(255,255,255), sys.maxint] #定义一个初始值，距离为-1
            for floss in COLOR_TABLE.itervalues():
                dis = floss.CalcDistance((red, green, blue))
                #如果距离小于上一个值，则替代之
                if dis < min[1]:
                    min[0] = floss.rgb
                    min[1] = dis
                if dis == 0:
                    break
            #将该映射关系补充道颜色映射表中
            self.__flossmap.AppendData((red, green, blue), min[0])
            return min[0] 
        
class Logger():
    '''
    Log记录器, 抽象类
    '''
    def Log(self, content):
        pass
    
    def Clear(self):
        pass
    
def LoadColorTable():
    '''
    加载绣线颜色表
    '''
    print "Loading Color Table"
    path = Common.GetAppPath() + "/colortable.dat"
    if os.path.exists(path) and os.path.isfile(path):
        result = Common.LoadFromDisk(path)
    else:
        lines = open(Common.GetAppPath() + "/Color_Table/DMC.txt").readlines()
        if len(lines) % 3:
            raise Exception("DMC.txt contains some error.")
        result = {}
        for i in range(len(lines) // 3 - 1):
            id = lines[i * 3][:-1]        
            description = lines[i * 3 + 1][:-1]
            colors = lines[i * 3 + 2].split(',')        
            rgb = (int(colors[0]), int(colors[1]), int(colors[2]))
            result[rgb] = Floss(id, description, rgb)
        Common.SaveToDisk(result, path)
    return result
        
COLOR_TABLE = LoadColorTable()