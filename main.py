'''
Created on Jan 17, 2016

@author: masood
'''
import sys

if __name__ == '__main__':
    pass
    from xmls import xmls
    path = None
    if(len(sys.argv) > 1):
        path = sys.argv[1]
    b = xmls(path)
    b.load()
    b.mean()
    b.printOut()
    b.plot()