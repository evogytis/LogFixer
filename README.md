LogFixer
========

LogFixer is a simple Python script that corrects BEAST output files with missing or incomplete states.

Running LogFixer
To run LogFixer type 'python Log_Fixer.py' in command-line once you are in the directory where Log_Fixer.py is located.
If everything goes according to plan, a dialog should pop up asking to first select a tree file
(you can press cancel if you only want to deal with log files) and then any other BEAST output files you wish to be checked
for consistency. The dialog will keep popping up after each file selected until all files have been selected, at
which point press cancel to proceed.

The way it works
Log_Fixer loads in the states of selected BEAST output files, finds the states shared by all of 
them but also checks whether log files have the same number of reported parameters (i.e. whether each state is complete) 
and prints renumbered states that are shared (and complete) between all output files into new files (in the same directory) 
which have the creative extension .fixed.txt

