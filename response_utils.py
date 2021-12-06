from __future__ import annotations # to support var types in older python versions
from utils import NUMBERVIDEOSKEY, read_json_file

parse_exception = Exception("Json object response has an unexpected format, did youtube change their json object structure or UI?")


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

all_titles = ['Guest Videos', 'Guest Videos', 'Desktop Power supplies', 'Raspberry Pi Pico', 'Arduino Signal Generator', 'Viewer Projects', 'Building a guitar vacuum tube amplifier', 'FPGA', 'Desktop CNC', 'Arduino FPGA', 'Micsig STO1104c Oscilloscope', 'Multipurpose Lab Tool Build', 'Micro: Bit', 'Classic Circuits', 'Guest Video', 'BITX', 'Nixie Tubes', 'Amplifiers', 'Radio Related Stuff', 'Smart Home', 'PCB Design', 'Filters', '7400 Logic', '3D Printing', 'Particle Photon', 'Arduino and DC Motors', 'Blynk', 'esp32', 'Raspberry Pi', 'Oscillators']
num_videos = 30
j = read_json_file('tests/fixtures/get_response/datachannel[slash]playlists.json')
playlists = extract_playlists_from_json_response(j)

titles = []
for p in playlists:
    titles.append(p['title'])
    
assert all_titles == titles, "didn't download all playlist titles"
assert len(playlists) == num_videos, "didn't get all playlists"
