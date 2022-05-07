"""
ChimeraScript - YouTubeScraper.py

This script allows to automate download of videos and whole playlists from YouTube.
The CLI presents two subcommands: "video" or "playlist" either to download a single video
or a list of videos from a public playlist. Both commands allows the user to specify wether
to download captions as .srt (standard subtitle format) files.

Example:
    To download the YouTube Rewind 2018 video with captions use::
        $ python3 YouTubeScraper.py video https://www.youtube.com/watch?v=YbJOTdZBX1g \
            ~/Videos --captions

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

from fire import Fire
from pytube import Playlist
from pytube import YouTube as Video
from rich.console import Console

# Rich console instance for pretty printing on the terminal
console = Console(record=True)


def download_playlist(
    url: str, out: PathLike = ".", overwrite: bool = False, captions: bool = False
):
    """
    Downloads a whole playlist given her YouTube URL. Eventually is possible to
    specify a resolution (default is 1080p) and enable download of captions as .srt file.
    The downloaded files will all be saved in a folder in the "out" directory named
    as the playlist. Via the overwrite flag is possible to determine the behavior in case of
    existing files conflict: either the dest file can be overwritten or the download can be skipped.

    Args:
        url (str): The youTube URL for the given playlist
        out (PathLike): The relative or absolute destination folder
        overwrite (bool): Flag to overwrite the previously existent folder/file
        captions (bool): Flag to download captions as .srt files

    Raises:
        NotADirectoryError: The given path doesn't exist or isn't a directory
    """
    if not isdir(abspath(out)):
        raise NotADirectoryError(f"{abspath(out)} is not a directory")

    yt_playlist = Playlist(url)  # Gets a reference to the playlist object
    # The out folder will be named as the playlist and be inside "out" path
    out_folder = join(abspath(out), yt_playlist.title)

    # Creates the out folder if non already existent
    if not exists(out_folder):
        mkdir(out_folder)

    # For each video in the playlist starts a download with the requested params
    for url in yt_playlist.video_urls:
        download_video(url, out_folder, overwrite, captions)


def download_video(url: str, out: PathLike = ".", overwrite: bool = False, captions: bool = False):
    """
    Downloads a whole video from YouTube given its URL. Eventually is possible to
    specify a resolution (default is 1080p) and enable download of captions as .srt file.
    The downloaded file(s) will be saved in the "out" directory and named as the video.
    Via the overwrite flag is possible to determine the behavior in case of existing file conflict:
    either the dest file can be overwritten or the download can be skipped.

    Args:
        url (str): The youTube URL for the given video
        out (PathLike): The relative or absolute destination folder
        overwrite (bool): Flag to overwrite the previously existent folder/file
        captions (bool): Flag to download captions as .srt files

    Raises:
        NotADirectoryError: The given path doesn't exist or isn't a directory
        VideoUnavailable: The given URL points to a non existent/unavailable video
    """
    if not isdir(abspath(out)):
        raise NotADirectoryError(f"{abspath(out)} is not a directory")

    yt_video = Video(url)  # Gets a reference the the YouTube video object
    # Filters out the desired stream chosen by the user
    stream = yt_video.streams.get_highest_resolution()
    # And downloads it in the requested directory, eventually overwriting the previous
    stream.download(out, skip_existing=not overwrite)

    # If the user wants the captions/subtitles to be downloaded as well
    if captions and len(yt_video.captions):
        # Checks both for english subtitles (priority) and eventually settles for autogenerated
        for candidate in ["en", "a.en"]:
            # If the candidate isn't available for the current video skips the iteration
            if yt_video.captions.get(candidate) is None:
                continue

            try:
                # Else tries to download the better suited candidate as .srt file
                subtitles = yt_video.captions.get(candidate).generate_srt_captions()
                export_path = join(abspath(out), f"{yt_video.title}.srt")
                open(export_path, "w", encoding="UTF-8").write(subtitles).close()
            except KeyError:
                console.print(f"[bold red]Error while downloading captions for '{yt_video.title}'")


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
