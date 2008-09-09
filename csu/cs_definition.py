# -*- coding: utf-8 -*-
import wx
import wx.lib.newevent
#系统设置
Application_Settings = {}

#菜单ID
ID_MenuItem_OpenFile = wx.NewId()
ID_MenuItem_Exit = wx.NewId()
ID_MenuItem_About = wx.NewId()
ID_MenuItem_ShowOptionPanel = wx.NewId()
ID_MenuItem_ShowLogPanel = wx.NewId()
ID_MenuItem_ShowFlossPanel = wx.NewId()

#ID_MenuItem_ShowImageFormat1 = wx.NewId()
#ID_MenuItem_ShowImageFormat2 = wx.NewId()
#ID_MenuItem_ShowImageFormat3 = wx.NewId()

ID_MenuItem_Debug = wx.NewId()
#工具栏
ID_ToolBar_ShowOptionPanel = wx.NewId()
ID_ToolBar_ShowLogPanel = wx.NewId()
ID_ToolBar_ShowFlossPanel = wx.NewId()
ID_ToolBar_OpenFile = wx.NewId()

ID_ToolBar_ZoomImage = wx.NewId()
ID_ToolBar_ZoomImageSpin = wx.NewId()
ID_ToolBar_GeneratePreview = wx.NewId()

ID_ToolBar_ShowImageFormat1 = wx.NewId()
ID_ToolBar_ShowImageFormat2 = wx.NewId()
#参数区
ID_Panel_Option = wx.NewId()
ID_Option_PrintScale = wx.NewId()
ID_Option_PreviewScale = wx.NewId()
ID_Option_BgColour = wx.NewId()
ID_Option_MaxColourNum = wx.NewId()
ID_Option_MinFlossNum = wx.NewId()
ID_Option_MixColourDist = wx.NewId()
ID_Option_Width = wx.NewId()
ID_Option_Height = wx.NewId()
ID_Option_CT = wx.NewId()
ID_Option_CropSide = wx.NewId()
ID_Option_AntiNoise = wx.NewId()
ID_Option_AntiBgColour = wx.NewId()
ID_Option_OnlyPreview = wx.NewId()
ID_Option_ForTaobao = wx.NewId()
ID_Option_DisabledBgColour = wx.NewId()

#图片区ID
#ID_Panel_Work = wx.NewId()
ID_Frame_Work_ImageReviewPanel = wx.NewId()
ID_Frame_Work_ImageReview = wx.NewId()

#Log区
ID_Panel_Log = wx.NewId()

#绣线区
ID_Panel_Floss = wx.NewId()

(WorkFrameMouseMoveEvent, EVT_WORK_FRAME_MOUSE_MOVE_EVENT) = wx.lib.newevent.NewEvent()
(WorkFrameCloseEvent, EVT_WORK_FRAME_CLOSE_EVENT) = wx.lib.newevent.NewEvent()

from wx.lib.embeddedimage import PyEmbeddedImage

