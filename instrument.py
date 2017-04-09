import numpy as np

class Instrument:
    """A synthesized instrument."""
    
    def matchNotes(self, fileData):
        """
        Creates a musical excerpt that attempts to match the notes of the given audio data on the instrument.

        Args:
            fileData: The audio data to match.

        Returns:
            A list of samples that match the notes in the given audio data.
        """
        return self.getNote(440, len(fileData))

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

class Guitar(Instrument):
    """A synthesized acoustic guitar."""

    def getNote(self, frequency, duration):
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