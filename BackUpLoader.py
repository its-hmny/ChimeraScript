"""
TODO Add docstring
"""
from asyncio import gather, run
from datetime import datetime
from distutils.command.upload import upload
from os import PathLike
from os.path import abspath, basename
from typing import List
from tarfile import open as open_tar

from asyncssh import connect, scp
from fire import Fire
from rich.console import Console

# Rich console instance for pretty printing on the terminal
console = Console(record=True)


async def scp_path(path: PathLike, host: str = "localhost", user: str = "root", psw: str = ""):
    """
    TODO add docstrig
    """
    console.print(f"[bold yellow]Uploading {path}...[/bold yellow]")

    async with connect(host, username=user, password=psw) as conn:
        await scp(path, (conn, f"/public/hmny/{basename(path)}"), preserve=True, recurse=True)

    console.print(f"[bold green]Completed upload of {path}[/bold green]")


def upload_backup(*args: List[PathLike], compress: bool = False):
    """
    TODO add docstrig
    """
    upload_paths = [abspath(path) for path in args]

    # Compress the uploads path into a .tar.gz archive
    if compress is True:
        with open_tar("/tmp/dump.tar.gz", "w:gz") as archive:
            _ = [archive.add(path) for path in upload_paths]
            # Overwrites the upload_paths so that only the archive is uploaded
            upload_paths = ["/tmp/dump.tar.gz"]

    host = console.input(prompt="[bold yellow]Insert host name or IP: [/bold yellow]")
    username = console.input(prompt="[bold yellow]Insert your username: [/bold yellow]")
    password = console.input(prompt="[bold red]Insert your password: [/bold red]", password=True)

    async def wrapper():
        upload_tasks = [scp_path(path, host, username, password) for path in upload_paths]
        await gather(*upload_tasks)

    run(wrapper())


if __name__ == "__main__":
    try:
        Fire(upload_backup)
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
