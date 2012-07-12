LogFixer
========

LogFixer is a simple Python script that corrects up to 4 BEAST output files with missing states.

Configuring LogFixer
To use LogFixer simply open Log_Fixer.py with a text editor and paste in the paths to BEAST output files.
If you don't have gmrf or rates files don't worry - just leave '' where it says gmrffile and ratesfile.
There's nothing special about which files go where (except for log and trees files), because 
all non-trees files are parsed the same way.

If you have more than 4 BEAST output files it's possible to modify the script to add those too.

Running LogFixer
To run LogFixer type 'python Log_Fixer.py' in command-line once you are in the directory where Log_Fixer.py is located.

The way it works
Log_Fixer loads in the states of BEAST output files whose paths are given, finds the states shared by all of 
them and prints renumbered states that are shared between all output files into new files (in the same directory) 
which have the creative extension .txtcorrected.txt

