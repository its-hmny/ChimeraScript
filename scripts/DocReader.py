"""
ChimeraScript - DocReader.py

This scripts allow extract text from pdf files and converting the content via Google's
Text To Speech API to an amp3 audio stream that can be either saved to a file or played/streamed
upon completion of the conversion. The CLI present two subcommands "export" and "stream".

Example:
    To save the output audio streams in a file, use::
        $ python3 DocReader.py export mock.pdf

    To play the audio as well with vlc , use::
        $ python3 DocReader.py stream mock.pdf player=vlc


Copyright 2022 Enea Guidi (hmny). All rights reserved.
This file are distributed under the General Public License v 3.0.
A copy of abovesaid license can be found in the LICENSE file.
"""
from datetime import datetime
from os import PathLike, getcwd, system
from os.path import abspath, basename, exists, isfile, join, splitext
from shutil import which
from tempfile import NamedTemporaryFile
from typing import Optional

from fire import Fire
from gtts import gTTS, gTTSError
from rich.console import Console
from textract import process as extract_text

# Rich console instance for pretty printing on the terminal
console = Console(record=True)


class FileTypeError(Exception):
    """
    Exception raised when the file provided by the user it's not a PDF.
    At the moment text extraction is always supported from pdf file but more may come in future
    """


class MissingPlayerError(Exception):
    """
    Exception raised when the user choses a player such as VLC, Rhythmbox, and others
    but the program couldn't find it for execution in the machine.
    """


def pdf_to_speech(pdf_path: PathLike) -> gTTS:
    """
    Convert the textual content of a pdf file to an audio mp3 stream via Google's
    Text To Speech API. Once the setup is completed returns the audio object.

    Args:
        pdf_path (Pathlike): The path to the pdf file to convert in speech

    Raises:
        FileNotFoundError: The given path doesn't exist or point to a directory
        FileTypeError: The given path doesn't points to a .pdf file
    """
    # Retrieves the absolute file and file extension for argument checking
    pdf_abspath = abspath(pdf_path)
    _, file_ext = splitext(pdf_abspath)

    if not exists(pdf_abspath) or not isfile(pdf_abspath):
        raise FileNotFoundError(f"The given path {pdf_path} is wrong or not a file")
    elif file_ext != ".pdf":
        raise FileTypeError("The given file is not a PDF")

    # Extracts the text content from the pdf file
    text_content = str(extract_text(pdf_abspath), "utf8")
    # Converts the text to audio stream with Google's Text to Speech API
    audio = gTTS(text=text_content, lang="en", slow=False)
    return audio


def export(pdf_path: PathLike, mp3_path: Optional[PathLike] = None) -> None:
    """
    Converts the given pdf file to audio and then subsequently saves the incoming audio
    streams in the desired output file (.mp3 audio)

    Args:
        pdf_path (Pathlike): The path to the pdf file to convert in audio
        mp3_path (Optional[Pathlike]): The output file path, optional arguments
    """
    # If an output path is not provided the file is saved in the current working
    # directory and named as the input file
    if mp3_path is None:
        filename, _ = splitext(basename(pdf_path))
        mp3_path = join(getcwd(), f"{filename}.mp3")

    try:
        # Converts the PDF content to audio/speech and writes it to the output file
        audio = pdf_to_speech(pdf_path)
        # Saving the converted audio in a mp3 file
        audio.save(abspath(mp3_path))
    except gTTSError:
        console.print("[yellow]Text to Speech conversion terminated by the server[/yellow]")


def stream(pdf_path: PathLike, player: str = "nvlc") -> None:
    """
    Converts the given pdf file to audio and then subsequently saves the incoming streams in
    a temporary file and once completed start reproducing it with the desired player.

    Args:
        pdf_path (Pathlike): The path to the pdf file to convert in audio
        player (str): The name of the program the user would like to play the audio

    Raises:
        MissingPlayerError: The desired player is not available or could not be found
    """
    # Initialize a temp file in which the mp3 content will be written
    tmp_file = NamedTemporaryFile("w", delete=True)

    try:
        # Writes the stream into the file as they come from gTTS
        audio = pdf_to_speech(pdf_path)
        audio.save(join("/tmp", tmp_file.name))
    except gTTSError:
        console.print("[yellow]Text to Speech conversion terminated by the server[/yellow]")

    if which(player) is None:
        raise MissingPlayerError(f"{player} is not installed or available on your machine")

    # Once completed, nvlc (the TUI version of VLC) is started, giving a user the audio
    # reproduction as well as a minimal UI to play, pause, skip and so on...
    system(f"{player} {join('/tmp', tmp_file.name)}")


if __name__ == "__main__":
    try:
        Fire({"stream": stream, "export": export})
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
