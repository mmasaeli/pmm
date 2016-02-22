'''
Created on Jan 17, 2016

@author: masood
'''


if __name__ == '__main__':
    pass
    #filename = ('/home/masood/workspace/musicMining/music/homayoun/test/1.xml')
    from xmls import xmls
    b = xmls('/home/masood/workspace/musicMining/music/homayoun/test')
    b.load()
    b.mean()
    b.printOut()
    b.plot()