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
