import unittest
import json
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
        # Debug and print of dict and other data types
        file = open("./ExampleConfig.json")
        obj = json.loads(file.read())
        file.close()
        obj2 = list(obj)
        log.details(obj, obj2, "This is  string")
        log.debug(obj, obj2, "This is  string")
        # Test of documentation mechanism
        tmp = """
        GitPuller is a script that automates, the action of pulling changes of the projects I'm
        currently working on (mine as well as other's) keeping me always up to date with the origin/master.
        I tried to make it less verbose as possible but there will be some warnings and/or
        authentication request, especially for private repositories. Also it clones all the
        repositories that currently aren't in the projectDirectory folder as well as all your
        starred repositories that aren't already cloned.

        Note: that all the repositories are pulled so be aware of the risk (merge conflict and so on...).

        Created by Enea Guidi on 09/03/2020. Please check the README.md for more informations.
        """
        log.documentation("Documentation 1", tmp)
        file = open("./README.md")
        log.documentation("Documentation 2", file.read(), markdown=True)
        file.close()


if __name__ == '__main__':
    unittest.main()
