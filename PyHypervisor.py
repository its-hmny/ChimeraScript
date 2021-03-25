"""
PyHypervisor: a script to rule them all. It takes a list of script both from a JSON file or
from the argv vector (more on that later) and executes them concurrently and indipently from
thing such as interpreter (shell, python3, etc) and permission. It will detect automatically
if shebang and permission are correct and eventually will try to execute manually.

Note: due to its concurrent nature is higly advised to not use with any scrpt that requires
to get line from stdin as parameters, moreover at the moement it doesn't support arguments passing
so all your script should have a default option in order to work properly.

Example:
    "python3 PyHypervisor.py -l Update.sh EmptyDirRemover.py"
        -> Will execute automatically both Updae.sh and EmptyDirRemover.py
     "python3 PyHypervisor.py -j ExampleConfig.json"
        -> Will execute concurrently all the ScriptList array in the JSON file (duplicate name will execute more times)
     "python3 PyHypervisor.py -j ExampleConfig.json Cleaning"
        -> Will execute the ScriptList array in the object with GroupName "Cleaning"

Created by Enea Guidi on 18/07/2020. Please check the README.md for more informations.
"""

import os
import sys
import json
import platform
from threading import Thread
from chimera_utils import Log

log = Log()
task_pool = []

usageInfo = """
Usage: python3 PyHypervisor.py [option] [input] [JSON_subclass]
Option: -l to execute script from argv[], -j to execute script grouped in a JSON file
Input: the list of script to execute (-l) or the JSON file (-j)
Only for JSON file you can name groups each with their own scripts
and select only one of them to be executed, else every group will be executed
            """


# Return the complete string that has to be given to os.system() for a
# correct execution
def getExecutableString(script, interpreter):
    script_mode = oct(os.stat(script).st_mode & 0o700)
    script_has_hashbang = open(script).readline().find("#!") != -1
    # If the script has execution permission and hashbang as first line
    if script_mode == oct(0o700) and script_has_hashbang:
        return str(os.path.join(os.getcwd(), script))
    # Else interpolate with the correct interpreter
    else:
        return (f"{interpreter} {os.path.join(os.getcwd(), script)}")


# Receives as input an array of string (that shoul be script path) and
# trie to execute them
def loadScriptFromArray(array):
    for string in array:
        f_name, extension = os.path.splitext(string)

        if extension == ".py":
            python_name = 'python' if platform.system() == "Windows" else 'python3'
            toExecute = getExecutableString(string, python_name)
        elif extension == ".sh" and platform.system() != "Windows":
            toExecute = getExecutableString(string, "sh")

        new_task = Thread(target=os.system, args=(toExecute, ), name=f_name)
        task_pool.append(new_task)
        new_task.start()


# Load the script list from JSON with the possiility select one specific
# group or all of them
def loadScriptFromJSON():
    if len(sys.argv) >= 3 and os.path.splitext(sys.argv[2])[-1] == ".json":
        parsedInput = json.loads(open(sys.argv[2]).read())
        groupsVector = parsedInput["ScriptGroups"]

        if len(sys.argv) >= 4:
            for group in groupsVector:
                if group["GroupName"] == sys.argv[3]:
                    loadScriptFromArray(group["ScriptList"])
        else:
            completeList = []
            for group in groupsVector:
                completeList += group["ScriptList"]
            loadScriptFromArray(completeList)


def PyHypervisor():
    # Execution option checking
    if len(sys.argv) > 2 and sys.argv[1] == "-l":
        loadScriptFromArray(sys.argv[2:])
    elif len(sys.argv) > 2 and sys.argv[1] == "-j":
        loadScriptFromJSON()
    else:
        log.warning(usageInfo)
        return -1

    # Wait for all the task to complete
    for task in task_pool:
        log.success(f"Task '{task.name}' completed")
        task.join()

    len(task_pool) and log.success("---> All task completed")


PyHypervisor()
