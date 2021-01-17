"""

"""

import os
import platform
from chimera_utils import Log, Drive_fs
from datetime import datetime

log = Log()
drivefs = None


# Platform specific fields
# This are mappings to the root folder in Drive and to the respective
# folder on my computers
if (platform.system() == "Windows"):
    homePath = "C:/Users/eneag/"
    dirToSync = {"Immagini": "Pictures", "Università": "Desktop/Università",
                 "Documenti": "Documents", "Others": "Desktop/Others"}
    # This is the amount of shit that Windows has by default
    blacklist = [
        "Modelli di Office personalizzati",
        "WindowsPowerShell",
        "desktop.ini",
        "Musica",
        "Video",
        "Immagini",
        "Foto",
        "Camera Roll",
        "Saved Pictures"]
elif (platform.system() == "Linux"):
    homePath = "/home/hmny/"
    dirToSync = {"Immagini": "Pictures",
                 "Università": "University", "Documenti": "Documents"}
    blacklist = []
else:
    log.error("This OS is not supported yet")
    os._exit(os.EX_OSERR)


def mergeFiles(remote, local):
    r_lastMod = datetime.strptime(remote.lastModified, "%Y-%m-%d").timestamp()
    l_lastMod = os.path.getmtime(local)
    # When file are merged the more recent modification time
    # is picked to determine which version has to override the counterpart
    # If the date is the same then no change at all happens
    if r_lastMod > l_lastMod:
        drivefs.downloadFile(r_lastMod)
    elif r_lastMod < l_lastMod:
        drivefs.uploadFile(os.path.abspath(local))


def tupleIterator(first, second, valueFirst, valueSecond):
    tmpFirst = [valueFirst(item)
                for item in first if item not in blacklist]
    tmpSecond = [valueSecond(item)
                 for item in second if item not in blacklist]
    conglomerate = []

    # Pair every elements wih its counterpart, if couterpart is not found pair
    # itself with None
    for i, element in enumerate(tmpFirst):
        try:
            j = tmpSecond.index(element)
            conglomerate.append((first[i], second[j]))
            tmpSecond[j] = None
        except ValueError:
            conglomerate.append((first[i], None))
    # The remaining file are paired with None but specularly in relation to
    # above
    for j, element in enumerate(tmpSecond):
        if element is None:
            continue
        else:
            conglomerate.append((None, second[j]))

    return conglomerate


# Synchronizes a directory in both direction: remote -> local and local ->
# remote at the same time
def synchDir(remotepath, localpath):
    os.chdir(localpath)
    remote_entries = drivefs.listDir(remotepath)
    local_entries = [entry for entry in os.listdir(
        '.') if entry not in blacklist]

    def getRemoteName(r_file): return r_file.filename
    # Because of fucking Windows "'file.txt'" string representation instead of
    # "file.txt"
    def getLocalName(l_file): return "{}".format(l_file)

    for r_entry, l_entry in tupleIterator(
            remote_entries, local_entries, getRemoteName, getLocalName):
        l_exist = l_entry is not None
        r_exist = r_entry is not None
        # If the file/dir already exist on local and remote then additional
        # check has to be done
        if l_exist and r_exist:
            if drivefs.isFile(r_entry):
                mergeFiles(r_entry, l_entry)
            elif drivefs.isDir(r_entry):
                synchDir(r_entry, os.path.join(os.getcwd(), l_entry))

        # If the current entry doesn't exist locally then simply download its
        elif r_exist and not l_exist:
            if drivefs.isFile(r_entry):
                drivefs.downloadFile(r_entry)
            elif drivefs.isDir(r_entry):
                drivefs.downloadDir(r_entry)

        # If the current entry doesn't exist remotely then simply upload it
        elif l_exist and not r_exist:
            if os.path.isfile(l_entry):
                drivefs.uploadeFile(remotepath, l_entry)
            elif os.path.isdir(l_entry):
                drivefs.uploadDir(remotepath, l_entry)

    # For recursive call returns to previous directory so the caller can start
    # without inconsistencies
    os.chdir('..')


def DriveDiffMerger():
    log.warning("An authorization dialog should open...")
    global drivefs
    drivefs = Drive_fs()

    if (drivefs is None):
        log.error("Could not authenticate with Google")
        return -1
        # Iteration on the main entry mapping them to their local counterpart
    # From now on we can assume specularity between the remote and the local
    # tree structure
    for entry in drivefs.listDir('root'):
        # The remote is ASSUMED to be the most updated version
        try:
            synchDir(entry, homePath + dirToSync[entry.filename])
            log.success("{} synchronized with your Google Drive".format(
                dirToSync[entry.filename]))
        except KeyError:
            log.error(
                "Missing mapping for Google Drive directory {}".format(
                    entry.filename))


DriveDiffMerger()
