'''
Created on Jan 17, 2016

@author: masood
'''

from musicXml import xml

if __name__ == '__main__':
    pass
    filename = ('/home/masood/workspace/musicMining/music/homayoun/test/2.xml')
    a = xml(filename)
    a.count()
    print(a.allCounted)
    a.plot()