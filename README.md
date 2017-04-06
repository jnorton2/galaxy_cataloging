# check-spectra

Skidmore Astro, check-spectra python translation from IDL. 
A basic GUI program written in python that processes json galaxy source files.

*	Input source files should be places in the folder titled 'srcfies_json' and their titles should follow the format'AGC####.json'

*	After creating a plot for a src file, it gets saved into 'out/plots/AGC#####.html'

*	out/checkspectra.log - log file 

*	checkspectra.py - python module which contains the logic

*	main.py - GUI

*	config.py - Strings and configs

*	agclist.txt - a text file containing neighboring galaxy information

*	srcLayout.json - src file layout

*	outputs accepted data and rejected data to out/reject.csv and out/accept.csv


Instructions for setup:

1) Make sure python is installed
	Run ```python -V``` and make sure it is python 2 (this code will not work in python 3)

2) Run ```pip -V``` to make sure pip is installed. If it is, you will get back a message
	like this ```pip 9.0.1 from <some_folder>```
	If you have pip, make sure to update - ```pip install --upgrade pip```
	If you dont have pip installed at all: follow the guide below to install it
	https://packaging.python.org/installing/

4) Install the dependencies using pip:
	```pip install -r requirements.txt```

5) Load the srcfiles_json directory with source files.

6) Run the program with ```python main.py```


This program is in beta. If you find bugs, have comments or questions, hate the program, love the program, or just want to talk, send me an email at jnorton2@skidmore.edu. Feedback makes software better :)