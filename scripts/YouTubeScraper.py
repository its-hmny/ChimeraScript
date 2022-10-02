#! /usr/bin/env python3
"""
ChimeraScript - YouTubeScraper.py

This script allows to automate download of videos and whole playlists from YouTube.
The CLI presents two subcommands: "video" or "playlist" either to download a single video
or a list of videos from a public playlist.

Example:
    To download the YouTube Rewind 2018 video use::
        $ python3 YouTubeScraper.py video https://www.youtube.com/watch?v=YbJOTdZBX1g \
            ~/Videos

    To download this tutorial playlist use::
        $ python3 YouTubeScraper.py playlist \
            https://www.youtube.com/watch?v=RAwntanK4wQ&list=PLwgFb6VsUj_lQTpQKDtLXKXElQychT_2j \
            ~/Videos

Copyright 2022 Enea Guidi (hmny). All rights reserved.
This file are distributed under the General Public License v 3.0.
A copy of abovesaid license can be found in the LICENSE file.
"""
from datetime import datetime
from os import PathLike, mkdir
from os.path import basename, exists, isdir, join
from posixpath import abspath
from urllib.error import URLError

from fire import Fire
from pytube import Playlist
from pytube import YouTube as Video
from rich.console import Console

# Rich console instance for pretty printing on the terminal
console = Console(record=True)


def download_playlist(playlist_url: str, out: PathLike = ".", overwrite: bool = False):
    """
    Downloads a whole playlist given her YouTube URL. Eventually is possible to
    specify a resolution (default is 1080p). The downloaded files will all be saved
    in a folder in the "out" directory named as the playlist. Via the overwrite flag
    is possible to determine the behavior in case of existing files conflict: either
    the dest file can be overwritten or the download can be skipped.

    Args:
        playlist_url (str): The youTube URL for the given playlist
        out (PathLike): The relative or absolute destination folder
        overwrite (bool): Flag to overwrite the previously existent folder/file

    Raises:
        NotADirectoryError: The given path doesn't exist or isn't a directory
    """
    if not isdir(abspath(out)):
        raise NotADirectoryError(f"{abspath(out)} is not a directory")

    yt_playlist = Playlist(playlist_url)  # Gets a reference to the playlist object
    # The out folder will be named as the playlist and be inside "out" path
    out_folder = join(abspath(out), yt_playlist.title)

    # Creates the out folder if non already existent
    if not exists(out_folder):
        mkdir(out_folder)

    # The list/queue keep tracks of the video downloaded for the first time
    # as well as the ones that failed before (this is needed in order to
    # determine the behaviour of the 'download_video' function)
    pl_videos_urls = list([(v, False) for v in yt_playlist.video_urls])

    # Until the queue of video to download is not empty keeps going
    while len(pl_videos_urls) != 0:
        url2download, has_failed = pl_videos_urls.pop()

        try:
            download_video(url2download, out_folder, has_failed or overwrite)
            console.print(f"[green]Downloaded {url2download} successfully![/green]")
        # YouTube videos that fails to be downloaded are put back in the queue for later.
        # This choice has been made in order to avoid the user interaction whenever a download
        # fails based on minor network error (DNS Resolve, YouTube's Internal Server Errors, ...).
        except URLError:
            console.print(f"[red]Failed to download {url2download}, retrying later...[/red]")
            pl_videos_urls.append((url2download, True))


def download_video(video_url: str, out: PathLike = ".", overwrite: bool = False):
    """
    Downloads a whole video from YouTube given its URL. Eventually is possible to
    specify a resolution (default is 1080p). The downloaded file(s) will be saved in
    the "out" directory and named as the video. Via the overwrite flag is possible
    to determine the behavior in case of existing file conflict: either the dest file
    can be overwritten or the download can be skipped.

    Args:
        video_url (str): The youTube URL for the given video
        out (PathLike): The relative or absolute destination folder
        overwrite (bool): Flag to overwrite the previously existent folder/file

    Raises:
        NotADirectoryError: The given path doesn't exist or isn't a directory
        VideoUnavailable: The given URL points to a non existent/unavailable video
    """
    if not isdir(abspath(out)):
        raise NotADirectoryError(f"{abspath(out)} is not a directory")

    yt_video = Video(video_url)  # Gets a reference the the YouTube video object
    # Filters out the desired stream chosen by the user
    stream = yt_video.streams.get_highest_resolution()
    # And downloads it in the requested directory, eventually overwriting the previous
    stream.download(out, skip_existing=not overwrite)


if __name__ == "__main__":
    try:
        Fire({"playlist": download_playlist, "video": download_video})
    except KeyboardInterrupt:
        console.print("[yellow]Interrupt received, closing now...[/yellow]")
    except Exception:
        console.print("[red]An unexpected error occurred[/red]")
        console.print_exception()
    finally:
        script_name = basename(__file__)
        current_date = datetime.now().strftime("%d-%m-%Y %H:%M")
        console.save_html(f"logs/{script_name} {current_date}.html", clear=False)
        console.save_text(f"logs/{script_name} {current_date}.log", clear=False)
