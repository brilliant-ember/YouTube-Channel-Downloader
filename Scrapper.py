# this is a class implementation of the scarepper

#pytube and selenium implementation

from enum import unique
import traceback
# from selenium import webdriver
from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from Logger import Log
import time
import pdb
import utils
from utils import Keys
from response_utils import Response_Utils

from Playlist import Playlist
import re
import json


class ChannelScrapper():
	def __init__(self, channel_url: str, logger:Log, headless = True, default_wait = 1, debug_mode=False):
		self.default_wait = default_wait
		self.scroll_wait = default_wait/2
		self.channel_url = channel_url

		seleniumwire_options = {
			'request_storage': 'memory',
    		'request_storage_max_size': 500  # Store no more than 500 requests in memory
		}
		if not headless:
			self.driver = webdriver.Firefox(seleniumwire_options=seleniumwire_options) 
		else:
			options = Options()
			options.add_argument("--headless")
			self.driver = webdriver.Firefox(options=options, seleniumwire_options=seleniumwire_options)
			
		self.driver.scopes.append('.*youtube.com.*')# capture only youtube traffic

		self.initial_scroll_height = 0 # initial scroll height
		self.current_scroll_height = 0
		if not debug_mode:
			self.logger = logger
			self.get_channel_name()

	def __del__(self):
		self.driver.quit()
	
	def log(self, msg:str, level="info")-> None:
		msg = "Scrapper_Log - " + msg
		self.logger.log(msg, level=level)
	
	def get(self, url:str) -> None:
		'''Go to a website if we are not already on it'''
		self.current_scroll_height = 0
		if self.driver.current_url != url:
			self.driver.get(url)

	def get_channel_name(self)-> str:
		id = 'channel-name'
		self.get(self.channel_url)
		self.wait_for_page_load(id, type='id')
		names = self.driver.find_elements_by_id(id)
		for name in names:
			if name.text:
				return name.text

	def wait_for_page_load(self, name:str, type="class_name"):
		by = By.CLASS_NAME
		type = type.lower()
		wait = WebDriverWait(self.driver, self.default_wait)

		if type == "tag_name" or type =='tag':
			by = By.TAG_NAME

		elif type== "id":
			by=By.ID

		try:
			wait.until(EC.element_to_be_clickable((by, name)))
		except TimeoutException:
			# sometimes it errors even if the element is clickable
			pass 

	def get_all_channel_playlists_info(self, channel_playlists_url:str):
		'''gets all playlists info from the channel given a url, doesn't include all uploads playlists, example url https://www.youtube.com/c/greatscottlab/playlists
		
		'''
		all_playlists_info = {}
		response_utils = Response_Utils()
		all_pl = response_utils.get_playlists_listing(channel_playlists_url)
		num_playlists = len(all_pl)
		for playlist_card in all_pl:
			url = playlist_card['url']
			playlist = self.get_playlist_info(url)
			pl_id = playlist.pop('playlist_id')
			all_playlists_info[pl_id] = playlist

		return all_playlists_info

	def get_all_uploads_playlist_url(self, videos_tab_link:str)->str:
		''' takes the link that you get after you press videos in the channel tab, example link input
		https://www.youtube.com/user/FireSymphoney/videos'''
		self.get(videos_tab_link)
		self.wait_for_page_load('play-all', "id")
		try:
			elem = self.driver.find_element_by_id('play-all').find_element_by_class_name('yt-simple-endpoint')
			all_uploads_url = elem.get_attribute('href')
			all_uploads_url = all_uploads_url.split('&')[0] # get rid of the query
		except NoSuchElementException: #sometimes youtube doesn't have the play all button
			# breakpoint()
			raise Exception("Could not find play all button, it may work if you try again")
		return all_uploads_url

	def clear_stored_requests(self):
		'''works for selenium-wire only'''
		del self.driver.requests
	def  _decode_response_body(self,  response):
		decoded = decode(response.body, response.headers.get('Content-Encoding', 'identity'))
		decoded = str(decoded, 'utf-8', errors='replace')
		return decoded


	def _get_response_from_request(self,request_url:str) -> str:
		''' goes over the requests stored in the buffer, and returns the response of the request_url for a specific playlist'''
		for i in range(len(self.driver.requests)):
			request = self.driver.requests[i]
			response = request.response
			playlist_id = request_url.replace("https://youtube.com/playlist?list=","")
			playlist_id = playlist_id.replace("https://www.youtube.com/playlist?list=","") # in case url has www
			if playlist_id in request.url and response and response.body:
				return self._decode_response_body(response)
				
		raise Exception("Didn't find the requested url")

	def get_playlist_info(self, playlist_url)->dict:
		'''takes playlist url, returns the number of videos in that playlist and an object {"video1Title": "video1url", video2:url ... and so on}
		example playlist url https://www.youtube.com/playlist?list=UU6mIxFTvXkWQVEHPsEdflzQ'''
		self.clear_stored_requests()
		self.get(playlist_url)
		html_body = self._get_response_from_request(playlist_url)
		response_utils = Response_Utils()
		my_json = response_utils.extract_json_from_specific_playlist_get_response(html_body)
		playlist_handler = Playlist()
		need_to_scroll = playlist_handler.extract_playlist_info_from_json_payload(my_json)
		if need_to_scroll:
			self.clear_stored_requests()
			self.scroll_down()
			self.__scroll_down_and_get_remaining_videos(html_body, playlist_handler)
		return playlist_handler.get_playlist_info_as_dict()

	def __scroll_down_and_get_remaining_videos(self, html_get_response:str, playlist:Playlist):
		from utils import json_value_extract
		pattern = "(?<=\"INNERTUBE_API_KEY\":\")[\w]*(?=\",)*"
		api_key = re.search(pattern, html_get_response).group(0)
		keep_scrolling = True
		infinite_loop_safety = 1000
		while(keep_scrolling and infinite_loop_safety > 0):
			infinite_loop_safety -= 1
			for req in self.driver.requests:
				response = req.response
				if api_key in req.url and response and response.body:
					decoded_resp_body = self._decode_response_body(response)
					decoded_resp_body = json.loads(decoded_resp_body)
					# there are other json objects that don't include videos and the need_to_scroll key
					# so I need to make sure that the video element key is in the response body
					videos_payload = json_value_extract(decoded_resp_body, Keys.VIDEO_ELEMENT_KEY)
					if len(videos_payload) > 0:
						infinite_loop_safety += 1
						keep_scrolling = playlist.extract_playlist_info_from_json_payload(decoded_resp_body)

			self.clear_stored_requests()
			self.scroll_down()


	def get_channel_about(self, playlist_about_url:str)->dict:
		self.get(playlist_about_url)
		desc_id = 'description'
		self.wait_for_page_load(desc_id, type='id')
		about_page = self.driver # alias
		desc = about_page.find_elements_by_id(desc_id)
		desc_text = ""
		for tag in desc:
			desc_text += tag.text
		
		details_id = 'details-container'
		details = about_page.find_elements_by_id(details_id)
		details_text = ""
		for d in details:
			details_text += d.text
		
		links_id = "links-container"
		links_tag = about_page.find_element_by_id(links_id)
		links = {}
		for link_tag in links_tag.find_elements_by_tag_name('a'):
			text = link_tag.text
			url = link_tag.get_attribute('href')
			links[text] = url
		
		stats_id = "right-column"
		stats = about_page.find_elements_by_id(stats_id)
		stats_text = ""
		for s in stats:
			stats_text += s.text

		return {
			"description": desc_text,
			"details": details_text,
			"links": links,
			"stats":stats_text
		}

	def scroll_down(self, scroll_offset = 700):
		"""A method for scrolling the page."""
		self.current_scroll_height += self.current_scroll_height + scroll_offset
		self.driver.execute_script(f"window.scrollTo(0, {self.current_scroll_height});")
		time.sleep(self.scroll_wait)




