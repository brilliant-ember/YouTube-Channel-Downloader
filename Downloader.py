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
import pdb
from pytube import YouTube
from pytube.extract import channel_name, publish_date
from pytube.request import get, head
from Scrapper import ChannelScrapper
from Logger import Log
from utils import get_now_date, compare_dicts, get_days_between_dates, over_write_json_file,read_json_file, DATEKEY, NUMBERVIDEOSKEY, ALL_UPLOADS_PLAYLIST_NAME, remove_slash_from_strings
import os
from sys import stdout, exit
from signal import signal, SIGINT
import shutil
import traceback


class Downloader():
	def __init__(self, channel_url, max_update_lag = 0, browser_wait = 3):

		## things needed for first initalization in order
		self.root_path = "youtube_backup"
		self.init_root_dir()
		log_file_path = os.path.join(self.root_path, "logfile.txt")
		self.logger = Log(log_file_path) # the logger must follow the init root dir directly
		self.log = self.logger.log #make an alias to the Log.log() function so I don't have to type it all the time
		self.scrapper = ChannelScrapper(channel_url, self.logger, headless=False, default_wait=browser_wait)
		self.channel_name = remove_slash_from_strings(fr"{self.scrapper.get_channel_name()}")
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
		self.download_in_progress = False
		self.allow_download = True
		self.max_update_lag = max_update_lag # scrape the channel if the current json record is more than x days old, put zero to scrape the channel once regardless of the freshness of the record
		
		self.log(f'Bismillah! initialized a Download for channel {self.channel_name} at {self.channel_path}', print_log=True)
		
	
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
		if (self.download_in_progress):
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
			self.log(f"failed to write video info json object for {self.playlists_path}", level="error")
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

	def download_all_videos_from_channel(self)-> None:
		self.log("Attempting to download All Uploads playlist")
		all_videos_info = self.get_all_uploads_playlist_data()
		num_vids = all_videos_info.pop(NUMBERVIDEOSKEY) # since we don't wanna iterate over the number of videos
		all_videos_info.pop(DATEKEY) # since we dont wanna iternate over the date
		videos_counter = 0
		for link in all_videos_info.values():
			self.download_video(link)
			videos_counter += 1
			if not (self.allow_download):
				break
		if videos_counter == num_vids:
			self.log(f"WOOHOO! Successfully Downloaded all the channel videos! ---- {self.all_uploads_url}")
			self.log("Goodbye and God bless you!")
		else:
			self.log(f"There was a problem and I couldnt download all the videos... Downloaded {videos_counter} out of {num_vids} for {self.all_uploads_url}")

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
		channel_info["url"] = self.channel_url
		channel_info[DATEKEY] = get_now_date()
		try:
			json_file_path = os.path.join(self.info_path, "channel_info.json")
			over_write_json_file(json_file_path, channel_info)
			self.log(f'Wrote the json file for channel info at {json_file_path}')

		except Exception as e:
			self.log(f"failed to write channell info json object for {json_file_path}", level="error")
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
	
