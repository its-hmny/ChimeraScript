"""
gitPuller is a script that automates, the action of pulling changes of the projects I'm currently
working on (mine as well as other's) keeping me always up to date with the origin/master. I tried
to make it less verbose as possible but there will be some warnings and/or authentication request,
especially for private repositories. Also it clones all the repositories that currently aren't in
the projectDirectory folder as well as all your starred repositories that aren't already cloned.
Note that all the repositories are pulled so be aware of the risk (merge conflict and so on...).  
Created by Enea Guidi on 09/03/2020. Please check the README.md for more informations.
"""

import os, requests

projectDirectory = "/home/hmny/Templates/"


def existingRepoPuller():
    # Lists of all the projects in the given directory
    for project in os.listdir(projectDirectory):
        # Changes the current working directory to the project one
        os.chdir(projectDirectory + project)
        # Pulls from origin, less verbosely as possible, returning confirmation
        os.system("git pull > /dev/null")
        print("Pulled " + project + "from GitHub \n")

def newRepoCloner():
    # Use GitHub API to get all my publicly hosted repositories as JSON
    response = requests.get("https://api.github.com/search/repositories?q=user:its-hmny")
    fullRepoList = response.json()
    
    if response.status_code != 200:
        raise ConnectionRefusedError

    for repo in fullRepoList["items"]:
        # If the current repo isn't in the directory, clone it
        if not os.path.isdir(projectDirectory + repo["name"]):
            os.system("git clone " + repo["clone_url"])
            print("Cloned your new repo: " + repo["name"])

def starredRepoCloner():
    # Uses GitHub API to get my starred repos and eventually clone them
    response = requests.get("https://api.github.com/users/its-hmny/starred")
    starsList = response.json()
    
    if response.status_code != 200:
        raise ConnectionRefusedError

    for starredRepo in starsList[0:]:
        # If the current repo isn't in the project directory then clone it
        if not os.path.isdir(projectDirectory + starredRepo["name"]):
            os.system("git clone " + starredRepo["clone_url"])
            print("Cloned your starred repo: " + repo["name"])


def gitPuller():
    try:
        # Pulls the change from the existing project directory
        existingRepoPuller()
        
        # CSets back the current working directory to the project root directory
        os.chdir(projectDirectory)
        
        # Clones the repo that are not yet present in the folder
        newRepoCloner()
        
        # Clones the starred repo that are not yet present in the folder
        starredRepoCloner()
    
    except FileNotFoundError:
        print("Error project directory doesn't exist")

    except ConnectionRefusedError:
        print("Error with the GitHub's API request")


gitPuller()