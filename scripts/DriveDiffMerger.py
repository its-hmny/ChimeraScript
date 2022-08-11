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
from os import PathLike, listdir, mkdir, utime
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


def gd_exists(entry: GoogleDriveFile) -> bool:
    """TODO: Add pydoc annotations"""
    return entry.uploaded == True


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


def gd_join(parent: GoogleDriveFile, name: str) -> bool:
    """TODO: Add pydoc annotations"""
    query = {"q": f"'{parent['id']}' in parents and title='{name}' and trashed=false"}
    match_list = gdrive.ListFile(query).GetList()

    if len(match_list) != 0:
        return match_list.pop()
    else:
        query = {'title': name, 'parents': [{"id": parent["id"], "kind": "drive#fileLink"}]}
        return gdrive.CreateFile(query)


def gd_listdir(gd_dir: GoogleDriveFile) -> list[GoogleDriveFile]:
    """Returns the list of all the items in the current 'gd_dir' direcctory"""
    if not gd_isdir(gd_dir):
        raise NotADirectoryError(f"{gd_dir} isn't a Google Drive Direcotry")

    query = {"q": f"'{gd_dir['id']}' in parents and trashed=false"}
    return gdrive.ListFile(query).GetList()


def gd_mkdir(gd_dir: GoogleDriveFile) -> list[GoogleDriveFile]:
    """TODO: Add pydoc annotations"""
    gd_dir["mimeType"] = GD_FOLDER_MIMETYPE
    gd_dir.Upload()


def gd_getmtime(entry: GoogleDriveFile) -> int:
    """Returns the last time (in UNIX timestamp format) the file was modified"""
    return datetime.strptime(entry["modifiedDate"], ISO_FORMAT).timestamp()


def gd_download(entry: GoogleDriveFile, dest: PathLike) -> None:
    """Downloads the content of the provided Google Drive file 'entry' to the local 'dest' path"""
    if not gd_isfile(entry):
        raise FileNotFoundError(f"{entry['title']} is not a Google Drive file")
    # Downloads the file at the provided destination path (full path with filename as well)
    entry.GetContentFile(dest)
    # Changes the file atime & mtime to reflect the one of the remote entry
    utime(dest, (gd_getmtime(entry), gd_getmtime(entry)))


def gd_upload(entry: PathLike, dest: GoogleDriveFile) -> None:
    """TODO: Add pydoc annotations"""
    if not isfile(entry):
        raise FileNotFoundError(f"{entry['title']} is not a local file")
    dest.SetContentFile(entry)
    dest.Upload()


def pull(l_prnt: PathLike, r_parent: GoogleDriveFile = gdrive.CreateFile({"id": "root"})) -> None:
    """TODO: Add pydoc annotations"""
    # Gets a list of remote children from the given parent
    remote_childrens = {r_entry["title"]: r_entry for r_entry in gd_listdir(r_parent)}

    for entry_name, r_child in remote_childrens.items():
        l_child = join(l_prnt, entry_name)  # Interpolates the local counterpart path

        # If the 'r_child' is a direcotry then is recursively pulled
        if gd_isdir(r_child):
            mkdir(l_child) if not exists(l_child) else None
            pull(l_child, r_child)

        # Skips the current iteration if 'r_child' isn't a file
        if not gd_isfile(r_child):
            continue

        # If the 'r_child' is newer or the local one doesn't exist then we pull from Drive
        if not exists(l_child) or gd_getmtime(r_child) > getmtime(l_child):
            console.print(f"[green]Pulling {l_child} from Google Drive[green]")
            gd_download(r_child, l_child)


def push(l_prnt: PathLike, r_parent: GoogleDriveFile = gdrive.CreateFile({"id": "root"})) -> None:
    """TODO: Add pydoc annotations"""
    # Gets a list of local children from the given parent
    local_childrens = {basename(l_entry): join(l_prnt, l_entry) for l_entry in listdir(l_prnt)}

    for entry_name, l_child in local_childrens.items():
        # Interpolates the local counterpart path
        r_child = gd_join(r_parent, entry_name)

        # If the 'l_child' is a direcotry then is recursively pushed
        if isdir(l_child):
            gd_mkdir(r_child) if not gd_exists(r_child) else None
            push(l_child, r_child)

        # Skips the current iteration if 'l_child' isn't a file
        if not isfile(l_child):
            continue

        # If the 'r_child' is newer or the local one doesn't exist then we pull from Drive
        if not gd_exists(r_child) or getmtime(l_child) > gd_getmtime(r_child):
            console.print(f"[green]Pushing {l_child} to Google Drive[green]")
            gd_upload(l_child, r_child)


def sync(root: PathLike) -> None:
    """TODO: Add pydoc annotations"""
    pull(abspath(root), gdrive.CreateFile({"id": "root"}))
    push(abspath(root), gdrive.CreateFile({"id": "root"}))


if __name__ == "__main__":
    try:
        Fire({"sync": sync, "pull": pull, "push": push})
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
