"""PyTest module with test suite implementation for the DriveDiffMerger.py script"""
from os import listdir
from os.path import getmtime
from random import randint
from tempfile import NamedTemporaryFile as TmpFile
from tempfile import TemporaryDirectory as TmpDir

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pytest import fixture
from scripts.DriveDiffMerger import (
    gd_exists, gd_getmtime, gd_isdir, gd_isfile, gd_join, gd_listdir, gd_mkdir, gd_upload,
    push_to_drive
)


@fixture(autouse=True)
def setup_gdrive_test_dir():
    """
    Initializes the base test directory for other test cases on Google Drive
    NOTE: This is only executed once before each test cases (kinda like a middleware)
    """
    # Authenticates and initializes the Google Drive proxy
    gdrive = GoogleDrive(GoogleAuth())
    # Gets a reference to the root of the Google Drive filesystem
    drive_root = gdrive.CreateFile({"id": "root"})

    # If the Google Drive folder hasn't been already created then is done
    if not gd_exists(gd_join(drive_root, "test")):
        gd_mkdir(gd_join(drive_root, "test"))


class TestDriveDiffMerger:
    """Test suite for the BackUpLoader script"""
    # Authenticates and initializes the Google Drive proxy
    gdrive = GoogleDrive(GoogleAuth())

    def test_file_upload(self):
        """Creates a file and uploads it to a Google Drive folder"""
        # Creates a temporary files to use as a mock upload
        tmp_file = TmpFile(delete=True)

        # Gets a reference to the test foolder in Google Drive
        test_folder = gd_join(self.gdrive.CreateFile({"id": "root"}), "test")
        # Upload the local temp file to Google Drive folder
        gd_upload(tmp_file.name, gd_join(test_folder, tmp_file.name))

        # Checks that everything went accordingly
        remote_file = gd_join(test_folder, tmp_file.name)
        assert gd_exists(remote_file), "Remote file not created on Drive"
        assert gd_isfile(remote_file), "Upload of file has not created a file in Drive"
        # The cast to int is necessary because the local mtime is more precise than the remote one
        remote_mtime, local_mtime = gd_getmtime(remote_file), getmtime(tmp_file.name)
        assert int(remote_mtime) == int(local_mtime), "mtime mismatch between remote and local"

    def test_dir_upload(self):
        """Creates a directory with some files inside and test recursive upload"""
        tmp_dir = TmpDir()  # Creates a temporary directory
        # Populates the directory with a random number of files
        [TmpFile(dir=tmp_dir.name) for _ in range(randint(3, 30))]
        # Gets a reference to the test foolder in Google Drive
        test_folder = gd_join(self.gdrive.CreateFile({"id": "root"}), "test")

        # Creates the directory on Google Drive
        gd_mkdir(gd_join(test_folder, tmp_dir.name))
        # Checks that everything went accordingly
        remote_dir = gd_join(test_folder, tmp_dir.name)
        assert gd_exists(remote_dir), "Remote folder not created on Drive"
        assert gd_isdir(remote_dir), "Upload of folder has not created a folder in Drive"

        # Uploads the directory content to remote
        push_to_drive(tmp_dir.name, remote_dir)

        # Checks that the remote and local dir have the same number of children
        n_remote, n_local = len(gd_listdir(remote_dir)), len(listdir(tmp_dir.name))
        assert n_remote == n_local, "Children mismatch between remote and local dir"

    def test_file_download(self):
        """Creates a file on Google Drive and downloads it"""
        assert False, "Test case not implemented"

    def test_dir_download(self):
        """Creates a folder on Google Drive and test recursive download"""
        assert False, "Test case not implemented"
