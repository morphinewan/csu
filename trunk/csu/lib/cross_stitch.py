# -*- coding: utf-8 -*-
import sys,os
import wx
import math
import time
import func as Common
from cross_stitch_event import *

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
        self.__printconvas = None
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
        
        #转换条件
        self.__args = None
        #历史记录
        self._history = []
        
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
        
        if self.__stitchconvas:
            self.__stitchconvas.Destroy()
            del self.__stitchconvas
            
        if self.__printconvas:
            self.__printconvas.Destroy()
            del self.__printconvas
            
        for item in self._history:
            item.Destroy()            
        self._history = []
            
    def GetPreviewImage(self):
        '''
        取得预览图
        '''       
        return self.__previewimage
    
    def GetStitchConvas(self):
        '''
        取得绣图视图1  带格子线
        '''
        return self.__stitchconvas
    
    def GetPrintConvas(self):
        '''
        取得绣图视图2  带格子线和符号
        '''
        return self.__printconvas
        
    def GeneratePreviewImage(self, dic_args):
        '''
        #生成预览图片
        '''
        wx.PostEvent(self.__sender, PIGenerateStartEvent())
        #清楚历史记录
        if not hasattr(self, "_history"):
            for item in self._history:
                item.Destroy()            
            self._history = []
        
        #处理背景色
        rgb = Common.Hex2RGB(dic_args["BgColour"])
        self.__BackgroundColor = self.__GetMinDistanceColor(rgb[0], rgb[1], rgb[2])
        #保存参数
        self.__args = dic_args
        #生成图片
        self.__previewimage = self.__GeneratePreviewImage()
        wx.PostEvent(self.__sender, PIGenerateEndEvent())
        #如果只是生成预览，则不生成2个视图
        if not self.__args["OnlyPreview"]:
            self.GenerateStitchConvas()
            self.GeneratePrintConvas()
            
    def GenerateStitchConvas(self):
        '''
        生成视图1
        '''
        wx.PostEvent(self.__sender, PIStitchConvasGenerateStartEvent())
        self.__stitchconvas = self.__GetStitchConvas()
        wx.PostEvent(self.__sender, PIStitchConvasGenerateEndEvent())
    
    def GeneratePrintConvas(self):
        '''
        生成视图2
        '''
        wx.PostEvent(self.__sender, PIPrintConvasGenerateStartEvent())
        self.__printconvas = self.__GetPrintConvas()     
        wx.PostEvent(self.__sender, PIPrintConvasGenerateEndEvent())
    
    def SaveCrossStitch(self, outputPath, dic_args):
        '''
        保存绣品文件
        '''
        #如果还没有生成打印文件，则生成一下
        if not self.GetPreviewImage():
            self.GeneratePreviewImage(dic_args)
            
        #将打印图片分页处理
        images = self.__GetPrintPages()
        wx.PostEvent(self.__sender, PICrossStitchSaveStartEvent())
        count = 1
        total = len(images) + 3        
        #按比例缩略图
        preview_im = self.GetStitchConvas()
        if self.__args["ForTaobao"]:#淘宝上传专用图处理
            new_size = (preview_im.GetWidth(), preview_im.GetHeight())
            if new_size[0] > 500:
                new_size = (500, int(float(500 * new_size[1]) / new_size[0]))
            if new_size[1] > 500:
                new_size = (int(float(500 * new_size[0]) / new_size[1]), 500)
            preview_im = preview_im.Scale(new_size)
        elif self.__args["PreviewScale"]:#按比例缩图
            preview_im = preview_im.Scale(int(preview_im.GetWidth()* float(self.__args["PreviewScale"])), 
                        int(preview_im.GetHeight()* float(self.__args["PreviewScale"])))
        save_name = Common.GetOutputFileName(self.GetSourceImageFileName(), outputPath, suffix=u"预览图")
        preview_im.SaveFile(save_name, wx.BITMAP_TYPE_JPEG)
        preview_im.Destroy()
        del preview_im
        wx.PostEvent(self.__sender, PICrossStitchSavingEvent(count=count, total=total))
        count += 1
        
        #如果参数决定，则只输出预览图
        if self.__args["OnlyPreview"]:
            wx.PostEvent(self.__sender, PICrossStitchSaveEndEvent())
            return
        
        #如果还没有生成打印文件，则生成一下
        if not self.GetStitchConvas():
            self.GenerateStitchConvas()
        if not self.GetPrintConvas():
            self.GeneratePrintConvas()
        
        #输出用线统计
        s = self.__MakeFlossSummaryReport()
        fo = open(Common.GetOutputFileName(self.GetSourceImageFileName(), outputPath, suffix=u"统计", ext=".csv"), 'w')
        try:
            fo.write(unicode.encode(s, 'gb2312'))
        finally:
            fo.close()
        wx.PostEvent(self.__sender, PICrossStitchSavingEvent(count=count, total=total))
        count += 1
        
        #输出符号对照表
        symbol_im = self.__GetSymbolConvas()
        symbol_im = self.__AddWaterMark(symbol_im)
        symbol_im.SaveFile(Common.GetOutputFileName(self.GetSourceImageFileName(), outputPath, suffix=u"符号对照表"), wx.BITMAP_TYPE_JPEG)
        symbol_im.Destroy()
        del symbol_im
        wx.PostEvent(self.__sender, PICrossStitchSavingEvent(count=count, total=total))
        count += 1
        #分页打印        
        for p_im in images:
            #按比例缩略图
            if self.__args["PrintScale"]:
                p_im = p_im.Rescale(int(p_im.GetWidth()* float(self.__args["PrintScale"])), 
                            int(p_im.GetHeight()* float(self.__args["PrintScale"])))
            #加注版权水印
            p_im = self.__AddWaterMark(p_im)
            #增加页码
            p_im = self.__AddPageCount(p_im, count - 3, total - 3)
            #保存打印文件
            save_name = Common.GetOutputFileName(self.GetSourceImageFileName(), outputPath, suffix = u'绣图%s' % (count - 3))
            p_im.SaveFile(save_name, wx.BITMAP_TYPE_JPEG)
            p_im.Destroy()
            wx.PostEvent(self.__sender, PICrossStitchSavingEvent(count=count, total=total))
            count += 1
        wx.PostEvent(self.__sender, PICrossStitchSaveEndEvent())
    
    def RemoveColor(self, rgb):
        #移除特定颜色，将旧颜色加入履历
        self.__history.Append(self.GetPreviewImage())
        
        im = self.GetPreviewImage().Copy()
        im.Replace(rgb[0], rgb[1], rgb[2], self.__BackgroundColor[0], 
                   self.__BackgroundColor[1], self.__BackgroundColor[2])
        self.__previewimage = im
        
        #如果只是生成预览，则不生成2个视图
        if not self.__args["OnlyPreview"]:
            self.GenerateStitchConvas()
            self.GeneratePrintConvas()
    
    def ReplaceColor(self, flossids1, flossid2):
        #替代颜色
        self.__history.Append(self.GetPreviewImage())
        rgb2 = COLOR_TABLE2[flossid2]
        im = self.GetPreviewImage().Copy()
        for flossid in flossids1:
            rgb1 = COLOR_TABLE2[flossid]
            im.Replace(rgb1[0], rgb1[1], rgb1[2], 
                       rgb2[0], rgb2[1], rgb2[2])
        self.__previewimage = im
        
        #如果只是生成预览，则不生成2个视图
        if not self.__args["OnlyPreview"]:
            self.GenerateStitchConvas()
            self.GeneratePrintConvas()
        
    def __GeneratePreviewImage(self):
        '''
        根据参数作成预览图
        '''
        im = self.__sourceimage[1]
        #计算绣图像素级大小
        (w, h) = self.__GetStitchSize(im.GetSize())
        #把原图片按照格子数重新Resize
        new_im = im.Scale(w, h)
        wx.PostEvent(self.__sender, PIResizedEvent(width=w, height=h))
        #替换调色板
        wx.PostEvent(self.__sender, PIColourTableChangeStartEvent())       
        new_im = self.__ChangeColorTable(new_im)
        wx.PostEvent(self.__sender, PIColourTableChangeEndEvent())
        #减少颜色数
        self.__previewimage = new_im  #提前复制，以备计算线量
        new_im = self.__ReduceFloss(new_im)
        wx.PostEvent(self.__sender, PIColourTableChangeEndEvent())
        #裁边
        if self.__args["CropSide"]:
            wx.PostEvent(self.__sender, PICropSideStartEvent())
            new_im = self.__CropSide(new_im)
            wx.PostEvent(self.__sender, PICropSideEndEvent())
        #反噪点
        if self.__args["AntiNoise"]:
            wx.PostEvent(self.__sender, PIAntiNoiseStartEvent())
            new_im = self.__AntiNoise(new_im)
            wx.PostEvent(self.__sender, PIAntiNoiseEndEvent())
        #除去背景相近颜色
        if self.__args["AntiBgColour"]:
            wx.PostEvent(self.__sender, PIAntiBGColourStartEvent())
            new_im = self.__AntiBgColor(new_im, self.__args["MixColourDist"])
            wx.PostEvent(self.__sender, PIAntiBGColourEndEvent())        
        return new_im
    
    def __GetStitchSize(self, size):
        #没有设置输出大小，默认为宽度200格
        width = 200
        height = 200
        p_size = [self.__args["Width"], self.__args["Height"]]
        if p_size[0].count("cm") > 0:
            #厘米为长度的场合,折算一下，厘米折算成英寸
            p_size[0] = p_size[0].replace("cm", "")
            p_size[0] = "%0.2finches" % (float(p_size[0]) / 2.45)
        if p_size[1].count("cm") > 0:
            #厘米为长度的场合,折算一下，厘米折算成英寸
            p_size[1] = p_size[1].replace("cm", "")
            p_size[1] = "%0.2finches" % (float(p_size[1]) / 2.45)
        ct = self.__args["CT"]
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
        
