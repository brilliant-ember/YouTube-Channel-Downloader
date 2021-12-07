from __future__ import annotations # to support var types in older python versions
from utils import NUMBERVIDEOSKEY, read_json_file
import re
import json

parse_exception = Exception("Json object response has an unexpected format, did youtube change their json object structure or UI?")

def extract_json_from_get_response(html_get_response:str)->dict:
    regex_pattern = r"(var ytInitialData = )[\s|\S]*}]}}}" #matches the variable that contains the json object of interest
    json_str = re.search(regex_pattern, html_get_response).group(0)
    remove_substr = "var ytInitialData = "
    json_str = json_str[len(remove_substr):]
    return json.loads(json_str)
    

def extract_playlists_from_json_response(json_respone_var:dict) -> list[dict]:
    '''Takes the response of a GET requests on youtube.com/channel/playlists, and spits out the playlists data'''
    j = json_respone_var['contents']['twoColumnBrowseResultsRenderer']['tabs']
    # currently (dec 6 -2021) there are two types 1. Created playlists and Saved playlists
    created_playlists = j[2]['tabRenderer']['content']['sectionListRenderer']['contents'][0]
    created_playlists = created_playlists['itemSectionRenderer']['contents'][0]['shelfRenderer']
    # this should be "Created playlists"
    playlist_type =  created_playlists['title']['runs'][0]['text'] 
    if playlist_type != 'Created playlists':
        raise parse_exception
    created_playlists = created_playlists['content']['horizontalListRenderer']['items']
    channel_created_playlists_metadata = []
    for p in created_playlists:
        p = p['gridPlaylistRenderer']
        title = p['title']['runs'][0]['text']
        playlist_id = p['playlistId']
        video_count = int(p['videoCountShortText']['simpleText'])
        channel_created_playlists_metadata.append({
            'title':title,
            'playlist_id': playlist_id,
            NUMBERVIDEOSKEY: video_count
        })

    return channel_created_playlists_metadata


