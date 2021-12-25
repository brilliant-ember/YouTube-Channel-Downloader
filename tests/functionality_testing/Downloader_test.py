import sys
import os

cwd = os.getcwd()
# src_code_wd = os.path.split(cwd)[0]
# adding source code folder to the system path so I can import 
sys.path.insert(0, cwd)

from utils import Keys, read_json_file
import unittest
from Downloader import Downloader
from unittest import mock
from unittest.mock import patch

class TestDownloader(unittest.TestCase):
	def setUp(self) -> None:
		self.response_utils = Response_Utils()
		return super().setUp()


    def test_get_all_uploads_playlist_data():
        channel_url = "https://www.youtube.com/user/FireSymphoney"

        browser_wait = 3
        d = Downloader(channel_url ,browser_wait=browser_wait, headless=False)
        # d.download_all_videos_from_channel()
        d.get_all_uploads_playlist_data()


    def test_download_all_videos_from_channel():
        channel_url = "https://www.youtube.com/user/FireSymphoney"

        browser_wait = 3
        d = Downloader(channel_url ,browser_wait=browser_wait, headless=False)
        d.download_all_videos_from_channel()

if __name__ == '__main__':
	unittest.main()