"""
GitPuller is a script that automates, the action of pulling changes of the projects I'm
currently working on (mine as well as other's) keeping me always up to date with the origin/master.
I tried to make it less verbose as possible but there will be some warnings and/or
authentication request, especially for private repositories. Also it clones all the
repositories that currently aren't in the projectDirectory folder as well as all your
starred repositories that aren't already cloned.

Note: that all the repositories are pulled so be aware of the risk (merge conflict and so on...).

Created by Enea Guidi on 09/03/2020. Please check the README.md for more informations.
"""

import os
import sys
import platform
from typing import List
from chimera_utils import Log
from requests import get, Response

log = Log()

# Platform specific fields
if (platform.system() == "Windows"):
    projectDirectory = "C:/Users/eneag/Desktop/Progetti"
    starredDirectory = "C:/Users/eneag/Desktop/Public"
elif (platform.system() == "Linux"):
    projectDirectory = "/home/hmny/Projects"
    starredDirectory = "/home/hmny/Public"
else:
    log.error("Unrecognized or unsupported OS")
    sys.exit(-1)


def existingRepoPuller(path: str) -> None:
    # Lists of all the projects in the given directory
    for project in os.listdir(path):
        current_path = os.path.join(path, project)
        if not os.path.isdir(current_path):
            log.warning(f"{project} is not a directory, skipped!")
            continue

        exit_code = os.system(f"cd {current_path} && git pull")

        if exit_code == 0:
            log.success(f"Pulled {project} from GitHub")
        else:
            log.error(f"Errors occured pulling {project} from GitHub")


# Given the HTTP response, the item list to scroll and the (eventual) message
def cloneList(
        response: Response,
        repos_list: List[str],
        msg: str,
        path: str) -> None:
    if response.status_code != 200:
        raise ConnectionRefusedError

    for repo in repos_list:
        repo_name, repo_url = repo["name"], repo["clone_url"]
        current_path = os.path.join(path, repo_name)
        if not os.path.isdir(current_path):
            os.system(f"git clone {repo_url}")
            log.success(f"{msg} {repo_name}")


def newRepoCloner() -> None:
    # Uses GitHub API to get all my publicly hosted repositories as JSON
    res = get("https://api.github.com/search/repositories?q=user:its-hmny")
    publicRepos = res.json()["items"]
    cloneList(res, publicRepos, "Cloned your new repo:", projectDirectory)


def starredRepoCloner() -> None:
    # Uses GitHub API to get my starred repos and eventually clone them
    res = get("https://api.github.com/users/its-hmny/starred")
    starredRepos = res.json()
    cloneList(res, starredRepos, "Cloned your starred repo:", starredDirectory)


def GitPuller() -> None:
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
        sys.exit(-1)
    except ConnectionRefusedError:
        log.error("Error with the GitHub's API request")
        sys.exit(-1)


if __name__ == "__main__":
    GitPuller()
