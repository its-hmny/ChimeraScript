"""
ChimeraScript - BackUpLoader.py

This script allows automation of the backup process by copying sensitive folder and files
to a remote server. The CLI presents two subcommand "raw" and "compress" to upload the folder/files
as they are or to compress them in a .tar.gz archive before uploading it to the server.
Both method allow the user to specificy username and hostname from the CLI and avoid manual
insertion, either way the password (and the eventually missing data) will be requested via prompt.

Example:
    To upload the current folder without compression use::
        $ python3 BackUpLoader.py raw .

    To upload your home directory with compression use::
        $ python3 BackUpLoader.py compress ~ --username=enea.guidi --host=pinkerton.cs.unibo.it


Copyright 2022 Enea Guidi (hmny). All rights reserved.
This file are distributed under the General Public License v 3.0.
A copy of abovesaid license can be found in the LICENSE file.
"""
from asyncio import gather, run
from datetime import datetime
from os import PathLike
from os.path import abspath, basename
from typing import List
from tarfile import open as open_tar

from asyncssh import connect, scp
from fire import Fire
from rich.console import Console

# Rich console instance for pretty printing on the terminal
console = Console(record=True)


async def scp_path(path: PathLike, host: str, user: str, psw: str):
    """
    Uploads the given local (absolute) path to the remote location/server (the host).
    Handles connection establishment and authentication with the host via username and password.

    Args:
        path (Pathlike): The local path (file or folder) to be uploaded
        host (str): The hostname or IP address of the remote server
        user (str): The username to be used for authentication
        psw (str): The password for the abovesaid user

    Raises:
        SFTPFailure: Error encountered during upload
    """
    console.print(f"[bold yellow]Uploading {path}...[/bold yellow]")

    async with connect(host, username=user, password=psw) as conn:
        await scp(path, (conn, f"/public/hmny/{basename(path)}"), preserve=True, recurse=True)

    console.print(f"[bold green]Completed upload of {path}[/bold green]")


def compress_paths(*args: List[PathLike], host: str = None, username: str = None):
    """
    Handles the compression of the given paths to in a .tar.zg archive and the upload of the
    latter to a remote server

    Args:
        args (List[Pathlike]): List of relative/absolute paths to be compressed
        host (Optional[str]): The hostname or IP address of the remote server
        user (Optional[str]): The username to be used for authentication
    """
    # If not provided asks the user to fill in username and destination host (IP or domain name)
    if host is None:
        host = console.input(prompt="[bold yellow]Insert host name or IP: [/bold yellow]")
    if username is None:
        username = console.input(prompt="[bold yellow]Insert your username: [/bold yellow]")

    # Asks the user ot insert the access password
    password = console.input(prompt="[bold red]Insert your password: [/bold red]", password=True)

    # Compress the uploads path into a .tar.gz archive
    with open_tar("/tmp/archive.tar.gz", "w:gz") as archive:
        for path in args:
            archive.add(abspath(path))

    async def wrapper():  # Uploads the archive to the remote location
        await gather(scp_path("/tmp/archive.tar.gz", host, username, password))

    run(wrapper())  # Waits for all coroutines to complete


def upload_paths(*args: List[PathLike], host: str = None, username: str = None):
    """
    Handles the "concurrent" upload of the given paths to the remote server without compression

    Args:
        args (List[Pathlike]): List of relative/absolute paths to be uploaded
        host (Optional[str]): The hostname or IP address of the remote server
        user (Optional[str]): The username to be used for authentication
    """
    # If not provided asks the user to fill in username and destination host (IP or domain name)
    if host is None:
        host = console.input(prompt="[bold yellow]Insert host name or IP: [/bold yellow]")
    if username is None:
        username = console.input(prompt="[bold yellow]Insert your username: [/bold yellow]")

    # Asks the user ot insert the access password
    password = console.input(prompt="[bold red]Insert your password: [/bold red]", password=True)

    async def wrapper():  # Uploads each path on its coroutine and with its own connection
        await gather(*[scp_path(abspath(path), host, username, password) for path in args])

    run(wrapper())  # Waits for all coroutines to complete


if __name__ == "__main__":
    try:
        Fire({"raw": upload_paths, "compress": compress_paths})
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
