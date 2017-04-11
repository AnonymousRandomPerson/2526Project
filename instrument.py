import numpy as np
import queue

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pylab as plt

import audioprocessor

# Whether to plot the returned signals.
debug = False

class Instrument:
    """A synthesized instrument."""
    
    def matchNotes(self, notes, sampleRate):
        """
        Creates a musical excerpt that attempts to match the given notes on the instrument.

        Args:
            notes: The notes to produce sounds for.
            sampleRate: The sample rate to create audio for.

        Returns:
            A list of samples that match the given notes.
        """
        samples = []

        lpfCutoff = audioprocessor.AudioProcessor.HIGHEST_NOTE
        alpha = lpfCutoff / sampleRate
        for channel in notes:
            channelSamples = []
            for note in channel:
                if note[0] == 0:
                    newSamples = np.zeros(note[1])
                else:
                    newSamples = self.getNote(note[0], note[1], sampleRate)

                # Low-pass filter to smooth out sound.
                for i in range(1, len(newSamples)):
                    newSamples[i] += alpha * (newSamples[i - 1] - newSamples[i])

                for sample in newSamples:
                    channelSamples.append(np.float32(sample))

            samples.append(channelSamples)

        if len(notes) > 1:
            samples = np.transpose(samples)
        else:
            samples = samples[0]

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

        # Try to end the wave close to 0.
        waveDuration = int(frequency * int(duration / frequency))
        time = np.linspace(0, seconds, waveDuration)
        samples = np.sin(frequency * 2 * np.pi * time)
        samples = np.append(samples, np.zeros(duration - waveDuration))

        return samples

class AcousticGuitar(Instrument):
    """A synthesized acoustic guitar."""

    def __init__(self):
        """Initializes an acoustic guitar instrument."""
        self.delaySize = 200

    def getBaseStringSound(self, frequency, duration, sampleRate):
        """
        Gets a plucked string note without any distortion effects.

        Args:
            frequency: The frequency of the note.
            duration: The duration of the note in samples.

        Returns:
            A list of samples representing the note.
        """
        samples = []

        # Karplus-Strong algorithm, subtractive synthesis from white noise
        bufferLength = int(sampleRate / frequency)
        buffer = np.random.standard_normal(bufferLength)
        last = buffer[0]
        # Delay effect
        delayLine = queue.Queue(maxsize = self.delaySize)
        bufferCounter = 0
        for i in range(0, duration):
            # Low-pass filter
            current = (last + buffer[bufferCounter]) / 2
            if delayLine.full():
                delayed = delayLine.get()
                delayed *= 0.999
                # Feedback system
                current += delayed
                current /= 2

            samples.append(current)
            delayLine.put(current)
            last = current
            buffer[bufferCounter] = current

            bufferCounter += 1
            if bufferCounter >= len(buffer):
                bufferCounter = 0
        
        if debug:
            seconds = duration / sampleRate
            time = np.linspace(0, seconds, duration)
            plt.plot(time, samples)
            plt.show()

        return samples

    def getNote(self, frequency, duration, sampleRate):
        """
        Gets a note of a certain frequency.

        Args:
            frequency: The frequency of the note.
            duration: The duration of the note in samples.

        Returns:
            A list of samples representing the note.
        """
        samples = self.getBaseStringSound(frequency, duration, sampleRate)

        return samples

class ElectricGuitar(AcousticGuitar):
    """A synthesized electric guitar."""

    def __init__(self):
        """Initializes an electric guitar instrument."""
        self.delaySize = 300

    def getNote(self, frequency, duration, sampleRate):
        """
        Gets a note of a certain frequency.

        Args:
            frequency: The frequency of the note.
            duration: The duration of the note in samples.

        Returns:
            A list of samples representing the note.
        """
        samples = AcousticGuitar.getBaseStringSound(self, frequency, duration, sampleRate)

        # Bitcrusher effect, taking advantage of quantization noise.
        crushFactor = 8
        crushCounter = 0
        currentIndex = 0
        for i in range(duration):
            samples[i] = samples[currentIndex]
            crushCounter += 1
            if crushCounter > crushFactor:
                currentIndex += crushCounter
                crushCounter = 0

        return samples

class Trumpet(Instrument):
    """A synthesized trumpet."""

    def getNote(self, frequency, duration, sampleRate):
        """
        Gets a note of a certain frequency.

        Args:
            frequency: The frequency of the note.
            duration: The duration of the note in samples.

        Returns:
            A list of samples representing the note.
        """
        seconds = duration / sampleRate

        # ADSR curve
        attackLength = int(0.075 * sampleRate)
        decayLength = int(0.3 * sampleRate)
        releaseLength = int(0.2 * sampleRate)
        sustainLength = duration - attackLength - decayLength - releaseLength

        if duration < attackLength:
            return np.zeros(duration)

        # Additive synthesis
        envelope = [3.6, 2.825, 3, 2.688, 1.464, 1.520, 1.122, 0.940, 0.738, 0.495, 0.362, 0.237, 0.154, 0.154, 0.101, 0.082, 0.054, 0.038, 0.036]

        time = np.linspace(0, seconds, duration)
        samples = np.zeros(duration)
        for i, amplitude in enumerate(envelope):
            samples += amplitude * np.sin(frequency * (i + 1) * 2 * np.pi * time)

        # High-pass filter
        RC = 1 / (np.pi * frequency * 32)
        alpha = RC / (RC + 1.0 / sampleRate)
        newSamples = np.zeros(duration)
        newSamples[0] = samples[0]
        for i in range(1, duration):
            newSamples[i] = alpha * (newSamples[i - 1] + samples[i] - samples[i - 1])
        samples = newSamples

        peak = 0.1
        sustain = peak * 0.8

        adsr = np.linspace(0, peak, attackLength)
        if sustainLength < 0:
            # Quickly fade out after attack if duration is too short for full ADSR curve.
            adsr = np.append(adsr, np.linspace(peak, 0, duration - attackLength))
        else:
            adsr = np.append(adsr, np.linspace(peak, sustain, decayLength))
            adsr = np.append(adsr, np.full(sustainLength, sustain))
            adsr = np.append(adsr, np.linspace(sustain, 0, releaseLength))

        samples *= adsr

        return samples