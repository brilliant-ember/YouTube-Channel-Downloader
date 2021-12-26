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
from Logger import Log

class TestDownloader(unittest.TestCase):
	def setUp(self) -> None:
		some_random_url = "https://www.youtube.com/c/greatscottlab"
		log_file_path = os.path.join(cwd, "logfile.txt")
		logger = Log(log_file_path)
		self.scrapper = Scrapper.ChannelScrapper(some_random_url, logger, headless=False, test_mode=True)
		return super().setUp()

	def tearDown(self) -> None:
		self.scrapper.__del__()
		return super().tearDown()

	def test_get_playlist_info(self):
		'''Note that I put hard coded numbers for the number of videos, these numbers can
		change if the channel owner added or removed videos from the playlist'''
		# urls for different playlists
		playlist_with_hidden_videos = 'https://www.youtube.com/playlist?list=PL2BDEDA6CC782D568'
		playlist_with_membership_videos_and_scroll = 'https://www.youtube.com/playlist?list=PL0o_zxa4K1BWYThyV4T2Allw6zY0jEumv'
		all_videos_are_available_playlist_without_scroll = "https://www.youtube.com/playlist?list=PLTaK2N2T1t_fNmfuQpIig0GYJWgaiSZhu"

		url = all_videos_are_available_playlist_without_scroll
		json_dict = self.scrapper.get_playlist_info(url)
		assert type(json_dict) == dict, f"{url} didn't return a dictionary"
		assert bool(json_dict), f"{url} returned an empty dictionary"
		assert json_dict[Keys.PLAYLIST_AVAILABLE_VIDEOS_NUMBER] == 30 , f"{url} didn't extract all videos, expected 30 but found {json_dict[Keys.PLAYLIST_AVAILABLE_VIDEOS_NUMBER]}"
		assert json_dict[Keys.PLAYLIST_MEMBERS_ONLY_VIDEOS_NUMBER] == 0, f"{url} didn't correctly get all members only videos"


		url = playlist_with_membership_videos_and_scroll
		json_dict = self.scrapper.get_playlist_info(url)
		assert type(json_dict) == dict, f"{url} didn't return a dictionary"
		assert bool(json_dict), f"{url} returned an empty dictionary"
		assert json_dict[Keys.PLAYLIST_AVAILABLE_VIDEOS_NUMBER] == 284 , f"{url} didn't extract all videos, expected 284 but found {json_dict[Keys.PLAYLIST_AVAILABLE_VIDEOS_NUMBER]}"
		assert json_dict[Keys.PLAYLIST_MEMBERS_ONLY_VIDEOS_NUMBER] == 23, f"{url} didn't correctly get all members only videos"

		url = playlist_with_hidden_videos
		json_dict = self.scrapper.get_playlist_info(url)
		assert type(json_dict) == dict, f"{url} didn't return a dictionary"
		assert bool(json_dict), f"{url} returned an empty dictionary"
		assert json_dict[Keys.PLAYLIST_AVAILABLE_VIDEOS_NUMBER] == 16 , f"{url} didn't extract all videos, expected 16 but found {json_dict[Keys.PLAYLIST_AVAILABLE_VIDEOS_NUMBER]}"
		assert json_dict[Keys.PLAYLIST_MEMBERS_ONLY_VIDEOS_NUMBER] == 0, f"{url} didn't correctly get all members only videos"


	# def test_get_all_channel_playlists_info(self):
		playlists_only_default_view_no_scroll = "https://www.youtube.com/c/3thestorm/playlists"
		playlist_wrong_view_with_scroll = "https://www.youtube.com/c/MegwinTVOfficial/playlists"
		playlist_correct_view_with_scroll = "https://www.youtube.com/c/learnelectronics/playlists?view=1"
		extra_with_scroll = 'https://www.youtube.com/c/CrunchyrollCollection/playlists'

		url = playlists_only_default_view_no_scroll
		created_playlists = self.scrapper.get_all_channel_playlists_info(url)
		num_playlists = len(created_playlists.keys())
		assert num_playlists == 3, f"found {num_playlists} should have been 3,didn't get correct number of playlists for f {url}"

		url = playlist_correct_view_with_scroll
		created_playlists = self.scrapper.get_all_channel_playlists_info(url)
		num_playlists = len(created_playlists.keys())
		assert num_playlists == 40, f"found {num_playlists} should have been 40, didn't get correct number of playlists for f {url}"

		url = extra_with_scroll
		created_playlists = self.scrapper.get_all_channel_playlists_info(url)
		num_playlists = len(created_playlists.keys())
		assert num_playlists == 213, f"found {num_playlists} should have been 213, didn't get correct number of playlists for f {url}"

		url = playlist_wrong_view_with_scroll
		created_playlists = self.scrapper.get_all_channel_playlists_info(url)
		num_playlists = len(created_playlists.keys())
		assert num_playlists == 241,f"found {num_playlists} should have been 241, didn't get correct number of playlists for f {url}"


	def test_get_all_uploads_info_for_channel(self):
		with_scroll = 'https://www.youtube.com/c/3thestorm/videos'
		expected_with_scroll = 52 

		no_scroll = 'https://www.youtube.com/user/FireSymphoney/videos'
		expected_no_scroll = 12

		lot_of_scrolling = 'https://www.youtube.com/c/EevblogDave/videos'
		expected_scroll_lot = 1755

		url = with_scroll
		json_dict = self.scrapper.get_all_uploads_info_for_channel(url)
		num = len(list(json_dict.keys()))
		assert num == expected_with_scroll, f'expected {expected_with_scroll} videos, but got {num} for {url}'

		url = no_scroll
		json_dict = self.scrapper.get_all_uploads_info_for_channel(url)
		num = len(list(json_dict.keys()))
		assert num == expected_no_scroll, f'expected {expected_no_scroll} videos, but got {num} for {url}'

		url = lot_of_scrolling
		json_dict = self.scrapper.get_all_uploads_info_for_channel(url)
		num = len(list(json_dict.keys()))
		assert num == expected_scroll_lot, f'expected {expected_scroll_lot} videos, but got {num} for {url}'
		

	def test_scrape_for_playlists(self):
		pass

if __name__ == '__main__':
	unittest.main()