""" TODO Add pydoc annotation """
from datetime import datetime
from io import BytesIO
from os import PathLike, system
from os.path import abspath, basename, exists, isfile, join, splitext
from shutil import which
from tempfile import NamedTemporaryFile

from fire import Fire
from gtts import gTTS, gTTSError
from rich.console import Console
from textract import process as extract_text

# Rich console instance for pretty printing on the terminal
console = Console(record=True)


class FileTypeError(Exception):
    """ TODO add pydoc annotations """


class MissingPlayerError(Exception):
    """ TODO add pydoc annotations """


def pdf_to_speech(pdf_path: PathLike) -> gTTS:
    """ TODO Add comments """
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


def export(pdf_path: PathLike, mp3_path: PathLike = "./out.mp3") -> None:
    """ TODO Add pydoc annotation """
    try:
        # Converts the PDF content to audio/speech and writes it to the output file
        audio = pdf_to_speech(pdf_path)
        # Saving the converted audio in a mp3 file
        audio.save(abspath(mp3_path))
    except gTTSError:
        console.print("[yellow]Text to Speech conversion terminated by the server[/yellow]")


def stream(pdf_path: PathLike) -> None:
    """ TODO Add pydoc annotation """
    # Initialize a temp file in which the mp3 content will be written
    tmp_file = NamedTemporaryFile("w", delete=True)

    try:
        # Writes the stream into the file as they come from gTTS
        audio = pdf_to_speech(pdf_path)
        audio.save(join("/tmp", tmp_file.name))
    except gTTSError:
        console.print("[yellow]Text to Speech conversion terminated by the server[/yellow]")

    if which("nvlc") is None:
        raise MissingPlayerError("nvlc is not installed or available on your machine")

    # Once completed, nvlc (the TUI version of VLC) is started, giving a user the audio
    # reproduction as well as a minimal UI to play, pause, skip and so on...
    system(f"nvlc {join('/tmp', tmp_file.name)}")


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
