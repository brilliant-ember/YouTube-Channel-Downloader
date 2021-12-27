from utils import json_value_extract, Keys, get_now_date, generate_playlist_url, YtElms, generate_video_url
from selenium.webdriver.remote.webelement import WebElement


class Playlist():
    def __init__(self):
        # self.playlist_url = playlist_url
        self.gross_number_of_videos = 0 #num of videos includeding private, membersOnly and available videos
        self.num_available_videos = 0
        self.num_members_only_videos = 0
        self.playlist_id = ""
        self.playlist_name=""
        self.playlist_description=""
        self.available_videos = {}
        self.members_only_videos = {}


    def get_playlist_info_as_dict(self):
        '''
        {
            "playlist_id":id,
            "playlist_name":name,
            "playlist_description":desc,
            "url":str,
            "num_available_videos":int,
            "gross_number_of_videos":int,
            "num_members_only_videos":int,
            "update_dates":"right now date"
            "videos":{"id":{ "title":title, 'length':lengthText}, "id":{} ...}
        }
        '''
        return {
            Keys.PLAYLIST_ID: self.playlist_id,
            Keys.PLAYLIST_NAME: self.playlist_name,
            Keys.PLAYLIST_DESCRIPTION: self.playlist_description,
            Keys.PLAYLIST_URL:generate_playlist_url(self.playlist_id),
            Keys.PLAYLIST_AVAILABLE_VIDEOS_NUMBER: self.num_available_videos,
            Keys.PLAYLIST_GROSS_VIDEOS_NUMBER:self.gross_number_of_videos,
            Keys.PLAYLIST_MEMBERS_ONLY_VIDEOS_NUMBER:self.num_members_only_videos,
            Keys.PLAYLIST_MEMBERS_ONLY_VIDEOS:self.members_only_videos,
            Keys.DATEKEY: get_now_date(),
            Keys.PLAYLIST_AVAILABLE_VIDEOS: self.available_videos
        }

    def extract_playlist_info_from_json_payload(self, playlist_json:dict)->bool:
        '''Returns True if we need to scroll, False otherwise
         takes a playlist json dict from the response and updates the list data, it updates things like the videos, playlist name ..etc
        returns True if we need to scroll, otherwise returns false if we reached the end and got all available videos
        NOTE that you can only get the 1st 100 video links, after that you need to 
        scroll down to generate the remaining video links.
        '''
        if not (self.playlist_id or self.playlist_name or self.playlist_description):
            self.playlist_name = playlist_json['metadata']['playlistMetadataRenderer']['title']
            self.playlist_description = playlist_json['microformat']['microformatDataRenderer']['description']
            self.playlist_id = json_value_extract(playlist_json, 'playlistId')[0] # we can also get it from the url
            self.__find_gross_number_of_videos(playlist_json)

        videos_obj = json_value_extract(playlist_json, YtElms.VIDEO_ELEMENT_KEY)
        for video_obj in videos_obj:
            self.__extract_video_info_from_playlistVideoRenderer(video_obj)
            
        need_to_scroll = json_value_extract(playlist_json, YtElms.PLAYLIST_NEED_TO_SCROLL) # this exists if we need to scroll to get videos
        if len(need_to_scroll) != 0:
            return True
        return False

    def __find_gross_number_of_videos(self, json_get_resp:dict):
        side_bar_info = json_value_extract(json_get_resp, 'playlistSidebarPrimaryInfoRenderer')[0]
        stats = json_value_extract(side_bar_info, 'stats')[0]
        self.gross_number_of_videos = stats[0]['runs'][0]['text'] # number of all videos including unavailable videos


    def __is_video_members_only(self, video_playlist_renderer:dict)->bool:
        '''some videos are only available to people who purchased a membership'''
        video_badge_style = json_value_extract(video_playlist_renderer, 'style')
        if len(video_badge_style)>0 and video_badge_style[0] == "BADGE_STYLE_TYPE_MEMBERS_ONLY":
            return True
        return False

    # test this in functional testing TODO
    def using_html_element_is_video_members_only(self, web_element: WebElement, members_only_tag_name:str) -> bool:
        ''' checks if the provided html tag contains 'Members only' text '''
        for i in web_element.find_elements_by_tag_name(members_only_tag_name):
            if "Members only" in i.text:
                return True
        return False

    def __extract_video_info_from_playlistVideoRenderer(self, video_obj:dict)->dict:
        video_id = video_obj[YtElms.VIDEO_ID]
        video_title = video_obj['title']['runs'][0]['text']
        video_url = generate_video_url(video_id)
        # length_text = video_obj['lengthText']['simpleText']
        # length_text = video_obj['lengthText']['accessibility']['accessibilityData']['label']
        if self.__is_video_members_only(video_obj):
            self.members_only_videos[video_id] = {Keys.VIDEO_NAME: video_title, Keys.URL: video_url}
            self.num_members_only_videos +=1
        else:
            self.available_videos[video_id] = {Keys.VIDEO_NAME: video_title, Keys.URL: video_url}
            self.num_available_videos = self.num_available_videos + 1
    
    def does_key_exist(self, key):
        if key in self.available_videos.keys() or key in self.members_only_videos.keys():
            return True
        return False

    def add_missing_videos_if_any(self, video_id:str, video_title:str, video_url:str, is_members_only:bool) -> bool:
        '''if the passed video wasn't already recorder returns true and adds it to record, otherwise return False'''
        if not self.does_key_exist(video_id):
            if is_members_only:
                self.members_only_videos[video_id] = {Keys.VIDEO_NAME: video_title, Keys.URL: video_url}
                self.num_members_only_videos +=1
            else:
                self.available_videos[video_id] = {Keys.VIDEO_NAME: video_title, Keys.URL: video_url}
                self.num_available_videos +=1
            return True
        return False