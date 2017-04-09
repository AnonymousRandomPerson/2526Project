import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pylab as plt

# Whether to plot the returned signals.
debug = False

class Instrument:
    """A synthesized instrument."""
    
    def matchNotes(self, fileData, sampleRate):
        """
        Creates a musical excerpt that attempts to match the notes of the given audio data on the instrument.

        Args:
            fileData: The audio data to match.
            sampleRate: The sample rate to create audio for.

        Returns:
            A list of samples that match the notes in the given audio data.
        """
        samples = self.getNote(440, len(fileData), sampleRate)
        return samples

    def duplicateChannel(self, channel):
        """
        Duplicates a single channel of data into two channels.

        Args:
            channel: The single channel to duplicate.

        Returns:
            A double-channel list duplicated from the single channel
        """
        newSamples = []
        for sample in channel:
            sample32 = np.float32(sample / 2)
            newSamples.append((sample32, sample32))
        return newSamples

class Beep(Instrument):
    """A sine wave."""

    def getNote(self, frequency, duration, sampleRate):
        """
        Gets a note of a certain frequency.

        Args:
            frequency: The frequency of the note.
            duration: The duration of the note in samples.
            sampleRate: The sample rate to create audio for.

        Returns:
            A list of samples representing the note.
        """
        seconds = duration / sampleRate

        time = np.linspace(0, seconds, duration)
        samples = np.sin(frequency * 2 * np.pi * time)

        if debug:
            plt.plot(time, samples)
            plt.show()

        samples = self.duplicateChannel(samples)

        return samples

class Guitar(Instrument):
    """A synthesized acoustic guitar."""

    def getNote(self, frequency, duration, sampleRate):
        """
        Gets a note of a certain frequency.

        Args:
            frequency: The frequency of the note.
            duration: The duration of the note in samples.

        Returns:
            A list of samples representing the note.
        """
        samples = np.random.standard_normal(duration)

        samples = self.duplicateChannel(samples)

        return samples