import librosa
import numpy as np
from pathlib import Path
from fractions import Fraction

from musicscore.beat import Beat
from musicscore.chord import Chord
from musicscore.measure import Measure
from musicscore.part import Part
from musicscore.score import Score
from musicscore.staff import Staff
from musicscore.voice import Voice

def buildScoreFromMP3(filePath):
    # Create score
    score = Score()
    part = score.add_child(Part('P1', name='Part 1'))
    # measure = part.add_child(Measure(number=1))
    # staff = measure.add_child(Staff(number=1))
    # voice = staff.add_child(Voice(number=1))

    # Load file
    y, sr = librosa.load(filePath)

    # Probablistic YIN
    freqs, voiced_flag, voiced_probs = librosa.pyin(
        y=y, 
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7'),
        sr=sr)
    
    times = librosa.times_like(freqs)
    tempo = librosa.feature.tempo(y=y, sr=sr)

    # get onset detecion times, append last frame
    onsetDetectionTimes = np.append(
        librosa.onset.onset_detect(
            y=y, 
            sr=sr, 
            units='frames'), 
        len(freqs))
    
    # Harmonic content extraction
    y_harmonic, y_percussive = librosa.effects.hpss(y)

    # use Constant Q Transform to calculate Pitch Class Profile (PCP), normalized
    chromagram = librosa.feature.chroma_cqt(
        y=y_harmonic, 
        sr=sr, 
        n_octaves=7)

    quarterNoteInSeconds = 60.0 / float(tempo[0])
    quarterNoteFrames = np.round(quarterNoteInSeconds / times[1])
    currentNoteFrames = 0
    currentChord = [0] * 12
    onsetDetectionTimesFrameCounter = 0

    # loop through each frame
    for i in range(0, len(freqs)):
        currentNoteFrames += 1

        # loop through each note in chromagram at frame i, generate running total of intensity for each note
        for j in range(0, 12):
            currentChord[j] += chromagram[j][i]

        # if current frame equals next onset frame, add chord to score
        if i == onsetDetectionTimes[onsetDetectionTimesFrameCounter]:
            noteDurationFloat = float(currentNoteFrames) / quarterNoteFrames
            noteDurationRational = Fraction(noteDurationFloat).limit_denominator(1)

            if noteDurationRational != 0:
                midiValues = []

                # normalize values in currentChord list, then add then to chord if value is above a threshold
                for note in range(0, 12):
                    normalizedNoteIntensity = currentChord[note] / currentNoteFrames
                    if normalizedNoteIntensity > 0.3:
                        midiValues.append(60 + note)

                # add rest instead of a chord if no notes in chord
                if len(midiValues) == 0: 
                    midiValues.append(0)

                part.add_chord(Chord(midiValues, noteDurationRational))

            # next onset frame
            onsetDetectionTimesFrameCounter += 1
            currentNoteFrames = 0
            currentChord = [0] * 12

    return score

if __name__ == '__main__':
    filename = "Reference Scales_On C.mp3"
    filePath = Path(str(Path(__file__).parent) + "/" + filename)

    score = buildScoreFromMP3(filePath)

    xml_path = filePath.with_suffix('.xml')
    score.export_xml(xml_path)
    
