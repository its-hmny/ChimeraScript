"""
ChimeraScript - DriveDiffMerger.py

TODO : Add script documentation
TODO : Add script documentation
TODO : Add script documentation

TODO: Add script usage template
! Example:
!     To save the output audio streams in a file, use::
!         $ python3 DocReader.py export mock.pdf
! 
!     To play the audio as well with vlc , use::
!         $ python3 DocReader.py stream mock.pdf player=vlc


Copyright 2022 Enea Guidi (hmny). All rights reserved.
This file are distributed under the General Public License v 3.0.
A copy of abovesaid license can be found in the LICENSE file.
"""
from datetime import datetime
from os import PathLike, mkdir
from os.path import abspath, basename, exists, getmtime, join

from fire import Fire
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive, GoogleDriveFile
from rich.console import Console

# TODO Comment
ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
# Rich console instance for pretty printing on the terminal
console = Console(record=True)
# Starts a local webserver that handles OAuth authentication.
# Injects the auth payload and obtains a proxy to Drive access.
gdrive = GoogleDrive(GoogleAuth().LocalWebserverAuth())


def gd_listdir(gd_dir: GoogleDriveFile) -> list[GoogleDriveFile]:
    """TODO: Add pydoc annotations"""
    query = {"q": f"'{gd_dir['id']}' in parents and trashed=false"}
    return gdrive.ListFile(query).GetList()


def gd_getmtime(entry: GoogleDriveFile) -> int:
    """TODO: Add pydoc annotations"""
    return datetime.strptime(entry["modifiedDate"], ISO_FORMAT).timestamp()


def gd_download(entry: GoogleDriveFile, dest: PathLike) -> None:
    """TODO: Add pydoc annotations"""


def gd_upload(entry: PathLike, dest: GoogleDriveFile) -> None:
    """TODO: Add pydoc annotations"""


def pull_recursively(local: PathLike, remote: GoogleDriveFile) -> None:
    """TODO: Add pydoc annotations"""
    for r_entry in gd_listdir(remote):
        # Based on the remote entry extracts the expected local one
        l_entry = abspath(join(local, remote["title"]))

        # If the local one doesn't exist, we pull from Google Drive
        if not exists(l_entry) or getmtime(l_entry) > gd_getmtime(r_entry):
            return gd_download(r_entry, l_entry)


def main(local_root: PathLike) -> None:
    """TODO: Add pydoc annotations"""
    for remote_folder in gd_listdir(gdrive.CreateFile({"id": "root"})):
        # From the root path creates the expected local counterpart
        local_folder = abspath(join(local_root, remote_folder["title"]))
        # Creates the local folder if it doesn't exist
        mkdir(local_folder) if not exists(local_folder) else None
        # ! Debug only, will be removed later
        console.print(f"Pulling Drive folder {remote_folder['title']} in  {local_folder}")
        # Synchronizes both from remote to local and viceversa at the same time
        pull_recursively(local_folder, remote_folder)


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
