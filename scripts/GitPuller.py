"""
ChimeraScript - GitPuller.py

This script allows to keep synchronized personal and starred repositories on GitHub
with the local copies on your machine. The CLI interface presents two subcommand "repos"
and "stars" to interact with both the categories of repositories.

Example:
    To clone and pull all the starred repo, use::
        $ python3 GitPuller.py stars dir_path --clone_new

    To pull all your repositories ignoring the archived ones, use::
        $ python3 GitPuller.py repos dir_path --ignore_archived


Copyright 2022 Enea Guidi (hmny). All rights reserved.
This file are distributed under the General Public License v 3.0.
A copy of abovesaid license can be found in the LICENSE file.
"""

from datetime import datetime
from os import PathLike, system
from os.path import abspath, basename, exists, join

from fire import Fire
from genericpath import isdir
from requests import get
from rich.console import Console

# Rich console instance for pretty printing on the terminal
console = Console(record=True)


def fetch_stars(path: PathLike, clone_new: bool = False) -> None:
    """
    Fetches a list of starred repositories from GitHub API, pulls the already existent repositories
    in the given path and eventually clones the missing ones (if the "clone_new" flag has been set)

    Args:
        path (Pathlike): The path where we want to pull/clone the starred repo
        clone_missing (bool): Optional flag to clone repositories that are not present in "path"

    Raises:
        ConnectionError: Error encountered during GitHub API call
        NotADirectoryError: The given path doesn't point to a directory
    """
    # Extract the absolute path to the folder containing the repos
    folder_abspath = abspath(path)

    # Uses GitHub API to get a list of all my public repositories
    res = get("https://api.github.com/users/its-hmny/starred")

    if not exists(folder_abspath) or not isdir(folder_abspath):
        raise NotADirectoryError(f"{folder_abspath} is not a directory or does not exist")
    elif res.status_code != 200:
        raise ConnectionError(f"Received {res.status_code} from GitHub API")

    for repo in res.json():
        # Destructure the needed properties
        name, clone_url = repo["name"], repo["clone_url"]

        # If the repo already exist in the folder then pulls the latest changes
        if exists(join(folder_abspath, name)):
            cmd = f"cd {join(folder_abspath, name)} && git pull"
            if system(cmd) != 0:
                console.print(f"[bold red]Error while pulling {name}[/bold red]")
            else:
                console.print(f"[bold green]{name} pulled successfully[/bold green]")

        # If it doesn't already exist and the "clone_new" flag is active, clones the repo from GitHub
        if not exists(join(folder_abspath, name)) and clone_new is True:
            cmd = f"cd {folder_abspath} && git clone {clone_url}"
            if system(cmd) != 0:
                console.print(f"[bold red]Error while cloning {name}[/bold red]")
            else:
                console.print(f"[bold green]{name} cloned successfully[/bold green]")


def fetch_repos(path: str, clone_new: bool = False, ignore_archived: bool = False) -> None:
    """
    Fetches a list of starred repositories from GitHub API, pulls the already existent repositories
    in the given path and eventually clones the missing ones (if the "clone_new" flag has been set)

    Args:
        path (Pathlike): The path where we want to pull/clone the starred repo
        clone_missing (bool): Optional flag to clone repositories that are not present in "path"
        ignore_archived (bool): Optional flag to ignore archived repositories

    Raises:
        NotADirectoryError: The given path doesn't point to a directory
        ConnectionError: Error encountered during GitHub API call
    """
    # Extract the absolute path to the folder containing the repos
    folder_abspath = abspath(path)
    # Uses GitHub API to get a list of all my public repositories
    res = get("https://api.github.com/search/repositories?q=user:its-hmny")

    if not exists(folder_abspath) or not isdir(folder_abspath):
        raise NotADirectoryError(f"{folder_abspath} is not a directory or does not exist")
    elif res.status_code != 200:
        raise ConnectionError(f"Received {res.status_code} from GitHub API")

    for repo in res.json().get("items", []):
        # Destructure the needed properties
        name, clone_url, is_archived = repo["name"], repo["clone_url"], repo["archived"]

        # Skips the archived repositories if the user said so
        if ignore_archived and is_archived:
            continue

        # If the repo already exist in the folder then pulls the latest changes
        if exists(join(folder_abspath, name)):
            cmd = f"cd {join(folder_abspath, name)} && git pull"
            if system(cmd) != 0:
                console.print(f"[bold red]Error while pulling {name}[/bold red]")
            else:
                console.print(f"[bold green]{name} pulled successfully[/bold green]")

        # If it doesn't already exist and the "clone_new" flag is active, clones the repo from GitHub
        if not exists(join(folder_abspath, name)) and clone_new is True:
            cmd = f"cd {folder_abspath} && git clone {clone_url}"
            if system(cmd) != 0:
                console.print(f"[bold red]Error while cloning {name}[/bold red]")
            else:
                console.print(f"[bold green]{name} cloned successfully[/bold green]")


if __name__ == "__main__":
    try:
        Fire({"repos": fetch_repos, "stars": fetch_stars})
    except KeyboardInterrupt:
        console.print("[yellow]Interrupt received, closing now...[/yellow]")
    except Exception:
        console.print("[red]An unexpected error occurred[/red]")
        console.print_exception()
    finally:
        script_name = basename(__file__)
        current_date = datetime.now().strftime('%d-%m-%Y %H:%M')
        console.save_html(f"logs/{script_name} {current_date}.html", clear=False)
        console.save_text(f"logs/{script_name} {current_date}.log", clear=False)
