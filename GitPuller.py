"""
gitPuller is a script that automates, the action of pulling changes of the projects I'm currently
working on (mine as well as other's) keeping me always up to date with the origin/master. I tried
to make it less verbose as possible but there will be some warnings and/or authentication request,
especially for private repositories. Also it clones all the repositories that currently aren't in
the projectDirectory folder as well as all your starred repositories that aren't already cloned.

Note: that all the repositories are pulled so be aware of the risk (merge conflict and so on...).  

Created by Enea Guidi on 09/03/2020. Please check the README.md for more informations.
"""

import os, requests, platform
from utility import Log

log = Log()
# Platform specific fields
if (platform.system() == "Windows"):
	projectDirectory = "C:/Users/eneag/Desktop/Progetti/"
	starredDirectory = "C:/Users/eneag/Desktop/Public/"
elif (platfom.system() == "Linux"):
    projectDirectory = "/home/its-hmny/Projects/"
    starredDirectory = "/home/its-hmny/Public/"
else: 
    log.error("Unrecognized or unsupported OS")


def existingRepoPuller(path):
    # Lists of all the projects in the given directory
    for project in os.listdir(path):
        try:
            # Changes the current working directory to the project one
            os.chdir(path + project)
            print(os.getcwd())
            # Pulls from origin, less verbosely as possible, returning confirmation
            os.system("git pull")
            log.success("Pulled " + project + " from GitHub")
        
        except NotADirectoryError:
            log.warning(project + " is not a directory, skipped!")



# Given the HTTP response, the item list to scroll and the (eventual) message
def cloneList(response, scroll_list, msg, path):
    if response.status_code != 200:
        raise ConnectionRefusedError
    
    os.chdir(path) # Updates direcotry to current path

    for item in scroll_list:
        if not os.path.isdir(path + item["name"]):
            os.system("git clone " + item["clone_url"])
            log.success(msg + item["name"])


def newRepoCloner():
    # Uses GitHub API to get all my publicly hosted repositories as JSON
    response = requests.get("https://api.github.com/search/repositories?q=user:its-hmny")
    cloneList(response, response.json()["items"], "Cloned your new repo: ", projectDirectory)


def starredRepoCloner():
    # Uses GitHub API to get my starred repos and eventually clone them
    response = requests.get("https://api.github.com/users/its-hmny/starred")
    cloneList(response, response.json()[0:], "Cloned your starred repo: ", starredDirectory)


def gitPuller():
    try:
        # Pulls the change from the existing project directory
        existingRepoPuller(projectDirectory)
        existingRepoPuller(starredDirectory)
        
        # Clones the repo that are not yet present in the folder
        newRepoCloner()
        
        # Clones the starred repo that are not yet present in the folder
        starredRepoCloner()
    
    except FileNotFoundError:
        log.error("Error! The project directory doesn't exist")

    except ConnectionRefusedError:
        log.error("Error with the GitHub's API request")


gitPuller()