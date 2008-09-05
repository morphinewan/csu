# -*- coding: utf-8 -*-
import sys,os
import wx
import wx.lib.newevent
import time
import func as Common

(FlossMapLoadedEvent, EVT_FLOSSMAP_LOADED) = wx.lib.newevent.NewEvent()

(PIGenerateStartEvent, EVT_PI_GENERATE_START) = wx.lib.newevent.NewEvent()
(PIGenerateEndEvent, EVT_PI_GENERATE_END) = wx.lib.newevent.NewEvent()
(PIResizedEvent, EVT_PI_RESIZED) = wx.lib.newevent.NewEvent()
(PIColourTableChangeStartEvent, EVT_PI_COLOURTABLE_CHANGE_START) = wx.lib.newevent.NewEvent()
(PIColourTableChangeEndEvent, EVT_PI_COLOURTABLE_CHANGE_END) = wx.lib.newevent.NewEvent()
(PIColourTableChangingEvent, EVT_PI_COLOURTABLE_CHANGING) = wx.lib.newevent.NewEvent()

(PIColourDistMixStartEvent, EVT_PI_COLOUR_DIST_MIX_START) = wx.lib.newevent.NewEvent()
(PIColourDistMixEndEvent, EVT_PI_COLOUR_DIST_MIX_END) = wx.lib.newevent.NewEvent()
(PIColourDistMixingEvent, EVT_PI_COLOUR_DIST_MIXING) = wx.lib.newevent.NewEvent()

(PIMaxColourNumReduceStartEvent, EVT_PI_MAX_COLOUR_NUM_REDUCE_START) = wx.lib.newevent.NewEvent()
(PIMaxColourNumReduceEndEvent, EVT_PI_MAX_COLOUR_NUM_REDUCE_END) = wx.lib.newevent.NewEvent()
(PIMaxColourNumReducingEvent, EVT_PI_MAX_COLOUR_NUM_REDUCING) = wx.lib.newevent.NewEvent()

