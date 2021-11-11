# this is a class implementation of the scarepper

#pytube and selenium implementation

from enum import unique
import traceback
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from Logger import Log
import time
import pdb


class ChannelScrapper():
	def __init__(self, channel_url: str, logger:Log, headless = True, default_wait = 1):
		self.default_wait = default_wait
		self.scroll_wait = default_wait/2
		if not headless:
			self.driver = webdriver.Firefox() 
		else:
			options = Options()
			options.add_argument("--headless")
			self.driver = webdriver.Firefox(options=options)
			
		self.channel_url = channel_url
		self.logger = logger

		self.initial_scroll_height = 0 # initial scroll height
		self.current_scroll_height = 0
		self.get_channel_name()


	def __del__(self):
		self.driver.quit()
	
	def log(self, msg:str, level="info")-> None:
		msg = "Scrapper_Log - " + msg
		self.logger.log(msg, level=level)
	
	def get(self, url:str) -> None:
		self.current_scroll_height = 0
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


	def get_playlists_info(self, channel_playlists_url:str):
		'''gets all playlists info from the channel given a url, doesnt include all uploads playlists, example url https://www.youtube.com/c/greatscottlab/playlists
		sample output
		{
		'Testing Circuits I found on the Internet!': {'num_videos': '2', 'videos':{videoName: videoURL, video2Name: video2Url, ...etc} 'url': 'https://www.youtube.com/playlist?list=PLAROrg3NQn7ccopMKCIOQq4NyVfWIz0Nz'},
		'Q&A': {'num_videos': '15', 'videos':{videoName: videoURL, video2Name: video2Url, ...etc} 'url': 'https://www.youtube.com/playlist?list=PLAROrg3NQn7e2Eztc9zXlwZNn_heDZTtP'}, 
		'DIY or Buy': {'num_videos': '24', 'videos':{videoName: videoURL, video2Name: video2Url, ...etc} 'url': 'https://www.youtube.com/playlist?list=PLAROrg3NQn7e3GQlBhuE_TIde0eJZHuzt'},
		'3D Printing': {'num_videos': '13', 'videos':{videoName: videoURL, video2Name: video2Url, ...etc} 'url': 'https://www.youtube.com/playlist?list=PLAROrg3NQn7ctleg5jTtJKuW9jkdxXGSq'}, 
		'Fix It!': {'num_videos': '3', 'videos':{videoName: videoURL, video2Name: video2Url, ...etc} 'url': 'https://www.youtube.com/playlist?list=PLAROrg3NQn7eBsxqekLpVbpCy-KAVKywG'},
		'Electronics Projects': {'num_videos': '147', 'videos':{videoName: videoURL, video2Name: video2Url, ...etc} 'url': 'https://www.youtube.com/playlist?list=PLAROrg3NQn7dGPxb9CFtxwbgzLNaaj1Oe'},
		'HACKED!': {'num_videos': '19', 'url': 'https://www.youtube.com/playlist?list=PLAROrg3NQn7fELM8O_Gm8wVqZIik8qzyv'}, 
		'VS': {'num_videos': '16', 'videos':{videoName: videoURL, video2Name: video2Url, ...etc} 'url': 'https://www.youtube.com/playlist?list=PLAROrg3NQn7dDSD7_STXb94bX_EQrp01y'}, 
		'Electronic Basics': {'num_videos': '49', 'videos':{videoName: videoURL, video2Name: video2Url, ...etc} 'url': 'https://www.youtube.com/playlist?list=PLAROrg3NQn7cyu01HpOv5BWo217XWBZu0'},
		'num_playlists': 9
		}
		'''
		playlist_class_name = 'ytd-grid-playlist-renderer'
		self.get(channel_playlists_url)
		self.wait_for_page_load(playlist_class_name)
		elems = self.driver.find_elements_by_class_name(playlist_class_name)
		num_playlists = 0
		playlists_info = {}
		for playlist_counter in range(0, len(elems), 6): # every 6 elements there is a new playlist (could change in the future)
			num_videos = elems[playlist_counter].text
			title = elems[playlist_counter +1].text
			link =elems[playlist_counter +5].find_element_by_tag_name('a').get_attribute('href')
			playlists_info[title] = {'_number_of_videos':num_videos.split('\n')[0], "url":link}
			num_playlists += 1

		for playlistName in playlists_info.keys():
			# pdb.set_trace()
			playlist = playlists_info[playlistName]
			url = playlist["url"]
			_, vids = self.get_video_info_from_playlist(url)
			playlist["videos"] = vids

		playlists_info['num_playlists'] = num_playlists

		return playlists_info

	def get_all_uploads_playlist_url(self, videos_tab_link:str)->str:
		''' takes the link that you get after you press videos in the channel tab, example link input
		https://www.youtube.com/user/FireSymphoney/videos'''
		self.get(videos_tab_link)
		self.wait_for_page_load('play-all', "id")
		elem = self.driver.find_element_by_id('play-all').find_element_by_class_name('yt-simple-endpoint')
		all_uploads_url = elem.get_attribute('href')
		all_uploads_url = all_uploads_url.split('&')[0] # get rid of the query
		return all_uploads_url


	def get_video_info_from_playlist(self, playlist_url):
		'''takes playlist url, returns the number of videos in that playlist and an object {"video1Title": "video1url", video2:url ... and so on}
		example playlist url https://www.youtube.com/playlist?list=UU6mIxFTvXkWQVEHPsEdflzQ'''
		self.get(playlist_url)
		containers_tag = 'ytd-playlist-video-renderer'
		self.wait_for_page_load(containers_tag)
		try:
			# we get the number of videos from the playlist sidebar, only works if there's more than one video, if there's more an exception will be triggered and we have to catch that exception
			num_videos = self.driver.find_element_by_xpath("/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-playlist-sidebar-renderer/div/ytd-playlist-sidebar-primary-info-renderer/div[1]/yt-formatted-string[1]/span[1]").text
			num_videos = num_videos.replace(',', '')
			num_videos = int(num_videos)
		except NoSuchElementException:
			# There is an edge case when the playlist has only one video, and in that case the html xpath is different and the element innner html is not just a number
			#  it is something like this '1 video'
			xpath = '/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-playlist-sidebar-renderer/div/ytd-playlist-sidebar-primary-info-renderer/div[1]/yt-formatted-string[1]'
			num_videos = self.driver.find_element_by_xpath(xpath).text
			num_videos = num_videos.split(' ')[0]
			num_videos = int(num_videos.replace(',', ''))
		except Exception as e:
			traceback.print_exc()
			raise "Scrapper error, didnt find element"

		i = 0
		vids = {} # this is the videos we keep from scrapping
		infinite_loop_saftey = 10 #if we go through the program this many times without changes to the main list we will shut the while loop down
		useless_loops_counter = 0 # to protect us against the infinite while loops that are possible in case i never increments above a certain thing
		all_videos_links_with_duplicates = []
		all_videos_titles_with_duplicates = []
		while i  < num_videos:
			# this only shows the first 100 videos or so, you need to keep scrolling down to load the rest
			videos_batch = self.driver.find_elements_by_tag_name(containers_tag) # this updates everytime we scroll down
			for video_container in videos_batch:
				video = video_container.find_elements_by_id('video-title')[0]
				link = video.get_attribute('href')
				all_videos_links_with_duplicates.append(link)
				title = video.get_attribute('title')
				all_videos_titles_with_duplicates.append(title)
				
				# catches videos we dont have
				if not (title in vids.keys()):
					vids[title] = link
					i += 1
					useless_loops_counter = 0

				# catches videos that we dont have if they have the same name as a video we already have
				elif vids[title] != link:
					# we have a duplicate name but the video url they point is different
					duplicate_title = title + "_" +str(i) # the link is different so we add the video but we change the name a bit
					vids[duplicate_title]=link
					i += 1
					useless_loops_counter = 0
				
			useless_loops_counter +=1
			if useless_loops_counter >= infinite_loop_saftey:
				obtained_videos_num = len(vids.keys())
				self.log(f'couldnt get all videos from the playlist as some videos are hidden or something, got {obtained_videos_num}/{num_videos} for playlist {playlist_url}', level="warn")
				break_while_loop = True
				break

			self.scroll_down()
			time.sleep(self.scroll_wait)
		
		num_videos_real = len(vids.keys()) # we want the true number of videos without the hidden videos
		x = min(abs(num_videos_real - num_videos), 10)
		if(x >= 10):
			self.log(f"Warning, this playlist has many videos not availabe for download {playlist_url}")

		return num_videos_real, vids

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



