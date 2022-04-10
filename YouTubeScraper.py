"""
TODO Add pydoc annotation

https://towardsdatascience.com/the-easiest-way-to-download-youtube-videos-using-python-2640958318ab
https://www.the-analytics.club/download-youtube-videos-in-python/
https://typer.tiangolo.com/
"""
from datetime import datetime
from os.path import basename

from fire import Fire
from pytube import YouTube
from rich.console import Console

# Rich console instance for pretty printing on the terminal
console = Console(record=True)


def main():
    """
    TODO Add pydoc annotation
    """
    console.print("[green]Hello world[/green]")
    YouTube('https://www.youtube.com/watch?v=tt2k8PGm-TI'
           ).streams.get_highest_resolution().download()


if __name__ == "__main__":
    try:
        Fire(main)
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
