# ChimeraScript
A suit of Python scripts to automate my everyday task, all written by me.
See below or in the source files for requirements, infos or implementation of each script.

## How-To
In order to execute this script you'll need to have previously installed Python 3, you could do so on linux with the command:
``` console
usr@computer:~/ChimeraScript$ sudo apt update
usr@computer:~/ChimeraScript$ sudo apt install python3
```
then you can execute each script with the command:
``` console
usr@computer:~/ChimeraScript$ python3 <script_name.py>
```

## Back_up_Loader
Back_up_Loader is a simple Python scipt used to automate my regular backup upload to the university sftp server, this script 
works recursively so (as the example show) ypu only need to put the directory you want to upload and it will automate the 
process for you. PLEASE NOTE THAT THIS WON'T WORK ON WINDOWS (due to the use of \ instead of / in Windows terminal).
Please also note that in order to function the server must be in your known host list else the script will raise an exception

### *Requirements
The only dependencies is pysftp, you can install with pip (Python Package Manager) with the command:
``` console
usr@computer:~/ChimeraScript$ pip install pysftp
```

## EmptyDirRemover
EmptyDirRemover is a simple Python script used for deleting my old/empty folder. The script works recursivly from the input
directory to all the subdirectories and so on, for this reason use it only in directories where you're sure to not delete nothing important.
The script has no package dependencies and relies only on standard python library.

## GIF_Converter
GIF_Converter is a simple script to convert a .mp4 file to a .gif file.
At the moment only mp4 and mkv filetype are tested, more filetype will eventually be added in future (Feel free to contribute)

### *Requirements
The only dependencies is imageio, you can install it with pip with the command:
``` console
usr@computer:~/ChimeraScript$ pip install imageio
```
## garbageCleaner
garbageCleaner is a simple script that I use to clean the location in which I usually save my temporary and/or garbage file,
wipeDir() works recursively so everything inside that dir will be deleted (I warned you).
The script has no package dependeces.

## gitPuller
gitPuller is a simple script that I use to keep up to date all my public/private/cloned/etc GitHub repos. It simply iterates
within my projects folder and executes "git pull" in each of them. Also it clones all your starred and new repos...
The script has no package dependencies.