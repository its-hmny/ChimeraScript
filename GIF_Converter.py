"""
GIF_Converter is a simple script to convert a .mp4 or .mkv file to a .gif file,
more extension type to convert coming soon...

Note: In order to work it relies on imageio as third party library,
you can install with "pip3 install imageio" from command line

Created by Enea Guidi on 31/08/2019, please check the Readme.md for more information.
"""

import os
import sys
import imageio
from chimera_utils import Log, exception_handler

log = Log()
supported_file_type = [".mp4", ".mkv"]


def video_to_Gif(input: str, output: str) -> None:
    gif_fps = 24
    reader = imageio.get_reader(input)
    writer = imageio.get_writer(output, fps=gif_fps)

    for i, frame in enumerate(reader):
        if i % gif_fps == 0:
            writer.append_data(frame)

    writer.close()
    reader.close()

@exception_handler
def GIF_Converter() -> None:
    # At least one file must be provided
    if len(sys.argv) < 2:
        log.error("Need the path to file")
        sys.exit(-1)

    for arg in sys.argv[1:]:
        file_path = os.path.abspath(arg)
        file_name, file_ext = os.path.splitext(file_path)
        log.warning(f"Converting {arg}....")

        if file_ext in supported_file_type:
            out_file = file_name + ".gif"
            video_to_Gif(file_path, out_file)
            log.success("Done!")
        else:
            log.error("Unsupported file type")


if __name__ == "__main__":
    GIF_Converter()
