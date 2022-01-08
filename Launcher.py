"""
Channel url must be in on of these forms
https://www.youtube.com/user/channel_name
https://www.youtube.com/channel/special_code_for_channel
https://www.youtube.com/c/channel_name/
Make sure there's no '/featured' or '/videos' or '/' anything at the end of the link
Examples of valid channel urls
https://www.youtube.com/channel/UCVryWqJ4cSlbTSETBHpBUWw
https://www.youtube.com/c/iforce2d/
https://www.youtube.com/user/eaterbc
"""

### Edit this channel url with the channel you want to backup

channel_url = "https://www.youtube.com/user/FireSymphoney"
playlist_url = "https://www.youtube.com/playlist?list=PLD1pHgB031cn-CzKqOuJp9NoVKI9xFDV6"
single_video_url = "https://www.youtube.com/watch?v=OhnLmp7a_7w"

## How long should the automatic browser window wait until page loads, if you have slow internet connection you should increase this number
browser_wait = 1

#### Don't edit past this line #################

from Downloader import Downloader
from utils import Quality

d = Downloader(channel_url ,browser_wait=browser_wait, quality=Quality.LOW)
d.download_all_videos_from_channel() # backup the entire channel

# d.download_specific_playlist(playlist_url) # backup a certain playlist
# d.download_specific_video(single_video_url) #backup a certain video


