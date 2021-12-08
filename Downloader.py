## interface
''' Flow 1 backup entire channel.
- user puts a channel url. program (P) goes to the "all uploaded" playlists and downloads all 
of them and puts them in "videos" folder, it will also download all descriptions, states and thumbnails url
 then puts them accordingly in files with the same name as the video

Note some videos exist in a playlist but not in the 'all uploads' playlist!!! 
This happens if a video link is 'not listed' or points to another channel's video.


Flow 2 download a single playlist - TODO

'''

## Glossary
'''
AUP : all uploads playlist
mVideo: muted video,adaptive video it doesn't come with sound aka adaptive_video
video: has both video and audio combined
playlist: the video playlist whose url we passed
'''

from genericpath import exists
from pytube import YouTube
from pytube.extract import channel_name, publish_date
from pytube.request import get, head
from Scrapper import ChannelScrapper
from Logger import Log
from utils import get_now_date, compare_dicts, get_days_between_dates, over_write_json_file,read_json_file,CREATED_PLAYLISTS,NUMBER_OF_PLAYLISTS ,DATEKEY, NUMBERVIDEOSKEY, ALL_UPLOADS_PLAYLIST_NAME, remove_slash_from_strings
import response_utils
import os
from sys import stdout, exit
from signal import signal, SIGINT
import shutil
import traceback
import re
import time