#    def __GetMinDistanceColor(self, red, green, blue):
#        '''
#        求颜色表中距离目标颜色最短的颜色
#        '''
#        if self.__flossmap.GetValue((red, green, blue)):
#            #如果在颜色映射表里面已经存在，则直接返回该颜色
#            return self.__flossmap.GetValue((red, green, blue))
#        else:
#            if COLOR_TABLE.has_key((red, green, blue)):
#                return (red, green, blue)
#            else:
#                for dist in range(0, 256): 
#                    for i in range((lambda x: (x -dist <= 0 and [0] or [x-dist])[0])(red), 
#                                (lambda x: (x + dist >= 255 and [255] or [x + dist])[0])(red) + 1):
#                        for j in range((lambda x: (x -dist <= 0 and [0] or [x-dist])[0])(green), 
#                                (lambda x: (x + dist >= 255 and [255] or [x + dist])[0])(green) + 1):
#                            for k in range((lambda x: (x -dist <= 0 and [0] or [x-dist])[0])(blue), 
#                                (lambda x: (x + dist >= 255 and [255] or [x + dist])[0])(blue) + 1):
#                                
#                                if COLOR_TABLE.has_key((i, j, k)):
#                                    print "bingo"
#                                    return (i, j, k)
#                                else:
#                                    print (i, j, k)
            
    
    def GetFlossSummary(self):
        '''
        求绣线使用统计
              返回按使用量来倒序排列的dic
        '''
        result = {}
        im = self.GetPreviewImage()
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
    
    def __ReduceFloss(self, im):
        '''
        减少绣线数量
        '''
        summary = self.GetFlossSummary()
        total = len(summary)
        count = 1
        if  self.__args["MixColourDist"]:
            #合并颜色相近像素
            wx.PostEvent(self.__sender, PIColourDistMixStartEvent(total=total))
            mapping_table = {}#映射表
            for i in range(len(summary)):
                for j in range(i+1, len(summary)):
                    #如果两种颜色小于特定距离，则记录在映射表里面
                    dist = Common.GetRGBDistance(summary[i][0], summary[j][0])
                    if dist <= self.__args["MixColourDist"]:
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
            summary = self.GetFlossSummary()
            total = len(summary)
            count = 1
            wx.PostEvent(self.__sender, PIColourDistMixEndEvent(total=total))
        if self.__args["MaxColourNum"]  or self.__args["MinFlossNum"]:
            #取得绣线使用统计
            if self.__args["MaxColourNum"]:
                wx.PostEvent(self.__sender, PIMaxColourNumReduceStartEvent(total=total, param=self.__args["MaxColourNum"]))
                #限定最多使用线量
                #如果实际颜色数大于要求数
                total = len(summary) - self.__args["MaxColourNum"]
                while len(summary) > self.__args["MaxColourNum"]:
                    self.__MergePixelColor(im, summary[0][0])
                    wx.PostEvent(self.__sender, PIMaxColourNumReducingEvent(total=total, count=count))
                    count += 1
                    summary = self.GetFlossSummary()
                total = len(summary)
                count = 1
                wx.PostEvent(self.__sender, PIMaxColourNumReduceEndEvent(total=total, param=self.__args["MaxColourNum"]))                
            if self.__args["MinFlossNum"]:                
                wx.PostEvent(self.__sender, PIMinFlossNumReduceStartEvent(total=total, param=self.__args["MinFlossNum"]))
                #剔除使用量少于特定值的线条
                #如果检索到数量大于特定值的，则跳出不做了
                while summary[0][1]  < self.__args["MinFlossNum"]:
                    self.__MergePixelColor(im, summary[0][0])
                    wx.PostEvent(self.__sender, PIMinFlossNumReducingEvent(total=total, count=count))
                    count += 1
                    summary = self.GetFlossSummary()
                    if len(summary) == 0:
                        break
                total = len(summary)
                count = total
                wx.PostEvent(self.__sender, PIMinFlossNumReduceEndEvent(total=total, param=self.__args["MinFlossNum"])) 
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
        return im.GetSubImage((x1, y1, x2 - x1, y2 - y1))
    
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
        count = 1
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
        count = 1
        for i in range(im.GetWidth()):
            for j in range(im.GetHeight()):
                wx.PostEvent(self.__sender, PIAntiBGColouringEvent(count=count, total=total))
                count += 1
                if (im.GetRed(i, j), im.GetGreen(i, j), im.GetBlue(i, j)) != self.__BackgroundColor \
                    and Common.GetRGBDistance((im.GetRed(i, j), im.GetGreen(i, j), im.GetBlue(i, j)), self.__BackgroundColor) <= dist:
                    im.SetRGB(i, j, self.__BackgroundColor[0], self.__BackgroundColor[1], self.__BackgroundColor[2])
        return im
    
    def __GetStitchConvas(self):
        '''
        转换绣图，带边框
        '''
        source_im = self.GetPreviewImage()
        w, h = source_im.GetWidth()*self.__StitchSize, source_im.GetHeight()*self.__StitchSize
        im = source_im.Scale(w, h)
        #把背景色替换成白色
        if self.__args["DisabledBgColour"]:
            #如果禁止输出背景色，则替换
            im.Replace(self.__BackgroundColor[0], self.__BackgroundColor[1], self.__BackgroundColor[2], 255, 255, 255)
        dc = wx.MemoryDC()
        bitmap = wx.BitmapFromImage(im)
        dc.SelectObject(bitmap)
        normal_pen = wx.Pen((0, 0, 0), self.__NormalGridLineWidth)
        bold_pen = wx.Pen((0, 0, 0), self.__BoldGridLineWidth)
        event_total = w + h
        #画横线
        #第一行
        dc.SetPen(bold_pen)
        dc.DrawLine(0, 0, w, 0)
        #最后一行
        dc.DrawLine(0, h, w, h)
        event_count = 2       
        for row in range(1 , h):
            #画当中的线
            #普通线
            cell = row % self.__StitchSize
            if not cell:
                if row / self.__StitchSize % self.__BoldGridLinePerStitch:
                    dc.SetPen(normal_pen)
                else:
                #粗线
                    dc.SetPen(bold_pen)
                dc.DrawLine(0, row, w, row)
            wx.PostEvent(self.__sender, PIStitchConvasGeneratingEvent(total=event_total, count=event_count))
            event_count += 1
        #画纵线
        #第一列
        dc.SetPen(bold_pen)
        dc.DrawLine(0, 0, 0, h)
        #最后一列
        dc.DrawLine(w, 0, w, h)
        event_count += 2
        for col in range(1 , w):
            #画当中的线
            #普通线
            cell = col % self.__StitchSize
            if not cell:
                if col / self.__StitchSize % self.__BoldGridLinePerStitch:
                    dc.SetPen(normal_pen)
                else:
                #粗线
                    dc.SetPen(bold_pen)
                dc.DrawLine(col, 0, col, h)
            wx.PostEvent(self.__sender, PIStitchConvasGeneratingEvent(total=event_total, count=event_count))
            event_count += 1
        return bitmap.ConvertToImage()
    
    def __GetPrintConvas(self):
        '''
        转换绣图，带边框,带标记
        '''
        p_im = self.GetPreviewImage()
        mask_list = self.GetFlossMaskList()
        source_im = self.GetStitchConvas()
        w, h = p_im.GetWidth(), p_im.GetHeight()
        dc = wx.MemoryDC()
        bitmap = wx.BitmapFromImage(source_im.Copy())
        dc.SelectObject(bitmap)
        dc.SetFont(wx.Font(14,wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL,underline=0,encoding=wx.FONTENCODING_CP932))
        event_total = w * h
        event_count = 1
        for x in range(w):
            for y in range(h):
                rgb = (p_im.GetRed(x, y), p_im.GetGreen(x, y), p_im.GetBlue(x, y))
                if rgb != self.__BackgroundColor:
                    #不是背景色才有必要写标记
                    symbol = mask_list[rgb][1]
                    textsize = dc.GetTextExtent(symbol)
                    position = ((self.__StitchSize - textsize[0]) // 2, (self.__StitchSize - textsize[1]) // 2)
                    #如果颜色过于接近黑色，则用反色白色来填充
                    if Common.GetRGBDistance(rgb, (0,0,0)) < 200:
                        dc.SetTextForeground((255, 255, 255))
                    else:
                        dc.SetTextForeground((0, 0, 0))
                    dc.DrawText(symbol, x * self.__StitchSize + position[0], y * self.__StitchSize + position[1])                
                wx.PostEvent(self.__sender, PIPrintConvasGeneratingEvent(total=event_total, count=event_count))
                event_count += 1
        dc.Destroy()
        return bitmap.ConvertToImage()
 
    def GetFlossMaskList(self):
        '''
        根据用线统计列表，得到用线对应的符号列表
        '''
        result = {}
        summary = self.GetFlossSummary()
        for k in range(len(summary)):
            symbol = unichr(self.__Symbols[k])
            result[summary[k][0]] = (self.__GetSymbolMask(summary[k][0], symbol), symbol)
        return result
    
    def __GetSymbolMask(self, rgb, symbol):
        '''
            加注水印
        '''
        im = wx.EmptyBitmap(self.__StitchSize, self.__StitchSize)
        dc = wx.MemoryDC()
        dc.SelectObject(im)
        dc.SetBackground(wx.Brush(rgb))
        dc.Clear()
        dc.SetFont(wx.Font(14,wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL,underline=0,encoding=wx.FONTENCODING_CP932))
        textsize = dc.GetTextExtent(symbol)
        position = ((self.__StitchSize - textsize[0]) // 2, (self.__StitchSize - textsize[1]) // 2)
        #如果颜色过于接近黑色，则用反色白色来填充
        if Common.GetRGBDistance(rgb, (0,0,0)) < 200:
            dc.SetTextForeground((255, 255, 255))
        else:
            dc.SetTextForeground((0, 0, 0))
        dc.DrawText(symbol, position[0], position[1])
        return im.ConvertToImage()
    
    def __GetPrintPages(self):
        '''
        分页最终图片
        '''
        im = self.GetPrintConvas()
        __PageWith = 85 * self.__StitchSize
        __PageHeight = 120 * self.__StitchSize
        __BlankBarSize = 100 #旁边空白的空间大小
        results = []
        #计算页数
        if im.GetWidth() % __PageWith:
            wp = im.GetWidth() // __PageWith + 1
        else:
            wp = im.GetWidth() // __PageWith
        if im.GetHeight() % __PageHeight:
            hp = im.GetHeight() // __PageHeight + 1
        else:
            hp = im.GetHeight() // __PageHeight
        #绘图用DC
        dc = wx.MemoryDC()
        font = wx.Font(40, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL,underline=0,encoding=wx.FONTENCODING_CP932)        
        #为在图像上写字，准备设置字体
        dc.SetFont(font)
        #设置写字的颜色为黑色
        dc.SetTextForeground((0, 0, 0))
        #被复制图片的DC对象
        dc_temp = wx.MemoryDC()       
        #切割页面   
        for i in range(wp):
            for j in range(hp):
                #计算x,y轴起始坐标
                x_start = __PageWith*i
                y_start = __PageHeight*j
                x_end = (i+1)*__PageWith
                #如果超长，则用上限
                if x_end > im.GetWidth():
                    x_end = im.GetWidth()
                y_end = (j+1)*__PageHeight
                if y_end > im.GetHeight():
                    y_end = im.GetHeight()
                maskArea = []
                #往上往后得重复三行
                if y_start != 0:
                    if x_start != 0:
                        maskArea.append(wx.Rect(__BlankBarSize, __BlankBarSize, x_end - x_start + self.__StitchSize * 3, self.__StitchSize * 3))
                    else:
                        wx.Rect2D
                        maskArea.append(wx.Rect(__BlankBarSize, __BlankBarSize, x_end - x_start, self.__StitchSize * 3))
                    y_start -= self.__StitchSize * 3
                if x_start != 0:                
                    if y_start != 0:
                        maskArea.append(wx.Rect(__BlankBarSize, __BlankBarSize +  self.__StitchSize * 3, self.__StitchSize * 3, y_end - y_start - self.__StitchSize * 3))
                    else:
                        maskArea.append(wx.Rect(__BlankBarSize, __BlankBarSize, self.__StitchSize * 3, y_end - y_start))
                    x_start -= self.__StitchSize * 3
                #从原图截取所需的部分
                sub_im = im.GetSubImage((x_start, y_start, x_end - x_start, y_end - y_start))
                new_im = wx.BitmapFromImage(sub_im) #现在已经是bitmap格式了
                sub_im.Destroy()
                #新建一个位图
                result_im = wx.EmptyBitmap(__PageWith + __BlankBarSize*2, __PageHeight + __BlankBarSize*2)  #现在已经是bitmap格式了                
                #设置背景色为白色
                dc.SelectObject(result_im)
                dc.SetBackground(wx.Brush((255, 255, 255)))
                dc.Clear()                
                dc_temp.SelectObject(new_im)
                #复制截取部分的图像到新建的位图上
                dc.Blit(__BlankBarSize, __BlankBarSize, new_im.GetWidth(), new_im.GetHeight(), dc_temp, 0, 0)        
                grid_size = self.__StitchSize * 10
                for x in range(x_start, x_end):
                    #描绘X轴
                    #当遍历到第10根格子线的时候，写上列数
                    if not x % grid_size:
                        value = str(x / grid_size)                        
                        textsize = dc.GetTextExtent(value)
                        dc.DrawText(value, x - x_start + __BlankBarSize - textsize[0] // 2, __BlankBarSize - textsize[1])
                for y in range(y_start, y_end):
                    #描绘Y轴
                    #当遍历到第10根格子线的时候，写上行数
                    if not y % grid_size:
                        value = str(y / grid_size)
                        textsize = dc.GetTextExtent(value)
                        dc.DrawText(value, __BlankBarSize - textsize[0] - 10, y + __BlankBarSize - y_start - textsize[1] // 2)
                gcdc = wx.GCDC(dc)
                gcdc.SetPen(wx.Pen((0, 0, 0, 128)))
                gcdc.SetBrush(wx.Brush((0, 0, 0, 128)))
                #增加前页输出部分的阴影效果
                for area in maskArea:
                     #阴影效果专用dc                    
                    gcdc.DrawRectangleRect(area)
                gcdc.Destroy()
                #返回wxImage格式
                results.append(result_im.ConvertToImage())
                del new_im
                del result_im
        dc_temp.Destroy()
        dc.Destroy()
        return results
    
    def __AddWaterMark(self, im):
        '''
        加注版权水印
        '''
        dc = wx.MemoryDC()
        image = wx.BitmapFromImage(im)
        dc.SelectObject(image)
        gcdc = wx.GCDC(dc)
        gcdc.SetTextForeground((0, 0, 0, 50))
        font = wx.Font(60, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL,underline=0,encoding=wx.FONTENCODING_CP932)
        mark = u"彩雲阁姊妹篇工作室出品"
        gcdc.SetFont(font)
        textsize = gcdc.GetTextExtent(mark)
        gcdc.DrawText(mark, (im.GetWidth() - textsize[0]) //2 ,(im.GetHeight() - textsize[1]) //2)
        gcdc.Destroy()
        dc.Destroy()
        return image.ConvertToImage()
    
    def __AddPageCount(self, im, index, total):
        dc = wx.MemoryDC()
        image = wx.BitmapFromImage(im)
        dc.SelectObject(image)
        font = wx.Font(34, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL,underline=0,encoding=wx.FONTENCODING_CP932)
        dc.SetFont(font)
        dc.SetTextForeground((0, 0, 0))
        text = u"页码:%d/%d" % (index, total)
        textsize = dc.GetTextExtent(text)
        dc.DrawText(text, im.GetWidth() - textsize[0] - 10 , 5)
        dc.Destroy()
        return image.ConvertToImage()
    
    def __MakeFlossSummaryReport(self):
        '''
        输出用线统计
        '''
        result = u"\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"\n" % (u'线号', u'描述', u'格子数', u'支数(每支1800格)', u'支数')
        count = 0
        summary = self.GetFlossSummary()
        for k in summary:
            if COLOR_TABLE.has_key(k[0]) == 0:
                raise Exception("Can't found floss defination in map. Something wrong maybe happend.")
            floss = COLOR_TABLE.get(k[0])
            skeins = (k[1] % 1800 == 0 and [k[1] / 1800] or [k[1] / 1800 + 1])[0]
            result += "\"%s\",\"%s\",\"%d\",\"%0.2f\",\"%d\"\n" % \
                (floss.id, floss.description, k[1], float(k[1]) / 1800, skeins)
            count += skeins
        result += u"\"总计\",\"\",\"\",\"\",\"%d\"" % count
        return result
    
    def __GetSymbolConvas(self):
        '''
        获取针线一览
        '''
        floss_mask_list = self.GetFlossMaskList()
        gridsize = (self.GetPreviewImage().GetWidth(), self.GetPreviewImage().GetHeight())
        floss_count = len(floss_mask_list)
        height = (self.__StitchSize + 5) * (floss_count // 3 + 1) + 150
        
        dc = wx.MemoryDC()
        image = wx.EmptyBitmap(1000, height)
        dc.SelectObject(image)
        dc.SetBackground(wx.Brush((255, 255, 255)))
        dc.Clear()
        dc.SetTextForeground((0, 0, 0))
        dc.SetPen(wx.Pen((0, 0, 0)))
        font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD,underline=0,encoding=wx.FONTENCODING_CP932)
        dc.SetFont(font)
        dc.DrawText(u"彩雲阁姊妹篇工作室出品", 10, 10)
        dc.DrawLine(0, 40, 1000, 40)
        font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD,underline=0,encoding=wx.FONTENCODING_CP932)
        dc.SetFont(font)
        dc.DrawText(u"作者:", 10, 50)
        dc.DrawText(u"版权:", 10, 70)
        dc.DrawText(u"格子数:", 10, 90)
        dc.DrawText(u"大小:", 10, 110)
        dc.DrawText(u"shizixiu@morphinewan.com", 130, 50)
        dc.DrawText(u"Copyright (C) 2008-2099 All Rights Reserved.", 130, 70)
        dc.DrawText(u"宽%d格 × 高%d格" % gridsize, 130, 90)
        if self.__args["CT"]:
            ct = self.__args["CT"]
        else:
            ct = 14
        gridsize = (gridsize[0] * 2.54 / ct, gridsize[1] * 2.54 / ct, ct)
        dc.DrawText(u"宽%0.2f厘米 × 高%0.2f厘米  %dct" % gridsize, 130, 110)
        x, y, count = 5, 150, 0
        dc_temp = wx.MemoryDC()
        for k in floss_mask_list.iteritems():
            #画标记        
            dc_temp.SelectObject(wx.BitmapFromImage(k[1][0]))
            #复制截取部分的图像到新建的位图上
            dc.Blit(x, y, k[1][0].GetWidth(), k[1][0].GetHeight(), dc_temp, 0, 0)
            #画原图样
            x += self.__StitchSize + 5
            dc.SetPen(wx.Pen(k[0]))
            dc.SetBrush(wx.Brush(k[0]))
            dc.DrawRoundedRectangle(x, y, self.__StitchSize, self.__StitchSize, 1)
            #取得Floss信息
            floss = COLOR_TABLE[k[0]]
            #画ID号
            x += self.__StitchSize + 5
            textsize = dc.GetTextExtent('%- 10s' % floss.id)
            dc.SetPen(wx.Pen((0, 0, 0)))
            dc.DrawText('%- 10s' % floss.id, x, y + (self.__StitchSize - textsize[1]) // 2)
             #画描述
            x += 50
            dc.DrawText(floss.description, x, y + (self.__StitchSize - textsize[1]) // 2)
            if count == 0:
                x = 400
                count += 1
            elif count == 1:
                x = 700
                count += 1
            else:
                x = 5   
                y += self.__StitchSize + 5
                count = 0
        dc_temp.Destroy()
        dc.Destroy()
        result = image.ConvertToImage()
        image.Destroy()
        return result

            
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
COLOR_TABLE2 = {}
for floss in COLOR_TABLE.itervalues():
    COLOR_TABLE2[floss.id] = floss