IMAGE_APP_ICON = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAABxBJ"
    "REFUWIWdl0uMXEcVhr9TVffenp7unnHjeTiOjB/xK57EgYiAwCaRiZClKERBLIIIj4inkMgG"
    "CZZhxcZrs2GDkJIVSEGRUDa8IgWkWEiIYDxSkONJzNjxxJ5xz/R09723zmHR3Y4n3ZM4HKlU"
    "V9VV5/x16q+/TouqGmPMzIgx4r3HzBCRLb/HGLlx4wZFUdBoNKhUKlvmqioxRrIsu+VnrKmq"
    "jWsxRiuKwmKM9vbbb9vZs2dtYWHBKpWKee9NRAwwETERMeecAVav1+3EiRP20ksvWafTsbIs"
    "Lc9zK4pibJxtAZRlab1ezx588EEDDLgV5PbvIZBhExELIZj33nbt2mUvvviitdttizHeGYAY"
    "o5Vlaa1Wy37w/e8Z9HcoYG7Q/C0gzhAx58S8YBXBpjJviWAM5pw8edJWVlYsz/OxAOR2Dpi9"
    "R4fFxUWOLdwHAs0sZa6acfDA3ayvr/PG8nV6BoUaDmFuMuHhTz3A00+cZrI+xct/eZWf/+o3"
    "tHs5AGfOnOHZZ58dy4MRAKrKhQsXePzxx7l8+TI/furLfP2xk9wzM4U4h4gg4onRKMoC54Tg"
    "HaaKNyMq+ImEC1fX+eIPf8rKaotarcbq6uoIkQHC+5kfQmBxcZFr164hpvzkO09T1VUkgkTF"
    "zDCUaIp3Hh88RZkTDEyMIq2j7TWO7J6lmlYwu0mr1UIYDT4CYHi9rly5QqfTIQMyybEYGIIf"
    "9glusEBJJTD0H/IuPqlS5h0qA58OwUwRcSMARkZEhDRNERF2VQMVgSBjpWK8iWJaIjFy8pP3"
    "EgBFYJsMjAAwM5IkIQmBbzz1JHlnE9P4EQAY3guC8aPvfovjR/bjQ3gvdR8GwDnHoUOHqFUr"
    "PPPY57GQUpbCeqvN6voG7U4PNVDVfjOjWxasrW/wbqvN6s0erVYXicKhTPja6VNkacAYn8UR"
    "DgAcPnyYRq3G7uYMF5eWaHVzJoNnwwTrtjm47wDVxPdZLcJb19fQ7iYqKQC1iiOrBrwY81OT"
    "HF9YALOxWRgBYGY0Gg2OHD2CCUijybE901B2cWmKE8HyAtM4uBHGwbvmiIVS9ApS70gqnl7R"
    "w4g061VOnTq17RH455577me3B1dVRAQH7J/KaAYFM/IIf/znebq9nJnpxmCF4oBOt+Dc0jJn"
    "f/s7fDUj9xk7qxMAJEmVe048yuzcHNAn+VDwRGSrEKkqGiPtN8/TkRR74zWaicM5z8VWzrnX"
    "z3Pvwf0km5sc3b+HGLtEg26pRACfMeUM5xylKiIl1262cfc/ws5dd5NWawMAADYeQMx7LP3+"
    "eVauXGbf/r1Mh0AQcCGwmUcqaUpZ5oh3WFniBMBTEnEiRImIOkDwlCzfaHFp+SqffuKbTOw9"
    "NAJgCweGpJqZm6OT5zSzFDEhak5Uw3uIWqIa8SjeQREVgsOp4KLhNYAXFMUjkOfUJcFVq7c2"
    "ebskjwqRD2h9J7p6nU5ZDBY4gglOBY0KIigQB8p27eq7dLo9ClMsKCYREcEPZFuaTWR6dstG"
    "hyBGboGIIElK8rEZYqmQCiIONcVEiGVkdX2NrDJBVCVJElrRmMtSkiwl9npDSlMKmARmZ+a2"
    "rYi2ZsDAO09IKszvaNLb7KE2UEHnMDNc8DRqdbIkpej2yNKMu3fU8SEQixzvPd57nHMkSYKb"
    "qFG777M4N/oOAKMkBCjLko21Vdb++jLzVcMLRBcIBmp9ssnAoUXF+YAqmAhoRDG8QYw5q+kU"
    "Oz/3GCHNxoIYq4TOOeo7mryV1JlnHXB4U9p5yX+uXOPvry/y5tLSljVHDx/hS595gFptEo/D"
    "xLh4fZPedJ3ZkGzzFG0DQERwzjF17ydoXzxHnYhpQXVigmP79lLcXGNtYwPVyERlgoePH+Xg"
    "no+TBI8ziE5YubnO5XdvcN8DJ/Heo6qMY8HIEdyuVKrKuRd+wYHZJnUPJoqT0H+Aur1+UYKn"
    "moAEh4hHXML6Zpt/L7/D0dNfpTG/m+D7j9G4I9gy4gYl17D33nP8yWe4nCdcvXGTRATvwJtS"
    "qyQ0JipUM0/I+qWHAa2NDV594xLTB45Tn5kjhH6xsh0Jx48OM2JGyDJ2P/Qw/1haZqNwOFPc"
    "4A3wYgRRKHNKVS6++V9+/efXmH/oUY4+cpqQZh/kfvQI3m8xDl4866fvb394mRo92u8sU66v"
    "stnNCbFAG7MkO5rExhyPfOHRvuNBJoff4wrSDwXwfjDDvtvp8KdfnuH+vbup13dwaeU6C1/5"
    "Nt77fsoHQe/EPvAIbrdhFsyMNMvYt/su7mpMMik9Yqn93d5h0P8LgIgQY8Q5R6vVYnnlOt2k"
    "gq/WOXf+Xzz/wgvYQMg+io3Vge0AmBmXLl3ilVdeQarzXOil5Otd3J5jTFarbGxsMD09fWv+"
    "Hfm9Uw4MNUK1n+7hX+6hJJdFcevqfhT7H/B1CMVpal1hAAAAAElFTkSuQmCC")

