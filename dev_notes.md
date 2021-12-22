## Notes

- `tests/fixtures/get_response/payload.json` this is the variable 'var ytInitialData' extracted from the GET request of 'https://www.youtube.com/c/learnelectronics/playlists' 
the complete response is in  YouTube-Channel-Downloader/tests/fixtures/get_response/full_response
- the url for a specific playlist is `https://www.youtube.com/c/learnelectronics/playlists?list=playlist_id`
- tests in `/tests/functionality_testing`  are not typical unit tests, they do network requests to check if youtube has changed the response format that we can't parse it anymore.
- Headless mode doesn't work, it yields timeout error when it tries to get all uploads playlist

---

### About dynamic scrolling in playlists

#### inside a specific playlist
If the playlist has more than 100 videos youtube will only render the first 100 videos (each video is represented with the key `playlistVideoRenderer`), to get the rest you need to scroll down.
Youtube passes a certain key in the json file to signal that the playlist needs to be scrolled down to get the rest of the videos, that key is `continuationItemRenderer`.
In the youtube UI when you reach the end of the 100 videos a loading spinner will appear at the end, when it does the browser will do a POST request that has values of the key `continuationItemRenderer` and youtube server will respond by sending back a json object that has some of the remaining videos and if there are more remaining videos that didn't get sent over then that json will contain another `continuationItemRenderer` which has data on how to scroll down again if we need to get the rest of the videos. On the last batch of videos the json response will not have the `continuationItemRenderer` key anymore since there's no more videos that we can get if we scroll down, ie we reached the end of the playlist.

Example playlist url : https://www.youtube.com/playlist?list=PL0o_zxa4K1BWYThyV4T2Allw6zY0jEumv

#### Inside the channel's list of playlists
If the channel has more than just one playlist you will see all of the playlists in `channel/playlists` however if they have a lot of playlists there will be a horizontal scroll option to see their playlists in different categories that they created, example categories are Created Playlists, Saved Playlists ...etc

right now it seems that adding `?view=1` to the tail of the url can give us the created videos playlist 

examples : `youtube.com/c/MegwinTVOfficial/playlists` and `https://www.youtube.com/c/MegwinTVOfficial/playlists?view=1`

<br>

### About all uploads playlist not truly having all videos

There are videos in 'all uploads' that are not in any of the playlists, there are also videos in the playlists that could are not in the 'all uploads' for example when a video is restricted and viewable only for ppl with the link and the link in the playlist
My strategy: find all videos in 'all uploads' and all other playlists and keep a hashmap of all their videos

After that all of the urls will be combined in one set, and downloaded. right now we only do all uploads and dont combine all playlists to it. this is a TODO

---

## Commands
- Run unit tests `python3 tests/Downloader_test.py
- run a single test, write the testing function name as a string after -k ` python3 tests/Downloader_test.py -k "test_generate_playlist_url"`