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

(PICropSideStartEvent, EVT_PI_CROPSIDE_START) = wx.lib.newevent.NewEvent()
(PICropSideEndEvent, EVT_PI_CROPSIDE_END) = wx.lib.newevent.NewEvent()
(PICropSidingEvent, EVT_PI_CROPSIDING) = wx.lib.newevent.NewEvent()

(PIAntiNoiseStartEvent, EVT_PI_ANTINOISE_START) = wx.lib.newevent.NewEvent()
(PIAntiNoiseEndEvent, EVT_PI_ANTINOISE_END) = wx.lib.newevent.NewEvent()
(PIAntiNoisingEvent, EVT_PI_ANTINOISING) = wx.lib.newevent.NewEvent()

(PIAntiBGColourStartEvent, EVT_PI_ANTIBGCOLOUR_START) = wx.lib.newevent.NewEvent()
(PIAntiBGColourEndEvent, EVT_PI_ANTIBGCOLOUR_END) = wx.lib.newevent.NewEvent()
(PIAntiBGColouringEvent, EVT_ANTIBGCOLOURING) = wx.lib.newevent.NewEvent()

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
        self.__stitchconvas = None
        #颜色映射表
        self.__flossmap = flossmap
        #定义事件发送对象
        self.__sender = sender
        
        self.__BoldGridLinePerStitch = 10  #多少格子显示粗线条
        self.__NormalGridLineWidth = 1     #普通线条宽度
        self.__BoldGridLineWidth = 5      #粗线条宽度
        self.__StitchSize = 22             #一个格子占据多少像素
        
        self.__MaxColorNumber = 150 #支持最多的颜色数        
        
        #绣图标记
        self.__Symbols = range(0x0030, 0x005B)
        self.__Symbols.extend(range(0x0061, 0x007B))
        self.__Symbols.extend(range(0x2190, 0x2199))
        self.__Symbols.extend(range(0x2460, 0x2500))
        
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
    
    def GetStitchConvas(self):
        '''
        取得绣图
        '''
        return self.__stitchconvas
    
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
        self.__stitchconvas = self.__GetStitchConvas(self.__previewimage, dic_args)        
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
        #替换调色板
        wx.PostEvent(self.__sender, PIColourTableChangeStartEvent())       
        new_im = self.__ChangeColorTable(new_im)
        wx.PostEvent(self.__sender, PIColourTableChangeEndEvent())
        #减少颜色数
        new_im = self.__ReduceFloss(new_im, dic_args)
        wx.PostEvent(self.__sender, PIColourTableChangeEndEvent())
        #裁边
        if dic_args["CropSide"]:
            wx.PostEvent(self.__sender, PICropSideStartEvent())
            new_im = self.__CropSide(new_im)
            wx.PostEvent(self.__sender, PICropSideEndEvent())
        #反噪点
        if dic_args["AntiNoise"]:
            wx.PostEvent(self.__sender, PIAntiNoiseStartEvent())
            new_im = self.__AntiNoise(new_im)
            wx.PostEvent(self.__sender, PIAntiNoiseEndEvent())
        #除去背景相近颜色
        if dic_args["AntiBgColour"]:
            wx.PostEvent(self.__sender, PIAntiBGColourStartEvent())
            new_im = self.__AntiBgColor(new_im, dic_args["MixColourDist"])
            wx.PostEvent(self.__sender, PIAntiBGColourEndEvent())        
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
        
    def __CropSide(self, im):
        '''
        裁剪边框
        '''
        x1, y1, x2, y2 = 0, 0, im.GetWidth(), im.GetHeight()
        #处理顶部
        while self.__IsAllPixelBackgroundColor(im, row = y1):
            y1 += 1
        #处理底部
        while self.__IsAllPixelBackgroundColor(im, row = y2 - 1):
            y2 -= 1
        #处理左部
        while self.__IsAllPixelBackgroundColor(im, col = x1):
            x1 += 1
        #处理右部
        while self.__IsAllPixelBackgroundColor(im, col = x2 - 1):
            x2 -= 1
        return im.GetSubImage((x1, y1, x2, y2))
    
    def __IsAllPixelBackgroundColor(self, im, col = -1, row  = -1):
        '''
        检查某行某列是否为全空
        '''
        checkFlg = True
        if row > -1:
            for i in range(im.GetWidth()):
                if (im.GetRed(i, row), im.GetGreen(i, row), im.GetBlue(i, row)) != self.__BackgroundColor:
                    checkFlg = False
                    break
        elif col > -1:
            for i in range(im.GetHeight()):
                if (im.GetRed(col, i), im.GetGreen(col, i), im.GetBlue(col, i)) != self.__BackgroundColor:
                    checkFlg = False
                    break
        return checkFlg
    
    def __AntiNoise(self, im):
        '''
        反噪点
        '''
        total = im.GetWidth() * im.GetHeight()
        count = 0
        for i in range(im.GetWidth()):
            for j in range(im.GetHeight()):
                wx.PostEvent(self.__sender, PIAntiNoisingEvent(count=count, total=total))
                count += 1
                if i > 0 and (im.GetRed(i - 1, j), im.GetGreen(i - 1, j), im.GetBlue(i - 1, j)) != self.__BackgroundColor:
                    continue
                if j > 0 and (im.GetRed(i, j - 1), im.GetGreen(i, j - 1), im.GetBlue(i, j - 1)) != self.__BackgroundColor:
                    continue
                if i < im.GetWidth() - 1 and (im.GetRed(i + 1, j), im.GetGreen(i + 1, j), im.GetBlue(i + 1, j)) != self.__BackgroundColor:
                    continue
                if j < im.GetHeight() - 1 and (im.GetRed(i, j + 1), im.GetGreen(i, j + 1), im.GetBlue(i, j + 1)) != self.__BackgroundColor:
                    continue
                im.SetRGB(i, j, self.__BackgroundColor[0], self.__BackgroundColor[1], self.__BackgroundColor[2])
        return im
    
    def __AntiBgColor(self, im, dist):
        '''
        去除和背景颜色相近的颜色
        '''
        total = im.GetWidth() * im.GetHeight()
        count = 0
        for i in range(im.GetWidth()):
            for j in range(im.GetHeight()):
                wx.PostEvent(self.__sender, PIAntiBGColouringEvent(count=count, total=total))
                count += 1
                if (im.GetRed(i, j), im.GetGreen(i, j), im.GetBlue(i, j)) != self.__BackgroundColor \
                    and Common.GetRGBDistance((im.GetRed(i, j), im.GetGreen(i, j), im.GetBlue(i, j)), self.__BackgroundColor) <= dist:
                    im.SetRGB(i, j, self.__BackgroundColor[0], self.__BackgroundColor[1], self.__BackgroundColor[2])
        return im
        
    def __GetStitchConvas(self, source_im, dic_args, mask_dic = None):
        '''
        转换绣图，带边框
        '''
        w, h = source_im.GetWidth(), source_im.GetHeight()
        #计算带边框后的图像像素值
        #1.扩大像素为马赛克块后的数值
        w_total = w * (self.__StitchSize + self.__NormalGridLineWidth) #加上右边和下边两条边框
        h_total = h * (self.__StitchSize + self.__NormalGridLineWidth)
        #如果宽度大于一个基本的格子，则开始计算粗线条（默认整体图片边框为非粗线条）
        if w > self.__BoldGridLinePerStitch:        
            if w % self.__BoldGridLinePerStitch:  
                #如果宽度不能整除格子宽度，则表示图像内部的粗线条数等于格子数       
                w_total = w_total + (w // self.__BoldGridLinePerStitch) * (self.__BoldGridLineWidth - self.__NormalGridLineWidth) 
            else:
                #如果宽度整除格子宽度，则表示图像内部的粗线条数等于格子数-1
                w_total = w_total + (w // self.__BoldGridLinePerStitch - 1) * (self.__BoldGridLineWidth - self.__NormalGridLineWidth)
        if h > self.__BoldGridLinePerStitch:
            if h % self.__BoldGridLinePerStitch:            
                h_total = h_total + (h // self.__BoldGridLinePerStitch) * (self.__BoldGridLineWidth - self.__NormalGridLineWidth)
            else:
                h_total = h_total + (h // self.__BoldGridLinePerStitch - 1) * (self.__BoldGridLineWidth - self.__NormalGridLineWidth)
        #再处理顶部和左部的边框，默认为细边框
        w_total = w_total + self.__BoldGridLineWidth * 2 - self.__NormalGridLineWidth
        h_total = h_total + self.__BoldGridLineWidth * 2 - self.__NormalGridLineWidth
        #根据最新的大小，新建一个图像
        im = wx.EmptyImage(w_total, h_total)
        #第一行第一列定位
        x = y = self.__BoldGridLineWidth
        for j in range(h):
            for i in range(w):
                #循环处理各行各列
                if mask_dic:
                    #如果参数mask_dic存在的话，则表示这是在输出正式绣图
                    if (source_im.GetRed(i, j), source_im.GetGreen(i, j), source_im.GetBlue(i, j)) == self.__BackgroundColor:
                        if dic_args["DisabledBgColour"]:#如果禁止输出背景色，则输出白色
                            im.SetRGBRect(wx.Rect(x, y, self.__StitchSize, self.__StitchSize), 255, 255, 255)
                        else:
                            im.SetRGBRect(wx.Rect(x, y, self.__StitchSize, self.__StitchSize), \
                                          source_im.GetRed(i, j), source_im.GetGreen(i, j), source_im.GetBlue(i, j))
                    else:
                        mask = mask_dic[(source_im.GetRed(i, j), source_im.GetGreen(i, j), source_im.GetBlue(i, j))]
                        im.SetRGBRect(wx.Rect(x, y, x + self.__StitchSize, y + self.__StitchSize), mask[0], mask[1], mask[2])
                else:
                    #否则则是在输出预览图
                    im.SetRGBRect(wx.Rect(x, y, self.__StitchSize, self.__StitchSize), \
                                          source_im.GetRed(i, j), source_im.GetGreen(i, j), source_im.GetBlue(i, j))
                #加上绣格块宽度
                x = x + self.__StitchSize
                #如果下一列正好是新的一块开始格子，则横坐标必须加上粗线条宽度
                if (i + 1) % self.__BoldGridLinePerStitch:
                    x = x + self.__NormalGridLineWidth
                else:
                    #否则加上细线条
                    x = x + self.__BoldGridLineWidth
            #初始化横坐标
            x = self.__BoldGridLineWidth
            #加上绣格块宽度
            y = y + self.__StitchSize
            #如果下一列正好是新的一块开始格子，则纵坐标必须加上粗线条宽度
            if (j + 1) % self.__BoldGridLinePerStitch:
                y = y + self.__NormalGridLineWidth
            else:
                #否则加上细线条
                y = y + self.__BoldGridLineWidth
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