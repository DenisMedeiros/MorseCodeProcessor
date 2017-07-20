# MorseCodeProcessor
This project is a application of Digital Signal Processing with Morse Code. It has two modules: a generator and a receiver.
The purpose of the generator is to make a audio file containing some text encoded in morse code. The user can add additive white gaussian noise to the audio. Also, each symbol (dit or dah) has a random and different frequency, that is, it can be represented by different musical tones.
The receiver, on the other hand, reads a audio file containing a Morse Code message, applies some filtering and try to recover the original text encoded.

It was developed completely in Python, using the libraries Numpy, SciPy, Matplotlib and soundfile. All dependencies can be found in the file 'requirements.txt'.







