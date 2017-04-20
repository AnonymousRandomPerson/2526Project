# Instrument Changer
## Requirements
Python 3 is required to run the application.

### 3rd-party libraries
* Matplotlib
* NumPy
* PyAudio
* PySoundFile
* SciPy
* Tkinter

### Use
1. Run the application using main.py (e.g., "python3 main.py").
2. Select "Load audio file" and find an audio file on your system. The application accepts most major audio formats like .wav, .aiff, and .ogg. However, there are some formats that it cannot accept, including .mp3 and .mp4. It will also not take MIDI files directly.
3. Select an instrument using the drop-down menu.
4. There are two sets of enabled buttons and volume sliders. The top set controls the original audio file, while the bottom controls the new, synthesized sound. The sounds can be played together or separately and at different volumes.
5. Playback can be controlled with the "Play", "Pause", and "Stop" buttons.
6. Whenever a new audio file is loaded, the detected note data will be written to "output.mid". Whenever a new instrument is selected, the audio sample data will be written  to "output.wav".
