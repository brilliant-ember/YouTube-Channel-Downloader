import sys
import os

cwd = os.getcwd()
# src_code_wd = os.path.split(cwd)[0]
# adding source code folder to the system path so I can import 
sys.path.insert(0, cwd)

from utils import Keys, read_json_file
import unittest
from Channel import Channel
from unittest import mock
from unittest.mock import patch

class TestDownloader(unittest.TestCase):
	def setUp(self) -> None:
		return super().setUp()

	def test_extract_playlists_from_json_payload(self):
		# a playlist where we need to scroll
		channel = Channel()
		all_titles = ['バトルofダンディ（BOD）', 'お父さんは心配症', 'Hallo BABY', 'オレ料理正直ランキング', 'キャンプ場にログハウスをDIY - MCV', 'ゾンビ肉シリーズ', 'VEMANJI - 自販機ゲーム - 指定された様々な自販機の食べ物を食い尽くし、不思議な世界から無事に戻る事は出来るのか？【ベマンジ】', 'THE DRUNK  - ミッションをこなしルーレットにより指定された大量のビールを飲み打ち上げ会場へのヒントを手に入れろ！【ジ・ドランク】', '世界一運の悪い男が挑むスーパーアクション Die easy｜A Good Day to Die Hard （ダイイージー）', '干支チェンジ | Remake Chinese Zodiac', '【WRG】ワールドレートゲーム', '12/2018★365シリーズ一気見だぜ！', '11/2018★365シリーズ一気見だぜ', '食べ歩きかるた山手線の細道', '10/2018★365シリーズ一気見だぜ！', '09/2018★365シリーズ一気見だぜ！', '08/2018★365シリーズ一気見だぜ！', '長編10分以上の動画！！暇つぶしに最適', '07/2018★365シリーズ一気見だぜ！', '06/2018★365シリーズ一気見だぜ！', '10次会するまで帰れま10！！！', '大食いぶらり旅', '笑ってはいけない', '05/2018★365シリーズ一気見だぜ！', '04/2018★365シリーズ一気見だぜ！', '03/2018★365シリーズ一気見だぜ！', '本格ピザ窯作り！', '02/2018★365シリーズ一気見だぜ！', '01/2018★365シリーズ一気見！', '12/2017★365シリーズ一気見！']
		num_videos = 30
		j = read_json_file(cwd + "/tests/fixtures/all_channel_created_playlists/all_channel_playlist_scroll/initial_get_request_payload.json")
		need_to_scroll = channel.extract_all_playlists_from_a_playlists_category_json_response(j)
		playlists = channel.created_playlists_metadata
		titles = []
		for p in playlists.values():
			titles.append(p[Keys.PLAYLIST_NAME])
			
		assert all_titles == titles, "didn't download all playlist titles"
		assert len(playlists) == num_videos, "didn't get all playlists"
		assert need_to_scroll, "didn't know that we should have scrolled"

		# a playlist where we don't need to scroll
		channel = Channel()
		all_titles = ['Testing Circuits I found on the Internet!', 'Q&A', 'DIY or Buy', '3D Printing', 'Fix It!', 'Electronics Projects', 'HACKED!', 'VS', 'Electronic Basics']
		num_videos = 9
		j = read_json_file(cwd + "/tests/fixtures/all_channel_created_playlists/created_playlists_no_scroll_json_resp.json")
		need_to_scroll = channel.extract_all_playlists_from_a_playlists_category_json_response(j)
		playlists = channel.created_playlists_metadata
		titles = []
		for p in playlists.values():
			titles.append(p[Keys.PLAYLIST_NAME])
			
		assert all_titles == titles, "didn't download all playlist titles"
		assert len(playlists) == num_videos, "didn't get all playlists"
		assert need_to_scroll == False, "Thought that we should scroll when we shouldn't"


if __name__ == '__main__':
	unittest.main()