'''
Created on Feb 22, 2016

@author: masood
'''


class root(object):

    def __init__(self):
        self.invConv = {v: k for k, v in list(self.noteConv.items())}

    noteConv = {'F': 0, 'G': 1, 'A': 2, 'B': 3, 'C': 4, 'D': 5, 'E': 6}
    noteConvJump = {'C': 0, 'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6}
    invConv = {v: k for k, v in list(noteConv.items())}
    invConvJump = {v: k for k, v in list(noteConvJump.items())}

    def plot(self):
        import matplotlib.pyplot as plt
        plt.figure()
        plt.plot(self.timePlotData, self.jumpPlotData, label="jumps")
        plt.plot(self.timePlotData, self.notePlotData, 'r', label='notes')
        y_axis = range(int(self.otherPlotData['min'] - 1),
            int(self.otherPlotData['max'] + 2))
        y_values = []
        for i in y_axis:
            y_values = y_values + [self.invConvJump[i % 7]]
        plt.yticks(y_axis, y_values)
        plt.legend()
        plt.show()