import sys
import os

cwd = os.getcwd()
# src_code_wd = os.path.split(cwd)[0]
# adding source code folder to the system path so I can import 
sys.path.insert(0, cwd)

import utils
import unittest
from unittest import mock
from unittest.mock import patch

class TestDownloader(unittest.TestCase):
	def setUp(self) -> None:
		return super().setUp()

	def test_generate_playlist_url(self):
		playlist_url = utils.generate_playlist_url("PLGhvWnPsCr59gKqzqmUQrSNwl484NPvQY")
		expected = "https://www.youtube.com/playlist?list=PLGhvWnPsCr59gKqzqmUQrSNwl484NPvQY"
		assert playlist_url == expected, "wrong playlist url"


	def test_generate_video_url(self):
		url = utils.generate_video_url("e3LqeN0e0as")
		expected = "https://www.youtube.com/watch?v=e3LqeN0e0as"

		assert url == expected, "wrong video url"


if __name__ == '__main__':
    unittest.main()