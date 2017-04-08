from tkinter import *
import tkinter.filedialog as filedialog
import sys
import os

class Gui:

    """File extensions that are accepted by the application."""
    ALLOWED_EXTENSIONS = [".mp4", ".m4a"]

    """The main GUI screen."""

    def __init__(self):
        """Initializes the screen elements."""

        self.root = Tk()
        self.root.wm_title("2526 Project")

        self.frame = Frame(self.root)
        self.frame.grid(row=0, column=0)

        self.error = None

        self.createButton("Load audio file", self.loadAudioFile, 0, 0)
        self.createButton("Quit", self.quitApp, 2, 0)

        self.root.mainloop()

    def createButton(self, buttonText, buttonCommand, buttonRow, buttonColumn):
        """
        Creates a button on the GUI.
        
        Args:
            buttonText: The text to display on the button.
            buttonCommand: The callback to fire when the button is pressed.
            buttonRow: The row of the GUI to place the button in.
            buttonColumn: The column of the GUI to place the button in.

        Returns:
            The created button.
        """

        button = Button(self.frame, text = buttonText, command = buttonCommand)
        button.grid(row = buttonRow, column = buttonColumn)
        return button

    def loadAudioFile(self):
        """Prompts the user to select an audio file for the base of the application."""

        audioFile = filedialog.askopenfilename()

        # Validate file type.
        extensionIndex = audioFile.rfind(".")
        if extensionIndex >= 0:
            extension = audioFile[extensionIndex:]
        else:
            extension = None
        if not extension in Gui.ALLOWED_EXTENSIONS:
            error = "Allowed file types:"
            first = True
            for extension in Gui.ALLOWED_EXTENSIONS:
                if not first:
                    error += ","
                error += " " + extension
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

    def quitApp(self):
        """Quits the application."""

        sys.exit()