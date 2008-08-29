# -*- coding: utf-8 -*-
import Common
import pickle,math
import os,sys
import Image,ImageDraw,ImageFont
import threading,time
import wx,wx.aui,wx.lib.scrolledpanel as scrolled,wx.lib.imagebrowser as ib

class Logger():
    def __init__(self, output):
        self.logger = output
        
    def Log(self, content):
        self.logger.config(state=NORMAL)
        self.logger.insert(END, "%s %s\n" % (time.strftime('%Y-%m-%d %X', time.localtime() ), content))
        self.logger.config(state=DISABLED)
        time.sleep(0.001)

class SysArgs():        
    def __init__(self):
        self.path = ""
        #加载配置文件
        self.__path = "SysArgs.config"        
        if os.path.isfile(self.__path) and os.path.exists(self.__path):
            f = open(self.__path, 'r')
            tmp = pickle.load(f)
            self.size = tmp.size
            self.maxflossnum = tmp.maxflossnum
            self.mincolorused = tmp.mincolorused
            self.bgcolor = tmp.bgcolor
            self.cropside = tmp.cropside
            self.printimagescale = tmp.printimagescale
            self.previewimagescale = tmp.previewimagescale
            self.antinoise = tmp.antinoise
            self.antibgcolor = tmp.antibgcolor
            self.onlypreview = tmp.onlypreview
            self.fortaobao = tmp.fortaobao
            self.disabledbgcolor = tmp.disabledbgcolor
            self.ct = tmp.ct
            self.path = tmp.path
            self.antibgcolordist = tmp.antibgcolordist
            self.mixcolordist = tmp.mixcolordist
            f.close()
        else:
            #初始化
            self.size = (200, 0)
            self.maxflossnum = "50"
            self.mincolorused = "20"
            self.bgcolor = "FFFFFF"
            self.cropside = True
            self.printimagescale = "1.0"
            self.previewimagescale = "0.1"
            self.antinoise = True
            self.antibgcolor = True
            self.onlypreview = True
            self.fortaobao = False
            self.disabledbgcolor = True
            self.antibgcolordist = 30
            self.ct = 14
            self.mixcolordist = 30
    def Save(self):
        f = open(self.__path, 'w')        
        pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
        f.close()
        
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
        self.__fl = self.__LoadMap()
        self.__savedFlg = True
    
    def __LoadMap(self):
        '''
        加载颜色映射表
        程序中使用的都是RGB形式，保存为Hex形式
        '''
        path = os.path.split(sys.argv[0])[0] + '/FlossMap.txt'
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
    def __init__(self, args, logger):
        self.__args = args
        self.__logger = logger
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
        
    def Init(self, callback = None):
        '''
        初始化系统参数，耗时，所以放在执行时候做
        '''
        #初始化系统参数，耗时，所以放在初始化时候做
        self.__logger.Log(Common.Message["MF215"])
        #加载色彩映射表
        self.__Color2FlossMap = FlossMap()
        #加载绣线颜色表
        self.__ColorTable = self.__LoadColorTable()
        #背景颜色，默认为白色
        self.__BackgroundColor = Common.Hex2RGB(self.__args.bgcolor)
        #如果背景色不是标准的绣线颜色，则需要转换
        if not self.__ColorTable.has_key(self.__BackgroundColor):
            #先查找有无已存在的映射关系，如果没有则计算最近颜色。
            if self.__Color2FlossMap.GetValue(self.__BackgroundColor):
                self.__BackgroundColor = self.__Color2FlossMap.GetValue(self.__BackgroundColor)
            else:
                self.__BackgroundColor = self.__GetMinDistanceColor(self.__BackgroundColor)
        if callback:
            callback()
        self.__logger.Log(Common.Message["MF221"])
    def __LoadColorTable(self):
        '''
        加载绣线颜色表
        '''
        path = os.path.split(sys.argv[0])[0] + '/Color_Table/DMC.txt'
        lines = open(path).readlines()
        if len(lines) % 3:
            Common.ShowError(Common.Message["MF301"] % "DMC.txt")
            raise Exception(Common.Message["MF301"] % "DMC.txt")
        result = {}
        for i in range(len(lines) // 3 - 1):
            id = lines[i * 3][:-1]        
            description = lines[i * 3 + 1][:-1]
            colors = lines[i * 3 + 2].split(',')        
            rgb = (int(colors[0]), int(colors[1]), int(colors[2]))
            result[rgb] = Floss(id, description, rgb)
        return result
    
    def __GetMinDistanceColor(self, rgb):
        '''
        求颜色表中距离目标颜色最短的颜色
        '''
        if self.__Color2FlossMap.GetValue(rgb):
            #如果在颜色映射表里面已经存在，则直接返回该颜色
            return self.__Color2FlossMap.GetValue(rgb)
        else:
            min = [(255,255,255), sys.maxint] #定义一个初始值，距离为-1
            for floss in self.__ColorTable.itervalues():
                dis = floss.CalcDistance(rgb)
                #如果距离小于上一个值，则替代之
                if dis < min[1]:
                    min[0] = floss.rgb
                    min[1] = dis
                if dis == 0:
                    break
            #将该映射关系补充道颜色映射表中
            self.__Color2FlossMap.AppendData(rgb, min[0])
            return min[0] 
               
    def __GetStitchSize(self, size):
        #没有设置输出大小，默认为宽度200格
        width = 200
        height = 200
        p_size = self.__args.size
        if p_size[0].count("cm") > 0:
            #厘米为长度的场合,折算一下，厘米折算成英寸
            p_size[0] = p_size[0].replace("cm", "")
            p_size[0] = "%0.2finches" % (float(p_size[0]) / 2.45)
        if p_size[1].count("cm") > 0:
            #厘米为长度的场合,折算一下，厘米折算成英寸
            p_size[1] = p_size[1].replace("cm", "")
            p_size[1] = "%0.2finches" % (float(p_size[1]) / 2.45)
        if self.__args.ct:
            ct = int(self.__args.ct)
        else:
            ct = 14
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
        pix = im.load()
        #逐个分析各个像素的颜色，找到颜色表内对应最接近的颜色替代
        for i in range(im.size[0]):
            for j in range(im.size[1]):
                pix[i,j] = self.__GetMinDistanceColor(pix[i,j])
        #保存颜色映射表
        self.__Color2FlossMap.SaveData()
        return im
    
    def __MergePixelColor(self, im, rgb):     
        '''
        将图片中的特定颜色和周围颜色混合
        '''
        pix = im.load()
        #搜索所有的像素点
        for i in range(im.size[0]):
            for j in range(im.size[1]):
                if pix[i, j] == rgb:
                    #找到目标像素,寻找上下左右四个元素的颜色，按出现最多的颜色赋值   
                    result = [self.__BackgroundColor, sys.maxint]
                    #左边
                    if i != 0 and pix[i - 1, j] != rgb:
                        distence = Common.GetRGBDistance(pix[i, j], pix[i - 1, j])
                        if distence < result[1]:
                            result[0] = pix[i - 1, j]
                            result[1] =  distence
                    #上边
                    if j != 0 and pix[i, j - 1] != rgb:
                        distence = Common.GetRGBDistance(pix[i, j], pix[i, j - 1])
                        if distence < result[1]:
                            result[0] = pix[i, j - 1]
                            result[1] =  distence
                    #右边
                    if i != im.size[0] - 1 and pix[i + 1, j] != rgb:
                        distence = Common.GetRGBDistance(pix[i, j], pix[i + 1, j])
                        if distence < result[1]:
                            result[0] = pix[i + 1, j]
                            result[1] =  distence
                    #下边
                    if j != im.size[1] - 1 and pix[i, j + 1] != rgb:
                        distence = Common.GetRGBDistance(pix[i, j], pix[i, j + 1])
                        if distence < result[1]:
                            result[0] = pix[i, j + 1]
                            result[1] =  distence
                    pix[i, j] = result[0]
    
    def __GetFlossSummary(self, im):
        '''
        求绣线使用统计
        返回按使用量来倒序排列的dic
        '''
        result = {}
        pix = im.load()
        for i in range(im.size[0]):
            for j in range(im.size[1]):
                if pix[i, j] != self.__BackgroundColor:
                    if result.has_key(pix[i, j]):
                        result[pix[i, j]] += 1
                    else:
                        result[pix[i, j]] = 1    
        return sorted(result.items(), key = lambda i : i[1])
    
    def __ReduceFloss(self, im, maxflossnum, mincolorused):
        '''
        减少绣线数量
        '''        
        if self.__args.mixcolordist:
            #合并颜色相近像素
            summary = self.__GetFlossSummary(im)
            self.__logger.Log(Common.Message["MF203"] % len(summary))
            self.__logger.Log(Common.Message["MF222"])
            mapping_table = {}#映射表
            for i in range(len(summary)):
                for j in range(i+1, len(summary)):
                    #如果两种颜色小于特定距离，则记录在映射表里面
                    dist = Common.GetRGBDistance(summary[i][0], summary[j][0])
                    if dist <= self.__args.mixcolordist:
                        if mapping_table.has_key(summary[i][0]):
                            #如果存在key，则判断是否距离更小
                            if mapping_table[summary[i][0]][1] > dist:
                                mapping_table[summary[i][0]] = [summary[j][0], dist]
                        else:
                            mapping_table[summary[i][0]] = [summary[j][0], dist]
            pix = im.load()
            #遍历所有像素点，替换映射表内的颜色
            for i in range(im.size[0]):
                for j in range(im.size[1]):
                    while mapping_table.has_key(pix[i, j]):
                        pix[i, j] = mapping_table[pix[i, j]][0]
        summary = self.__GetFlossSummary(im)
        self.__logger.Log(Common.Message["MF203"] % len(summary))
        if maxflossnum or mincolorused:
            #取得绣线使用统计
            if maxflossnum:
                #限定最多使用线量
                self.__logger.Log(Common.Message["MF207"] % maxflossnum)
                #如果实际颜色数大于要求数
                while len(summary) > maxflossnum:
                    self.__MergePixelColor(im, summary[0][0])
                    summary = self.__GetFlossSummary(im)
                self.__logger.Log(Common.Message["MF203"] % len(summary))
            if mincolorused:
                #剔除使用量少于特定值的线条
                self.__logger.Log(Common.Message["MF208"] % mincolorused)
                #如果检索到数量大于特定值的，则跳出不做了
                while summary[0][1]  < mincolorused:
                    self.__MergePixelColor(im, summary[0][0])
                    summary = self.__GetFlossSummary(im)
                    if len(summary) == 0:
                        break
                self.__logger.Log(Common.Message["MF203"] % len(summary))
        return im
        
    
    def __CropSide(self, im):
        '''
        裁剪边框
        '''
        x1, y1, x2, y2 = 0 ,0 ,im.size[0] ,im.size[1]
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
        
        n_im = Image.new("RGB", (x2 - x1, y2 - y1))
        pix = n_im.load()
        pix_s = im.load()
        for i in range(n_im.size[0]):
            for j in range(n_im.size[1]):
                pix[i, j] = pix_s[i + x1, j + y1]
        return n_im
    
    def __IsAllPixelBackgroundColor(self, im, col = -1, row  = -1):
        '''
        检查某行某列是否为全空
        '''
        checkFlg = True
        pix = im.load()
        if row > -1:
            for i in range(im.size[0]):
                if pix[i, row] != self.__BackgroundColor:
                    checkFlg = False
                    break
        elif col > -1:
            for i in range(im.size[1]):
                if pix[col, i] != self.__BackgroundColor:
                    checkFlg = False
                    break
        return checkFlg
    
    def __AntiNoise(self, im):
        '''
        反噪点
        '''
        pix = im.load()
        for i in range(im.size[0]):
            for j in range(im.size[1]):
                if i > 0 and pix[i - 1, j] != self.__BackgroundColor:
                    continue
                if j > 0 and pix[i, j - 1] != self.__BackgroundColor:
                    continue
                if i < im.size[0] - 1 and pix[i + 1, j] != self.__BackgroundColor:
                    continue
                if j < im.size[1] - 1 and pix[i, j + 1] != self.__BackgroundColor:
                    continue
                pix[i, j] = self.__BackgroundColor
        return im
    
    def __AntiBgColor(self, im, dist):
        '''
        去除和背景颜色相近的颜色
        '''
        pix = im.load()
        for i in range(im.size[0]):
            for j in range(im.size[1]):
                if pix[i, j] != self.__BackgroundColor and Common.GetRGBDistance(pix[i,j], self.__BackgroundColor) <= dist:
                    pix[i, j] = self.__BackgroundColor
        return im

    def __GetStitchConvas(self, source_im, mask_dic = None):
        '''
        转换绣图
        '''
        w, h = source_im.size
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
        im = Image.new('RGB', (w_total, h_total))
        #第一行第一列定位
        x = y = self.__BoldGridLineWidth
        pix = source_im.load()
        for j in range(h):
            for i in range(w):
                #循环处理各行各列
                if mask_dic:
                    #如果参数mask_dic存在的话，则表示这是在输出正式绣图
                    if pix[i, j] == self.__BackgroundColor:
                        if self.__args.disabledbgcolor:#如果禁止输出背景色，则输出白色
                            im.paste((255,255,255), (x,y, x + self.__StitchSize, y + self.__StitchSize))
                        else:
                            im.paste(pix[i,j], (x,y, x + self.__StitchSize, y + self.__StitchSize))
                    else:
                        im.paste(mask_dic[pix[i,j]], (x,y, x + self.__StitchSize, y + self.__StitchSize))
                else:
                    #否则则是在输出预览图
                    im.paste(pix[i,j], (x,y, x + self.__StitchSize, y + self.__StitchSize))
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
    
    def __MakeFlossSummaryReport(self, summary):
        '''
        输出用线统计
        '''
        result = "\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"\n" % ('Floss ID','Description','Stitches', 'Skeins(per 1800 stitches)', 'Skeins')
        count = 0
        for k in summary:
            if self.__ColorTable.has_key(k[0]) == 0:
                raise Exception("Can't found floss defination in map. Something wrong maybe happend.")
            floss = self.__ColorTable.get(k[0])
            skeins = k[1] % 1800 == 0 and (k[1] / 1800,)[0] or k[1] / 1800 + 1
            result += "\"%s\",\"%s\",\"%d\",\"%0.2f\",\"%d\"\n" % \
                (floss.id, floss.description, k[1], float(k[1]) / 1800, skeins)
            count += skeins
        result += "\"Total\",\"\",\"\",\"\",\"%d\"" % count
        return result
    
    def __GetFlossMaskList(self, summary):
        '''
        根据用线统计列表，得到用线对应的符号列表
        '''
        result = {}
        for k in range(len(summary)):
            result[summary[k][0]] = self.__GetSymbolMask(summary[k][0], unichr(self.__Symbols[k]))
        return result
    
    def __GetSymbolMask(self, rgb, symbol):
        '''
            加注水印
        '''
        im = Image.new("RGB", (self.__StitchSize, self.__StitchSize), rgb)    
        textdraw = ImageDraw.Draw(im)
        font = ImageFont.truetype("simsun.ttc", 20, encoding="Unicode")
        textsize = textdraw.textsize(symbol, font)
        position = ((self.__StitchSize - textsize[0]) // 2, (self.__StitchSize - textsize[1]) // 2)
        #如果颜色过于接近黑色，则用反色白色来填充
        if Common.GetRGBDistance(rgb, (0,0,0)) < 200:        
            textdraw.text(position, symbol, font=font, fill=(255, 255, 255))
        else:        
            textdraw.text(position, symbol, font=font, fill=(0, 0, 0))
        del textdraw
        return im
    
    def __GetSymbolConvas(self, floss_mask_list, gridsize):
        '''
        获取针线一览
        '''    
        floss_count = len(floss_mask_list)
        height = (self.__StitchSize + 5) * (floss_count // 3 + 1) + 140
        im = Image.new("RGB", (900, height), (255, 255, 255))
        textdraw = ImageDraw.Draw(im)
        font = ImageFont.truetype("ARIALBD.ttf", 18)
        textdraw.text((10,10) , "shizixiu@morphinewan.com", font = font, fill=(0, 0, 0))
        textdraw.line([0,30, 900, 30], width=1,  fill=(0, 0, 0))
        font = ImageFont.truetype("ARIAL.ttf", 11)
        textdraw.text((10,40) , "Author:", font = font, fill=(0, 0, 0))
        textdraw.text((10,55) , "Copyright:", font = font, fill=(0, 0, 0))
        textdraw.text((10,70) , "Grid Size:", font = font, fill=(0, 0, 0))
        textdraw.text((10,85) , "Design Area:", font = font, fill=(0, 0, 0))
        textdraw.text((130,40) , "morphinewan", font = font, fill=(0, 0, 0))
        textdraw.text((130,55) , "Copyright (C) 2008-2099 All Rights Reserved", font = font, fill=(0, 0, 0))
        textdraw.text((130,70) , "%dW * %dH" % gridsize, font = font, fill=(0, 0, 0))
        if self.__args.ct:
            ct = int(self.__args.ct)
        else:
            ct = 14
        gridsize = (gridsize[0] * 2.54 / ct, gridsize[1] * 2.54 / ct, ct)
        textdraw.text((130,85) , "%0.2fcm * %0.2fcm  %dct" % gridsize, font = font, fill=(0, 0, 0))
        font = ImageFont.truetype("ARIALBD.ttf", 11)
        x, y, count = 5, 105, 0
        for k in floss_mask_list.iteritems():
            #画标记        
            im.paste(k[1], (x, y))
            #画原图样
            x += self.__StitchSize + 5
            im.paste(k[0], (x, y, x + self.__StitchSize, y + self.__StitchSize))
            #取得Floss信息
            floss = self.__ColorTable[k[0]]
            #画ID号
            x += self.__StitchSize + 5
            textsize = textdraw.textsize('%- 10s' % floss.id, font)
            textdraw.text((x, y + (self.__StitchSize - textsize[1]) // 2), '%- 10s' % floss.id, font=font, fill=(0, 0, 0))
            #画描述
            x += 50
            textdraw.text((x, y + (self.__StitchSize - textsize[1]) // 2), floss.description, font=font, fill=(0, 0, 0))
            if count == 0:
                x = 305
                count += 1
            elif count == 1:
                x = 605
                count += 1
            else:
                x = 5   
                y += self.__StitchSize + 5
                count = 0
        del textdraw
        return im

    def __GetPrintPages(self, im):
        '''
        分页最终图片
        '''
        __PageWith = 85 * self.__StitchSize
        __PageHeight = 120 * self.__StitchSize
        __BlankBarSize = 100 #旁边空白的空间大小
        results = []
        #计算页数
        if im.size[0] % __PageWith:
            wp = im.size[0] // __PageWith + 1
        else:
            wp = im.size[0] // __PageWith
        if im.size[1] % __PageHeight:
            hp = im.size[1] // __PageHeight + 1
        else:
            hp = im.size[1] // __PageHeight    
        font = ImageFont.truetype("simsun.ttc", 40, encoding="Unicode")
        #切割页面   
        for i in range(wp):
            for j in range(hp):
                #计算x,y轴起始坐标
                x_start = __PageWith*i
                y_start = __PageHeight*j
                x_end = (i+1)*__PageWith
                #如果超长，则用上限
                if x_end > im.size[0]:
                    x_end = im.size[0]
                y_end = (j+1)*__PageHeight
                if y_end > im.size[1]:
                    y_end = im.size[1]
                maskArea = []
                #往上往后得重复三行
                if y_start != 0:
                    if x_start != 0:
                        maskArea.append((__BlankBarSize, __BlankBarSize, __BlankBarSize + x_end - x_start + self.__StitchSize * 3, __BlankBarSize + self.__StitchSize * 3))
                    else:
                        maskArea.append((__BlankBarSize, __BlankBarSize, __BlankBarSize + x_end - x_start, __BlankBarSize + self.__StitchSize * 3))
                    y_start -= self.__StitchSize * 3
                if x_start != 0:                
                    if y_start != 0:
                        maskArea.append((__BlankBarSize, __BlankBarSize +  self.__StitchSize * 3, __BlankBarSize + self.__StitchSize * 3, __BlankBarSize + y_end - y_start))
                    else:
                        maskArea.append((__BlankBarSize, __BlankBarSize, __BlankBarSize + self.__StitchSize * 3, __BlankBarSize + y_end - y_start))
                    x_start -= self.__StitchSize * 3
                #从原图截取所需的部分
                new_im = im.crop((x_start, y_start, x_end, y_end))
                result_im = Image.new("RGBA", (__PageWith + __BlankBarSize*2, __PageHeight + __BlankBarSize*2), (255, 255, 255))
                result_im.paste(new_im, (__BlankBarSize, __BlankBarSize))
                textdraw = ImageDraw.Draw(result_im)
                grid_width = (self.__StitchSize + self.__NormalGridLineWidth) * self.__BoldGridLinePerStitch + (self.__BoldGridLineWidth - self.__NormalGridLineWidth)
                for x in range(x_start, x_end):
                    #描绘X轴
                    #当遍历到第10根格子线的时候，写上列数
                    if not (x - self.__BoldGridLineWidth) % grid_width:
                        value = str((x - self.__BoldGridLineWidth) * 10 // grid_width)
                        textsize = textdraw.textsize(value, font)
                        textdraw.text((x - x_start + __BlankBarSize - textsize[0] // 2, __BlankBarSize - textsize[1]), value, font=font, fill=(0, 0, 0))
                for y in range(y_start, y_end):
                    #描绘Y轴
                    #当遍历到第10根格子线的时候，写上行数
                    if not (y - self.__BoldGridLineWidth) % grid_width:
                        value = str((y - self.__BoldGridLineWidth) * 10 // grid_width)
                        textsize = textdraw.textsize(value, font)
                        textdraw.text((__BlankBarSize - textsize[0] - 10, y - y_start + __BlankBarSize - textsize[1] // 2), value, font=font, fill=(0, 0, 0))
                #增加遮盖
                for area in maskArea:
                    mask_image = Image.new("RGBA", (area[2] - area[0], area[3] - area[1]), (0, 0, 0, 200))       
                    result_im.paste((100, 100, 100), box = area, mask = mask_image)                
                del textdraw 
                results.append(result_im)
                del new_im
                del result_im    
        return results
    
    def __AddWaterMark(self, im):
        '''
        加注版权水印
        '''
        mask_size = (im.size[0] // 2, im.size[1] // 2)    
        draw = ImageDraw.Draw(im)
        mark = "shizixiu@morphinewan.com"
        font_size = 60
        font = ImageFont.truetype("ARIALBD.ttf", font_size)
        textsize = draw.textsize(mark, font = font)
        while textsize[0] > mask_size[0] or textsize[1] > mask_size[1]:
            font_size -= 1
            font = ImageFont.truetype("ARIALBD.ttf", font_size)
            textsize = draw.textsize(mark, font = font)
        mark_image = Image.new("RGBA", textsize, (255, 255, 255, 255)) 
        mask_image = Image.new("RGBA", textsize, (0, 0, 0, 50))   
        draw = ImageDraw.Draw(mark_image)
        draw.text((0,0) , mark, font = font, fill=(0, 0, 0))  
        im.paste(mark_image, ((im.size[0] - mark_image.size[0]) //2 ,(im.size[1] - mark_image.size[1]) //2), mask = mask_image)
        del draw
        return im
    
    def __AddPageCount(self, im, index, total):
        draw = ImageDraw.Draw(im)
        text = u"页码:%d/%d" % (index, total)
        font = ImageFont.truetype("SIMSUN.ttc", 24)
        textsize = draw.textsize(text, font = font)
        draw.text((im.size[0] - textsize[0] - 10,5) , text, font = font, fill=(0, 0, 0))    
        del draw
        return im
        
    def MakeCrossStitch(self, files, callback):        
        for imageFile in files:
            #先建立输出目录
            outputPath = Common.MakeOutputPath(imageFile)
            #得到文件名
            fileName = Common.GetFileName(imageFile)            
            self.__logger.Log(Common.Message["MF204"] % fileName)
            #打开文件
            im = Image.open(imageFile)
            if im.mode != "RGB":
                im = im.convert("RGB")
            #计算绣图像素级大小
            (w, h) = self.__GetStitchSize(im.size)
            #把原图片按照格子数重新Resize
            self.__logger.Log(Common.Message["MF205"] % (w, h))
            new_im = im.resize((w, h))
            del im
            #替换调色板
            self.__logger.Log(Common.Message["MF206"])
            new_im = self.__ChangeColorTable(new_im)
            #减少颜色数(目前只支持最多150种颜色）
            if self.__args.maxflossnum:
                maxflossnum = int(self.__args.maxflossnum) > self.__MaxColorNumber \
                 and (self.__MaxColorNumber,)[0] or int(self.__args.maxflossnum)
            else:
                maxflossnum = 50 #默认设置为50种颜色 
            if self.__args.mincolorused:
                mincolorused = int(self.__args.mincolorused)
            else:
                mincolorused = None
            new_im = self.__ReduceFloss(new_im, maxflossnum, mincolorused)
            #裁边
            if self.__args.cropside:
                self.__logger.Log(Common.Message["MF209"])
                new_im = self.__CropSide(new_im)
            #反噪点
            if self.__args.antinoise:
                self.__logger.Log(Common.Message["MF210"])
                new_im = self.__AntiNoise(new_im)
            #除去背景相近颜色
            if self.__args.antibgcolor:
                self.__logger.Log(Common.Message["MF211"])
                new_im = self.__AntiBgColor(new_im, int(self.__args.antibgcolordist))
            #转换绣图(预览图）
            self.__logger.Log(Common.Message["MF212"])
            preview_im = self.__GetStitchConvas(new_im)
            #按比例缩略图
            if self.__args.fortaobao:#淘宝上传专用图处理
                new_size = preview_im.size
                if new_size[0] > 500:
                    new_size = (500, int(float(500 * new_size[1]) / new_size[0]))
                if new_size[1] > 500:
                    new_size = (int(float(500 * new_size[0]) / new_size[1]), 500)
                preview_im = preview_im.resize(new_size, Image.ANTIALIAS)
            elif self.__args.previewimagescale:#按比例缩图
                new_size = (int(preview_im.size[0]* float(self.__args.previewimagescale)), 
                            int(preview_im.size[1]* float(self.__args.previewimagescale)))
                preview_im = preview_im.resize(new_size, Image.ANTIALIAS)
            preview_im.save(Common.GetOutputFileName(imageFile, outputPath, suffix = 'preview'))
            del preview_im
            
            #如果参数决定，则只输出预览图
            if self.__args.onlypreview:
                continue
            
            #输出用线统计
            self.__logger.Log(Common.Message["MF216"])
            summary = self.__GetFlossSummary(new_im)
            #如果使用线量大于定义的表示数，则抛一个错误出来
            if len(summary) > self.__MaxColorNumber:
                self.__logger.Log(Common.Message["MF217"])
                raise Exception(Common.Message["MF217"])
            s = self.__MakeFlossSummaryReport(summary)
            fo = open(Common.GetOutputFileName(imageFile, outputPath, suffix = 'summary', extation = '.csv'), 'w')
            try:
                fo.write(s)
            finally:
                fo.close()
            #输出正式绣图，带标识   
            self.__logger.Log(Common.Message["MF218"])
            floss_mask_list = self.__GetFlossMaskList(summary)
            print_im = self.__GetStitchConvas(new_im, floss_mask_list)
            print_im_pages = self.__GetPrintPages(print_im)
            del print_im
            count = 1
            for p_im in print_im_pages:
                #按比例缩略图
                if self.__args.printimagescale:
                    new_size = (int(p_im.size[0]* float(self.__args.printimagescale)), 
                                int(p_im.size[1]* float(self.__args.printimagescale)))
                    p_im = p_im.resize(new_size, Image.ANTIALIAS)
                #加注版权水印
                p_im = self.__AddWaterMark(p_im)
                #增加页码
                p_im = self.__AddPageCount(p_im, count, len(print_im_pages))
                p_im.save(Common.GetOutputFileName(imageFile, outputPath, suffix = 'print%s' % count))
                del p_im
                count += 1
            print_im_pages = []
            del print_im_pages            
            #输出符号对照表
            self.__logger.Log(Common.Message["MF219"])
            symbol_im = self.__GetSymbolConvas(floss_mask_list, (w, h))
            symbol_im = self.__AddWaterMark(symbol_im)
            symbol_im.save(Common.GetOutputFileName(imageFile, outputPath, suffix = 'symbol'))
            del symbol_im
            self.__logger.Log(Common.Message["MF220"] % fileName)          
        self.__logger.Log(Common.Message["MF213"])
        #回调函数
        callback()
        
ID_OpenFile = wx.NewId()
ID_OpenDirectory = wx.NewId()
ID_Exit = wx.NewId()
ID_About = wx.NewId()

ID_PrintScale = wx.NewId()
ID_PreviewScale = wx.NewId()
ID_BgColour = wx.NewId()
ID_MaxColourNum = wx.NewId()
ID_MinFlossNum = wx.NewId()
ID_MixColourDist = wx.NewId()
ID_Width = wx.NewId()
ID_Height = wx.NewId()
ID_CT = wx.NewId()

ID_CropSide = wx.NewId()
ID_AntiNoise = wx.NewId()
ID_AntiBgColour = wx.NewId()
ID_OnlyPreview = wx.NewId()
ID_ForTaobao = wx.NewId()
ID_DisabledBgColour = wx.NewId()

class MainFrame(wx.Frame):
    def __init__(
            self, parent, ID, title, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE
            ):
        
        wx.Frame.__init__(self, parent, ID, title, pos, size, style)        
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        #菜单
        mb = wx.MenuBar()
        
        file_menu = wx.Menu()
        file_menu.Append(ID_OpenFile, "Open File")
        file_menu.Append(ID_OpenDirectory, "Open Path")
        file_menu.AppendSeparator()
        file_menu.Append(ID_Exit, "Exit")
        
        mb.Append(file_menu, "File")
        self.SetMenuBar(mb)
        #左部设置项目
        option_panel = scrolled.ScrolledPanel(self, -1, size=(160, 400),
                                 style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER, name="option_panel" )
        option_panel.SetBackgroundColour(wx.Colour(red=255, green=255, blue=255) )
        sizer = wx.GridBagSizer(vgap=1, hgap=1)
        
        input = wx.TextCtrl(option_panel, ID_PrintScale, "1.0", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"打印图片缩放比例")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(0,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(0,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_PreviewScale, "1.0", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"预览图片缩放比例")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(1,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(1,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_BgColour, "FFFFFF", style=wx.TE_LEFT | wx.TE_READONLY, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"背景颜色")
        input.SetMaxLength(6)
        sizer.Add(label,pos=(2,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(2,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_MaxColourNum, "50", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"最高颜色数")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(3,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(3,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_MinFlossNum, "20", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"最低颜色数")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(4,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(4,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_MixColourDist, "20", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"混合颜色距离")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(5,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(5,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_Width, "20", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"宽度")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(6,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(6,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_Height, "20", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"高度")
        input.SetMaxLength(3)
        sizer.Add(label,pos=(7,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(7,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        input = wx.TextCtrl(option_panel, ID_CT, "20", style=wx.TE_RIGHT, size=(45,20))
        label = wx.StaticText(option_panel, -1, u"CT")
        input.SetMaxLength(2)
        sizer.Add(label,pos=(8,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(input,pos=(8,1), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        checkbox = wx.CheckBox(option_panel, ID_CropSide, "")
        label = wx.StaticText(option_panel, -1, u"切除边缘空白")
        sizer.Add(label,pos=(9,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(9, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        checkbox = wx.CheckBox(option_panel, ID_AntiNoise, "")
        label = wx.StaticText(option_panel, -1, u"去除噪点")
        sizer.Add(label,pos=(10,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(10, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        checkbox = wx.CheckBox(option_panel, ID_OnlyPreview, "")
        label = wx.StaticText(option_panel, -1, u"只输出预览图片")
        sizer.Add(label,pos=(11,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(11, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        checkbox = wx.CheckBox(option_panel, ID_ForTaobao, "")
        label = wx.StaticText(option_panel, -1, u"淘宝上传图片模式")
        sizer.Add(label,pos=(12,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(12, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
                
        checkbox = wx.CheckBox(option_panel, ID_AntiBgColour, "")
        label = wx.StaticText(option_panel, -1, u"去除背景颜色")
        sizer.Add(label,pos=(13,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(13, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
        
        checkbox = wx.CheckBox(option_panel, ID_DisabledBgColour, "")
        label = wx.StaticText(option_panel, -1, u"禁止输出背景颜色")
        sizer.Add(label,pos=(14,0), flag=wx.ALIGN_LEFT | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=1)
        sizer.Add(checkbox, pos=(14, 1), flag=wx.ALIGN_CENTER | wx.FIXED_MINSIZE | wx.ALL , border=1)
   
        option_panel.SetSizer(sizer)
        option_panel.SetupScrolling()

        self._mgr.AddPane(option_panel,
                          wx.aui.AuiPaneInfo().Name("option_panel").Caption(u"选项面板").Left()
                          .CloseButton(True).TopDockable(False).BottomDockable(False).MaximizeButton(True))
        
        #右部工作区
        work_panel = wx.Panel(self, -1)
        self._mgr.AddPane(work_panel,
                          wx.aui.AuiPaneInfo().Name("work_panel").CentrePane().MaximizeButton(True))
               
        self._mgr.Update()
        #窗口关闭
        self.Bind(wx.EVT_CLOSE, self.__OnCloseWindow)

    
        #绑定事件
        self.Bind(wx.EVT_MENU, self.__OnExit, id=ID_Exit)
        self.Bind(wx.EVT_MENU, self.__OnOpenFile, id=ID_OpenFile)
        self.FindWindowById(ID_BgColour).Bind(wx.EVT_LEFT_DCLICK, self.__PickupColour)
        
    def __ValidateForm(self):
        #校验浮点数
        for id in (ID_PrintScale, ID_PreviewScale):
            obj = self.FindWindowById(id)
            if not Common.IsFloat(obj.GetValue()):
                self.__ShowError(u"请输入正小数。")
                obj.SetFocus()
                obj.SetSelection(-1, -1)
                return False
        for id in (ID_MaxColourNum, ID_MinFlossNum, ID_MixColourDist, 
                   ID_Width, ID_Height, ID_CT):
            obj = self.FindWindowById(id)
            if not Common.IsInt(obj.GetValue()):
                self.__ShowError(u"请输入正整数。")
                obj.SetFocus()
                obj.SetSelection(-1, -1)
                return False
        return True            
            
    def __OnOpenFile(self, event):
        # get current working directory
        dir = os.getcwd()

        # open the image browser dialog
        dlg = ib.ImageDialog(self, dir)

        dlg.Centre()

        if dlg.ShowModal() == wx.ID_OK:
            # show the selected file
            self.log.WriteText("You Selected File: " + dlg.GetFile())        
        else:
            self.log.WriteText("You pressed Cancel\n")

        dlg.Destroy()
        
    def __PickupColour(self, event):
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            event.GetEventObject().SetValue(Common.RGB2Hex(data.GetColour().Get()))
        dlg.Destroy()
            
    def __OnExit(self, event):
        '''
        关闭按钮
        '''
        self.Close(True)

    def __OnCloseWindow(self, event):
        '''
        窗口关闭
        '''
        self.Destroy()
     
    def __ShowError(self, message, title = None):
        dlg = wx.MessageDialog(self, message, title or Common.Message["MF201"], style= wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        
    def __ShowInfo(self, message, title = None):
        dlg = wx.MessageDialog(self, message, title or Common.Message["MF214"], style= wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
    
    class __ChildFrame(wx.Frame):
        '''
        子窗口名
        '''
        def __init__(
            self, parent, ID, title, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE
            ):
            wx.Frame.__init__(self, parent, ID, title, pos, size, style)


class Application(wx.App):
    def OnInit(self):
        win = MainFrame(None, -1, Common.Message["MF001"], size=(660, 550),
                  style = wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(win)
        win.Show(True)
        return True

def main():
    Application(0).MainLoop()
    
if __name__ == '__main__':
    main()