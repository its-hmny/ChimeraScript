# Default module exports
from .log import Log
from .compressor import Compressor
from .drive_fs import GDriveFileSystem as Drive_fs


from rich.console import Console

def exception_handler(function):
    console = Console()
    
    def wrapper() -> None:
        try:
            function()
        except KeyboardInterrupt:
            console.print("[yellow]Interrupt received, closing now...[/yellow]")
        except Exception:
            console.print("[red]An unexpected error occured[/red]")
            console.print_exception()
    
    return wrapper
