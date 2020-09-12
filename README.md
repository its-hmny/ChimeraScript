# ChimeraScript
A suit of Python scripts to automate my everyday task, all written by me.

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
In each script file there the third party requirements for each script (if needed) as well as some example and the explanation of how the script 
work and what task will automate.

## Requirements
The script are meant to work for Python 3.0 and later version, they are untested on other version, so you must necessarily
use python3 as interpreter.

The vast majority of the given script will work as is, but some of them relies on third party library, you can install this
dependencies through pip with the command:
``` console
usr@computer:~/ChimeraScript$ pip3 install -r requirements.txt
```