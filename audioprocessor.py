import math
import midiutil as midi
import numpy as np
from scipy import signal
import soundfile as sf

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pylab as plt

import audioplayer
import instrument

# Whether to plot the returned signals.
debug = False

class AudioProcessor:
    """Handles direct processing of audio data."""

    # The highest note that pitch detection will recognize.
    HIGHEST_NOTE = 2093
    # The lowest note that pitch detection will recognize.
    LOWEST_NOTE = 27.5
    
    def __init__(self):
        self.fileTrack = AudioTrack()
        self.synthesizedTrack = AudioTrack()

        self.notes = None

        self.channels = 1
        self.audioLength = 0
        self.sampleRate = 0

        self.player = audioplayer.AudioPlayer(self)

        self.instruments = {"Beep": instrument.Beep(), "Acoustic Guitar": instrument.AcousticGuitar(), "Electric Guitar": instrument.ElectricGuitar(), "Trumpet": instrument.Trumpet()}
        self.currentInstrument = None

    def getInstruments(self):
        """
        Gets the instruments that the processor can synthesize.

        Returns: A list of the instruments that the processor can synthesize.
        """
        return sorted(self.instruments.keys())

    def loadAudioFile(self, filePath):
        """
        Loads an audio file into the processor.

        Args:
            filePath: The file path of the audio file.
        """
        self.player.stop()
        fileData, self.sampleRate = sf.read(filePath, dtype = 'float32')
        self.audioLength = len(fileData)
        try:
            self.channels = len(fileData[0])
        except:
            self.channels = 1
        self.fileTrack.loadSamples(fileData)
        self.notes = None
        self.synthesizeInstrument()
        self.player.loadAudioFile()

    def getTrackByIndex(self, trackIndex):
        """
        Gets a track by its index number.

        Args:
            trackIndex: 0 for the file track, 1 for the synthesized track.
        """
        if trackIndex == 0:
            track = self.fileTrack
        else:
            track = self.synthesizedTrack
        return track

    def setEnabled(self, trackIndex, enabled):
        """
        Sets whether an audio track is enabled.

        Args:
            trackIndex: The track to reload.
            enabled: Whether the audio track is enabled.
        """
        track = self.getTrackByIndex(trackIndex)
        track.enabled = enabled

    def setVolume(self, trackIndex, volume):
        """
        Sets the volume of an audio track.

        Args:
            trackIndex: The track to reload.
            volume: The volume [0,1] of the track.
        """
        track = self.getTrackByIndex(trackIndex)
        if track:
            track.volume = np.float32(volume)

    def reloadData(self, trackIndex):
        """
        Reloads the audio data after a setting has changed.

        Args:
            trackIndex: The track to reload.
        """
        reloadTrack = self.getTrackByIndex(trackIndex)
        self.stop()
        reloadTrack.reload()

        self.player.loadSamples()

    def selectInstrument(self, newInstrument = None):
        """
        Selects a new instrument to be overlaid over the audio data.

        Args:
            newInstrument: The name of the new instrument to select.
        """
        self.currentInstrument = self.instruments[newInstrument]
        self.synthesizeInstrument()

    def synthesizeInstrument(self):
        """Creates new instrument data to match the current loaded track."""

        if self.fileTrack.baseSamples is not None:
            if self.notes is None:
                self.notes = self.detectPitches()
                self.writeMidi(self.notes)
            synthesizedData = self.currentInstrument.matchNotes(self.notes, self.sampleRate)
            self.synthesizedTrack.loadSamples(synthesizedData)
            self.reloadData(1)

    def detectPitches(self):
        """
        Does pitch detection on the currently loaded audio file.

        Returns:
            A list of lists [frequency, sample duration] representing notes that were detected.
        """
        audioData = self.fileTrack.baseSamples
        notes = []
        for channel in range(self.channels):
            notes.append([])
        duration = len(audioData)

        increment = int(self.sampleRate / 16)
        sampleDuration = increment
        startIndex = 0
        lastNote = 0
        while startIndex < duration:
            for channel in range(self.channels):
                channelNotes = notes[channel]
                endIndex = startIndex + increment
                if endIndex > duration:
                    endIndex = duration
                    sampleDuration = duration - startIndex
                if self.channels == 1:
                    currentSamples = audioData[startIndex:endIndex]
                else:
                    currentSamples = audioData[startIndex:endIndex, channel]

                # Autocorrelation pitch detection.
                autocorrelation = signal.correlate(currentSamples, currentSamples)
                autoLength = len(autocorrelation)

                peakCheck = sampleDuration
                difference = 0
                while difference <= 0 and peakCheck + 1 < autoLength:
                    last = autocorrelation[peakCheck]
                    current = autocorrelation[peakCheck + 1]
                    difference = current - last
                    peakCheck += 1
        
                if debug:
                    time = np.linspace(-self.audioLength / self.sampleRate, self.audioLength / self.sampleRate, autoLength)
                    plt.plot(time, autocorrelation)
                    plt.show()

                maxIndex = peakCheck
                maxValue = 0
                for i in range(peakCheck, autoLength):
                    current = abs(autocorrelation[i])
                    if current > maxValue:
                        maxValue = current
                        maxIndex = i

                frequency = self.sampleRate / (maxIndex - sampleDuration)
                newNote = Note(frequency, sampleDuration)
                channelNotes.append(newNote)

            startIndex += increment

        for channel in range(self.channels):
            if self.channels == 1:
                currentSamples = audioData
            else:
                currentSamples = audioData[:, channel]
            channelNotes = notes[channel]

            def mergeNotes():
                """Merges notes that are very similar to each other."""
                i = 0
                prevNote = None
                while i < len(channelNotes):
                    currentNote = channelNotes[i]
                    currentMidi = currentNote.midi

                    if not self.isNoteInRange(currentNote.frequency):
                        # 0-out notes that are below A0 or above C8.
                        currentNote.setZero()
                        currentMidi = 0


                    if not prevNote:
                        prevNote = currentNote
                        i += 1
                        continue

                    prevMidi = prevNote.midi

                    if currentMidi == prevMidi:
                        # Merge notes that are about the same (within a semitone).
                        prevNote.duration += currentNote.duration
                        del channelNotes[i]
                    else:
                        prevNote = currentNote
                        i += 1

            mergeNotes()

            # Find the maximum volume of the track.
            peak = 0
            for sample in currentSamples:
                peak = max(abs(sample), peak)

            # Change volumes of notes based on peaks of original track.
            timeCounter = 0
            for note in channelNotes:
                if note.frequency > 0:
                    noteEnd = timeCounter + note.duration
                    maxSample = 0
                    for i in range(timeCounter, noteEnd):
                        maxSample = max(maxSample, abs(currentSamples[i]))
                    note.volume = maxSample / peak
                timeCounter += note.duration

            # 0-out notes that are too soft.
            for note in channelNotes:
                if note.frequency > 0 and note.volume < 0.2:
                    note.setZero()

            mergeNotes()
            
            # 0 out notes that deviate too far from the mean note.
            usedNotes = []
            for note in channelNotes:
                if self.isNoteInRange(note.frequency):
                    for i in range(int(note.duration / increment)):
                        usedNotes.append(note.midi)
            mean = np.mean(usedNotes)
            deviation = np.std(usedNotes)
            print("Mean:", mean)
            print("Standard deviation:", deviation)
            for note in channelNotes:
                difference = abs(note.midi - mean)
                if difference > deviation * 2:
                    note.setZero()

            mergeNotes()
                
                
        print("Notes:", notes)

        return notes

    def writeMidi(self, notes):
        """
        Writes notes to a MIDI file.

        Args:
            notes: The notes to write to MIDI.
        """
        track = 0
        channel = 0
        time = 0
        duration = 1
        tempo = 100

        samplesPerBeat = self.sampleRate / (tempo / 60)

        midiFile = midi.MIDIFile(1)
        midiFile.addTempo(track, time, tempo)

        started = False
        for note in notes[0]:
            if note.midi > 0:
                midiFile.addNote(track, channel, note.midi, time / samplesPerBeat, note.duration / samplesPerBeat, int(127 * note.volume))
                started = True
            if started:
                time += note.duration

        with open("output.mid", "wb") as output_file:
            midiFile.writeFile(output_file)

    def isNoteInRange(self, note):
        """
        Checks if a note is in the audio processor's range.

        Args:
            note: The note to check.

        Returns:
            Whether the note is in the audio processor's range.
        """
        return note >= AudioProcessor.LOWEST_NOTE and note <= AudioProcessor.HIGHEST_NOTE

    def initialized(self):
        """
        Returns whether the processor has audio loaded into it.

        Returns:
            Whether the processor has audio loaded into it.
        """
        return self.fileData

    def play(self):
        """Starts playback for the current audio."""
        self.player.play()

    def pause(self):
        """Pauses playback for the current audio."""
        self.player.pause()

    def stop(self):
        """Stop playback for the current audio."""
        self.player.stop()

    def close(self):
        """Cleans up the processor before quitting the applicaiton."""
        self.player.close()

