"""PyTest module with test suite implementation for the GitPuller.py script"""
from os import listdir, system
from os.path import exists, isdir, join
from random import choice, randint, random
from tempfile import NamedTemporaryFile, mkdtemp

from pytest import raises
from requests import get
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

    def test_repos_clone_new_flag(self):
        """Checks that the "clone_new" flags works correctly for repo subcommand"""
        # Creates a temporary directory
        tmp_dir = mkdtemp()
        # Uses GitHub API to get a list of all my public repositories
        res = get("https://api.github.com/search/repositories?q=user:its-hmny")
        repo_list = res.json().get("items", [])

        # Clones a random number of repos manually
        for _ in range(randint(0, len(repo_list))):
            to_be_cloned = choice(repo_list)
            system(f"cd {tmp_dir} && git clone {to_be_cloned['clone_url']}")

        # Executes the script on the temp directory to tests that the missing ones are cloned
        fetch_repos(tmp_dir, clone_new=True)
        assert len(listdir(tmp_dir)) == len(repo_list), "Not all the repos have been cloned"

    def test_stars_clone_new_flag(self):
        """Checks that the "clone_new" flags works correctly for stars subcommand"""
        # Creates a temporary directory
        tmp_dir = mkdtemp()
        # Uses GitHub API to get a list of all my public repositories
        stars_list = get("https://api.github.com/users/its-hmny/starred").json()

        # Clones a random number of repos manually
        for _ in range(randint(0, len(stars_list))):
            to_be_cloned = choice(stars_list)
            system(f"cd {tmp_dir} && git clone {to_be_cloned['clone_url']}")

        # Executes the script on the temp directory to tests that the missing ones are cloned
        fetch_stars(tmp_dir, clone_new=True)
        assert len(listdir(tmp_dir)) == len(stars_list), "Not all the repos have been cloned"

    def test_repos_ignore_archived_flags(self):
        """Checks that the "ignore_archived" flags works correctly"""
        # Creates a temporary directory
        tmp_dir = mkdtemp()
        # Uses GitHub API to get a list of all my public repositories
        res = get("https://api.github.com/search/repositories?q=user:its-hmny")
        not_archived = [repo for repo in res.json().get("items", []) if not repo["archived"]]

        # Executes the script on the temp directory and tests that only the not archived are cloned
        fetch_repos(tmp_dir, clone_new=True, ignore_archived=True)
        assert len(listdir(tmp_dir)) == len(not_archived), "Some archived repos have been cloned"
