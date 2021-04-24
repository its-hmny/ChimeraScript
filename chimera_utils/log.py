"""
This utility module containes a basics class that are used all over this project.
The Log class is a basic wrapper to print function, it has also the option to set personal codes.
"""

from rich import inspect
from rich.console import Console
from rich.markdown import Markdown


class Log():
    def __init__(self):
        self.__console = Console()

    def success(self, msg: str, **kwargs):
        self.__console.print(f"[green]{msg}[/green]", **kwargs)

    def error(self, msg: str, **kwargs):
        self.__console.print(f"[red]{msg}[/red]", **kwargs)

    def warning(self, msg: str, **kwargs):
        self.__console.print(f"[yellow]{msg}[/yellow]", **kwargs)

    # Get all the details avaiable about one or more object passed to it
    def details(self, *args):
        for arg in args:
            inspect(arg, methods=True)

    # This a simple and quick variadic print with option for some styling as
    # well
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
