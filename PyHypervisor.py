"""
PyHypervisor: a script to rule them all. It takes a list of script both from a JSON file or
from the argv vector (more on that later) and executes them concurrently and indipently from
thing such as interpreter (shell, python3, etc) and permission. It will detect automatically
if shebang and permission are correct and eventually will try to execute manually.

Note: due to its concurrent nature is higly advised to not use with any scrpt that requires
to get line from stdin as parameters, moreover at the moement it doesn't support arguments passing
so all your script should have a default option in order to work properly.

Example: "python3 PyHypervisor.py -l Update.sh EmptyDirRemover.py"
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
from chimera_utils import Log, TaskPool

log = Log()
jobsPool = TaskPool()
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
    # If the script has execution permission and hashbang as first line
    if oct(os.stat(script).st_mode & 0o700) == oct(
            0o700) and open(script).readline().find("#!") != -1:
        return str(os.path.join(os.getcwd(), script))

    # Else interpolate with the correct interpreter
    elif interpreter != "":
        return "{} {}".format(interpreter, os.path.join(os.getcwd(), script))

    else:
        return ""


# Receives as input an array of string (that shoul be script path) and
# trie to execute them
def loadScriptFromArray(array):
    for string in array:
        inputExtension = os.path.splitext(string)[-1]

        if inputExtension == ".py":
            formattedStr = getExecutableString(string, 'python3')
        elif inputExtension == ".sh":
            formattedStr = getExecutableString(string, "sh")

        def execFunction(command): return __import__("os").system(command)
        jobsPool.submit(execFunction, command=formattedStr)


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
    try:
        if sys.argv[1] == "-l":
            loadScriptFromArray(sys.argv[2:])
        elif sys.argv[1] == "-j":
            loadScriptFromJSON()
    except IndexError:
        log.warning(usageInfo)
        os._exit(os.EX_OK)

    jobsPool.waitAll()

    log.error("No script scheduled for execution") if len(
        sys.argv) == 1 else log.success("---> All task completed")


PyHypervisor()
