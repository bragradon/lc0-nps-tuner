# lc0-nps-tuner
A parameter CLOP runner for the LeelaZero chess engine

## Story behind this program
My father has always been an avid computer chess fan. 
As a hobby, he runs his own round-robin tournaments and spectates the results
between the various chess engines. For his 60th birthday, my brother and I
build a new computer for him to run his chess tournaments with hardware specs 
similar to the TCEC system (at the time). A few months later, the LeelaZero
chess engine was released and he became enamoured with it and wanted to help
the project. As he could dedicate time and resource to run games, rather than
help with finding neural net parameters, he opted to do hyper-parameter tuning tests.

As this is quite time consuming, He asked me to create a tuning program which
can take a number of commandline parameters and search for a combination which results
in a maximum NPS (for a given time limit).

The program is a written in Python 3.7 since this was meant to be a quick "gift"
to help him. It is designed to be packaged with Pyinstaller, since
it is easier to give my father an executable than explain how to install python 🤷‍

## How to run
This program requires Python 3.7 or above
It uses the [Poetry](https://poetry.eustace.io) packaging tool to manage dependencies.
It is recommened to install Poetry as per its documentation and then from the root folder
of this project run `poetry install`

This should install all the dependencies within a virtual environment.
If you copy a LeelaZero executable, a weights file and create an options.json file in the tuner folder, you can then run: `python -m tuner`

However, for ease of distribution this can be packaged into a single executable via: `pyinstaller --onefile tuner.spec`
