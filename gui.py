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

        self.audioProcessor = audioprocessor.AudioProcessor()

        self.error = None

        self.createButton("Load audio file", self.loadAudioFile, 0, 0)

        self.playFrame = Frame(self.frame)
        self.playFrame.grid(row = 2, column = 0)
        playButton = self.createButton("Play", self.playAudio, 0, 0, self.playFrame)
        pauseButton = self.createButton("Pause", self.pauseAudio, 0, 1, self.playFrame)
        stopButton = self.createButton("Stop", self.stopAudio, 0, 2, self.playFrame)
        self.playButtons = [playButton, pauseButton, stopButton]
        self.setPlayButtonsEnabled(False)

        self.createButton("Quit", self.quitApp, 3, 0)
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

        audioFile = filedialog.askopenfilename()
        #audioFile = "/Users/chenghanngan/Documents/School/GT/MUSI2526/Project/2526Project/PC.ogg"

        try:
            self.audioProcessor.loadAudioFile(audioFile)
            self.setPlayButtonsEnabled(True)
            self.resetErrorText()
        except RuntimeError:
            error = "Invalid file type."
            self.setErrorText(error)

    def setErrorText(self, errorText):
        """
        Sets the contents of the error message.
        Args:
            errorText: The contents of the error message.
        """
        if self.error:
            self.error.grid_forget()
        self.error = Label(self.frame, text = errorText, fg = "red")
        self.error.grid(row = 1, column = 0)

    def resetErrorText(self):
        """Removes the current error message."""
        if self.error:
            self.error.grid_forget()

    def playAudio(self):
        """Starts playback for the current audio."""
        self.audioProcessor.play()

    def pauseAudio(self):
        """Pauses playback for the current audio."""
        self.audioProcessor.pause()

    def stopAudio(self):
        """Stops playback for the current audio."""
        self.audioProcessor.stop()

    def quitApp(self):
        """Quits the application."""
        try:
            self.audioProcessor.close()
        except:
            traceback.print_exc()
        sys.exit()