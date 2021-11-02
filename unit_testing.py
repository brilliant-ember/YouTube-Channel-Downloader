#### unit testing
# video = "https://www.youtube.com/watch?v=isutYMU2HHU"
# channel = "https://www.youtube.com/c/greatscottlab"
# d = Downloader(channel)
# d.download_video(video)
# d.download_all_videos_from_channel()

## Expect that it wrote the json file testing with the passed dict, and an _updates_dates key
# {
#     "title": "url",
#     "_number_of_videos": 1,
#     "_update_dates": {
#         "31/10/2021 05:24:06": "initial install"
#     }
# }
# d.write_playlist_info_json("testing", {"title":"url", NUMBERVIDEOSKEY:1})

# expects that it updates the testing json file with the new key and it mentiones what keys got added
# {
#     "title": "url",
#     "title2": "url2",
#     "_number_of_videos": 2,
#     "_update_dates": {
#         "31/10/2021 05:35:20": "initial install",
#         "31/10/2021 05:35:49": {
#             "new_entries_since_last_backup": [
#                 "title2"
#             ],
#             "removed_entries_since_last_backup": []
#         }
#     }
# }
# d.write_playlist_info_json("testing", {"title":"url", "title2":"url2", NUMBERVIDEOSKEY:2})



# # expects that it updates the testing json file with the new key and it mentiones what keys got added and what keys got removed
# even if a video got removed from the channel we should still retain a copy, so we should increment the number of videos
# {
#     "title2": "url2",
#     "title3": "url3",
#     "_number_of_videos": 3,
#     "title": "url",
#     "_update_dates": {
#         "31/10/2021 05:35:20": "initial install",
#         "31/10/2021 05:35:49": {
#             "new_entries_since_last_backup": [
#                 "title2"
#             ],
#             "removed_entries_since_last_backup": []
#         },
#         "31/10/2021 05:37:22": {
#             "new_entries_since_last_backup": [
#                 "title3"
#             ],
#             "removed_entries_since_last_backup": [
#                 "title"
#             ]
#         }
#     }
# }
# d.write_playlist_info_json("testing", {"title2":"url2", "title3":"url3", NUMBERVIDEOSKEY:3})

