"""PyTest module with test suite implementation for the GitPuller.py script"""
from os.path import exists, isdir, isfile, join
from posixpath import basename
from random import random
from tempfile import NamedTemporaryFile as TmpFile
from tempfile import TemporaryDirectory as TmpDir

from pytest import raises
from requests import get
from scripts.DocReader import FileTypeError, MissingPlayerError, export, stream


class TestDocReader:
    """Test suite for the Gitpuller script"""
    def test_non_existent_pdf_path(self):
        """Gives a non existent pdf path to both 'export' and 'stream'"""
        # Generates a random non existent path to a pdf file
        non_existent_path = join("/tmp", f"{str(random())}.pdf")

        # Tests that "export" blocks the execution instead of continuing
        with raises(FileNotFoundError):
            export(non_existent_path)
        assert not exists(non_existent_path), "(export): Non existent pdf path has been created"
        assert not isfile(non_existent_path), "(export): Non existent pdf path is a file"

        # Tests that "stream" blocks the execution instead of continuing
        with raises(FileNotFoundError):
            stream(non_existent_path)
        assert not exists(non_existent_path), "(stream): Non existent pdf path has been created"
        assert not isfile(non_existent_path), "(stream): Non existent pdf path is a file"

    def test_dir_path(self):
        """Gives a directory path to both 'export' and 'stream'"""
        # Creates a temporary directory to be passed as input arg
        tmp_dir = TmpDir()

        # Tests that "export" blocks the execution instead of continuing
        with raises(FileNotFoundError):
            export(tmp_dir.name)
        assert isdir(tmp_dir.name), "(export): Input directory has been removed"
        assert not isfile(tmp_dir.name), "(export): Directory has been overwritten to file"

        # Tests that "stream" blocks the execution instead of continuing
        with raises(FileNotFoundError):
            export(tmp_dir.name)
        assert isdir(tmp_dir.name), "(export): Input directory has been removed"
        assert not isfile(tmp_dir.name), "(export): Directory has been overwritten to file"

    def test_not_a_pdf_file(self):
        """Gives a existent filepath to both 'export' and 'stream' but is not a pdf"""
        # Creates a temporary directory to be passed as input arg
        tmp_mp3, tmp_file = TmpFile(suffix=".mp3"), TmpFile()

        # Tests that "export" blocks the execution for both mp3 and other file
        with raises(FileTypeError):
            export(tmp_mp3.name)
        with raises(FileTypeError):
            export(tmp_file.name)

        # Checks that strange side effect hasn't happened during "export" execution
        assert isfile(tmp_mp3.name), "(export): MP3 file has been deleted"
        assert isfile(tmp_file.name), "(export): Tmp file without extension has been deleted"

        # Tests that "stream" blocks the execution for both mp3 and other file
        with raises(FileTypeError):
            stream(tmp_mp3.name)
        with raises(FileTypeError):
            stream(tmp_file.name)

        # Checks that strange side effect hasn't happened during "stream" execution
        assert isfile(tmp_mp3.name), "(stream): MP3 file has been deleted"
        assert isfile(tmp_file.name), "(stream): Tmp file without extension has been deleted"

    def test_correct_file(self):
        """Gives a correct path to a pdf file and checks that an audio file is produced"""
        # Create the temporary input file and populates it with content from an online mock pdf
        tmp_pdf_file = TmpFile("bw", suffix=".pdf")
        tmp_pdf_file.write(get("https://www.orimi.com/pdf-test.pdf").content)
        # Initializes an output file to which write the output of the Text To Speech
        tmp_mp3_file = TmpFile(suffix=".mp3")

        # Test the export function with the mock pdf
        export(tmp_pdf_file.name, mp3_path=tmp_mp3_file.name)

        # Test that the output file exist and is an mp3 format
        assert exists(tmp_mp3_file.name), "(export): MP3 file output doesn't exist"
        assert isfile(tmp_mp3_file.name), "(export): MP3 file output isn't a file"

    def test_wrong_out_path(self):
        """Gives a correct path to a pdf file but mp3_path is a directory"""
        # Create the temporary input file and populates it with content from an online mock pdf
        tmp_pdf_file = TmpFile("bw", suffix=".pdf")
        tmp_pdf_file.write(get("https://www.orimi.com/pdf-test.pdf").content)
        # Initializes a temporary directory to be used as output path
        tmp_dir = TmpDir()

        # Test the export function with the mock pdf
        export(tmp_pdf_file.name, mp3_path=tmp_dir.name)

        # Test that the output directory hasn't been changed
        assert exists(tmp_dir.name), "(export): The given directory has been deleted"
        assert isdir(tmp_dir.name), "(export): The given directory isn't a directory anymore"

        # Test that the file with same name as the input but .mp3 format has been created
        expected_file_name = basename(tmp_pdf_file.name).replace('.pdf', '.mp3')
        expected_out_path = join(tmp_dir.name, expected_file_name)
        assert exists(expected_out_path), "(export): No output file found"
        assert isfile(expected_out_path), "(export): No output file isn't a file"

    def test_wrong_audio_player(self):
        """Tests the stream option with non existent player"""
        # Create the temporary input file and populates it with content from an online mock pdf
        tmp_pdf_file = TmpFile("bw", suffix=".pdf")
        tmp_pdf_file.write(get("https://www.orimi.com/pdf-test.pdf").content)

        # Test the export function with the mock pdf
        with raises(MissingPlayerError):
            stream(tmp_pdf_file.name, player="rhythmbox")

    def test_audio_player(self):
        """Tests the stream option with an existent audio player"""
        # Create the temporary input file and populates it with content from an online mock pdf
        tmp_pdf_file = TmpFile("bw", suffix=".pdf")
        tmp_pdf_file.write(get("https://www.orimi.com/pdf-test.pdf").content)

        # Test the export function with the mock pdf, this tests as well flag forwarding
        #  because if the flag isn't forwarded correctly the player will never close itself
        # upon completion (the default behavior is to remain open) and in this case the
        # suite will never complete
        stream(tmp_pdf_file.name, player="nvlc", player_flags="--play-and-exit")
