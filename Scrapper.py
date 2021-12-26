
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
from utils import json_value_extract, Keys
from response_utils import Response_Utils

from Playlist import Playlist
from Channel import Channel
import re
import json
from typing import Union
from random import randint, random


class ChannelScrapper():
	def __init__(self, channel_url: str, logger:Log, headless = True, default_wait = 1, test_mode=False):
		self.default_wait = default_wait
		self.scroll_wait = default_wait/2
		self.channel_url = channel_url
		self.test_mode = test_mode

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
		self.logger = logger
		if not test_mode:
			self.get_channel_name()

	def __del__(self):
		self.driver.quit()
	
	def log(self, msg:str, level="debug")-> None:

		msg = "Scrapper_Log - " + msg
		self.logger.log(msg, level=level)
	
	def get(self, url:str, force=False) -> None:
		'''Go to a website if we are not already on it'''
		self.current_scroll_height = 0
		if self.driver.current_url != url or force:
			self.driver.get(url)
			self.log(f"performed get request on url {url}")

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

		elif type == "id":
			by=By.ID

		try:
			wait.until(EC.element_to_be_clickable((by, name)))
		except TimeoutException:
			# sometimes it errors even if the element is clickable
			pass
		self.wait_random_time()

	def wait_for_dynamic_content_loading_spinner_to_disappear(self):
		spinner_id = "spinner" # you can also use id ghost-cards
		wait = WebDriverWait(self.driver, self.default_wait)
		try:
			# this will raise an NoSuchElementException if the spinner id elem is not there
			self.driver.find_element_by_id(spinner_id).find_elements_by_class_name('active')
			self.log('found dynamic content loading spinner...')
			by = By.ID
			locator = (by, spinner_id)
			t = time.time()
			# this will raise TimeoutException 
			wait.until(EC.invisibility_of_element(locator))
			t = time.time() - t
			self.log(f"waited for dynamic content spinner to disappear for {t} seconds")
		except (TimeoutException, NoSuchElementException):
			# didn't find the spinner so all is good
			pass

	def get_all_channel_playlists_info(self, channel_playlists_url:str):
		'''gets all created playlists info from the channel given a url, 
		doesn't include all uploads playlists, example url https://www.youtube.com/c/greatscottlab/playlists
		'''
		self.log(f'getting all channel\'s created playlists for channel with url  {channel_playlists_url}')
		if not('?view=' in channel_playlists_url):
			channel_playlists_url = channel_playlists_url + "?view=1"
		# if a channel has only created playlists then it doesn't have ?view=x so it's fine if we don't have it in the req
		response_utils = Response_Utils()
		self.clear_stored_requests()
		self.get(channel_playlists_url)
		self.wait_for_page_load("playlist-thumbnails", type='id')

		html_body = self._get_response_from_created_playlists_or_all_uploads_request(channel_playlists_url)
		body_json = response_utils.extract_json_from_channel_playlists_get_response(html_body)
		channel = Channel()
		need_to_scroll = channel.extract_all_playlists_from_a_playlists_category_json_response(body_json)
		if need_to_scroll:
			self.clear_stored_requests()
			self.scroll_down()
			self.__scroll_down_and_get_remaining_elements(html_body, channel)
		all_pl = channel.created_playlists_metadata
		num_playlists = len(all_pl.keys())
		self.log(f"found {num_playlists} playlists for the channel with url {channel_playlists_url}")

		return all_pl


	def _get_response_from_created_playlists_or_all_uploads_request(self,request_url:str, is_all_uploads=False) -> str:
		''' goes over the requests stored in the buffer, and returns the response of 
			the request_url for a specific playlist, if you want all uploads then pass is_all_uploads=True and its going to look at channel/videos instead of a specific playlist'''

		if is_all_uploads:
			url_path = '/videos'
		else:
			url_path = '/playlists'

		for i in range(len(self.driver.requests)):
			request = self.driver.requests[i]
			response = request.response
			content_type = request.headers.get_content_type()
			is_content_text = 'text' in content_type
			if url_path in request.url and response and response.body and is_content_text:
				return self._decode_response_body(response)
		raise Exception("Didn't find excpected request URL ", request_url)


	def get_all_uploads_info_for_channel(self, channel_videos_url:str):
		'''Gets all video info in the "all uploads" link of the channel, example url https://www.youtube.com/c/greatscottlab/videos
		note that this gets the all-uploads playlist only, it doesn't get the unlisted videos that are only viewable inside the specific playlist that unlisted video is in '''

		self.log('Scrapping channel/videos for url  {channel_videos_url}')
		
		response_utils = Response_Utils()
		self.clear_stored_requests()
		self.get(channel_videos_url)
		self.wait_for_page_load("ytd-grid-video-renderer", type='tag')

		html_body = self._get_response_from_created_playlists_or_all_uploads_request(channel_videos_url, is_all_uploads=True)
		body_json = response_utils.extract_json_from_all_uploads_get_response(html_body)
		channel = Channel()
		need_to_scroll = channel.extract_videos_from_all_uploads_json_response(body_json)
		if need_to_scroll:
			self.clear_stored_requests()
			self.scroll_down()
			self.__scroll_down_and_get_remaining_elements(html_body, channel)

		video_info = channel.all_uploads_videos
		num = len(video_info.keys())
		self.log(f"found {num} videos in all uploads for the channel ")

		return video_info
	
	# obsolete, youtube changed their UI so this is no longer relevent
	# def get_all_uploads_playlist_url(self, videos_tab_link:str)->str:
	# 	''' takes the link that you get after you press videos in the channel tab, example link input
	# 	https://www.youtube.com/user/FireSymphoney/videos'''
	# 	self.get(videos_tab_link)
	# 	self.wait_for_page_load('play-all', "id")
	# 	try:
	# 		elem = self.driver.find_element_by_id('play-all').find_element_by_class_name('yt-simple-endpoint')
	# 		all_uploads_url = elem.get_attribute('href')
	# 		all_uploads_url = all_uploads_url.split('&')[0] # get rid of the query
	# 	except NoSuchElementException: #sometimes youtube doesn't have the play all button
	# 		breakpoint()
	# 		raise Exception("Could not find play all button, it may work if you try again")
	# 	return all_uploads_url

	def clear_stored_requests(self):
		'''works for selenium-wire only'''
		del self.driver.requests
		self.wait_random_time() # wait a second so we don't accidentally clear something that's happening right now
	
	def  _decode_response_body(self,  response):
		decoded = decode(response.body, response.headers.get('Content-Encoding', 'identity'))
		decoded = str(decoded, 'utf-8', errors='replace')
		return decoded

	def _get_response_from_playlist_request(self,request_url:str) -> str:
		''' goes over the requests stored in the buffer, and returns the response of the request_url for a specific playlist'''
		for i in range(len(self.driver.requests)):
			request = self.driver.requests[i]
			response = request.response
			playlist_id = request_url.replace("https://youtube.com/playlist?list=","")
			playlist_id = playlist_id.replace("https://www.youtube.com/playlist?list=","") # in case url has www
			if playlist_id in request.url and response and response.body:
				return self._decode_response_body(response)
				
		raise Exception("Didn't find the requested url")

	def get_playlist_info(self, playlist_url) -> dict:
		'''takes playlist url, returns the number of videos in that playlist and an object {"video1Title": "video1url", video2:url ... and so on}
		example playlist url https://www.youtube.com/playlist?list=UU6mIxFTvXkWQVEHPsEdflzQ'''
		self.clear_stored_requests()
		self.get(playlist_url)
		self.wait_for_page_load("ytd-playlist-video-renderer")
		self.log(f"getting all videos for playlist:  {playlist_url}")
		html_body = self._get_response_from_playlist_request(playlist_url)
		response_utils = Response_Utils()
		my_json = response_utils.extract_json_from_specific_playlist_get_response(html_body)
		playlist_handler = Playlist()
		need_to_scroll = playlist_handler.extract_playlist_info_from_json_payload(my_json)
		if need_to_scroll:
			self.clear_stored_requests()
			self.scroll_down()
			self.__scroll_down_and_get_remaining_elements(html_body, playlist_handler)
		videos = playlist_handler.get_playlist_info_as_dict()
		num_videos = videos[Keys.PLAYLIST_AVAILABLE_VIDEOS_NUMBER]
		self.log(f"found {num_videos} videos for playlist {playlist_url}")
		return videos

	def __scroll_down_and_get_remaining_elements(self, html_get_response:str, object_to_scrape:Union[Playlist, Channel], all_uploads=False) -> None:
		'''scrolls down to get remaining content that's created dynamically when you scroll, accepts either a playlist or channel object
		ARGS: 
			html_get_response:str -> The html text of the response body
			object_to_scrape: either a Playlist or Channel -> do we want to extract dynamically created Playlists or Videos in a playlists
							  if we want to get a specific playlist dynamic videos pass a Playlist object. If you want all the dynamically created
							  playlists of a channel pass a Channel object
			all_uploads: if you're scrapping the channel/videos url for all_uploaded videos, then you must set this to True and pass a Channel object
		Returns:
			None -> since we update the passed Playlist or Channel object no need to return anything
		'''
		if isinstance(object_to_scrape, Playlist):
			extracting_function = object_to_scrape.extract_playlist_info_from_json_payload

		elif all_uploads and isinstance(object_to_scrape,Channel):
			extracting_function = object_to_scrape.extract_videos_from_all_uploads_json_response	

		elif isinstance(object_to_scrape, Channel):
			extracting_function = object_to_scrape.extract_all_playlists_from_a_playlists_category_json_response
		else:
			raise Exception('The object_to_scrape must be either a Playlist or a Channel, are you scrapping all_uploads, if so set it to all_uploads=True')
		
		pattern = "(?<=\"INNERTUBE_API_KEY\":\")[\w]*(?=\",)*"
		api_key = re.search(pattern, html_get_response).group(0)
		keep_scrolling = True
		infinite_loop_safety = 100

		while(keep_scrolling and infinite_loop_safety > 0):
			infinite_loop_safety -=1
			for req in self.driver.requests:
				response = req.response
				if api_key in req.url and "/browse" in req.url and response and response.body:
					self.log(f"The request url we're inspecting is: {req.url}")
					decoded_resp_body = self._decode_response_body(response)
					decoded_resp_body = json.loads(decoded_resp_body)
					keep_scrolling = extracting_function(decoded_resp_body)
					infinite_loop_safety += 1
									
			self.clear_stored_requests()
			self.scroll_down()
			self.wait_random_time() # give the spinner a chance to appear
			self.wait_for_dynamic_content_loading_spinner_to_disappear()

		if infinite_loop_safety <=0:
			self.log("Warning triggered infinite loop safety", level="warn")


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
		self.log("scrolling down")
		self.driver.execute_script(f"window.scrollTo(0, {self.current_scroll_height});")
		time.sleep(self.scroll_wait)

	def wait_random_time(self):
		x = max(self.default_wait, 3)
		x = randint(1, x) * random() * 1.33
		time.sleep(x)