class Downloader():
	def __init__(self, channel_url, max_update_lag = 0, browser_wait = 3, headless=False):

		## things needed for first initalization in order
		self.root_path = "youtube_backup"
		self.init_root_dir()
		log_file_path = os.path.join(self.root_path, "logfile.txt")
		self.logger = Log(log_file_path) # the logger must follow the init root dir directly
		self.log = self.logger.log #make an alias to the Log.log() function so I don't have to type it all the time
		self.scrapper = ChannelScrapper(channel_url, self.logger, headless=headless, default_wait=browser_wait)
		self.channel_name = remove_slash_from_strings(fr"{self.scrapper.get_channel_name()}")
		self.handle_null_channel_name(browser_wait, channel_url)
		
		signal(SIGINT, self.graceful_exit)
		#######

		## init paths
		self.channel_path = os.path.join(self.root_path, self.channel_name)
		self.info_path = os.path.join(self.channel_path, "info")
		self.playlists_path = os.path.join(self.info_path, "playlists")
		self.current_video_output_path = ""
		####

		self.init_dirs()

		## init urls
		self.channel_url = channel_url
		self.all_uploads_url = channel_url + "/videos" # example https://www.youtube.com/user/FireSymphoney/videos
		self.playlists_url = channel_url + "/playlists" # https://www.youtube.com/user/FireSymphoney/playlists
		self.about_url = channel_url + "/about"
		####
		
		self.current_video_information = {}
		self.failed_videos = {} # a title:url record of all failed downloads
		self.download_in_progress = False
		self.allow_download = True
		self.max_update_lag = max_update_lag # scrape the channel if the current json record is more than x days old, put zero to scrape the channel once regardless of the freshness of the record
		self.num_created_video_dirs = 0
		
		self.log(f'Bismillah! initialized a Download for channel {self.channel_name} at {self.channel_path}', print_log=True)
		
	def handle_null_channel_name(self, browser_wait:int, channel_url:str):
		if not self.channel_name or self.channel_name =="None":
			pause_time = browser_wait+5
			time.sleep(pause_time)
			self.channel_name = remove_slash_from_strings(fr"{self.scrapper.get_channel_name()}") # try again
			if not self.channel_name or self.channel_name =="None":
				self.log(f"Fatal Error channel name is null for {channel_url} ", 'critical')
				raise "Critical error not downloading {} because channel name was null, please try again"
	def init_root_dir(self):
		if not os.path.exists(self.root_path):
			os.mkdir(self.root_path)

	def init_dirs(self):
		if not os.path.exists(self.channel_path):
			os.mkdir(self.channel_path)
			self.log(f'Created channel dir {self.channel_path}')

		if not os.path.exists(self.info_path):
			os.mkdir(self.info_path)
			self.log(f'Created info dir {self.info_path}')
		
		if not os.path.exists(self.playlists_path):
			os.mkdir(self.playlists_path)
			self.log(f'Created playlists dir {self.playlists_path}')
		
	def graceful_exit(self, sig, frame):
		self.log('You pressed Ctrl+C!')
		self.allow_download = False
		self.scrapper.__del__()
		if (self.download_in_progress and self.current_video_output_path):
			msg = "There was a download in progress during exit signal, will delete that video to avoid having courrupted files"
			msg2 = f"will delete the last downloaded video at {self.current_video_output_path}"
			self.log(msg, "warn")
			self.log(msg2, "warn")
			self.delete_file(self.current_video_output_path)


		self.logger.exit()
		exit(0)
		
	def delete_file(self, path:str):
		if path:
			try:
				shutil.rmtree(path)
				msg = f"Delete complete {path}"
				self.log(msg, "warn")
			except OSError as e:
				#TODO make this use the handle_error function
				msg = "Error: %s - %s." % (e.filename, e.strerror)
				self.log(msg, "warn")

	def prepare_download_dir(self, video_title:str ) -> str:
		'''Creates the file tree needed for the download and return the directory where the video
		should be downloaded to.
		If video exists it will raise VideoExistsError as the file is already there,
		 because it should have been deleted if there was a partial download,
		 otherwise will return the path dir of the video'''
		video_title = remove_slash_from_strings(video_title)
		video_path = os.path.join(self.channel_path, "videos", video_title)
		if not os.path.exists(video_path):
			self.log(f'Created video dir {video_path}')
			os.makedirs(video_path)
			return video_path

		raise VideoExistsError

	def write_downloaded_video_info_json(self)-> None:
		'''Writes the video information to a json file at the self.current_video_output_path directory'''
		try:
			json_file_path = os.path.join(self.current_video_output_path, "info.json")
			over_write_json_file(json_file_path, self.current_video_information)
			self.log(f'Wrote the json file for video at {self.current_video_output_path}')

		except Exception as e:
			self.log(f"failed to write video info json object for {self.current_video_output_path}", level="error")
			self.handle_exception(e)


	def write_playlist_info_json(self, playlist_name:str, playlist_info:dict)-> None:
		'''Writes the playlist information to a json file at the self.=playlists_dir directory'''
		playlist_name = remove_slash_from_strings(playlist_name)
		try:
			json_file_path = os.path.join(self.playlists_path, f"{playlist_name}.json")
			if os.path.isfile(json_file_path):
				json_dict = read_json_file(json_file_path) # this is the old file
				# keep a record of what videos the channel uploaded and what videos got removed
				# this also records removed playlists and new playlists
				last_update = json_dict.pop(DATEKEY) # the new dict will not have this, so remove it while we compare
				added_stuff_since_last_backup, channel_removed_stuff = compare_dicts(json_dict, playlist_info )
				json_dict[DATEKEY] = last_update # return it back after comparing both dicts
				json_dict = {**playlist_info, **json_dict} # merge the two dicts, if there's overlapping keys, then use the one from the old file ie json_dict
				json_dict[DATEKEY][str(get_now_date())] = {"new_entries_since_last_backup": added_stuff_since_last_backup, "removed_entries_since_last_backup":channel_removed_stuff}
				json_dict[NUMBERVIDEOSKEY] = max(playlist_info[NUMBERVIDEOSKEY],json_dict[NUMBERVIDEOSKEY]  ) # since we are incrementing videos we want the total number of videos we have locally
				over_write_json_file(json_file_path, json_dict)
			else:
				playlist_info[DATEKEY] = {get_now_date(): "initial install"}
				over_write_json_file(json_file_path, playlist_info)
			self.log(f'Wrote the json file for {playlist_name} at {self.playlists_path}')

		except Exception as e:
			self.log(f"failed to write playlist info json object for {playlist_name} at {self.playlists_path}", level="error")
			self.handle_exception(e)
			

	def download_video(self, video_url:str, progressive=True) -> None:
		'''progressive is limited to 720p max, but is both video and audio together, the other type 
		is called DASH aka adaptive, it is higher resolution but needs to download video and audio sepertely and
		mix them after download'''

		error_msg = f"Failed to download {video_url} with progressive={progressive}"
		if(self.allow_download == False):
			self.log(f"Download stopped, will not download {video_url}")
			return

		self.download_in_progress = True

		try:
			yt = YouTube(video_url)
			self.current_video_information = {
				"title" : yt.title,
				"description" : yt.description ,
				"rating" : yt.rating,
				"views" : yt.views,
				"publish_date" : yt.publish_date,
				"length" : yt.length ,
				"thumbnail_url" : yt.thumbnail_url,
				"channel" : yt.author,
				"video_id" : yt.video_id,
				"date_of_download" : get_now_date(),
				"video_url": video_url,
				"keywords" : yt.keywords,
			}
			self.current_video_output_path = self.prepare_download_dir(fr"{yt.title}")

			def download_callback(stream, file_path:str):
				self.log(f'Downloaded {file_path}', print_log=True)
				self.write_downloaded_video_info_json()

			def progress_callback(stream, chunk, bytes_remaining):
				filesize = stream.filesize
				current = ((filesize - bytes_remaining)/filesize)
				percent = ('{0:.1f}').format(current*100)
				progress = int(50*current)
				status = '█' * progress + '-' * (50 - progress)
				stdout.write(' ↳ |{bar}| {video} | {percent}%\r'.format(bar=status,video=self.current_video_information["title"], percent=percent))
				stdout.flush()

			yt.register_on_complete_callback(download_callback)
			yt.register_on_progress_callback(progress_callback)
			
			if (progressive):
				# self.log(f"Attempt to download {title} with url {video_url}")
				yt.streams.get_highest_resolution().download(output_path=self.current_video_output_path)
		except VideoExistsError as ve:
			msg = f'''Video \"{self.current_video_information['title']}\" already exists, not downloading url {self.current_video_information['video_url']}'''
			self.log(msg, level="warning")
		except Exception as e:
			self.log(error_msg, level="error")
			self.handle_exception(e)
		finally:
			self.download_in_progress = False
			if self.did_download_fail(self.current_video_output_path):
				msg = f'''Failed to fully download \"{self.current_video_information['title']}\" will try again later {self.current_video_information['video_url']}'''
				self.log(msg, level="warning")
				self.failed_videos[self.current_video_information['title']] =  self.current_video_information["video_url"]
				self.log("deleting partial downloads if they exist")
				self.delete_file(self.current_video_output_path)
				

	def download_url_list(self, videos_url_list ):
		'''Takes a videos url list and loops over them to download each of them, return true when it finishes, otherwise returns null'''
		for link in videos_url_list:
			self.download_video(link)
			if not (self.allow_download):
				break
		return True

	def download_all_videos_from_channel(self)-> None:
		self.log("Attempting to download All Uploads playlist")
		all_videos_info = self.get_all_uploads_playlist_data()
		num_vids = all_videos_info.pop(NUMBERVIDEOSKEY) # since we don't wanna iterate over the number of videos
		all_videos_info.pop(DATEKEY) # since we dont wanna iterate over the date
		all_urls_list = list(all_videos_info.values())
		did_finish = self.download_url_list(all_urls_list)
		
		if did_finish:
			self.log(f"Finished going over all channel videos ---- {self.all_uploads_url}")
			self.log("God bless you!")
		else:
			self.log(f"There was a problem and I couldnt download all the videos... total downloads should be {num_vids} for {self.all_uploads_url}")
		self.finish_download_and_show_stats()

	def finish_download_and_show_stats(self):
		corrupted_downloads = self.validate_downloaded_videos() # this should be zero
		self.log(f"Created a total of {self.num_created_video_dirs} new video directories for {self.channel_name}")
		if len(corrupted_downloads) != 0:
			self.log(f"There are {len(corrupted_downloads)} corrupted downloads that should be deleted and repeated, please run the downloader again. here is a list: ", "error")
			self.log(str(corrupted_downloads))
			raise "Corrupted files downloaded"
		
		num_failed_downloads = len(self.failed_videos.keys())
		if num_failed_downloads > 0:
			self.log(f"{num_failed_downloads} videos failed to download, will try again")
			self.handle_failed_downloads()


		
	def handle_failed_downloads(self):
		self.log("Trying to retry failed downloads")
		list_of_urls = list(self.failed_videos.values())
		self.failed_videos = {} # reset it to empty
		self.download_url_list(list_of_urls)
		num_failed_downloads = len(self.failed_videos.keys())
		if num_failed_downloads > 0: # if we still have failed downloads we just write the file and move on
			self.log(f"{num_failed_downloads} videos failed to download, will try again")
			try:
				json_file_path = os.path.join(self.info_path, "failed_video_downloads.json")
				self.log(f"Failed again to download some videos, will record the list of failed downloads in this file and move on {json_file_path}", level="warning")
				over_write_json_file(json_file_path, self.failed_videos)
				self.log(f'Wrote the json file for failed videos at {json_file_path}')

			except Exception as e:
				self.log(f"failed to write failed videos info json object for {over_write_json_file}", level="error")
				self.handle_exception(e)



	def write_all_playlists_info(self)-> None:
		''' writes a json entry for each playlist which included all the videos in that playlist, this doesnt include the All Uploads playlist
		to do that use scrapper.get_all_uploads_playlist_url(self.all_uploads_url), which is already used in  download_all_videos_from_channel(self)'''
		self.log("Getting all of the playlists information...", print_log=True)
		all_playlists_info = self.scrapper.get_playlists_info(self.playlists_url)
		all_playlists_info.pop('num_playlists')
		for playlist in all_playlists_info.keys():
			self.write_playlist_info_json(playlist, all_playlists_info[playlist])

	def get_all_uploads_playlist_data(self) ->  dict :
		'''checks if we already have the links we need as a json file, if we do will read that json file and return a dict, otherwise will scrape the channel website then write the json file and finally return the channel info dict'''
		try:
			if self.should_update_json_record():
				# scrape the website in this case
				self.log(f"Current json is too old, will scrape the channel and create a new one")
				self.write_channel_info()
				all_videos_playlist_url = self.scrapper.get_all_uploads_playlist_url(self.all_uploads_url)
				self.write_all_playlists_info()
				# now we get all uploads playlist, note we should keep it in this order
				# writing all uploads playlists should happen last, as we need that to determine if we downloaded all playlists
				num_vids, all_videos_info = self.scrapper.get_video_info_from_playlist(all_videos_playlist_url)
				all_videos_info["videos"] = all_videos_info # abstract the videos info behind a key called videos
				all_videos_info[NUMBERVIDEOSKEY] = num_vids
				all_videos_info[DATEKEY] = get_now_date()
				self.write_playlist_info_json(ALL_UPLOADS_PLAYLIST_NAME , all_videos_info) 
				return all_videos_info
			else:
				# we shouldn't scrape the channel website, instead read the record directly from json
				self.log(f"Using current json record of the channel since it is still not too old")
				json_file_path = os.path.join(self.playlists_path, f"{ALL_UPLOADS_PLAYLIST_NAME}.json")
				json_dict = read_json_file(json_file_path)
				return json_dict
		except Exception as e:
			self.handle_exception(e)

	def write_channel_info(self) -> None:
		channel_info = self.scrapper.get_channel_about(self.about_url)
		all_playlists = response_utils.get_playlists_listing(self.playlists_url)
		channel_info["url"] = self.channel_url
		channel_info[DATEKEY] = get_now_date()
		channel_info[CREATED_PLAYLISTS] = all_playlists
		channel_info[NUMBER_OF_PLAYLISTS] = len(all_playlists)

		try:
			json_file_path = os.path.join(self.info_path, "channel_info.json")
			over_write_json_file(json_file_path, channel_info)
			self.log(f'Wrote the json file for channel info at {json_file_path}')

		except Exception as e:
			self.log(f"failed to write channel info json object for {json_file_path}", level="error")
			self.handle_exception(e)


	def should_update_json_record(self) -> bool:
		'''Checks if the current json records are fresh enough, if they are old returns true meaning we should update our records by scrapping'''
		try:
			playlists = os.listdir(self.playlists_path)
			if(len(playlists) == 0):
				return True 
			
			# all uploads playlist is downloaded last, so if it doesn't exist means that we didn't fetch all playlists and need to update
			all_uploads_file_path = os.path.join(self.playlists_path, f"{ALL_UPLOADS_PLAYLIST_NAME}.json")
			file_exists = os.path.isfile(all_uploads_file_path)
			if not file_exists:
				return True

			for pl in playlists:
				if (".json" in pl):
					pl = os.path.join(self.playlists_path, pl)
					json_dict = read_json_file(pl)
					date = list(json_dict[DATEKEY].keys())[-1] #example: '03/11/2021 05:46:32'
					date_now = get_now_date()
					days_delta = get_days_between_dates(date, date_now)
					if days_delta > self.max_update_lag:
						return True
		except Exception as e:
			self.handle_exception(e)
			return True # if we run into erros reading the files then scrape from online

		return False # no need to scrape the website 

	def handle_exception(self, e:Exception) -> None:
		self.log(repr(e), level="error")
		traceback.print_exc()
	
	def validate_downloaded_videos(self):
		'''Will go to each downloaded video folder anc checks if we have the video and the info json file,
		 it will also check if the the size of the files if more than 0 bytes. If the checks pass returns an empty list,
		  otherwise returns a dict of all the video folders that failed'''
		videos_dir = os.path.join(self.channel_path, "videos")
		failed_downloads = []
		for dir_path, _, _ in os.walk(videos_dir):
			if dir_path == videos_dir:
				continue # skip the iteration as this cannes /videos and we want /videos/actual_video
			if self.did_download_fail(dir_path):
				failed_downloads.append(dir_path)

			self.num_created_video_dirs = self.num_created_video_dirs + 1
		
		return failed_downloads

	def clean_bad_downloads(self):
		'''Will go to each downloaded video folder anc checks if we have the video and the info json file,
		 it will also check if the the size of the files if more than 0 bytes. If the checks fail will delete that bad download file.
		This method is called manually only for clean up of old downloads, before the implemntation of the current checks that delete the video as soon as it is not valid.
		 So this function should be regarded as a manual job to ensure goodness of downloads made before the implementation of the validators
		 '''
		self.log('Cleaning bad downloads up...')
		videos_dir = os.path.join(self.channel_path, "videos")
		for dir_path, _, _ in os.walk(videos_dir):
			if dir_path == videos_dir:
				continue # skip the iteration as this cannes /videos and we want /videos/actual_video
			if self.did_download_fail(dir_path):
				self.log("Clean up task, will delete {}".format(dir_path))
				self.delete_file(dir_path)

		


		
	
	def did_download_fail(self, video_dir:str):
		'''Returns True if video download failed and needs to be repeated, otherwise returns '''
		for dir_path, _, dir_files in os.walk(video_dir):
			if not len(dir_files) >= 2: # if we have less than two files, which are the info.json and video.mp4
				return True
			if not "info.json" in dir_files: # if we dont have the info json file
				return True
			is_there_mp4_file = False
			for f in dir_files:
				if re.search(".mp4$", f): # see if there's .mp4 at the end of one of the files
					is_there_mp4_file = True
				file_path = os.path.join(dir_path, f)
				if os.path.getsize(file_path) == 0:
					return True
			if not is_there_mp4_file:
				return True
		return False
		

			
class VideoExistsError(Exception):
# a custom exception if the video file already exists
     pass


video = "https://www.youtube.com/watch?v=isutYMU2HHU"
channel = "https://www.youtube.com/c/greatscottlab"
# d = Downloader(channel)
# d.write_channel_info()
# # d.download_video(video)
# # d.download_all_videos_from_channel()




def get_available_video_qualities():
	pass

def format_video():
	'''give user ability to change format to things like mp4, AVI, webm ...etc'''
	pass

def format_audio():
	pass

def get_highest_resolution_progressive():
	''' progressive is when both the audio and vidoe are combined max quality is 720
	in one file. Adaptive is when they are sepreate and it is of higher quality >720'''
	pass
def get_highest_resolution_adaptive():
	pass

def combine_adaptive_video_audio():
	pass
def download_adaptive_video():
	pass
def download_adpaptive_audio():
	pass

def get_videos_in_both_AUP_and_playlist(all_uploads_playlist_urls, playlists_urls ):
	'''returns the union of the AUP and the playlist urls'''
	return set(all_uploads_playlist_urls) & set(playlists_urls)
	
