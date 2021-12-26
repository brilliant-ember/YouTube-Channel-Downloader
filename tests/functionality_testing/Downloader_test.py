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
import shutil

class TestDownloader(unittest.TestCase):
	def setUp(self) -> None:
		self.test_dir = os.path.join(cwd ,"tests", "tmp")
		os.makedirs(self.test_dir)
		return super().setUp()

	def tearDown(self):
		shutil.rmtree(self.test_dir)
		return super().tearDown()
		
	def test_get_all_uploads_playlist_data(self):
		channel_url = "https://www.youtube.com/user/FireSymphoney"
		browser_wait = 3
		d = Downloader(channel_url ,browser_wait=browser_wait, headless=False, root_path=self.test_dir)
		d.get_all_uploads_playlist_data()

		pranks_pl = cwd + "/tests/fixtures/generated/youtube_backup/Brilliant Ember/info/playlists/Pranks.json"
		all_uploads_pl = cwd + "/tests/fixtures/generated/youtube_backup/Brilliant Ember/info/playlists/All Uploads.json"
		channel_info = cwd + '/tests/fixtures/generated/youtube_backup/Brilliant Ember/info/channel_info.json'

		expected_pranks_pl = read_json_file(pranks_pl)
		expected_all_uploads_pl = read_json_file(all_uploads_pl)
		expected_channel_info = read_json_file(channel_info)

		pranks_pl = read_json_file(self.test_dir+ "/Brilliant Ember/info/playlists/Pranks.json")
		all_uploads_pl = read_json_file(self.test_dir+ "/Brilliant Ember/info/playlists/All Uploads.json")
		channel_info = read_json_file(self.test_dir+ "/Brilliant Ember/info/channel_info.json")

		assert os.path.isfile(self.test_dir+ "/Brilliant Ember/info/playlists/Pranks.json") , "playlist json file wasn't created for Pranks"
		assert os.path.isfile(self.test_dir+ "/Brilliant Ember/info/playlists/All Uploads.json") , "playlist json file wasn't created for all uploads"
		assert os.path.isfile(self.test_dir+ "/Brilliant Ember/info/channel_info.json") , "channel info json file wasn't created"

		assert sorted(list(expected_pranks_pl)) == sorted(list(pranks_pl.keys())) , "keys of the pranks PL didn't match"
		assert sorted(list(expected_all_uploads_pl)) == sorted(list(all_uploads_pl.keys())) , "keys of all upl PL didn't match"
		assert sorted(list(expected_channel_info)) == sorted(list(channel_info.keys())) , "keys of the  channel info didn't match"

		generated_data = [pranks_pl, all_uploads_pl, channel_info]
		expected_data = [expected_pranks_pl, expected_all_uploads_pl, expected_channel_info]

		# checking the jsom values for matching values
		for index, json_file in enumerate(generated_data):
			expected_json  = expected_data[index]
			for key in json_file.keys():# the data value will be different always and the about will have different views value in desc
				if key == Keys.DATEKEY or key == Keys.CHANNEL_ABOUT:
					assert isinstance(json_file[key], dict), f"{key} value is supposed to be a dict, but received type {type(json_file[key])}"

				else: 
					assert json_file[key] == expected_json[key], f"{key} value didn't match expected value, expected {expected_json[key]} but received {json_file[key]}"



	# def test_download_all_videos_from_channel():
	#     channel_url = "https://www.youtube.com/user/FireSymphoney"

	#     browser_wait = 3
	#     d = Downloader(channel_url ,browser_wait=browser_wait, headless=False)
	#     d.download_all_videos_from_channel()

if __name__ == '__main__':
	unittest.main()