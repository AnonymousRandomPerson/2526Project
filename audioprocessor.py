import numpy as np
import soundfile as sf

import audioplayer
import instrument

class AudioProcessor:
    """Handles direct processing of audio data."""
    
    def __init__(self):
        self.audioData = []
        self.fileTrack = None
        self.synthesizedTrack = None

        self.channels = 1
        self.audioLength = 0
        self.sampleRate = 0

        self.player = audioplayer.AudioPlayer(self)

        self.instruments = {"Guitar": instrument.Guitar()}
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
        fileData, self.sampleRate = sf.read(filePath, dtype = 'float32')
        self.audioLength = len(fileData)
        self.channels = len(fileData[0])
        self.fileTrack = AudioTrack(fileData)
        self.synthesizeInstrument()
        self.audioData = self.fileTrack.samples + self.synthesizedTrack.samples
        self.player.loadAudioFile()

    def reloadData(self, trackIndex, enabled = None):
        """
        Reloads the audio data after a setting has changed.

        Args:
            trackIndex: The track to reload.
            enabled: Whether the audio track is enabled.
        """
        if trackIndex == 0:
            reloadTrack = self.fileTrack
        else:
            reloadTrack = self.synthesizedTrack
        self.stop()
        reloadTrack.reload(enabled)

        self.audioData = self.fileTrack.samples + self.synthesizedTrack.samples
        self.player.audioData = self.audioData

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

        if self.fileTrack:
            synthesizedData = self.currentInstrument.matchNotes(self.fileTrack.baseSamples)
            self.synthesizedTrack = AudioTrack(synthesizedData)

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

    def __init__(self, samples):
        """
        Initializes an audio track.

        Args:
            samples: The samples in the audio track.
        """
        self.samples = samples
        self.baseSamples = samples
        self.enabled = True

    def reload(self, enabled = None):
        """
        Reloads the audio data after a setting has changed.

        Args:
            enabled: Whether the audio track is enabled.
        """
        if enabled != None:
            self.enabled = enabled

        if not self.enabled:
            self.samples = np.zeros((len(self.baseSamples), len(self.baseSamples[0])), dtype = np.float32)
            return

        self.samples = self.baseSamples