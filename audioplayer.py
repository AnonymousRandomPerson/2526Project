import numpy as np
import pyaudio as pa

class AudioPlayer:
    """Plays back audio."""

    def __init__(self, processor):
        """
        Initializes the player.

        Args:
            processor: The audio processor for the application.
        """
        self.processor = processor
        self.stream = None
        self.playIndex = 0
        self.pyaudio = pa.PyAudio()

    def loadAudioFile(self):
        """
        Loads audio data into the player.
        """
        self.stop()
        self.channels = self.processor.channels
        self.sampleRate = self.processor.sampleRate
        self.audioLength = self.processor.audioLength
        self.loadSamples()
        self.stream = self.pyaudio.open(format = pa.paFloat32, channels = self.channels, rate = self.sampleRate, output = True, stream_callback = self.playCallback)
        self.stream.stop_stream()

    def loadSamples(self):
        """
        Loads audio sample data into the player.
        """
        self.fileTrack = self.processor.fileTrack
        self.synthesizedTrack = self.processor.synthesizedTrack

    def playCallback(self, inData, frameCount, timeInfo, status):
        numSamples = frameCount * self.channels
        if self.playIndex >= self.audioLength:
            return (np.zeros(numSamples), pa.paComplete)
        endIndex = self.playIndex + numSamples
        fileVolume = self.fileTrack.getVolume()
        synthesizedVolume = self.synthesizedTrack.getVolume()
        if endIndex >= self.audioLength:
            fileSamples = self.fileTrack.samples[self.playIndex:]
            synthesizedSamples = self.synthesizedTrack.samples[self.playIndex:]
        else:
            fileSamples = self.fileTrack.samples[self.playIndex:endIndex]
            synthesizedSamples = self.synthesizedTrack.samples[self.playIndex:endIndex]
        samples = np.multiply(fileSamples, fileVolume) + np.multiply(synthesizedSamples, synthesizedVolume)
        flag = pa.paContinue
        self.playIndex += frameCount
        return (samples, flag)

    def play(self):
        """Starts playback for the current audio."""
        self.checkResetStream()
        self.stream.start_stream()

    def pause(self):
        """Pauses playback for the current audio."""
        self.checkResetStream()
        if self.stream.is_stopped():
            self.play()
        else:
            self.stream.stop_stream()

    def stop(self):
        """Stop playback for the current audio."""
        if self.stream:
            self.stream.stop_stream()
            self.playIndex = 0

    def checkResetStream(self):
        """Resets the stream if it has finished playing."""
        if self.playIndex >= self.audioLength:
            self.playIndex = 0
            self.stream.stop_stream()

    def close(self):
        """Cleans up the player. before quitting the applicaiton."""
        self.pyaudio.terminate()