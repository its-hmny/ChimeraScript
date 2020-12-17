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

    def test_concurrency(self):
        pool = __import__("concurrency").TaskPool()
        xxx = "Scp[e test"

        def hello():
            print("Hello from a thread with no params")

        def hello_params(str1, str2):
            for i in range(1000000):
                i = i - 1
                i = i * 1
                i = i + 1
            print(
                "Hello from a thread with params: {} {} {}".format(
                    str1, str2, xxx))

        dummy_funcv = [hello, hello_params, hello_params, hello]
        dummy_args = [{"str1": "Test1a", "str2": "Test1b"},
                      {"str1": "Test2a", "str2": "Test2b"}]

        pool.submit(hello)
        pool.submit_OneToMany(hello_params, *dummy_args)
        pool.submit_ManyToMany(dummy_funcv, [{}, *dummy_args, {}])

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
