"""PyTest module with test suite implementation for the YouTubeScraper.py script"""
from os import getcwd, listdir
from os.path import exists, getmtime, isdir, isfile, join
from tempfile import NamedTemporaryFile as TmpFile
from tempfile import TemporaryDirectory as TmpDir

from pytest import raises
from pytube import Playlist
from pytube import YouTube as Video
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
        # but accessing any variable of the Playlist object will raise an KeyError
        with raises(KeyError):
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

    def test_correct_video_download(self):
        """Gives correct arguments to download_video and expects correct output"""
        # The "out" path and the YouTube video exist and are correct
        tmp_dir, video_url = TmpDir(), "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        # Tries to download the YT video
        download_video(video_url, out=tmp_dir.name)

        # Checks that the path hasn't been created by the script
        expected_file_path = join(tmp_dir.name, f"{Video(video_url).title}.mp4")
        assert exists(expected_file_path), "The expected output file doesn't exists"
        assert isfile(expected_file_path), "The expected output file isn't a file"

    def test_correct_playlist_download(self):
        """Gives correct arguments to download_video and expects correct output"""
        # The "out" path and the YouTube playlist exist and are correct
        tmp_dir = TmpDir()
        playlist_url = "https://www.youtube.com/watch?v=meTpMP0J5E8&list=PL0vfts4VzfNjurgyRawm_e0RevgP7g1Ao"

        # Tries to download the YT playlist (all the videos present in it)
        download_playlist(playlist_url, out=tmp_dir.name)

        # Retrieves the playlist name and determines the path
        yt_playlist = Playlist(playlist_url)
        expected_out_dir = join(tmp_dir.name, yt_playlist.title)
        # Checks that the script has created a sdirectory named as the playlist
        assert exists(expected_out_dir), "Playlist directory hasn't been created"
        assert isdir(expected_out_dir), "Playlist directory isn't a directory"

        # Extracts the names of the videos in the playlist
        yt_playlist_videos = [Video(v_url) for v_url in yt_playlist.video_urls]
        yt_video_downloaded = [join(expected_out_dir, entry) for entry in listdir(expected_out_dir)]

        # Checks that the number of videos in the playlist are in the same number as the file
        # inside the playlist folder. This is a sufficient approximation because some character
        # in the YouTube video are escaped/ignored in the filesystem.
        n_video_in_playlist = len(yt_playlist_videos)
        n_video_downloaded = len(yt_video_downloaded)
        assert n_video_in_playlist == n_video_downloaded, "Not all files have been downloaded"

        # Checks that the abovesaid directory contains a file for each video in the playlist
        for video_abspath in yt_video_downloaded:
            assert exists(video_abspath), "The expected output file doesn't exists"
            assert isfile(video_abspath), "The expected output file isn't a file"

    def test_overwrite_video(self):
        """Checks that already present files are overwritten when the 'overwrite' flag is provided"""
        # Creates a temporary direcotry in which the test case will be executed
        tmp_dir, video_url = TmpDir(), "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        expected_file_out = join(tmp_dir.name, f"{Video(video_url).title}.mp4")

        # Downloads the video for the first time
        download_video(video_url, out=tmp_dir.name, overwrite=False)
        assert exists(expected_file_out), "Expected file path non existent"
        assert isfile(expected_file_out), "Expected path not a file"
        m_time = getmtime(expected_file_out)  # Retrieve the modification timestamp

        # Tries to download again the video but this time should skip the download
        download_video(video_url, out=tmp_dir.name, overwrite=True)
        assert exists(expected_file_out), "Expected file path non existent"
        assert isfile(expected_file_out), "Expected path not a file"
        new_m_time = getmtime(expected_file_out)  # Get a new m_time measurement

        # Since the file shouldn't have been touched the m_time should be the same
        assert new_m_time != m_time, "File has been overwritten"

    def test_not_overwrite_video(self):
        """Checks that present files are not overwritten when the 'overwrite' flag is False"""
        # Creates a temporary direcotry in which the test case will be executed
        tmp_dir, video_url = TmpDir(), "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        expected_file_out = join(tmp_dir.name, f"{Video(video_url).title}.mp4")

        # Downloads the video for the first time
        download_video(video_url, out=tmp_dir.name, overwrite=False)
        assert exists(expected_file_out), "Expected file path non existent"
        assert isfile(expected_file_out), "Expected path not a file"
        m_time = getmtime(expected_file_out)  # Retrieve the modification timestamp

        # Tries to download again the video but this time should skip the download
        download_video(video_url, out=tmp_dir.name, overwrite=False)
        assert exists(expected_file_out), "Expected file path non existent"
        assert isfile(expected_file_out), "Expected path not a file"
        new_m_time = getmtime(expected_file_out)  # Get a new m_time measurement

        # Since the file shouldn't have been touched the m_time should be the same
        assert new_m_time == m_time, "File has been overwritten"
