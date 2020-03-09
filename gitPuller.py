"""
gitPuller is a script that automates, the action of pulling changes of the projects I'm currently
working on (mine as well as other's) keeping me always up to date with the origin/master. I tried
to make it less verbose as possible but there will be some warnings and/or authentication request,
especially for private repositories.
Created by Enea Guidi on 09/03/2020. Please check the README.md for more informations.
"""

import os

projectDirectory = "/home/hmny/Templates/"

def gitPuller():
    try:
        #Lists of all the projects in the given directory
        for project in os.listdir(projectDirectory):
            #Changes the current working directory to the project one
            os.chdir(projectDirectory + project)
            #And pulls from origin, less verbosely as possible, returning confirmation
            os.system("git pull > /dev/null")
            print("Pulled " + project + "from GitHub \n")
    
    except FileNotFoundError:
        print("Error project directory doesn't exist")

gitPuller()