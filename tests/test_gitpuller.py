from os.path import isdir, join, exists
from random import random
from tempfile import NamedTemporaryFile

from pytest import raises
from scripts.GitPuller import fetch_repos, fetch_stars


class TestGitPuller:
    """Test suite for the Gitpuller script"""
    def test_non_existent_input_path(self):
        """Gives false "path" argument to both fetch_stars and fetch_repos"""
        # Generates two random non existent paths
        wrong_repo_path = join("/tmp", str(random()))
        wrong_stars_path = join("/tmp", str(random()))

        # Tests that "fetch_repos" blocks the execution instead of continuing
        with raises(FileNotFoundError):
            fetch_repos(wrong_repo_path)
        assert exists(wrong_repo_path) is False, "(repo): Non existent out path has been created"

        # Tests that "fetch_stars" blocks the execution as well
        with raises(FileNotFoundError):
            fetch_stars(wrong_stars_path)
        assert exists(wrong_stars_path) is False, "(stars): Non existent out path has been created"

    def test_file_input_path(self):
        """Gives the path of a file to both the subcommands and test their response"""
        # Creates a temp file and saves its path
        with NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file_path = join("/tmp", tmp_file.name)

        # Tests that "fetch_repos" catches the error
        with raises(NotADirectoryError):
            fetch_repos(tmp_file_path)
        assert exists(tmp_file_path) is True, "(repos): Overritten the filepath"
        assert isdir(tmp_file_path) is False, "(repos): Changed the filepath to a directory"

        # Tests that "fetch_stars" catches the error
        with raises(NotADirectoryError):
            fetch_stars(tmp_file_path)
        assert exists(tmp_file_path) is True, "(stars): Overritten the filepath"
        assert isdir(tmp_file_path) is False, "(stars): Changed the filepath to a directory"

    def test_clone_new_flag(self):
        """Checks that the "clone_new" flags works correctly"""
        assert False, "Test case not completed"

    def test_ignore_archived(self):
        """Checks that the "ignore_archived" flags works correctly"""
        assert False, "Test case not completed"
