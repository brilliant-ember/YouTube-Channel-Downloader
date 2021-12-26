import sys
import os

cwd = os.getcwd()
# src_code_wd = os.path.split(cwd)[0]
# adding source code folder to the system path so I can import 
sys.path.insert(0, cwd)

from Downloader import Downloader
import unittest
from unittest import mock
from unittest.mock import patch

class TestDownloader(unittest.TestCase):
	def setUp(self) -> None:
		local_html_url = "file://" + cwd +  "/tests/channels/brilliant_ember_channel.html" # TODO use OS path join to make this work on windows machines too
		self.downloader = Downloader(local_html_url, browser_wait=0, headless=True)
		self.fixtures_downloaded_channel_path = cwd + "/tests/fixtures/downloaded/Brilliant Ember" #TODO use os.path.join
		
		return super().setUp()

	def tearDown(self) -> None:
		# delete the written files made by the downloader object
		# TODO
	    return super().tearDown()

	def test_init_dirs(self):
		# check that dirs have been created correctly after init
		pass

	def test_did_download_fail(self):
		all_videos_dir = os.path.join(self.fixtures_downloaded_channel_path, 'videos')

		info_but_no_video_download_dir = os.path.join(all_videos_dir, "ATTACK ON TITANS Vogel Im Kafig Guitar")
		assert True == self.downloader.did_download_fail(info_but_no_video_download_dir), "This file has an info.json file but no mp4 file, the check should say that the download has failed"

		video_but_no_info_download_dir = os.path.join(all_videos_dir, "Ottawa Bike Adventure Explore Canada")
		assert True == self.downloader.did_download_fail(video_but_no_info_download_dir), "This file has no info.json file, the check should say that the download has failed"

		empty_download_dir = os.path.join(all_videos_dir, "Lady guitarist show at Uottawa")
		assert True == self.downloader.did_download_fail(empty_download_dir), "the video dir is empty, the check should say that the download has failed"

		zero_bytes_video_download_dir = os.path.join(all_videos_dir, "Electronics: AC source MOSFET transistor circuit analysis")
		assert True == self.downloader.did_download_fail(zero_bytes_video_download_dir), "the video file has 0 bytes, the download should signale fail"

		zero_bytes_info_download_dir = os.path.join(all_videos_dir, "Real Life Lightning Attack")
		assert True == self.downloader.did_download_fail(zero_bytes_info_download_dir), "the info file has 0 bytes, the download should signale fail"

		good_download_dir = os.path.join(all_videos_dir, "Naruto Shippuuden Mini AMV All to Blame.mp4")
		assert False == self.downloader.did_download_fail(good_download_dir), "this is a health download file, check should return false"

	def test_validate_downloaded_videos(self):
		new_class_vars = dict(self.downloader.__dict__)
		new_class_vars['channel_path'] = self.fixtures_downloaded_channel_path
		with patch.dict(self.downloader.__dict__, new_class_vars, clear=True):
			failed_downloads = self.downloader.validate_downloaded_videos()
			assert len(failed_downloads) == 5, "The length of the list should be 4 as thats the num of faulty downloads"


	def test_clean_bad_downloads(self):
		# all_videos_dir = os.path.join(self.fixtures_downloaded_channel_path, 'videos')
		# {key: value[:] for key, value in self.downloader.__dict__.items()} # this is for deep copy which is not needed
		new_class_vars = dict(self.downloader.__dict__)
		new_class_vars['channel_path'] = self.fixtures_downloaded_channel_path
		with patch.dict(self.downloader.__dict__, new_class_vars, clear=True):
			with patch.object(self.downloader, "delete_file", return_value=None) as delete_mock:
				self.downloader.clean_bad_downloads()
				assert len(delete_mock.call_args_list) == 5, "the clean up should have called delete five times to clean up failed downloads"



if __name__ == '__main__':
    unittest.main()