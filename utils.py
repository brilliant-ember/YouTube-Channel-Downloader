from __future__ import annotations # to support var types in older python versions
from datetime import datetime
import json
import enum

####### Constants

DATEFORMAT = "%d/%m/%Y %H:%M:%S"

#### Enumerates

class Keys(str, enum.Enum):
	'''A class to hold all the keys to be used in the program, it also holds constants even though it's not supposed to TODO'''
	# this refers to an object in the json files where we have 
	# "update_dates": {
	#         "28/10/2021 09:09:51": "initial install",
	# 	  "20/11/2021 05:01:03": {"new_entries_since_last_backup": {added_stuff_since_last_backup}, "removed_entries_since_last_backup": {channel_removed_videos}"
	#     }
	# The DATEKEY is also used anywhere where we keep track of the date
	DATEKEY = "update_dates" 
	NUMBER_OF_PLAYLISTS ="number_of_playlists"
	ALL_UPLOADS_PLAYLIST_NAME = "All Uploads"
	CREATED_PLAYLISTS = "Created playlists"
	PLAYLIST_NEED_TO_SCROLL= "continuationItemRenderer" # if playlist has this key, we need to scroll to get all videos
	VIDEO_ELEMENT_KEY = "playlistVideoRenderer"

	CHANNEL_PLAYLISTS_NEED_TO_SCROLL = "continuationCommand" # on all created playlists for example
	SINGLE_CHANNEL_PLAYLIST_CARD = 'gridPlaylistRenderer' # a single playlist card has this key
	
	PLAYLIST_ID = "playlist_id",
	PLAYLIST_NAME = 'playlist_name'
	PLAYLIST_DESCRIPTION = 'playlist_description'
	PLAYLIST_URL = 'url'
	PLAYLIST_GROSS_VIDEOS_NUMBER = 'gross_videos_number'
	PLAYLIST_MEMBERS_ONLY_VIDEOS_NUMBER = 'members_only_videos_number'
	PLAYLIST_AVAILABLE_VIDEOS_NUMBER = "available_videos_number"
	PLAYLIST_AVAILABLE_VIDEOS = 'available_videos' 
	PLAYLIST_MEMBERS_ONLY_VIDEOS = "members_only_videos"


##### functions

def read_json_file(json_file_path:str)->dict:
	with open(json_file_path, "r") as file:
		data = file.read()
	return json.loads(data)

def over_write_json_file(file_path:str, data_dict:dict)->None:
	'''creates the file if it doesnt exisit otherwise overwrites it with the new dictionary passed'''
	with open(file_path, "w") as json_file:
		json_file.write(json.dumps(data_dict, indent=4, default=str))

def is_date1_after_date2(date1:str, date2:str) -> bool:
	'''checks if the date1 is after date2
	example:
	date1="28/10/2021 09:09:51"
	date2="28/11/2021 09:09:51"
	is_date1_after_date2(date1,date2)
	>>> False
	'''

	date1 = datetime.strptime(date1, DATEFORMAT )
	date2 = datetime.strptime(date2, DATEFORMAT )
	#if date2 is newer or happend after date1 then it will be bigger than date1
	return date1 > date2

def get_now_date() -> str:
		return datetime.now().strftime(DATEFORMAT)

def get_days_between_dates(date1:str, date2: str) -> int:
	'''returns the days delta between two dates'''
	date1 = datetime.strptime(date1, DATEFORMAT )
	date2 = datetime.strptime(date2, DATEFORMAT )
	delta = (date1 - date2).days # can be a negative number
	return max(0, delta)

def compare_dicts(existing_dict:dict, new_dict:dict) -> tuple[set, set]:
	# TODO improve doc string and add an example
	'''compares two dicts assuming unique keys,if new_dict has elements that existing_dict doesnt have those new keys will be returned as the first set.  
	Similarly if existing_dict has keys that are not found in the new_dict that means that the new dict has missing keys, and we will return that as the second set 
	Example:
	>>> a
	{1: '1', 2: '2', 3: '3'}
	>>> b
	{3: '3', 4: '4', 5: '5'}
	>>> compare_dicts(a,b)
	({4, 5}, {1, 2})
	'''
	existing_content = set(existing_dict.keys())
	current_online_content = set(new_dict.keys()) # the enw content
	# keep a record of what videos the channel uploaded and what videos got removed
	# this also records removed playlists and new playlists
	missing_keys = existing_content - current_online_content # if the video is renamed we still count it as removed
	newly_added_keys = current_online_content - existing_content
	return list(newly_added_keys), list(missing_keys)


def remove_slash_from_strings(s:str)->str:
	'''removes slashes and replaces them with -'''
	# replaces the "/" with "／" look at them next to each other ／/ , they are different
	# this is so video names with slashes in their names dont get created as multile dirs, example AC/DC
	# would get created as a directory tree instead of a file names AC/DC
	#
	# some unicodes are not supported in all machines, will replace with -

	s = s.replace("/","-")
	s = s.replace("\\", "-")
	return s

def generate_playlist_url(playlist_id:str)->str:
		"""Takes playlist Id and generates the playlist url
		example https://www.youtube.com/playlist?list=PLGhvWnPsCr59gKqzqmUQrSNwl484NPvQY
		"""
		return f'https://www.youtube.com/playlist?list={playlist_id}'

def generate_video_url(video_id:str)->str:
		"""Takes video Id and generates the video url
		example https://www.youtube.com/watch?v=e3LqeN0e0as
		"""
		return f'https://www.youtube.com/watch?v={video_id}'

def json_value_extract(obj:dict, wanted_key) -> list:
	'''Recursively finds the values of the argument key from nested dictionary JSON '''
	found_values = []

	def extract(obj:dict, found_values:list, key)->list:
		'''Recursively search for all values of the key in JSON tree, if return_first_match_only then it returns the value as soon as it finds a matching key'''
		if isinstance(obj, dict):
			for k, v in obj.items():
				if k == key:
					found_values.append(v)
				elif isinstance(v, (dict, list)):
					extract(v, found_values, key)
		elif isinstance(obj, list):
			for item in obj:
				extract(item, found_values, key)
		return found_values

	found_values = extract(obj, found_values, wanted_key)
	return found_values

class NeedToScrollDownError(Exception):
# a custom exception if you need to scroll down to render the rest of the content
	 pass