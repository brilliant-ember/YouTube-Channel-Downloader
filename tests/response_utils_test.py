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

	def test_extract_playlists_from_json_payload(self):
		all_titles = ['Guest Videos', 'Guest Videos', 'Desktop Power supplies', 'Raspberry Pi Pico', 'Arduino Signal Generator', 'Viewer Projects', 'Building a guitar vacuum tube amplifier', 'FPGA', 'Desktop CNC', 'Arduino FPGA', 'Micsig STO1104c Oscilloscope', 'Multipurpose Lab Tool Build', 'Micro: Bit', 'Classic Circuits', 'Guest Video', 'BITX', 'Nixie Tubes', 'Amplifiers', 'Radio Related Stuff', 'Smart Home', 'PCB Design', 'Filters', '7400 Logic', '3D Printing', 'Particle Photon', 'Arduino and DC Motors', 'Blynk', 'esp32', 'Raspberry Pi', 'Oscillators']
		num_videos = 30
		j = read_json_file(cwd + "/tests/fixtures/get_response/playlists/payload.json")
		playlists = self.response_utils._Response_Utils__extract_playlists_from_json_payload(j)

		titles = []
		for p in playlists:
			titles.append(p[Keys.PLAYLIST_NAME])
			
		assert all_titles == titles, "didn't download all playlist titles"
		assert len(playlists) == num_videos, "didn't get all playlists"
	
	def test_extract_json_from_channel_playlists_get_response(self)->None:
		get_resp_file = cwd + "/tests/fixtures/get_response/playlists/full_response"
		with open(get_resp_file, "r") as file:
			get_request_response_html = file.read()
		json_dict = self.response_utils.extract_json_from_channel_playlists_get_response(get_request_response_html)
		expected_json = read_json_file(cwd + "/tests/fixtures/get_response/playlists/payload.json")
		assert type(json_dict) == dict, "the type is not a dictionary"
		assert "contents" in json_dict.keys(), "json_dict doesn't have the proper first key"
		assert expected_json == json_dict, "extract json doesn't match expected json"

	def test_extract_json_from_playlist_id_get_response(self)-> None:
		get_resp_file = cwd + "/tests/fixtures/get_response/playlist?list=id/full_response"
		with open(get_resp_file, "r") as file:
			get_request_response_html = file.read()
		json_dict = self.response_utils.extract_json_from_specific_playlist_get_response(get_request_response_html)
		expected_json = read_json_file(cwd + "/tests/fixtures/get_response/playlist?list=id/payload.json")
		assert type(json_dict) == dict, "the type is not a dictionary"
		assert "contents" in json_dict.keys(), "json_dict doesn't have the proper first key"
		assert expected_json.keys() == json_dict.keys(), "extract json doesn't match expected json"

		# now repeat the test but with a playlist that doesn't have the horizontal scroll
		get_resp_file = cwd + "/tests/fixtures/get_response/playlist?list=id/full_response2"
		with open(get_resp_file, "r") as file:
			get_request_response_html = file.read()
		json_dict = self.response_utils.extract_json_from_specific_playlist_get_response(get_request_response_html)
		expected_json = read_json_file(cwd + "/tests/fixtures/get_response/playlist?list=id/payload2.json")
		assert type(json_dict) == dict, "the type is not a dictionary"
		assert "contents" in json_dict.keys(), "json_dict doesn't have the proper first key"
		assert len(set(expected_json.keys())) == len(set(json_dict.keys())), "extract json doesnt match expected json"

if __name__ == '__main__':
    unittest.main()