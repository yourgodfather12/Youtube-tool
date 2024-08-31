import unittest
from src import utils
import os

class TestUtils(unittest.TestCase):
    def test_ensure_dir(self):
        utils.ensure_dir("test_dir")
        self.assertTrue(os.path.exists("test_dir"))

    def test_get_file_extension(self):
        ext = utils.get_file_extension("video.mp4")
        self.assertEqual(ext, ".mp4")

    def test_save_and_load_json(self):
        test_data = {"key": "value"}
        utils.save_json(test_data, "test_data.json")
        loaded_data = utils.load_json("test_data.json")
        self.assertEqual(test_data, loaded_data)

    def test_save_and_load_yaml(self):
        test_data = {"key": "value"}
        utils.save_yaml(test_data, "test_data.yaml")
        loaded_data = utils.load_yaml("test_data.yaml")
        self.assertEqual(test_data, loaded_data)
