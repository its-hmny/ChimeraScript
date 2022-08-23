#! /usr/bin/env python3
"""
ChimeraScript - DriveDiffMerger.py

This script allows to keep synchronized your Google Drive folder with a folder of your choice.
There are 3 option available as of now, is possible to only pull from remote, only push to remote
and, at last, to both pull and push (in this order).
By default the remote file is assumed to be the newer one and will have priority over the local
one, so in case of conflict the remote versin will overwrite the local one.

Example:
    To only pull from Google Drive, use::
        $ python3 DriveDiffMerger.py pull ~/GoogleDrive

    To only push from local to Google Drive, use::
        $ python3 DriveDiffMerger.py push ~/GoogleDrive

    To both pull and then push, use::
        $ python3 DriveDiffMerger.py sync ~/GoogleDrive


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
    "application/vnd.google-apps.presentation",
]

# Rich console instance for pretty printing on the terminal
console = Console(record=True)
# Starts a local webserver that handles OAuth authentication.
# Injects the auth payload and obtains a proxy to Drive access.
gdrive = GoogleDrive(GoogleAuth())


def gd_exists(entry: GoogleDriveFile) -> bool:
    """
    Checks that a GoogleDriveFile effectively exist on drive (is uploaded)

    Args:
        entry (GoogleDriveFile): The remote file/entry to be tested
    """
    return entry.uploaded is True


def gd_isdir(entry: GoogleDriveFile) -> bool:
    """
    Determines if the 'entry' argument is a Google Drive directory/folder

    Args:
        entry (GoogleDriveFile): The remote file/entry to be tested
    """
    return entry["mimeType"] == GD_FOLDER_MIMETYPE


def gd_islink(entry: GoogleDriveFile) -> bool:
    """
    Determines if the 'entry' argument is a Google Drive link/shortcut

    Args:
        entry (GoogleDriveFile): The remote file/entry to be tested
    """
    return entry["mimeType"] == GD_LINK_MIMETYPE


def gd_isfile(entry: GoogleDriveFile) -> bool:
    """
    Determines if the 'entry' argument is a downloadable file (not a Goggle Apps one)

    Args:
        entry (GoogleDriveFile): The remote file/entry to be tested
    """
    is_document = not gd_islink(entry) and not gd_isdir(entry)
    # Google Apps (Docs, Sheets, Slides) can't be downloaded
    is_not_gapp = entry["mimeType"] not in GD_GAPPS_MIMETYPE
    return is_document and is_not_gapp


def gd_getmtime(entry: GoogleDriveFile) -> float:
    """
    Returns the last time (in UNIX timestamp format) the file was modified

    Args:
        entry (GoogleDriveFile): The remote file/entry
    """
    return datetime.strptime(entry["modifiedDate"], ISO_FORMAT).timestamp()


def gd_join(parent: GoogleDriveFile, name: str) -> GoogleDriveFile:
    """
    Returns the GoogleDriveEntity with the provided parent as well as
    the provided name/title. If no matching candidate is found then a new
    entity is created and can be uploaded manually by the user.

    Args:
        parent (GoogleDriveFile): The remote parent directory
        name (str): The child GoogleDriveFile name

    Raises:
        NotADirectoryError: The given 'parent' argument isn't a folder
    """
    if not gd_isdir(parent):
        raise NotADirectoryError(f"{parent['title']} isn't a Google Drive Direcotry")

    # Creates and execute the query, then converts it to a Python list
    query = {"q": f"'{parent['id']}' in parents and title='{name}' and trashed=false"}
    match_list = gdrive.ListFile(query).GetList()

    # Match found, the given child already exist
    if len(match_list) != 0:
        return match_list.pop()
    # The desired child is created but not uplaoded, so its not persistent
    else:
        query = {'title': name, 'parents': [{"id": parent["id"], "kind": "drive#fileLink"}]}
        return gdrive.CreateFile(query)


def gd_listdir(gd_dir: GoogleDriveFile) -> list[GoogleDriveFile]:
    """
    Returns the list of all the items in the current 'gd_dir' direcctory

    Args:
        gd_dir (GoogleDriveFile): The remote directory for which we want its content

    Raises:
        NotADirectoryError: The given 'gd_dir' argument isn't a folder
    """
    if not gd_isdir(gd_dir):
        raise NotADirectoryError(f"{gd_dir} isn't a Google Drive Direcotry")
    # Creates and execute the query, then converts it to a Python list
    query = {"q": f"'{gd_dir['id']}' in parents and trashed=false"}
    return gdrive.ListFile(query).GetList()


def gd_mkdir(gd_dir: GoogleDriveFile) -> None:
    """
    Given a partial or complete GoogleDriveFile 'gd_dir' overwrites itsmimetype
    to act as a folder, then uplaods the changes to make them permanent.

    Args:
        gd_dir (GoogleDriveFile): The remote directory for which we want its content
    """
    gd_dir["mimeType"] = GD_FOLDER_MIMETYPE
    gd_dir.Upload()


def gd_download(entry: GoogleDriveFile, dest: PathLike) -> None:
    """
    Downloads the content of the provided Google Drive file 'entry' to the local 'dest' path

    Args:
        entry (GoogleDriveFile): The remote file/entry to be downloaded
        dest (str): The full destination path (with filename and extension)

    Raises:
        FleNotFoundError: The provided 'entry' is not a downloadable file
    """
    if not gd_isfile(entry):
        raise FileNotFoundError(f"{entry['title']} is not a Google Drive file")
    # Downloads the file at the provided destination path (full path with filename as well)
    entry.GetContentFile(dest)
    # Changes the file atime & mtime to reflect the one of the remote entry
    utime(dest, (gd_getmtime(entry), gd_getmtime(entry)))


def gd_upload(entry: PathLike, dest: GoogleDriveFile) -> None:
    """
    Uploads the content of the provided 'dest' argument to the remote GoogleDriveFile 'entry'

    Args:
        entry (PathLike): The local file to be uplaoded (its content)
        dest (GoogleDriveFile): The remote file in which such content must be written

    Raises:
        FleNotFoundError: The provided 'entry' is not an uploadable file
    """
    if not isfile(entry):
        raise FileNotFoundError(f"{entry['title']} is not a local file")
    # Uploads and overwrites the 'dest' content
    dest.SetContentFile(entry)
    # Updates also the mtime of the remote resource to match the local one
    dest["modifiedDate"] = datetime.fromtimestamp(getmtime(entry)).strftime(ISO_FORMAT)
    # Saves the changes permanently
    dest.Upload()


def pull_from_drive(l_root: PathLike, r_root: GoogleDriveFile) -> None:
    """
    Pulls all the new or changed files remotely to the local filesystem counterpart location.
    A file is determined to be newer based on its last_modified timestamp, the bigger the newer.

    Args:
        l_root (PathLike): The local root dir from which start pulling
        r_root (GoogleDriveFile): The remote root from whic start pulling
    """
    # Gets a list of remote children from the given parent
    remote_childrens = {r_entry["title"]: r_entry for r_entry in gd_listdir(r_root)}

    for entry_name, r_child in remote_childrens.items():
        l_child = join(l_root, entry_name)  # Interpolates the local counterpart path

        # If the 'r_child' is a direcotry then is recursively pulled
        if gd_isdir(r_child):
            mkdir(l_child) if not exists(l_child) else None  # pylint: disable=expression-not-assigned
            pull_from_drive(l_child, r_child)

        # Skips the current iteration if 'r_child' isn't a file
        if not gd_isfile(r_child):
            continue

        # If the 'r_child' is newer or the local one doesn't exist then we pull from Drive
        if not (exists(l_child)) or gd_getmtime(r_child) > getmtime(l_child):
            console.log(f"Pulling {l_child} from Google Drive")
            gd_download(r_child, l_child)


def push_to_drive(l_root: PathLike, r_root: GoogleDriveFile) -> None:
    """
    Push all the new or changed files locally to the remote Goole Drive counterpart location.
    A file is determined to be newer based on its last_modified timestamp, the bigger the newer.

    Args:
        l_root (PathLike): The local root dir from which start pulling
        r_root (GoogleDriveFile): The remote root from whic start pulling
    """
    # Gets a list of local children from the given parent
    local_childrens = {basename(l_entry): join(l_root, l_entry) for l_entry in listdir(l_root)}

    for entry_name, l_child in local_childrens.items():
        # Interpolates the local counterpart path
        r_child = gd_join(r_root, entry_name)

        # If the 'l_child' is a direcotry then is recursively pushed
        if isdir(l_child):
            gd_mkdir(r_child) if not gd_exists(r_child) else None  # pylint: disable=expression-not-assigned
            push_to_drive(l_child, r_child)

        # Skips the current iteration if 'l_child' isn't a file
        if not isfile(l_child):
            continue

        # If the 'r_child' is newer or the local one doesn't exist then we pull from Drive
        if not (gd_exists(r_child)) or getmtime(l_child) > gd_getmtime(r_child):
            console.log(f"Pushing {l_child} to Google Drive")
            gd_upload(l_child, r_child)


def main(*paths: list[PathLike], pull: bool = True, push: bool = False) -> None:
    """
    Script entrypoint and dipsatcher, handles input validation and dispatch to both
    'pull_from_drive' and 'push_to_drive' functions.

    Args:
        paths (list[PathLike]): The list of local path to push and/or pull
        pull (bool): Enables the pull of new files/changes from Google Drive
        push (bool): Enables the push of new files/changes to Google Drive
    """
    # Gets a reference to the root of the Google Drive filesystem
    drive_root = gdrive.CreateFile({"id": "root"})

    for argpath in paths:
        if not exists(argpath):
            raise FileNotFoundError(f"{argpath} doesn't exists")

        console.print(f"[yellow]Synchronization of {argpath} to Google Drive[yellow]")

        # Generates interface compliant argument for both recursive pull and push functions
        local_entry, remote_entry = abspath(argpath), gd_join(drive_root, basename(argpath))

        # Pulls from Drive if the user has provided the flag
        pull_from_drive(local_entry, remote_entry) if pull else None  # pylint: disable=expression-not-assigned
        # Push to Drive if the user has provided the flag
        push_to_drive(local_entry, remote_entry) if push else None  # pylint: disable=expression-not-assigned


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