TOOLBAR_ICON_01 = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAntJ"
    "REFUOI1t0k1rU0EUxvH/zL1pm0STNLRUI740CkarC3UR3KiVgujKjSCoH8OFSBGKiGjrhxBE"
    "RQVFoboTdwGtiPhSsVVQTLAxSau3Nzf3zhkXSbXQDAwzm/nxnHNGsWoVCoX3+e07dokISimU"
    "on3SvgM4jkO5XG6USqX9wJeVt4lUKnXh6rXr8uXHgv3wtWznvldtuVq3C/Ul2/jt2d+ebz2/"
    "acNI7PTTpxY4AeB2gCOXJi5fOXX6HPMz07x8MIXrQmlOkxuErzWN6ypagTB69BAHj50B0KsB"
    "Z9vwML2JNJvcb3jhKwrHYWQYHj6G6Bc8+QibknAg76DV2X9lrwDWUQrtKPrX97F3BDafPEZe"
    "vebwvp9UX8HkI1j2IJ+K0zJ2DYDrOqyLw5uKpvYCNmSfEVsHtXew0enhfLGHO2//oJw40A1w"
    "HPoUVD3F/U+wfB+2Dyim5y2jI0OkMlmSAzV0cghrZS2gtQagKS6ziyAVRfqXZcFXhAtJ9mb6"
    "SQz2kMmmENMVaA/aKJdFA5VWgkWBZDpDfDDLYmSwSojFLEa6AaqdoBUJ9QCihoAVBqKAom6R"
    "jvdR9VvUvZBstwR0fpoXCJU/EOoIPzDUvBqlb1vwdIKhdJKfQYyUCdcCqiMEQRMLVJfCDgh6"
    "fY7k1j0sBXXCZZ8oirokAESEsbExJiYm0I4CC8YI/ek+BtJxPC/F5nwB0y5BrZlCGIbs3LmL"
    "8fHx/ygQtAzNoEVkhDAMuX3rJoBZDYjv+/jNJo1GBbEWMYIRwRghigxhFBLr7eXe3Tv2xtTk"
    "ReD5qtYxXCwWZ3K5XMaIYK3tbLBWELGItWitmZ/7/OHT7OzulYR/ARVMLf7zUuswAAAAAElF"
    "TkSuQmCC")

