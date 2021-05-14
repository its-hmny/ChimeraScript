"""
Back_up_Loader is a simple Python scipt used to automate my regular backup upload to the university sftp server, this script
works recursively so (as the example show) you only need to put the directory you want to upload and it will automate the
process for you. PLEASE NOTE THAT THIS WON'T WORK ON WINDOWS (due to the use of \ instead of / in Windows terminal)

Note: it requires pysftp as third party library, you can install it with "pip3 install pysftp"

Created by Enea Guidi on 08/11/2019. Please check the README.md for more informations
"""

import platform
import getpass
import pysftp
import os

from paramiko.ssh_exception import AuthenticationException
from paramiko.ssh_exception import SSHException
from chimera_utils import Log, exception_handler

# Fixed fields for every OS (platform indipendent)
dest_path = "/public/hmny/"  # The destinaion path on the server
dest_folder = dest_path + "Backup/"
hostname = "pinkerton.cs.unibo.it"
usrnm = "enea.guidi"
dir_blacklist = ["node_modules", "Musica", "Immagini", "Video"]

log = Log()

# Platform specific fields
if (platform.system() == "Windows"):
    home_path = "C:/Users/eneag/"
    dir_to_upload = ["Pictures", "Desktop/Progetti",
                     "Desktop/Università", "Documents"]
elif (platform.system() == "Linux"):
    home_path = "/home/hmny/"
    dir_to_upload = ["Pictures", "Projects", "University", "Documents"]
else:
    log.error("This OS is not supported yet")
    os._exit(os.EX_OSERR)


def get_folder_size(parent, folder):
    vec_sizes = []
    complete_path = os.path.join(parent, folder)

    for entry in os.scandir(complete_path):
        if entry.is_file():
            vec_sizes.append(entry.stat().st_size)
        elif entry.is_dir() and entry.name not in dir_blacklist:
            get_folder_size(folder, entry)

    return sum(vec_sizes)


def recursive_put(sftp, toUpload, destination, on_upload_completed):
    try:
        for entry in os.listdir(toUpload):
            local = os.path.join(toUpload, entry)
            remote = f"{destination}/{entry}"

            if os.path.isdir(local) and dir_blacklist.count(entry) == 0:
                sftp.makedirs(remote)
                recursive_put(sftp, local, remote, on_upload_completed)
                continue
            elif os.path.islink(local):
                continue
            elif os.path.isfile(local):
                sftp.put(local, remote)
                on_upload_completed(os.stat(entry).st_size, entry)

    except PermissionError:
        log.error(toUpload + " couldn't be opened")


def start_upload(sftp):
    # Creates the destination if it doesn't exist
    sftp.makedirs(dest_folder)
    # Private access to only owner
    sftp.chmod(dest_path, mode=700)
    sftp.chdir(dest_folder)

    total_upload_size = [
        get_folder_size(
            home_path,
            up_dir) for up_dir in dir_to_upload]
    progress_bar, update_bar = log.progress_bar_builder(
        "Uploading", total_upload_size)

    with progress_bar:
        for up_dir in dir_to_upload:
            cwd = home_path + up_dir
            remote_cwd = dest_folder + up_dir.split("/")[-1]
            sftp.makedirs(remote_cwd)
            recursive_put(sftp, cwd, remote_cwd, update_bar)
            log.success(cwd + " has been uploaded")


@exception_handler
def Back_up_Loader():
    try:
        pswd = getpass.getpass(prompt="Please insert password: ")
        with pysftp.Connection(host=hostname, username=usrnm, password=pswd) as sftp:
            log.warning("Connection established")
            start_upload(sftp)
            sftp.close()

    except AuthenticationException:
        log.error("Authentication failed, username or password invalid")

    except SSHException:
        log.error("Could not connect to the host")


Back_up_Loader()
