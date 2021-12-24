from __future__ import annotations # to support var types in older python versions
from utils import Keys, read_json_file, NeedToScrollDownError, json_value_extract
import re
import json
from requests import get

parse_exception = Exception("Json object response has an unexpected format, did youtube change their json object structure or UI?")

class Response_Utils():
	'''This class handeles processing of the responses from API requests'''

	def perform_get_request_text(self, url:str)->str:
		"""Takes a url and performs a GET request returning the response.text
		ARGS:
			url: string
		"""
		#TODO add timeout
		r = get(url)
		if r.ok:
			return r.text
		else:
			raise Exception("cant do GET request")


	# TODO remove here replaced with scrapper's method
	def get_playlists_listing(self, playlists_url:str)->list[dict]:
		''' 
		Takes the channels all-playlist url and returns all created playlists is the form:
		[
			{
				"title": "Guest Videos",
				"playlist_id": "PLGhvWnPsCr5-x1S6oAmAQk66rrDeZ2yoB",
				"_number_of_videos": 3
			},{},{} ...etc
			NOTE 
			you must perform a check to see if query ?view=number is in the text of the html request,
			if it is not we need to add that query to the url and do another req
		'''

		html_get_response = self.perform_get_request_text(playlists_url)
		# perform a check to see if query ?view=number is in the text of the html request, if it is not we need to add that query to the url and do another reqyest
		json_dict = self.extract_json_from_channel_playlists_get_response(html_get_response)
		return self.__extract_playlists_from_json_payload(json_str)

	def extract_json_from_specific_playlist_get_response(self, html_get_response:str)->dict:
		'''extracts json obj from response of request youtube.com?playlist?list=ID'''
		regex_pattern = r"(var ytInitialData = )[\s|\S]*}}};" #matches the variable that contains the json object of interest
		json_str = re.search(regex_pattern, html_get_response).group(0)
		remove_substr = "var ytInitialData = "
		json_str = json_str[len(remove_substr):-1]
		return json.loads(json_str)


	def extract_json_from_channel_playlists_get_response(self, html_get_response:str)->dict:
			''' gets the json object in the response of a request like
			youtube.com/c/channelName/playlists'''
			regex_pattern = r"(var ytInitialData = )[\s|\S]*}]}}}" #matches the variable that contains the json object of interest
			json_str = re.search(regex_pattern, html_get_response).group(0)
			remove_substr = "var ytInitialData = "
			json_str = json_str[len(remove_substr):]
			return json.loads(json_str)

	# TODO unit test this
	def are_we_in_correct_view_for_created_playlists(self, html_text:str)->bool:
		''' we need to make sure that we're in the created playlists proper url, one that has ?view=x, [x is any integer]'''
		if '?view=1' in html_text:
			return True
		return False
			
