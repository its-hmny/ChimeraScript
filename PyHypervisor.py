"""
PyHypervisor, created by its-hmny (Enea Guidi) on 18/07/2020
"""

import os, sys, json

# Return the complete string that has to be given to os.system() for a correct execution
def getString(script, interpreter):
    # If the script has execution permission and hashbang as first line
    if oct(os.stat(script).st_mode & 0o700) == oct(0o700) and open(script).readline().find("#!") != -1:
        return str(os.path.join(os.getcwd(), script))
    
    # Else interpolate with the correct interpreter
    elif interpreter != "":
        return "{} {}".format(interpreter, os.path.join(os.getcwd(), script))
    
    else:
        return ""
  

# Get the correct command string and create a child (that will execute it) 
def executeScript(script, interpreter=""):
    formattedStr = getString(script, interpreter)
    pid = os.fork()

    if pid == 0:
        #os.system(formattedStr)
        os._exit(os.EX_OK)
    
    else:
        return pid


def PyHypervisor():
    subprocessPid = []
    
    for string in sys.argv[1:]:
        inputExtension = os.path.splitext(string)[-1]

        if inputExtension == ".py":
            subprocessPid.append(executeScript(string, "python3"))
        
        elif inputExtension == ".sh":
            subprocessPid.append(executeScript(string))

        elif inputExtension == ".json":
            loadCluster(string.json())

    #for pid in subprocessPid:
        #os.waitpid(pid)


PyHypervisor()