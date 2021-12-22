import sys
import os

cwd = os.getcwd()
# src_code_wd = os.path.split(cwd)[0]
# adding source code folder to the system path so I can import 
sys.path.insert(0, cwd)

from Playlist import Playlist
from utils import Keys
import unittest
from unittest import mock
from unittest.mock import patch
from utils import read_json_file

class TestDownloader(unittest.TestCase):
	def setUp(self) -> None:
		return super().setUp()

	def test_extract_playlist_info_from_json_payload(self):

		initial_get_req_on_playlist = read_json_file(cwd + "/tests/fixtures/playlist_scroll_requests/get_response_playlist=id")
		playlist_handler = Playlist()
		keep_scrolling = playlist_handler.extract_playlist_info_from_json_payload(initial_get_req_on_playlist)
		json_dict = playlist_handler.get_playlist_info_as_dict()

		assert keep_scrolling, "didn't detect that it should scroll down"
		assert type(json_dict) == dict, f"didn't return a dictionary"
		assert bool(json_dict), f"returned an empty dictionary"
		assert json_dict[Keys.PLAYLIST_AVAILABLE_VIDEOS_NUMBER] == 86 , "didn't extract all videos"
		assert json_dict[Keys.PLAYLIST_MEMBERS_ONLY_VIDEOS_NUMBER] == 14, "didn't correctly get all members only videos"

if __name__ == '__main__':
	unittest.main()