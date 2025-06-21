import librosa
import matplotlib.pyplot as plt
import numpy as np
import time
from pathlib import Path
from fractions import Fraction

from musicscore.beat import Beat
from musicscore.chord import Chord
from musicscore.measure import Measure
from musicscore.part import Part
from musicscore.score import Score
from musicscore.staff import Staff
from musicscore.voice import Voice

import csv

def getValuesAtFrameStr(frame, chroma):
    returnStr = ''
    binNotes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

    for i in range(0,12):
        returnStr += binNotes[i]
        returnStr += ': '
        returnStr += str(chroma[i][frame-5])
        returnStr += ', '

    return returnStr

def buildScoreFromChroma(y, sr):
    # Create score
    score = Score()
    part = score.add_child(Part('P1', name='Part 1'))
    # measure = part.add_child(Measure(number=1))
    # staff = measure.add_child(Staff(number=1))
    # voice = staff.add_child(Voice(number=1))

    # Probablistic YIN
    freqs, voiced_flag, voiced_probs = librosa.pyin(
        y=y, 
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7'),
        sr=sr)
    
    times = librosa.times_like(freqs)
    tempo = librosa.feature.tempo(y=y, sr=sr)
    
     # Harmonic content extraction
    y_harmonic, y_percussive = librosa.effects.hpss(y)

    # use Constant Q Transform to calculate Pitch Class Profile (PCP), normalized
    chromagram = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr, n_octaves=7)

    # chromagramTransposed = list(map(list, zip(*chromagram)))
    # for i in range(0,len(voiced_probs)):
    #     chromagramTransposed[i].append(voiced_probs[i])
    #     chromagramTransposed[i].append(voiced_flag[i])

    # with open('chromagramTransposed.csv', 'w', newline='') as f:
    #     writer = csv.writer(f)
    #     writer.writerows(chromagramTransposed)

    quarterNoteInSeconds = 60.0 / float(tempo[0])
    quarterNoteFrames = np.round(quarterNoteInSeconds / times[1])
    # binNotes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    newChordBool = [False] * 12
    currentChordBool = [False] * 12
    currentNoteFrames = 0

    for i in range(0, len(freqs)):
        currentNoteFrames += 1
        newChordBool = [False] * 12

        for j in range(0, 12):
            if chromagram[j][i] > 0.25:
                newChordBool[j] = True

        if newChordBool != currentChordBool and voiced_probs[i] > 0.7:
            # New note, add current note to score if note duration is at least a quarter note

            noteDurationFloat = float(currentNoteFrames) / quarterNoteFrames
            noteDurationRational = Fraction(noteDurationFloat).limit_denominator(1)

            if noteDurationRational != 0:
                # Create list of midi values in chord
                midiValues = []
                for note in range(0, 12):
                    if currentChordBool[note]:
                        midiValues.append(60 + note)

                if len(midiValues) == 0: 
                    # add rest instead of a chord if no notes in chord
                    midiValues.append(0)

                part.add_chord(Chord(midiValues, noteDurationRational))
                print(i, currentNoteFrames)
                currentNoteFrames = 0

            currentChordBool = newChordBool

    return score

if __name__ == '__main__':
    filename = "Reference Scales_On C.mp3"
    filePath = Path(str(Path(__file__).parent) + "/" + filename)
    outputDirectory = Path(__file__).parent

    print("Loading file: %s" % filename)
    y, sr = librosa.load(filePath)

    score = buildScoreFromChroma(y, sr)

    xml_path = filePath.with_suffix('.xml')
    score.export_xml(xml_path)
    print("XML saved to: ", xml_path)
    