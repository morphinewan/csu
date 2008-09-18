# -*- coding: utf-8 -*-
import wx.lib.newevent

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

(PIStitchConvasGenerateStartEvent, EVT_PI_STITCHCONVASGENERATE_START) = wx.lib.newevent.NewEvent()
(PIStitchConvasGenerateEndEvent, EVT_PI_STITCHCONVASGENERATE_END) = wx.lib.newevent.NewEvent()
(PIStitchConvasGeneratingEvent, EVT_STITCHCONVASGENERATING) = wx.lib.newevent.NewEvent()

(PIPrintConvasGenerateStartEvent, EVT_PI_PRINTCONVASGENERATE_START) = wx.lib.newevent.NewEvent()
(PIPrintConvasGenerateEndEvent, EVT_PI_PRINTCONVASGENERATE_END) = wx.lib.newevent.NewEvent()
(PIPrintConvasGeneratingEvent, EVT_PRINTCONVASGENERATING) = wx.lib.newevent.NewEvent()

(PICrossStitchSaveStartEvent, EVT_PI_CROSSSTITCHSAVE_START) = wx.lib.newevent.NewEvent()
(PICrossStitchSaveEndEvent, EVT_PI_CROSSSTITCHSAVE_END) = wx.lib.newevent.NewEvent()
(PICrossStitchSavingEvent, EVT_CROSSSTITCHSAVING) = wx.lib.newevent.NewEvent()