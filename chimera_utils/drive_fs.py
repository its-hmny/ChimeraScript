"""
This utility module containes a basics class that are used all over this project.
The GDriveFileSystem class implements a simple API (very similar to the os module API) to navigate a Google Drive
file system comfortably. Also additional methods are added to upload and download files in both direction
"""

from pydrive.auth import GoogleAuth, AuthenticationError
from pydrive.files import FileNotDownloadableError
from pydrive.drive import GoogleDrive
from datetime import datetime
import os


class GDriveFile():
    def __init__(self, _apiResponseObject):
        self._internalData = _apiResponseObject
        # Basic field for easy interaction with the object
        self.lastModified = _apiResponseObject['modifiedDate'].split("T")[0]
        self.filetype = _apiResponseObject['mimeType']
        self.filename = _apiResponseObject['title']
        self.uuid = _apiResponseObject['id']

    def __str__(self):
        return self.filename

    def __repr__(self):
        return self.filename


class GDriveFileSystem():
    def __init__(self):
        try:
            (authentication := GoogleAuth()).LocalWebserverAuth()
        except AuthenticationError:
            return None
        self.driveRef = GoogleDrive(authentication)
        del authentication

    def _getContent(self, item_id):
        return [
            GDriveFile(item)
            for item in self.driveRef
            .ListFile({'q': f"'{item_id}' in parents and trashed=false", 'orderBy': "title"})
            .GetList()
        ]

    def isDir(self, GDrive_fd):
        if not isinstance(GDrive_fd, GDriveFile):
            raise TypeError("The input isn't a GDriveFile object")
        return GDrive_fd.filetype == 'application/vnd.google-apps.folder'

    def isFile(self, GDrive_fd):
        if not isinstance(GDrive_fd, GDriveFile):
            raise TypeError("The input isn't a GDriveFile object")
        return (
            GDrive_fd.filetype != 'application/vnd.google-apps.folder' and
            GDrive_fd.filetype != 'application/vnd.google-apps.shortcut'
        )

    def isLink(self, GDrive_fd):
        if not isinstance(GDrive_fd, GDriveFile):
            raise TypeError("The input isn't a GDriveFile object")
        return GDrive_fd.filetype != 'application/vnd.google-apps.shortcut'

    def listDir(self, GDrive_fd):
        if isinstance(GDrive_fd, GDriveFile) and self.isDir(GDrive_fd):
            return self._getContent(GDrive_fd.uuid)
        elif isinstance(GDrive_fd, str) and GDrive_fd == 'root':
            return self._getContent(GDrive_fd)
        else:
            raise TypeError(
                "The input entry is not a direcotry in Google Drive")

    def createFolder(self, folderName, folderParent):
        folder_metadata = {'title': folderName,
                           'mimeType': 'application/vnd.google-apps.folder',
                           'parents': [{"kind": "drive#fileLink",
                                        "id": folderParent.uuid}]}

        folder = self.driveRef.CreateFile(folder_metadata)
        folder.Upload()
        return GDriveFile(folder)

    def downloadFile(self, GDrive_fd):
        if os.path.exists(GDrive_fd.filename):
            os.remove(GDrive_fd.filename)
        remoteFile = self.driveRef.CreateFile({'id': GDrive_fd.uuid})
        try:
            remoteFile.GetContentFile(GDrive_fd.filename)
            timestamp = datetime.strptime(
                GDrive_fd.lastModified, "%Y-%m-%d").timestamp()
            os.utime(GDrive_fd.filename, (timestamp, timestamp))
        except FileNotDownloadableError:
            pass

    def downloadDir(self, GDrive_fd):
        # Create and move in the new root
        os.mkdir(GDrive_fd.filename)
        os.chdir(GDrive_fd.filename)
        for entry in self.listDir(GDrive_fd):
            if self.isFile(entry):
                self.downloadFile(entry)
            elif self.isDir(entry):
                self.downloadDir(entry)
            elif self.isLink(entry):
                continue  # ToDo
        # Return back in the prevoius dir (especially for recursive call)
        os.chdir('..')

    def uploadFile(self, remoteParent, filepath):
        if not os.path.isfile(filepath):
            raise TypeError("The input filepath is not a file")

        remoteFile = self.driveRef.CreateFile(
            {"parents": [{"kind": "drive#fileLink", "id": remoteParent.uuid}]})
        remoteFile.SetContentFile(os.path.basename(filepath))
        remoteFile.Upload()

    def uploadDir(self, remoteParent, dirpath):
        if not os.path.isdir(dirpath):
            raise TypeError("The input dirpath is not a direcotry")

        os.chdir(dirpath)
        newFolder = self.createFolder(dirpath, remoteParent)
        for entry in os.listdir('.'):
            if os.path.isfile(entry):
                self.uploadFile(newFolder, os.path.basename(entry))
            elif os.path.isdir(entry):
                self.uploadDir(newFolder, entry)
            elif self.isLink(entry):
                continue  # Ignore
        os.chdir('..')

    def removeFile(self, GDrive_fd):
        if self.isFile(GDrive_fd) or self.isLink(GDrive_fd):
            # Permanently delete the file
            remoteFile = self.driveRef.CreateFile({'id': GDrive_fd.uuid})
            remoteFile.Delete()
    
    def removeDir(self, GDrive_fd):
        for entry in self.listDir(GDrive_fd):
            if self.isFile(entry) or self.isLink(entry):
                self.downloadFile(entry)
            elif self.isDir(entry):
                self.downloadDir(entry)
        # After removing all the element inside the dir descriptor has to go
        remoteDir = self.driveRef.CreateFile({'id': GDrive_fd.uuid})
        remoteDir.Delete()



if __name__ == "__main__":
    log = __import__("log").Log()
    drive_fs = GDriveFileSystem()

    # Test of the root file system
    for entry in drive_fs.listDir('root'):
        log.warning(
            f"Check that {entry.filename} is a directory: {drive_fs.isDir(entry)} or is a file: {drive_fs.isFile(entry)}")
    print()
    # Test of nested directory
    newEntryPoint = drive_fs.listDir('root')[0]
    for entry in drive_fs.listDir(newEntryPoint):
        log.warning(
            f"Check that {entry.filename} is a directory: {drive_fs.isDir(entry)} or is a file: {drive_fs.isFile(entry)}")

        if entry.filename == "Curriculum Enea 2020.pdf":
            # Test of the download from Drive functionality
            log.warning("Test of the download from Drive functionality")
            drive_fs.downloadFile(entry)
            if (os.path.isfile(entry.filename)):
                log.success(
                    "Correctly downloaded the file {}".format(
                        entry.filename))
                os.remove(entry.filename)
            else:
                log.error(
                    f"I should have downloaded {entry.filename}, but I can't find it")

    print()

    log.warning("Test of the upload functionality to Drive")
    drive_fs.uploadFile("PyHypervisor.py")
    for entry in drive_fs.listDir('root'):
        if entry.filename == "PyHypervisor.py":
            log.success(
                f"File {entry.filename} created successfully: {entry.filetype} {entry.uuid}")
