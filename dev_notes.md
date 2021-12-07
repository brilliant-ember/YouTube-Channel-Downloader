## Notes

- `tests/fixtures/get_response/datachannel[slash]playlists.json` this is the variable 'var ytInitialData' extracted from the GET request of 'https://www.youtube.com/c/learnelectronics/playlists' 
the complete response is in  YouTube-Channel-Downloader/tests/fixtures/get_response/complete_channel[slash]playlists
- the url for a specific playlist is `https://www.youtube.com/c/learnelectronics/playlists?list=playlist_id`



## Commands
- Run unit tests `python3 tests/Downloader_test.py
- run a single test, write the testing function name as a string after -k ` python3 tests/Downloader_test.py -k "test_generate_playlist_url"`