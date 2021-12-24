from utils import Keys, json_value_extract

class Channel:
    def __init__(self):
        self.created_playlists_metadata = {} # we only regard the created playlists, other playlists jsons will not be passed to channel class for now at least

    
    def extract_all_playlists_from_a_playlists_category_json_response(self, playlists_category:dict)->bool:
        '''Extracts all playlists in the a category of playlists in a channel, for example created playlists category or saved playlists category
        Returns:
            bool: True if we need to scroll more to get the rest of the playlists, otherwise returns False
        '''
        playlists = json_value_extract(playlists_category, Keys.SINGLE_CHANNEL_PLAYLIST_CARD)
        found_new_playlists = 0
        for p in playlists:
            title = p['title']['runs'][0]['text']
            playlist_id = p['playlistId'] # this is the playlist id in the youtube json, don't use the Keys enum!
            video_count = p['videoCountShortText']['simpleText']
            video_count = int(video_count.replace(',','')) # remove comma if we have 4,999 or somthing

            if not self.does_key_exist(playlist_id):
                self.created_playlists_metadata[playlist_id] = {
                    Keys.PLAYLIST_NAME:title,
                    Keys.PLAYLIST_GROSS_VIDEOS_NUMBER: video_count
                }
                found_new_playlists +=1

        # print("number of playlists to add", found_new_playlists)
        need_to_scroll = len(json_value_extract(playlists_category, Keys.CHANNEL_PLAYLISTS_NEED_TO_SCROLL)) > 0
        return need_to_scroll


    def does_key_exist(self, key):
        if key in self.created_playlists_metadata.keys():
            return True
        return False




