"""
This utility module containes a basics class that are used all over this project.
The Log class is a basic wrapper to print function, it has also the option to set personal codes.
"""

from rich import inspect
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress
from rich.progress import (
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
    SpinnerColumn
)

class Log():
    def __init__(self):
        self.__progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description} {task.fields[current]}"), 
            "•", BarColumn(), "•",
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=Console(),
            transient=True, expand=True
        )
        self.__console = self.__progress.console

    def success(self, msg: str, **kwargs):
        self.__console.print(f"[bold green]{msg}[/bold green]", **kwargs)

    def error(self, msg: str, **kwargs):
        self.__console.print(f"[bold red]{msg}[/bold red]", **kwargs)

    def warning(self, msg: str, **kwargs):
        self.__console.print(f"[bold yellow]{msg}[/bold yellow]", **kwargs)

    # Get all the details avaiable about one or more object passed to it
    def details(self, *args):
        for arg in args:
            inspect(arg, methods=True)

    # This a simple and quick variadic print with option for some styling
    def debug(self, *args, **kwargs):
        for arg in args:
            self.__console.print(arg, **kwargs)

    # Print documentation both in a single string or markdown format
    def documentation(self, title: str, doc: str, markdown: bool = False):
        self.__console.rule(f"[bold yellow]{title}", align="center")
        if markdown:
            md = Markdown(doc)
            self.__console.print(md, justify="center")
        else:
            self.__console.print(f"[bold yellow]{doc}", justify="left")

    # Construct and return a tuple with ...
    def progress_bar_builder(self, label: str, total: int, current: str=""):
        task_id = self.__progress.add_task(label, total, current=current)

        def update_task(increment: int, current: str):
            self.__progress.update(task_id, current=current, advance=increment)
        
        return (self.__progress, update_task)



if __name__ == "__main__":
    log = Log()
    progress_bar, update_bar = log.progress_bar_builder("Test", 100, "xxx")
    with progress_bar as progress:
        for i in range(10):
            update_bar(0.5, "yy")
            log.success("DONE")