class AudioTrack():
    """Data about an audio track."""

    def __init__(self):
        """Initializes an audio track."""
        self.loadSamples(None)
        self.volume = np.float32(1.0)
        self.enabled = True

    def loadSamples(self, samples):
        """
        Loads samples into the audio track.

        Args:
            samples: The samples in the audio track.
        """
        self.samples = samples
        self.baseSamples = samples

    def reload(self):
        """
        Reloads the audio data after a setting has changed.

        Args:
            enabled: Whether the audio track is enabled.
        """
        self.samples = self.baseSamples

    def getVolume(self):
        """
        Gets the volume of the audio track.

        Returns:
            The volume of the audio track.
        """
        if self.enabled:
            return self.volume
        else:
            return 0

class Note():
    """A description of a note in a track."""

    def __init__(self, frequency, duration):
        """
        Initializes a note.

        Args:
            frequency: The frequency of the note.
            duration: The duration of the note in samples.
        """
        self.duration = duration
        self.setFrequency(frequency)
        self.volume = 1

    def setFrequency(self, frequency):
        """
        Sets the frequency of the note.

        Args:
            frequency: The frequency of the note.
        """
        self.midi = round(69 + 12 * math.log(frequency / 440, 2))
        # Round the frequency to nearest semitone.
        self.frequency = 2 ** ((self.midi - 69) / 12) * 440

    def setZero(self):
        """Sets the frequency of the note to 0."""
        self.midi = 0
        self.frequency = 0
        self.volume = 0

    def __repr__(self):
        """
        Converts the note into a string.

        Returns:
            The string representation of the note.
        """
        return "(" + str(self.frequency) + ", " + str(self.duration) + ")"