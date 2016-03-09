'''
Created on Feb 22, 2016

@author: masood
'''
from theRoot import root


class xmls(root):

    files = []
    xmls = []
    notes = {}
    durations = {}
    jumpPlotData = []
    notePlotData = []
    timePlotData = []
    otherPlotData = {}
    plotData = {}

    def __init__(self, path):
        from os import walk
        import os
        self.files = []
        char = '/'
        if path is None:
            path = os.path.dirname(os.path.realpath(__file__))
        import platform
        if platform.system() == "Windows":
            char = '\\'
        for (dirpath, dirnames, filenames) in walk(path):
            for f in filenames:
                if f.lower().find(".xml", len(f) - 4) < 0:
                    continue
                self.files.append(path + char + f)
            break

    def load(self):
        self.xmls = []
        from musicXml import xml
        for f in self.files:
            self.xmls = self.xmls + [xml(f)]
            self.xmls[len(self.xmls) - 1].count()
            self.xmls[len(self.xmls) - 1].makePlotData()
            #self.xmls[len(self.xmls) - 1].plot()

    def printOut(self):
        print('\nFrequencies:')
        print(sorted(self.notes.items()))
        print('\nDurations:')
        print(sorted(self.durations))

    def mean(self):
        if len(self.xmls) < 1:
            return
        theMin = float('Inf')
        theMax = -theMin
        ln = len(self.xmls)
        for f in self.xmls:
            for k in list(f.allCounted.keys()):
                self.notes[k] = (f.allCounted[k] if k not in self.notes else f.allCounted[k] + self.notes[k]) / ln
            for k in list(f.allDurations.keys()):
                self.durations[k] = (f.allDurations[k] if k not in self.durations else f.allDurations[k] + self.durations[k]) / ln
            for k in list(f.plotData.keys()):
                nc = 0 if f.plotData[k][0] is None else 1
                nj = 0 if f.plotData[k][1] is None else 1
                if k not in self.plotData:
                    self.plotData[k] = [f.plotData[k][0], f.plotData[k][1],
                        nc, nj]
                else:
                    n = 0
                    n = n + 0 if self.plotData[k][0] is None else self.plotData[k][0]
                    n = n + 0 if f.plotData[k][0] is None else f.plotData[k][0]
                    j = 0
                    j = j + 0 if self.plotData[k][1] is None else self.plotData[k][1]
                    j = j + 0 if f.plotData[k][1] is None else f.plotData[k][1]
                    ncn = self.plotData[k][2] + nc
                    njn = self.plotData[k][3] + nj
                    self.plotData[k] = [n, j, ncn, njn]
        self.timePlotData = []
        self.notePlotData = []
        self.jumpPlotData = []
        import collections
        od = collections.OrderedDict(sorted(self.plotData.items()))
        for k in od:
            self.plotData[k][0] = self.plotData[k][0] / self.plotData[k][2]
            if self.plotData[k][1] is not None:
                self.plotData[k][1] = self.plotData[k][1] / self.plotData[k][2]
            self.timePlotData.append(k)
            self.notePlotData.append(self.plotData[k][0])
            self.jumpPlotData.append(self.plotData[k][1])
            if self.plotData[k][0] is not None:
                theMax = theMax if theMax > self.plotData[k][0] else self.plotData[k][0]
                theMin = theMin if theMin < self.plotData[k][0] else self.plotData[k][0]
        self.otherPlotData['min'] = theMin
        self.otherPlotData['max'] = theMax