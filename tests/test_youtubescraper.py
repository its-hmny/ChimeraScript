"""PyTest module with test suite implementation for the YouTubeScraper.py script"""
from os import getcwd, listdir
from os.path import isfile, join
from tempfile import NamedTemporaryFile as TmpFile
from tempfile import TemporaryDirectory as TmpDir

from genericpath import exists, isdir
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

    def test_correct_video_download(self):
        """Gives correct arguments to download_video and expects correct output"""
        # The "out" path and the YouTube video exist and are correct
        tmp_dir, video_url = TmpDir(), "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        # Tries to download the YT video
        download_video(video_url, out=tmp_dir.name)

        # Checks that the path hasn't been created by the script
        expected_file_path = join(tmp_dir.name, Video(video_url).name)
        assert exists(expected_file_path), "The expected output file doesn't exists"
        assert isfile(expected_file_path), "The expected output file isn't a file"

    def test_correct_playlist_download(self):
        """Gives correct arguments to download_video and expects correct output"""
        # The "out" path and the YouTube playlist exist and are correct
        tmp_dir = TmpDir()
        playlist_url = "https://www.youtube.com/watch?v=TazHNpt6OTo&list=PLEijU2q67K_twQnJ06-3DnrvsAdEii_MQ"

        # Tries to download the YT playlist (all the videos present in it)
        download_playlist(playlist_url, out=tmp_dir.name)

        # Retrieves the playlist name and determines the path
        yt_playlist = Playlist(playlist_url)
        expected_out_dir = join(tmp_dir.name, yt_playlist.name)
        # Checks that the script has created a sdirectory named as the playlist
        assert exists(expected_out_dir), "Playlist directory hasn't been created"
        assert isdir(expected_out_dir), "Playlist directory isn't a directory"

        # Extracts the names of the videos in the playlist
        yt_playlist_videos = [Video(v_url).name for v_url in yt_playlist.video_urls]
        # Checks that the abovesaid directory contains a file for each video in the playlist
        for video in yt_playlist_videos:
            expected_out_file = join(expected_out_dir, video.name)
            assert exists(expected_out_file), "The expected output file doesn't exists"
            assert isfile(expected_out_file), "The expected output file isn't a file"

    def test_captions_flag(self):
        """
        Checks that the captions are downloaded and saved, when the flag is provided by the user.
        Since download_playlist internally uses download_video both method are (indirectly) tested.
        """
        # The "out" path and the YouTube playlist exist and are correct
        tmp_dir = TmpDir()
        playlist_url = "https://www.youtube.com/watch?v=TazHNpt6OTo&list=PLEijU2q67K_twQnJ06-3DnrvsAdEii_MQ"

        # Tries to download the YT playlist (all the videos present in it)
        download_playlist(playlist_url, out=tmp_dir.name)

        # Retrieves the playlist name and determines the path
        yt_playlist = Playlist(playlist_url)
        expected_out_dir = join(tmp_dir.name, yt_playlist.name)
        # Checks that the script has created a sdirectory named as the playlist
        assert exists(expected_out_dir), "Playlist directory hasn't been created"
        assert isdir(expected_out_dir), "Playlist directory isn't a directory"

        # Extracts the names of the videos in the playlist
        yt_playlist_videos = [Video(v_url).name for v_url in yt_playlist.video_urls]
        # Checks that the directory contains both an mp4 & srt file for each video in the playlist
        for video in yt_playlist_videos:
            # Checks that mp4 video file exist
            expected_video_path = join(expected_out_dir, f"{video.name}.mp4")
            assert exists(expected_video_path), "The expected output file doesn't exists"
            assert isfile(expected_video_path), "The expected output file isn't a file"
            # Checks that the captions/subtitle have been cloned as well
            expected_cc_path = join(expected_out_dir, f"{video.name}.srt")
            assert exists(expected_cc_path), "The expected output file doesn't exists"
            assert isfile(expected_cc_path), "The expected output file isn't a file"

    def test_resolution_arg(self):
        """
        Checks that the desired resolution is downloaded when provided by the user.
        Since download_playlist internally uses download_video both method are (indirectly) tested.
        """
        assert False, "Test not implemented"
