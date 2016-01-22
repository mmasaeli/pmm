'''
Created on Jan 17, 2016

@author: masood
'''


class xml(object):

    def __init__(self, filename):
        self.filename = filename
        self.tempname = filename + '~.xml'
        return self.readFile()

    _conv = {'C': 0, 'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6}
    measures = []
    filename = ''
    tempname = ''

    def _preProcessFile(self):
        counter = 0
        with open(self.filename,
            encoding='utf-16') as infile, open(self.tempname,
            'w', encoding='utf-16') as outfile:
            for line in infile:
                line = line.replace('<?DoletSibelius Unexported box?>',
                    '<DoletSibelius-Unexported-box>')
                line = line.replace('</direction>',
                    '</direction></DoletSibelius-Unexported-box>')
                line = line.replace('<note>',
                    "<note line-number='{}'>".format(counter))
                outfile.write(line)
                counter = counter + 1

    def _isNotPrintable(self, node):
        printobject = node.attrib.get('print-object')
        return printobject is not None and printobject.lower() == 'no'

    def _readNote(self, note):
        if self._isNotPrintable(note):
            return None
        duration = note.find('duration').text
        rest = note.find('rest') is not None
        step = None
        linenumber = note.attrib['line-number']
        new = {'duration': duration, 'step': step,
            'lineNumber': linenumber}
        if not rest:
            pitch = note.find('pitch')
            step = pitch.find('step').text
            octave = pitch.find('octave').text
            accidental = note.find('accidental')
            if accidental is not None:
                accidental = accidental.text
            new['octave'] = octave
            new['accidental'] = accidental
        return new

    def readFile(self):
        self._preProcessFile()
        from defusedxml.ElementTree import parse
        tree = parse(self.tempname)
        root = tree.getroot()
        for part in root.findall('part'):
            for measure in part.findall('measure'):
                data = []
                rep = measure.find('attributes/measure-style/measure-repeat')
                if rep is not None and rep.attrib['type'].lower() != 'start':
                    c = int(rep.text)
                    block = []
                    for i in range(len(self.measures) - c, len(self.measures)):
                        block.append(self.measures[i])
                    self.measures = self.measures + block
                else:  # Here we load the notes
                    for inthebox in measure.findall('DoletSibelius-Unexported-box'):
                        rep = inthebox.find('direction/direction-type/words')
                        if rep is not None:
                            rep = rep.text
                        for i in range(0, int(rep)):
                            for note in inthebox.findall('note'):
                                new = self._readNote(note)
                                if new is None:
                                    continue
                                data.append(new)
                    for note in measure.findall('note'):
                        new = self._readNote(note)
                        if new is None:
                            continue
                        data.append(new)
                if len(data) > 0:
                    self.measures.append(data)
                del data
        print(self.measures)

    def _calcjump(self, fromnote, tonote):
        if (fromnote is None) or (tonote is None):
            return None
        if (fromnote['step'] is None) or (tonote['step'] is None):
            return None
        octave1 = int(fromnote['octave'])
        octave2 = int(tonote['octave'])
        step1 = self._conv[fromnote['step']]
        step2 = self._conv[tonote['step']]
        return (octave2 - octave1) * 7 + step2 - step1
