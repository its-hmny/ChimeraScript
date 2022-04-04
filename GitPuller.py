"""
TODO: Add script docstring
"""

from datetime import datetime
from os import system
from os.path import abspath, basename, exists, join

from fire import Fire
from requests import get
from rich.console import Console

# Rich console instance for pretty printing on the terminal
console = Console(record=True)


def pull_stars(path: str, clone_new: bool = False) -> None:
    """
    TODO: Add function docstring
    """
    pass


def pull_repo(path: str, clone_new: bool = False, ignore_archived: bool = False) -> None:
    """
    TODO: Add function docstring
    """
    # Extract the absolute path to the folder containing the repos
    folder_abspath = abspath(path)
    # Uses GitHub API to get a list of all my public repositories
    res = get("https://api.github.com/search/repositories?q=user:its-hmny")

    if res.status_code != 200:
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

        # If the repo doesn't already exist and the "clone_new" flag is active then clones the repo from GitHub
        if not exists(join(folder_abspath, name)) and clone_new is True:
            cmd = f"cd {folder_abspath} && git clone {clone_url}"
            if system(cmd) != 0:
                console.print(f"[bold red]Error while cloning {name}[/bold red]")
            else:
                console.print(f"[bold green]{name} cloned successfully[/bold green]")


if __name__ == "__main__":
    try:
        Fire({"repos": pull_repo, "stars": pull_stars})
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
