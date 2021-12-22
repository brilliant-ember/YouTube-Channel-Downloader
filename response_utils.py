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

    def get_playlists_listing(self, playlists_url:str)->list[dict]:
        ''' 
        Takes the channels all-playlist url and returns all created playlists is the form:
        [
            {
                "title": "Guest Videos",
                "playlist_id": "PLGhvWnPsCr5-x1S6oAmAQk66rrDeZ2yoB",
                "_number_of_videos": 3
            },{},{} ...etc
            '''

        html_get_response = self.perform_get_request_text(playlists_url)
        json_str = self.extract_json_from_channel_playlists_get_response(html_get_response)
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
            

    def __extract_playlists_from_json_payload(self, json_respone_var:dict) -> list[dict]:
        '''Takes the response of a GET requests on youtube.com/channel/playlists, and spits out the playlists data
        TODO use utils. json_key_finder to parse the json tree instead of manually doing it like here, look at the Playlist.py file for ex'''
        j = json_respone_var['contents']['twoColumnBrowseResultsRenderer']['tabs']
        # currently (dec 6 -2021) there are two types 1. Created playlists and Saved playlists
        created_playlists = j[2]['tabRenderer']['content']['sectionListRenderer']['contents'][0]
        try:
            created_playlists = created_playlists['itemSectionRenderer']['contents'][0]['shelfRenderer']
            # this should be "Created playlists"
            playlist_type =  created_playlists['title']['runs'][0]['text'] 
            if playlist_type != 'Created playlists':
                raise parse_exception
            created_playlists = created_playlists['content']['horizontalListRenderer']['items']
        except KeyError:
            created_playlists = created_playlists['itemSectionRenderer']['contents'][0]['gridRenderer']['items']
            
        channel_created_playlists_metadata = []
        for p in created_playlists:
            p = p['gridPlaylistRenderer']
            title = p['title']['runs'][0]['text']
            playlist_id = p['playlistId']
            video_count = int(p['videoCountShortText']['simpleText'])
            channel_created_playlists_metadata.append({
                Keys.PLAYLIST_NAME:title,
                Keys.PLAYLIST_ID: playlist_id,
                Keys.PLAYLIST_GROSS_VIDEOS_NUMBER: video_count
            })

        return channel_created_playlists_metadata




r = Response_Utils()
p = "https://www.youtube.com/playlist?list=PL0o_zxa4K1BWYThyV4T2Allw6zY0jEumv"
