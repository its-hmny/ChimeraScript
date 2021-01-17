"""
This utility module containes a basics class that are used all over this project.
The GDriveFileSystem class implements a simple API (very similar to the os module API) to navigate a Google Drive
file system comfortably. Also additional methods are added to upload and download files in both direction
"""

from pydrive.auth import GoogleAuth, AuthenticationError
from pydrive.drive import GoogleDrive
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
            .ListFile({'q': "'{}' in parents and trashed=false".format(item_id), 'orderBy': "title"})
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

    def downloadFile(self, GDrive_fd):
        if os.path.exists(GDrive_fd.filename):
            os.remove(GDrive_fd.filename)
        remoteFile = self.driveRef.CreateFile({'id': GDrive_fd.uuid})
        remoteFile.GetContentFile(GDrive_fd.filename)

    def downloadDir(sel, GDrive_fd):
        # Create and move in the new root
        os.mkdir(GDrive_fd.filename)
        os.chdir(GDrive_fd.filename)
        for entry in self.listDir(GDrive_fd):
            if self.isFile(entry):
                self.downloadFile(remote_file)
            elif self.isDir(entry):
                self.downloadDir(entry)
            elif self.isLink(entry):
                continue  # ToDo
        # Return back in the prevoius dir (especially for recursive call)
        os.chdir('..')

    def uploadFile(self, filepath):
        remoteFile = self.driveRef.CreateFile()
        remoteFile.SetContentFile(filepath)
        remoteFile.Upload()

    def uploadDir(self, dirpath):
        pass


if __name__ == "__main__":
    log = __import__("log").Log()
    drive_fs = GDriveFileSystem()

    # Test of the root file system
    for entry in drive_fs.listDir('root'):
        log.warning("Check that {} is a directory: {} or is a file: {}" .format(
            entry.filename, drive_fs.isDir(entry), drive_fs.isFile(entry)))
    print()
    # Test of nested directory
    newEntryPoint = drive_fs.listDir('root')[0]
    for entry in drive_fs.listDir(newEntryPoint):
        log.warning("Check that {} is a directory: {} or is a file: {}" .format(
            entry.filename, drive_fs.isDir(entry), drive_fs.isFile(entry)))

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
                    "I should have downloaded {}, but I can't find it".format(
                        entry.filename))

    print()

    log.warning("Test of the upload functionality to Drive")
    drive_fs.uploadFile("PyHypervisor.py")
    for entry in drive_fs.listDir('root'):
        if entry.filename == "PyHypervisor.py":
            log.success(
                "File {} created successfully: {} {}".format(
                    entry.filename,
                    entry.filetype,
                    entry.uuid))
