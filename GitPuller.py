"""
    TODO: Add script docstring
"""

from datetime import datetime

from fire import Fire
from rich.console import Console

# Rich console instance for pretty printing on the terminal
console = Console(record=True)


def pull_repo(clone_new: bool = False) -> None:
    """
        TODO: Add function docstring
    """
    console.log("Hello world, im pulling repos")


def pull_stars(clone_new: bool = False) -> None:
    """
        TODO: Add function docstring
    """
    console.log("Hello world, im pulling starred repos")


if __name__ == "__main__":
    try:
        Fire({"repo": pull_repo, "star": pull_stars})
    except KeyboardInterrupt:
        console.print("[yellow]Interrupt received, closing now...[/yellow]")
    except Exception:
        console.print("[red]An unexpected error occurred[/red]")
        console.print_exception()
    finally:
        current_date = datetime.now().strftime('%d-%m-%Y %H:%M')
        console.save_html(f"logs/{current_date}.html", clear=False)
        console.save_text(f"logs/{current_date}.log", clear=False)