TOOLBAR_ICON_02 = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAnNJ"
    "REFUOI1tkrtrVFsUxn/7MeecTMZkbhIVRyFOYuJEO5ugNpZaqyDaiNhrJYKFIKII3vtPpFFu"
    "c+t7ixtsQhoLEcU3qDAmqJnM45w5Z78sMpGIs2HBbtZvfd+3lmDHazQaL2ZmDy145xBCIAQI"
    "IYCtP4DWmmaz2VpdXT0GfNCD3vLY2Ni1y1euNi5cvIQxOSWt0UqhtktKlJQkScz/y8vVM6dP"
    "L+wEnLp95+698+fO8nG9w8rzT/wxVqGSxGilCEKQe08nzZjdP8VEtQogAbYB6mC9TjxSZmqk"
    "y/EDiko1YjTWlJTAhUBWONJ2TiXusdENP21vA4ISAhUlTLkNJjdWiKmiogitBKYI2L7h+7cu"
    "9Gehsu83AFqrrWnlXRR7ZijGJ5FRglEK46CfW4rRLtH4bkLHDAEoxWhJ8Swb4b83FaJEEUkP"
    "wWF8oGcd7Z5loR44XP3dAlJKlNZ8bq7zz79PGK+MIhFAIPiADZ5WLyVrH2Xh1OFhgK1F9ze/"
    "03r/kjAxQdbvY5zDWIv1gc0s4+CeMp5hACEBsCZnc/0zZekoRyWC0uQ+sJF2aK+t0V5v4v0Q"
    "CwwuLQRPkXVIuwm5jtCliFKU0KhPU99fY7q2l7wYEqIYENJeyte1L5giRwqJKsUIqWnMTxMn"
    "CWm3i7V2iALAe8+Jk4vcf3CHJI4YHBsBgQfSLGNufg7r/E/Nv2zBGMP83Aw3b1wfNILzAess"
    "xlisdRTGsLS0BOB2AnyWZWT9Pq1WCx8C3nmc9zjnsdZhrKEUx/z9+FH468+Ht4DlHdFRX1xc"
    "fFqr1arOe0IIg9oK1fuADwEpJe/fvX35+tWrI9vKfwCBgSHeerDCvwAAAABJRU5ErkJggg==")

TOOLBAR_ICON_03 = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAApRJ"
    "REFUOI1t0ltLVFEYxvH/2qc5uceRPExTWmpN44GKCCS6qYQIv0B+jG4jIogO0OkrBB0g8QPk"
    "XV0FSkQlmIp20GwcTZ0Zx9kzs/daqwsPGM6C93L9eNZ6XsG+k8lkprq6T/QoJRFC7AwIBABC"
    "CEzTJJvN5sfHx88BP3bvRuPx+M2Hjx6rhT85/XPxt/6dXdbZlVW9srau1zbyOl8o6mKppH2/"
    "pt+OjWlgCMDaAS7duXvvwfDwdSY+z/JyZIxDjS4xxyJimzimgQC2KlX6T/fQe6oNwNgPmMc7"
    "O4nHXbZKZVaXsoSqZUIxByfq0GAbCAG1kkdt4y9Kt+49exfQphBYpkXUCuhNmpzPNHOsOUoy"
    "buBGFUGgyK2FCKdcqooDAJZlEnZsFn7N8WLkOZ+62hk8e4xrF5N0DfUTawzR8mEO33GZVh11"
    "ANMEwLZspIiwVDIZnVhlfnGLG6ZNOp1gerKIOOwhMnUSGIYBgJtow0100NraQveRQ6SbHDbX"
    "BZMTRb4u2iSigpOoesB219KvUFpfoNygWXdtZqoW544aGLZDYVPi+jWU1nUAsZ3AskOYlsNm"
    "YY18xIJYmI9fAmzH5t2C5kJbgXQ9YGfZsO0wyfY+kslmvHKRmeUVqqoBNxZhs5bnTy5HIOVB"
    "YHddc9l5lr5PUSk04UQaaWrp5MzlQZTv0VwqoIMq1UqlTgJAKcWVwavcvh/GVGVitiSVPIpH"
    "DK188jVNMpVCquJe5v9a8H2fnkya/r7tnjRQ9QOCoEYQSKSUBIHk1avXAHI/oDzPw6tUyOeX"
    "UVqjpEIqhZSKIJD4gY8dCjE68kY/e/rkFvB+39fROTAw8CmVSiWkUmitdwa0ViilUVpjGAbf"
    "5+e+zc7M9O4m/wd47SfAIdtXFgAAAABJRU5ErkJggg==")

TOOLBAR_ICON_04 = PyEmbeddedImage(
    "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")