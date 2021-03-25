import unittest
import os


class TestStringMethods(unittest.TestCase):
    def test_compressor(self):
        print("Testing Compressor")
        dump = __import__('compressor').Compressor("test.zip", True)
        self.assertTrue(dump)
        dump.compressDir(".")
        dump.compressDir("chimera_utils", blacklist=["drive_fs.py"])
        dump.compressFile("./GitPuller.py")
        with self.assertRaises(NotADirectoryError):
            dump.compressDir("log.py")
        with self.assertRaises(FileNotFoundError):
            dump.compressFile("NonExistent.txt")
        with self.assertRaises(TypeError):
            dump << "This doesn't exist either"
        dump.compressFile("./PyHypervisor.py", "chimera_utils/")
        dump << "./EmptyDirRemover.py"
        self.assertEqual(dump.runChecks(), None)
        del dump
        self.assertFalse(os.path.isfile("test.zip"))

    def test_log(self):
        print("Testing Log")
        log = __import__('log').Log()
        log.error("This should be red")
        log.warning("This should be orange/yellow")
        log.success("This should be green")
        # Code checking
        self.assertEqual(log._successCode, "\033[92m")
        self.assertEqual(log._warningCode, "\033[93m")
        self.assertEqual(log._errorCode, "\033[91m")


if __name__ == '__main__':
    unittest.main()
