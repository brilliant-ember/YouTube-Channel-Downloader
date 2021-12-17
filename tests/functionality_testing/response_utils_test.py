import sys
import os

cwd = os.getcwd()
# src_code_wd = os.path.split(cwd)[0]
# adding source code folder to the system path so I can import 
sys.path.insert(0, cwd)

from utils import NUMBERVIDEOSKEY, read_json_file
import unittest
from response_utils import Response_Utils
from unittest import mock
from unittest.mock import patch

class TestDownloader(unittest.TestCase):
	def setUp(self) -> None:
		self.response_utils = Response_Utils()
		return super().setUp()


	def test_get_playlists_listing(self):
		no_horizontal_scroll = 'https://www.youtube.com/c/greatscottlab/playlists'
		with_horizontal_scroll = 'https://www.youtube.com/c/learnelectronics/playlists'

		# j = perform_get_request_text(u)
		pass

	def test_get_playlist_info(self):
		playlists = {
		"playlist_with_private_videos":'https://www.youtube.com/playlist?list=PL2BDEDA6CC782D568',
		"playlist_with_membership_videos_and_scroll":'https://www.youtube.com/playlist?list=PL0o_zxa4K1BWYThyV4T2Allw6zY0jEumv',
		"all_videos_are_available_playlist_without_scroll" : "https://www.youtube.com/playlist?list=PLTaK2N2T1t_fNmfuQpIig0GYJWgaiSZhu"
		}

		for key, value in playlists.items():
			url = value

			json_dict = self.response_utils.get_playlist_info(url)
			assert type(json_dict) == dict, f"{key} didnt return a dictionary"
			assert bool(json_dict), f"{key} returned an empty dictionary"

if __name__ == '__main__':
	unittest.main()