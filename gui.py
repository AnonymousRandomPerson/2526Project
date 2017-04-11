from tkinter import *
import tkinter.filedialog as filedialog
import sys
import os
import traceback

import audioprocessor

class Gui:
    """The main GUI screen."""

    def __init__(self):
        """Initializes the screen elements."""
        self.root = Tk()
        self.root.wm_title("2526 Project")

        self.frame = Frame(self.root)
        self.frame.grid(row = 0, column = 0)

        self.processor = audioprocessor.AudioProcessor()

        self.error = None

        rowCounter = 0
        self.createButton("Load audio file", self.loadAudioFile, rowCounter, 0)

        rowCounter += 1
        # Error

        rowCounter += 1
        self.playFrame = Frame(self.frame)
        self.playFrame.grid(row = rowCounter, column = 0)
        playButton = self.createButton("Play", self.playAudio, 0, 0, self.playFrame)
        pauseButton = self.createButton("Pause", self.pauseAudio, 0, 1, self.playFrame)
        stopButton = self.createButton("Stop", self.stopAudio, 0, 2, self.playFrame)
        self.playButtons = [playButton, pauseButton, stopButton]

        rowCounter += 1
        self.settingsFrame = Frame(self.frame)
        self.settingsFrame.grid(row = rowCounter, column = 0)
        self.createSettingsBar(0)

        self.createSettingsBar(1)
        
        instruments = self.processor.getInstruments()
        currentInstrument = StringVar()
        currentInstrument.set(instruments[0])
        currentInstrument.set("Electric Guitar")
        self.processor.selectInstrument(currentInstrument.get())
        instrumentSelect = OptionMenu(self.settingsFrame, currentInstrument, *instruments, command = self.selectInstrument)
        instrumentSelect.config(width = 13)
        instrumentSelect.grid(row = 1, column = 0)
        self.playButtons.append(instrumentSelect)

        self.setPlayButtonsEnabled(False)

        rowCounter += 1
        self.createButton("Quit", self.quitApp, rowCounter, 0)
        self.root.protocol("WM_DELETE_WINDOW", self.quitApp)

        self.root.mainloop()

    def createButton(self, buttonText, buttonCommand, buttonRow, buttonColumn, frame = None):
        """
        Creates a button on the GUI.
        
        Args:
            buttonText: The text to display on the button.
            buttonCommand: The callback to fire when the button is pressed.
            buttonRow: The row of the GUI to place the button in.
            buttonColumn: The column of the GUI to place the button in.
            frame: The frame that the button should be contained in.

        Returns:
            The created button.
        """
        if not frame:
            frame = self.frame
        button = Button(frame, text = buttonText, command = buttonCommand)
        button.grid(row = buttonRow, column = buttonColumn)
        return button

    def createSettingsBar(self, row):
        """
        Creates a settings bar used to customize one of the tracks.

        Args:
            row: The row to create the bar on.

        Returns:
            A frame containing the settings bar.
        """
        columnCounter = 1
        enabled = IntVar()
        enabled.set(1)
        enabledButton = Checkbutton(self.settingsFrame, text = "Enabled", variable = enabled, command = lambda: self.enableTrack(row, enabled.get()))
        enabledButton.grid(row = row, column = columnCounter)
        self.playButtons.append(enabledButton)

        columnCounter += 1
        volumeVar = DoubleVar()
        volumeVar.set(1.0)
        volumeScale = Scale(self.settingsFrame, variable = volumeVar, from_ = 0.0, to = 1.0, resolution = 0.01, orient = HORIZONTAL, command = lambda volume: self.setVolume(row, volume))
        volumeScale.grid(row = row, column = columnCounter)
        self.playButtons.append(volumeScale)

    def enableTrack(self, track, enabled):
        """
        Enables or disables a certain track.

        Args:
            track: The track to enable or disable.
            enabled: Whether to enable the track.
        """
        self.processor.setEnabled(track, enabled)

    def setVolume(self, track, volume):
        """
        Sets the volume of a certain track.

        Args:
            track: The track to set the volume of.
            volume: The volume to set the track to.
        """
        self.processor.setVolume(track, volume)

    def setPlayButtonsEnabled(self, enabled):
        """
        Sets whether the play buttons are enabled or not.

        Args:
            enabled: Whether to enable the play buttons (True) or disable them (False).
        """
        if enabled:
            enableCode = NORMAL
        else:
            enableCode = DISABLED
        for button in self.playButtons:
            button.config(state = enableCode)

    def loadAudioFile(self):
        """Prompts the user to select an audio file for the base of the application."""
        audioFile = None
        audioFile = "/Users/chenghanngan/Documents/School/GT/PickAR/PickAR/Assets/Sounds/All Collected.wav"

        if not audioFile:
            audioFile = filedialog.askopenfilename()
        if not audioFile:
            return

        try:
            self.processor.loadAudioFile(audioFile)
            self.setPlayButtonsEnabled(True)
            self.resetErrorText()
        except RuntimeError:
            error = "Invalid file type."
            self.setErrorText(error)

    def selectInstrument(self, selectedInstrument):
        """
        Selects a new instrument to be used.

        Args:
            selectedInstrument: The new instrument to be used.
        """
        self.processor.selectInstrument(selectedInstrument)

    def setErrorText(self, errorText):
        """
        Sets the contents of the error message.
        Args:
            errorText: The contents of the error message.
        """
        self.resetErrorText()
        self.error = Label(self.frame, text = errorText, fg = "red")
        self.error.grid(row = 1, column = 0)

    def resetErrorText(self):
        """Removes the current error message."""
        if self.error:
            self.error.grid_forget()

    def playAudio(self):
        """Starts playback for the current audio."""
        self.processor.play()

    def pauseAudio(self):
        """Pauses playback for the current audio."""
        self.processor.pause()

    def stopAudio(self):
        """Stops playback for the current audio."""
        self.processor.stop()

    def quitApp(self):
        """Quits the application."""
        try:
            self.processor.close()
        except:
            traceback.print_exc()
        sys.exit()