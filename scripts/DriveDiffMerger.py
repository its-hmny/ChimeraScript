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
from os import PathLike, listdir, makedirs, mkdir, utime
from os.path import abspath, basename, exists, getmtime, isdir, isfile, join

from fire import Fire
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive, GoogleDriveFile
from rich.console import Console

# datetime.strptime format for ISO strings
ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
# Mimetype assigned to Google Drive folders
GD_FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'
# Mimetype assigned to Google Drive links/shortcuts
GD_LINK_MIMETYPE = 'application/vnd.google-apps.shortcut'
GD_GAPPS_MIMETYPE = [
    "application/vnd.google-apps.document",
    "application/vnd.google-apps.sheet",
    "application/vnd.google-apps.slide",
]

# Rich console instance for pretty printing on the terminal
console = Console(record=True)
# Starts a local webserver that handles OAuth authentication.
# Injects the auth payload and obtains a proxy to Drive access.
gdrive = GoogleDrive(GoogleAuth())


def gd_isdir(entry: GoogleDriveFile) -> bool:
    """Determines if the 'entry' argument is a Google Drive directory/folder"""
    return entry["mimeType"] == GD_FOLDER_MIMETYPE


def gd_islink(entry: GoogleDriveFile) -> bool:
    """Determines if the 'entry' argument is a Google Drive link/shortcut"""
    return entry["mimeType"] == GD_LINK_MIMETYPE


def gd_isfile(entry: GoogleDriveFile) -> bool:
    """Determines if the 'entry' argument is a downloadable file (not a Goggle Apps one)"""
    is_document = not gd_islink(entry) and not gd_isdir(entry)
    # Google Apps (Docs, Sheets, Slides) can't be downloaded
    is_not_gapp = entry["mimeType"] not in GD_GAPPS_MIMETYPE
    return is_document and is_not_gapp


def gd_listdir(gd_dir: GoogleDriveFile) -> list[GoogleDriveFile]:
    """Returns the list of all the items in the current 'gd_dir' direcctory"""
    if not gd_isdir(gd_dir):
        raise NotADirectoryError(f"{gd_dir} isn't a Google Drive Direcotry")

    query = {"q": f"'{gd_dir['id']}' in parents and trashed=false"}
    return gdrive.ListFile(query).GetList()


def gd_getmtime(entry: GoogleDriveFile) -> int:
    """Returns the last time (in UNIX timestamp format) the file was modified"""
    return datetime.strptime(entry["modifiedDate"], ISO_FORMAT).timestamp()


def gd_download(entry: GoogleDriveFile, dest: PathLike) -> None:
    """Downloads the content of the provided Google Drive 'entry' to the local 'dest' path"""
    todos = gd_listdir(entry) if gd_isdir(entry) else [entry]

    for todo in todos:
        if gd_isdir(todo):
            makedirs(dest) if not exists(dest) else None
            gd_download(todo, join(dest, todo["title"]))
        elif gd_isfile(todo):
            todo.GetContentFile(dest)
            utime(dest, (gd_getmtime(todo), gd_getmtime(todo)))


def pull_recursively(local: PathLike, remote: GoogleDriveFile) -> None:
    """TODO: Add pydoc annotations"""
    for r_entry in gd_listdir(remote):
        # Based on the remote entry extracts the expected local one
        l_entry = abspath(join(local, r_entry["title"]))

        # If the local entry (file or dir) doesn't exist, we pull it straight from Google Drive
        if not exists(l_entry):
            console.print(f"[yellow]Downloading {r_entry['title']} in {l_entry}[/yellow]")
            gd_download(r_entry, l_entry)
            continue

        # If the remote directory is older we pull that recursively
        if gd_isdir(r_entry):
            console.print("Recursion on", r_entry["title"], l_entry)
            pull_recursively(l_entry, r_entry)
        # If the remote file is older then we pull and overwrite the current one
        elif gd_isfile(r_entry) and gd_getmtime(r_entry) > getmtime(l_entry):
            gd_download(r_entry, l_entry)
            console.print(f"[yellow]Updating {r_entry['title']} in {l_entry}[/yellow]")


def main(local_root: PathLike) -> None:
    """TODO: Add pydoc annotations"""
    for remote_folder in gd_listdir(gdrive.CreateFile({"id": "root"})):
        # From the root path creates the expected local counterpart
        local_folder = abspath(join(local_root, remote_folder["title"]))
        # Creates the local folder if it doesn't exist
        mkdir(local_folder) if not exists(local_folder) else None
        # ! Debug only, will be removed later
        console.log(f"[green]Pulling from Drive {remote_folder['title']} in {local_folder}[/green]")
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
