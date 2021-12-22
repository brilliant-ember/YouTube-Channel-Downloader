import sys
import os

cwd = os.getcwd()
# src_code_wd = os.path.split(cwd)[0]
# adding source code folder to the system path so I can import 
sys.path.insert(0, cwd)

from utils import Keys, read_json_file
import unittest
from unittest import mock
from unittest.mock import patch
import Scrapper

class TestDownloader(unittest.TestCase):
	def setUp(self) -> None:
		some_random_url = "https://www.youtube.com/c/greatscottlab"
		self.scrapper = Scrapper.ChannelScrapper(some_random_url, None, headless=False, debug_mode=True)
		return super().setUp()

	def test_get_playlist_info(self):
		'''Note that I put hard coded numbers for the number of videos, these numbers can
		change if the channel owner added or removed videos from the playlist'''
		# urls for different playlists
		playlist_with_hidden_videos = 'https://www.youtube.com/playlist?list=PL2BDEDA6CC782D568'
		playlist_with_membership_videos_and_scroll = 'https://www.youtube.com/playlist?list=PL0o_zxa4K1BWYThyV4T2Allw6zY0jEumv'
		all_videos_are_available_playlist_without_scroll = "https://www.youtube.com/playlist?list=PLTaK2N2T1t_fNmfuQpIig0GYJWgaiSZhu"

		url = all_videos_are_available_playlist_without_scroll
		json_dict = self.scrapper.get_playlist_info(url)
		print(json_dict[Keys.PLAYLIST_AVAILABLE_VIDEOS_NUMBER])
		assert type(json_dict) == dict, f"{url} didn't return a dictionary"
		assert bool(json_dict), f"{url} returned an empty dictionary"
		assert json_dict[Keys.PLAYLIST_AVAILABLE_VIDEOS_NUMBER] == 30 , f"{url} didn't extract all videos"
		assert json_dict[Keys.PLAYLIST_MEMBERS_ONLY_VIDEOS_NUMBER] == 0, f"{url} didn't correctly get all members only videos"


		url = playlist_with_membership_videos_and_scroll
		json_dict = self.scrapper.get_playlist_info(url)
		print(json_dict[Keys.PLAYLIST_AVAILABLE_VIDEOS_NUMBER])
		assert type(json_dict) == dict, f"{url} didn't return a dictionary"
		assert bool(json_dict), f"{url} returned an empty dictionary"
		assert json_dict[Keys.PLAYLIST_AVAILABLE_VIDEOS_NUMBER] == 284 , f"{url} didn't extract all videos"
		assert json_dict[Keys.PLAYLIST_MEMBERS_ONLY_VIDEOS_NUMBER] == 23, f"{url} didn't correctly get all members only videos"

		url = playlist_with_hidden_videos
		json_dict = self.scrapper.get_playlist_info(url)
		assert type(json_dict) == dict, f"{url} didn't return a dictionary"
		assert bool(json_dict), f"{url} returned an empty dictionary"
		assert json_dict[Keys.PLAYLIST_AVAILABLE_VIDEOS_NUMBER] == 16 , f"{url} didn't extract all videos"
		assert json_dict[Keys.PLAYLIST_MEMBERS_ONLY_VIDEOS_NUMBER] == 0, f"{url} didn't correctly get all members only videos"


if __name__ == '__main__':
	unittest.main()