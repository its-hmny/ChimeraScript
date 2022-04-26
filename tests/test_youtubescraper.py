"""PyTest module with test suite implementation for the YouTubeScraper.py script"""
from os import getcwd, listdir
from os.path import isfile, join
from tempfile import NamedTemporaryFile as TmpFile

from genericpath import exists
from pytest import raises
from pytube.exceptions import VideoUnavailable
from scripts.YouTubeScraper import download_playlist, download_video


class TestYouTubeScrapers:
    """Test suite for the YouTubeScraper script"""
    def test_non_existent_video_url(self):
        """Gives false YouTube "url" argument to both download_video and download_playlist"""
        wrong_video_url = "https://www.youtube.com/watch?v=dhdaofhweoifhoi"
        n_file_in_cwd = len(listdir(getcwd()))  # Number of entries in the cwd
        with raises(VideoUnavailable):  # Checks that an exception is thrown
            download_video(wrong_video_url)
        # Checks that the directory hasn't been changed
        assert n_file_in_cwd is len(listdir(getcwd())), "An output file has been created"

        wrong_playlist_url = "https://www.youtube.com/watch?v=NrI-UBIB8Jk&list=3DnrvsAdEii_MQ"
        # Checks that an exception is thrown, pytube at the moment doesn't throw any exceptions
        # but accessing any variable of the Playlist object will raise an AttributeError
        with raises(AttributeError):
            download_playlist(wrong_playlist_url)
        # Checks that the directory hasn't been changed
        assert n_file_in_cwd is len(listdir(getcwd())), "An output dir has been created"

    def test_non_existent_path(self):
        """Gives non existent "out" argument to both download_video and download_playlist"""
        # The file, YouTube video and Playlist all exist but the first it's not a directory
        tmp_file = TmpFile()
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        playlist_url = "https://www.youtube.com/watch?v=TazHNpt6OTo&list=PLEijU2q67K_twQnJ06-3DnrvsAdEii_MQ"

        # Checks that a "NotADirectoryError" is correctly thrown
        with raises(NotADirectoryError):
            download_video(video_url, out=tmp_file.name)
        with raises(NotADirectoryError):
            download_playlist(playlist_url, out=tmp_file.name)

        # Checks that the file given hasn't been changed
        assert exists(tmp_file.name), "The 'out' file has been removed"
        assert isfile(tmp_file.name), "The 'out' file has been changed to something else"

    def test_file_path(self):
        """Gives non existent "out" argument to both download_video and download_playlist"""
        # The file and the YouTube video exist but the first it's not a directory
        wrong_path = join("/tmp", "fprgjwerignvaàoirI")
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        playlist_url = "https://www.youtube.com/watch?v=TazHNpt6OTo&list=PLEijU2q67K_twQnJ06-3DnrvsAdEii_MQ"

        # Checks that a "NotADirectoryError" is correctly thrown
        with raises(NotADirectoryError):
            download_video(video_url, out=wrong_path)
        # Checks that the path hasn't been created by the script
        assert not exists(wrong_path), "Non existent path has been created"

        # Checks that a "NotADirectoryError" is correctly thrown
        with raises(NotADirectoryError):
            download_playlist(playlist_url, out=wrong_path)
        # Checks that the file given hasn't been changed
        assert not exists(wrong_path), "Non existent path has been created"

    def test_resolution_flag(self):
        """
        Checks that the desired resolution is downloaded when provided by the user,
        both by download_video and download_playlist subcommands
        """
        assert False, "Test not implemented"

    def test_captions_flag(self):
        """
        Checks that the captions are downloaded and saved, when the flag is provided by
        the user, both by download_video and download_playlist subcommands
        """
        assert False, "Test not implemented"
