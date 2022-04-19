"""
TODO Add pydoc annotation

https://towardsdatascience.com/the-easiest-way-to-download-youtube-videos-using-python-2640958318ab
https://www.the-analytics.club/download-youtube-videos-in-python/
https://typer.tiangolo.com/
"""
from datetime import datetime
from os.path import basename, isdir, join
from posixpath import abspath
from typing import Literal

from fire import Fire
from pytube import Playlist, YouTube as Video
from rich.console import Console

# Type alias for available resolution in YouTube
Resolution = Literal["360p", "720p", "1080p", "2K", "4K", "8K"]

# Rich console instance for pretty printing on the terminal
console = Console(record=True)


def download_playlist(url: str, out: str = ".", res: Resolution = "1080p", captions: bool = False):
    """
    TODO Add pydoc annotation
    """
    if not isdir(abspath(out)):
        console.log(f"{abspath(out)} is not a directory")
        return

    yt_playlist = Playlist(url)  # Gets a reference to the playlist object
    # The out folder will be named as the playlist and be inside "out" path
    out_folder = join(abspath(out), yt_playlist.name)

    # Creates the out folder if non already existent
    if not exists(out_folder):
        mkdir(out_folder, mode=0o666)

    # For each video in the playlist starts a download with the requested params
    for item in yt_playlist.videos:
        download_video(item.url, out_folder, res, captions)


def download_video(url: str, out: str = ".", res: Resolution = "1080p", captions: bool = False):
    """
    TODO Add pydoc annotation
    """
    if not isdir(abspath(out)):
        console.log(f"{abspath(out)} is not a directory")
        return

    yt_video = Video(url)  # get a reference the the YouTube video object
    # Filters out the desired stream chosen by the user
    stream, *_ = yt_video.streams.filter(res=res, file_extension='mp4')
    # And downloads it in the requested directory, eventually overwriting the previous
    stream.download(out, skip_existing=False)

    # If the user wants the captions/subtitles as well and they're available then downloads as .srt
    if captions and yt_video.captions.get("en") is not None:
        subtitles = yt_video.captions.get("en").generate_srt_captions()
        export_path = join(abspath(out), f"{yt_video.title}.srt")
        open(export_path, "w", encoding="UTF-8").write(subtitles).close()


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
        current_date = datetime.now().strftime('%d-%m-%Y %H:%M')
        console.save_html(f"logs/{script_name} {current_date}.html", clear=False)
        console.save_text(f"logs/{script_name} {current_date}.log", clear=False)