(PIMinFlossNumReduceStartEvent, EVT_PI_MIN_FLOSS_NUM_REDUCE_START) = wx.lib.newevent.NewEvent()
(PIMinFlossNumReduceEndEvent, EVT_PI_MIN_FLOSS_NUM_REDUCE_END) = wx.lib.newevent.NewEvent()
(PIMinFlossNumReducingEvent, EVT_PI_MIN_FLOSS_NUM_REDUCING) = wx.lib.newevent.NewEvent()


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
    def __init__(self, sender):
        self.__savedFlg = True
        self.__fl = None
        self.__sender = sender
    
    def Load(self):
        '''
        加载flossmap
        '''
        if not self.__fl:
            self.__fl = Common.LoadFromDisk(Common.GetAppPath() + "/flossmap.dat")
            if not self.__fl:
                self.__fl = {}
            wx.PostEvent(self.__sender, FlossMapLoadedEvent())
    
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
    def __init__(self, filename, flossmap, sender):
        #定义原图
        self.__sourceimage = (filename, wx.Image(filename))
        #定义预览图
        self.__previewimage = None
        #颜色映射表
        self.__flossmap = flossmap
        #定义事件发送对象
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
            
    def GetPreviewImage(self):
        '''
        取得预览图
        '''       
        return self.__previewimage
    
    def GeneratePreviewImage(self, dic_args):
        '''
        #生成预览图片
        '''
        wx.PostEvent(self.__sender, PIGenerateStartEvent())
        #处理背景色
        rgb = Common.Hex2RGB(dic_args["BgColour"])
        self.__BackgroundColor = self.__GetMinDistanceColor(rgb[0], rgb[1], rgb[2])
        #生成图片
        self.__previewimage = self.__GeneratePreviewImage(dic_args)
        wx.PostEvent(self.__sender, PIGenerateEndEvent())
        
    def GetFlossSummary(self):
        result = []
        for floss in self.__GetFlossSummary(self.GetPreviewImage()):
            result.append([COLOR_TABLE[floss[0]], floss[1]])
        return result
      
    def __GeneratePreviewImage(self, dic_args):
        '''
        根据参数作成预览图
        '''
        im = self.__sourceimage[1]
        #计算绣图像素级大小
        (w, h) = self.__GetStitchSize(im.GetSize(), dic_args)
        #把原图片按照格子数重新Resize
        new_im = im.Scale(w, h)
        wx.PostEvent(self.__sender, PIResizedEvent(width=w, height=h))
        wx.PostEvent(self.__sender, PIColourTableChangeStartEvent())
        #替换调色板
        new_im = self.__ChangeColorTable(new_im)
        #减少颜色数
        new_im = self.__ReduceFloss(new_im, dic_args)
        wx.PostEvent(self.__sender, PIColourTableChangeEndEvent())
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
                evt = PIColourTableChangingEvent(min=min, max=max, pos=pos)
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
    
    def __GetFlossSummary(self, im):
        '''
        求绣线使用统计
              返回按使用量来倒序排列的dic
        '''
        result = {}
        for x in range(im.GetWidth()):
            for y in range(im.GetHeight()):
                rgb = (im.GetRed(x, y), im.GetGreen(x, y), im.GetBlue(x, y))
                if rgb != self.__BackgroundColor:
                    if result.has_key(rgb):
                        result[rgb] += 1
                    else:
                        result[rgb] = 1
        #根据数量排序返回数据，格式为 （(r,g,b), number)
        return sorted(result.items(), key = lambda i : i[1])
    
    def __MergePixelColor(self, im, rgb):     
        '''
        将图片中的特定颜色和周围颜色混合
        '''
        #搜索所有的像素点
        for x in range(im.GetWidth()):
            for y in range(im.GetHeight()):
                if (im.GetRed(x, y), im.GetGreen(x, y), im.GetBlue(x, y)) == rgb:
                    #找到目标像素,寻找上下左右四个元素的颜色，按出现最多的颜色赋值   
                    result = [self.__BackgroundColor, sys.maxint]
                    #左边
                    if x != 0 and (im.GetRed(x - 1, y), im.GetGreen(x - 1, y), im.GetBlue(x - 1, y)) != rgb:
                        distence = Common.GetRGBDistance((im.GetRed(x, y), im.GetGreen(x, y), im.GetBlue(x, y)), 
                                                         (im.GetRed(x - 1, y), im.GetGreen(x - 1, y), im.GetBlue(x - 1, y)))
                        if distence < result[1]:
                            result[0] = (im.GetRed(x - 1, y), im.GetGreen(x - 1, y), im.GetBlue(x - 1, y))
                            result[1] = distence
                    #上边
                    if y != 0 and (im.GetRed(x, y - 1), im.GetGreen(x, y - 1), im.GetBlue(x, y - 1)) != rgb:
                        distence = Common.GetRGBDistance((im.GetRed(x, y), im.GetGreen(x, y), im.GetBlue(x, y)), 
                                                         (im.GetRed(x, y - 1), im.GetGreen(x, y - 1), im.GetBlue(x, y - 1)))
                        if distence < result[1]:
                            result[0] = (im.GetRed(x, y - 1), im.GetGreen(x, y - 1), im.GetBlue(x, y - 1))
                            result[1] = distence
                    #右边
                    if x != im.GetWidth() - 1 and (im.GetRed(x + 1, y), im.GetGreen(x + 1, y), im.GetBlue(x + 1, y)) != rgb:
                        distence = Common.GetRGBDistance((im.GetRed(x, y), im.GetGreen(x, y), im.GetBlue(x, y)), 
                                                         (im.GetRed(x + 1, y), im.GetGreen(x + 1, y), im.GetBlue(x + 1, y)))
                        if distence < result[1]:
                            result[0] = (im.GetRed(x + 1, y), im.GetGreen(x + 1, y), im.GetBlue(x + 1, y))
                            result[1] = distence
                    #下边
                    if y != im.GetHeight() - 1 and (im.GetRed(x, y + 1), im.GetGreen(x, y + 1), im.GetBlue(x, y + 1)) != rgb:
                        distence = Common.GetRGBDistance((im.GetRed(x, y), im.GetGreen(x, y), im.GetBlue(x, y)), 
                                                         (im.GetRed(x, y + 1), im.GetGreen(x, y + 1), im.GetBlue(x, y + 1)))
                        if distence < result[1]:
                            result[0] = (im.GetRed(x, y + 1), im.GetGreen(x, y + 1), im.GetBlue(x, y + 1))
                            result[1] = distence
                    im.SetRGB(x, y, result[0][0], result[0][1], result[0][2])
    
    def __ReduceFloss(self, im, dic_args):
        '''
        减少绣线数量
        '''
        summary = self.__GetFlossSummary(im)
        total = len(summary)
        count = 0
        if dic_args["MixColourDist"]:
            #合并颜色相近像素
            wx.PostEvent(self.__sender, PIColourDistMixStartEvent(total=total))
            mapping_table = {}#映射表
            for i in range(len(summary)):
                for j in range(i+1, len(summary)):
                    #如果两种颜色小于特定距离，则记录在映射表里面
                    dist = Common.GetRGBDistance(summary[i][0], summary[j][0])
                    if dist <= dic_args["MixColourDist"]:
                        if mapping_table.has_key(summary[i][0]):
                            #如果存在key，则判断是否距离更小
                            if mapping_table[summary[i][0]][1] > dist:
                                mapping_table[summary[i][0]] = [summary[j][0], dist]
                        else:
                            mapping_table[summary[i][0]] = [summary[j][0], dist]
            #统合映射表
            for item in mapping_table.iteritems():
                value = item[1]
                while mapping_table.has_key(value[0]):
                    value = mapping_table[value[0]]
                mapping_table[item[0]] = value
            total = len(mapping_table)
            for item in mapping_table.iteritems():
                #根据映射表，替代颜色
                im.Replace(item[0][0], item[0][1], item[0][2], item[1][0][0], item[1][0][1], item[1][0][2])
                wx.PostEvent(self.__sender, PIColourDistMixingEvent(total=total, count=count))
                count += 1
            summary = self.__GetFlossSummary(im)
            total = len(summary)
            count = 0
            wx.PostEvent(self.__sender, PIColourDistMixEndEvent(total=total))
        if dic_args["MaxColourNum"]  or dic_args["MinFlossNum"]:
            #取得绣线使用统计
            if dic_args["MaxColourNum"]:
                wx.PostEvent(self.__sender, PIMaxColourNumReduceStartEvent(total=total, param=dic_args["MaxColourNum"]))
                #限定最多使用线量
                #如果实际颜色数大于要求数
                total = len(summary) - dic_args["MaxColourNum"]
                while len(summary) > dic_args["MaxColourNum"]:
                    self.__MergePixelColor(im, summary[0][0])
                    wx.PostEvent(self.__sender, PIMaxColourNumReducingEvent(total=total, count=count))
                    count += 1
                    summary = self.__GetFlossSummary(im)
                total = len(summary)
                count = 0
                wx.PostEvent(self.__sender, PIMaxColourNumReduceEndEvent(total=total, param=dic_args["MaxColourNum"]))                
            if dic_args["MinFlossNum"]:                
                wx.PostEvent(self.__sender, PIMinFlossNumReduceStartEvent(total=total, param=dic_args["MinFlossNum"]))
                #剔除使用量少于特定值的线条
                #如果检索到数量大于特定值的，则跳出不做了
                while summary[0][1]  < dic_args["MinFlossNum"]:
                    self.__MergePixelColor(im, summary[0][0])
                    wx.PostEvent(self.__sender, PIMinFlossNumReducingEvent(total=total, count=count))
                    count += 1
                    summary = self.__GetFlossSummary(im)
                    if len(summary) == 0:
                        break
                total = len(summary)
                count = total
                wx.PostEvent(self.__sender, PIMinFlossNumReduceEndEvent(total=total, param=dic_args["MinFlossNum"])) 
        return im

def LoadColorTable():
    '''
    加载绣线颜色表
    '''
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