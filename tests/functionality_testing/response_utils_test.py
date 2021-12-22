import sys
import os

cwd = os.getcwd()
# src_code_wd = os.path.split(cwd)[0]
# adding source code folder to the system path so I can import 
sys.path.insert(0, cwd)

from utils import Keys, read_json_file
import unittest
from response_utils import Response_Utils
from unittest import mock
from unittest.mock import patch

class TestDownloader(unittest.TestCase):
	def setUp(self) -> None:
		self.response_utils = Response_Utils()
		return super().setUp()


	def test_get_playlists_listing(self):
		'''the numbers are hardcoded for now and could change in the future if channel owners added or removed a playlist'''
		no_horizontal_scroll = 'https://www.youtube.com/c/greatscottlab/playlists?view=1'
		with_horizontal_scroll = 'https://www.youtube.com/c/learnelectronics/playlists?view=1'
		
		no_horizontal_scroll_needs_down_scroll = "https://www.youtube.com/c/CrunchyrollCollection/playlists?view=1"
		with_horizontal_scroll_needs_down_scroll = 'https://www.youtube.com/user/AnimeBancho/playlists?view=1'

		with_horizontal_scroll_needs_down_scroll_2 = "https://www.youtube.com/c/MegwinTVOfficial/playlists?view=1"

		playlists = self.response_utils.get_playlists_listing(no_horizontal_scroll)
		assert len(playlists) == 9, "Didn't get all the playlists for a channel playlists url without horizontal scroll"

		breakpoint()



		playlists = self.response_utils.get_playlists_listing(with_horizontal_scroll)
		assert len(playlists) == 40, "Didn't get all the playlists of a channel with horizontal scroll at its playlists url"

		
		breakpoint()


if __name__ == '__main__':
	unittest.main()