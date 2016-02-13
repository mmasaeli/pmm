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
    _accidentals = {'sharp': 0.5, 'flat': -0.5, 'quarter-flat': -0.25,
        'natural': 0}
    measures = []
    filename = ''
    tempname = ''
    sortedNotes = []
    allCounted = {}

    def plot(self):
        import matplotlib.pyplot as plt
        fig1 = plt.figure()
        data = []
        times = []
        time = 0
        for note in self.sortedNotes:
            data = data + [note['jump']]
            time = time + note['duration']
            times = times + [time]
        plt.plot(times, data)
        plt.show()

    def count(self):
        for note in self.sortedNotes:
            key = str(note['step'])
            if key == 'None':
                key = 'rest'
            if key not in self.allCounted:
                self.allCounted[key] = 1
                self.allCounted[key + '-duration'] = note['duration']
            else:
                self.allCounted[key] = self.allCounted[key] + 1
                self.allCounted[key + '-duration'] = self.allCounted[key + '-duration'] + note['duration']
            if key != 'rest' and note['accidental'] is not None:
                accid = str(note['accidental'])
                newkey = key + "_" + accid
                if newkey not in self.allCounted:
                    self.allCounted[newkey] = 1
                    self.allCounted[newkey + '-duration'] = note['duration']
                else:
                    self.allCounted[newkey] = self.allCounted[newkey] + 1
                    self.allCounted[newkey + '-duration'] = self.allCounted[newkey + '-duration'] + note['duration']

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
        new = {'duration': int(duration), 'step': step,
            'lineNumber': float(linenumber)}
        if not rest:
            self._accidental = self._getAccidentalOfFirstNote(note)
            pitch = note.find('pitch')
            step = pitch.find('step').text
            octave = pitch.find('octave').text
            accidental = self._setAccidental(note)
            new['octave'] = int(octave)
            new['accidental'] = accidental
            new['step'] = step
        return new

    def readFile(self):
        self.loadNotes()
        self.sortedNotes = []
        from operator import itemgetter
        for c in self.measures:
            notes = []
            for j in c:
                notes = notes + [j]
            self.sortedNotes = self.sortedNotes + sorted(notes,
                key=itemgetter('lineNumber'))
        lastNote = None
        for i in range(0, len(self.sortedNotes)):
            jump = self._calcjump(lastNote, self.sortedNotes[i])
            self.sortedNotes[i]['jump'] = jump
            lastNote = self.sortedNotes[i]

    def _setAccidental(self, note):
        accidental = note.find('accidental')
        if accidental is not None:
            #TODO identify BEKAAR and set lastAcc
            #if accidental
            return accidental.text
        #TODO: must get the numbers for notes
        #here
        pitch = note.find('pitch')
        if self._lastAcc is not None and pitch in self._lastAcc:
            return self._lastAcc[pitch]
        if self._accidental is not None and pitch in self._accidental:
            return self._accidental[pitch]
        return 'natural'

    def _getAccidentalOfFirstNote(self, note):
        notation = note.find('notations')
        if notation is None:
            return None
        accid = dict()
        x = None
        y = None
        inv_conv = {v: k for k, v in list(self._conv.items())}
        for accMark in notation.findall('accidental-mark'):
            if 'relative-x' in accMark.attrib:
                x = int(accMark.attrib['relative-x'])
            if 'default-y' in accMark.attrib:
                y = int(accMark.attrib['default-y'])
            if x is not None and y is not None:
                n = int((y - 5) / 5) % 7
                accid[inv_conv[n]] = accMark.text
        return accid

    def _calcRepeatedNumbers(self, measure, rep):
        minLine = float("Inf")
        maxLine = 0
        extraRep = 0
        extraLine = 0
        for note in measure:
            if note['lineNumber'] < minLine:
                minLine = note['lineNumber']
            if note['lineNumber'] > maxLine:
                maxLine = note['lineNumber']
        extraRep = 1 / (rep + 1)
        extraLine = extraRep / (maxLine - minLine + 1)
        return [minLine, maxLine, extraRep, extraLine]

    def _calcLineNumber(self, lineNumber, i, params):
        return params[1] + i * params[2] + params[3] * (lineNumber - params[0])

    _accidental = dict()
    _lastAcc = None

    def loadNotes(self):
        self._preProcessFile()
        from defusedxml.ElementTree import parse
        tree = parse(self.tempname)
        root = tree.getroot()
        for part in root.findall('part'):
            repCount = 0
            #Reading the part:
            for measure in part.findall('measure'):
                self._lastAcc = None
                #Reading one Measure
                data = []
                if repCount > 0:
                    repCount = repCount + 1
                rep = measure.find('attributes/measure-style/measure-repeat')
                if rep is not None and rep.attrib['type'].lower() == 'start':
                    repCount = 1
                else:
                    if rep is not None and rep.attrib['type'].lower() == 'stop':
                        c = int(rep.text)
                        block = []
                        repCount = repCount - 1
                        for i in range(len(self.measures) - repCount, len(self.measures)):
                            block.append(self.measures[i])
                        self.measures = self.measures + block
                        repCount = 0
                    # Here we load the notes
                    for inthebox in measure.findall('DoletSibelius-Unexported-box'):
                        #reading all the BOX REPEATS:
                        rep = inthebox.find('direction/direction-type/words')
                        if rep is not None:
                            rep = int(rep.text)
                        minLine = float("Inf")
                        maxLine = 0
                        extraRep = 0
                        extraLine = 0
                        for i in range(0, rep):
                            if i == 1:
                                extraRep = 1 / (rep + 1)
                                extraLine = extraRep / (maxLine - minLine + 1)
                            for note in inthebox.findall('note'):
                                #Notes in the box
                                new = self._readNote(note)
                                if new is None:
                                    continue
                                if i == 0:
                                    if new['lineNumber'] < minLine:
                                        minLine = new['lineNumber']
                                    if new['lineNumber'] > maxLine:
                                        maxLine = new['lineNumber']
                                else:
                                    new['lineNumber'] = self._calcLineNumber(new['lineNumber'],
                                        i, [minLine, maxLine, extraRep, extraLine])
                                data.append(new)
                    for note in measure.findall('note'):
                        #regular notes:
                        new = self._readNote(note)
                        if new is None:
                            continue
                        data.append(new)
                if len(data) > 0:
                    self.measures.append(data)
                del data

    def _calcjump(self, fromnote, tonote):
        if (fromnote is None) or (tonote is None):
            return None
        if (fromnote['step'] is None) or (tonote['step'] is None):
            return None
        octave1 = fromnote['octave']
        octave2 = tonote['octave']
        step1 = self._conv[fromnote['step']]
        step2 = self._conv[tonote['step']]
        if fromnote['accidental'] is not None:
            step1 = step1 + self._accidentals[fromnote['accidental']]
        if tonote['accidental'] is not None:
            step2 = step2 + self._accidentals[tonote['accidental']]
        return (octave2 - octave1) * 7 + step2 - step1
