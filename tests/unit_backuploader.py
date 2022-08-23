"""PyTest module with test suite implementation for the BackUpLoader.py script"""
from os import environ, getcwd
from os.path import basename, exists, join
from random import randint
from tempfile import NamedTemporaryFile as TmpFile
from tempfile import TemporaryDirectory as TmpDir

from asyncssh import connect
from pytest import fixture, mark, raises
from scripts.BackUpLoader import scp_path


@fixture(autouse=True)
async def setup_remote_test_dir():
    """
    Initializes the base test directory for other test cases on the remote location
    NOTE: This is only executed once before each test cases (kinda like a middleware)
    """
    hostname = environ["SSH_HOSTNAME"]
    username = environ["SSH_USERNAME"]
    password = environ["SSH_PASSWORD"]

    # Opens a connection to the remote server
    async with connect(hostname, username=username, password=password) as ssh:
        # If the root test directory already exists then skips the remaining steps
        if (await ssh.run("test -d /public/hmny/")).exit_status == 0:
            return

        # Check that the directory is present in the remote location
        cmd = await ssh.run("mkdir /public/hmny/")
        assert cmd.exit_status is 0, "Could not create test root folder on remote server"


@mark.asyncio
class TestBackUpLoader:
    """Test suite for the BackUpLoader script"""
    hostname = environ["SSH_HOSTNAME"]
    username = environ["SSH_USERNAME"]
    password = environ["SSH_PASSWORD"]

    async def test_missing_path(self):
        """Gives a not existent path argument to scp_path"""
        # Creates a non existent path
        wrong_path = join(getcwd(), "wrongpath")
        # Tests that "scp_path" blocks the execution when path doesn't exist
        with raises(FileNotFoundError):
            await scp_path(wrong_path, None, None, None)
        # Checks that the path hasn't been created
        assert exists(wrong_path) is False, "Non existent 'path' argument has been created"

    async def test_missing_hostname(self):
        """Doesn't provide hostname, username and password to scp_path"""
        # Creates a temporary files to use as a mock
        tmp_file = TmpFile(delete=True)

        # Tests that "scp_path" blocks the execution when hostname isn't provided
        with raises(ValueError):
            await scp_path(tmp_file.name, None, "root", "pasword")
        # Tests that "scp_path" blocks the execution when username isn't provided
        with raises(ValueError):
            await scp_path(tmp_file.name, "athena", None, "pasword")
        # Tests that "scp_path" blocks the execution when password isn't provided
        with raises(ValueError):
            await scp_path(tmp_file.name, "athena", "root", None)

    async def test_with_correct_path(self):
        """Tests scp_path with valid arguments"""
        # Creates a temporary files to use as a mock
        tmp_file = TmpFile(delete=True)

        # Uploads the temporary file
        await scp_path(tmp_file.name, self.hostname, self.username, self.password)

        # Opens a connection to the remote server
        async with connect(self.hostname, username=self.username, password=self.password) as ssh:
            cmd = await ssh.run(f"test -f /public/hmny/{basename(tmp_file.name)}")
            assert cmd.exit_status is 0, "Test doesn't exist on remote"

    async def test_with_dir_path(self):
        """Tests scp_path with valid arguments but given a directory path"""
        tmp_dir = TmpDir()  # Creates a temporary directory
        # Populates the directory with a random number of mock files and at the same time
        # initializes a list of all the file that will be uploaded to the remote
        to_check_list = [TmpFile(dir=tmp_dir.name) for _ in range(randint(3, 30))]

        # Uploads the temporary directory
        await scp_path(tmp_dir.name, self.hostname, self.username, self.password)

        # Opens a connection to the remote server
        async with connect(self.hostname, username=self.username, password=self.password) as ssh:
            # Check that the directory is present in the remote location
            cmd = await ssh.run(f"test -d /public/hmny/{basename(tmp_dir.name)}")
            assert cmd.exit_status is 0, "Temporary directory doesn't exist on remote"

            # Checks that all the nested files are present in the remote location
            for entry in to_check_list:
                remote_file_path = f"/public/hmny/{basename(tmp_dir.name)}/{basename(entry.name)}"
                cmd = await ssh.run(f"test -f {remote_file_path}")
                assert cmd.exit_status is 0, "Nested temporary file doesn't exist on remote"
