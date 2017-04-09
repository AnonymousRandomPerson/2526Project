import numpy as np
import soundfile as sf

import audioplayer

class AudioProcessor:
    """Handles direct processing of audio data."""
    
    def __init__(self):
        self.audioData = []
        self.channels = 1
        self.audioLength = 0
        self.sampleRate = 0
        self.player = audioplayer.AudioPlayer(self)

    def loadAudioFile(self, filePath):
        """
        Loads an audio file into the processor.

        Args:
            filePath: The file path of the audio file.
        """
        self.audioData, self.sampleRate = sf.read(filePath, dtype = 'float32')
        self.audioLength = len(self.audioData)
        self.channels = len(self.audioData[0])
        self.player.loadAudioFile()

    def initialized(self):
        """
        Returns whether the processor has audio loaded into it.

        Returns:
            Whether the processor has audio loaded into it.
        """
        return self.audioData

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