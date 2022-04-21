""" TODO Add pydoc annotation """
from datetime import datetime
from io import BytesIO
from os import PathLike
from os.path import abspath, basename, exists, isfile

from fire import Fire
from gtts import gTTS
from rich.console import Console

# Rich console instance for pretty printing on the terminal
console = Console(record=True)


def pdf_to_speech(pdf_path: PathLike) -> gTTS:
    """ TODO Add comments """
    pdf_abspath = abspath(pdf_path)

    if not exists(pdf_abspath) or not isfile(pdf_abspath):
        raise FileNotFoundError(f"The given path {pdf_path} is wrong or not a file")

    # TODO Read the PDF content as string

    # Passing the text and language to the engine,  here we have marked slow=False.
    # Which tells the module that the converted audio should have a high speed
    audio = gTTS(text="Hey you! Yeah you!! Fuck off mate!", lang="en", slow=False)
    # Saving the converted audio in a mp3 file named welcome
    return audio


def export(pdf_path: PathLike, mp3_path: PathLike = "./out.mp3") -> None:
    """ TODO Add pydoc annotation """
    # Converts the PDF content to audio/speech and writes it to the output file
    audio = pdf_to_speech(pdf_path)
    audio.save(abspath(mp3_path))

    console.print(f"[bold green]'{mp3_path}' exported successfully![/bold green]")


def stream(pdf_path: PathLike) -> None:
    """ TODO Add pydoc annotation """
    # Creates a memory buffer in which the audio data will be saved
    mp3_buffer = BytesIO()

    # Converts the PDF content to audio/speech and clones it onto the buffer
    audio = pdf_to_speech(pdf_path)
    audio.write_to_fp(mp3_buffer)

    # Now that the buffer has been populated stream/reproduce it
    console.print("[bold green]Starting reproduction just now[/bold green]")


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