# a = get_playlists_info(c, driver)
# print(a)

# cc = 'https://www.youtube.com/c/greatscottlab/videos'
# aa = get_all_uploads_playlist_url(cc, driver)
# print(aa)

# s = ChannelScrapper("blah", headless=False, default_wait=1)
# a = s.get_channel_about("https://www.youtube.com/c/ElectricianU/about")
# print(a)

def tests():
	s = ChannelScrapper("https://www.youtube.com/user/FireSymphoney/featured", headless=False)
	num, videos = s.get_video_info_from_playlist("https://www.youtube.com/playlist?list=UU6mIxFTvXkWQVEHPsEdflzQ")
	assert type(num) == int, "type of number of videos should be an int"
	assert type(videos) == dict, "type of videos must be dict"

	url = s.get_all_uploads_playlist_url('https://www.youtube.com/c/greatscottlab/videos')
	assert type(url) == str, "all uploads playlist url should be a string"

	pl_url = 'https://www.youtube.com/c/greatscottlab/playlists'
	playListInfo = s.get_playlists_info(pl_url)
	assert type(playListInfo) == dict, "the info should be dict"
	# pdb.set_trace()

# tests()

# c = "https://www.youtube.com/c/greatscottlab/playlists"
# s = ChannelScrapper(c, headless=False)
# playlist_info = s.get_playlists_info(c)
# print(playlist_info)
# # debug commands

'''
d = webdriver.Firefox()
url = "https://www.youtube.com/c/greatscottlab/videos"
d.get(url)
'''





'''
--- Channel backup

There are videos in 'all uploads' that are not in any of the playlists, there are also videos in the playlists that could are not in the 'all uploads' for example when a video is restricted and viewable only for ppl with the link and the link in the playlist
My strategy: find all videos in 'all uploads' and keep a hashmap where every playlist title is the key, and the value is a child hashmap that contains the videos in that playlist So at first 'all uploads' key will be populated with video names key and links as values, and then the same will happen for every
playlist.  So now we will have a hasmap where keys are playlist names and values are  another hash maps that has video names for keys and values are the video urls. 

After that all of the urls will be combined in one set, and downloaded

 {
	"PlayList1" : {
		"playlist-info": {
			"playlistLink" : "url-playlist",
			"number_of_videos" : 300
		}
		"video1_title": "video1 url",
		"video2_title": "video2_url",
		...},
	"PlayList2" : {...}
	"AllUploads" : {...}

	and so on ...
	}
}



'''