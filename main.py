import discord
import json
import requests
import sys
import time
import settings
import asyncio
from datetime import datetime, timedelta
from requests_oauthlib import OAuth1Session
from discord import app_commands

#Steam
STEAM_API_KEY = settings.STEAM_API_KEY
STEAM_ID = settings.STEAM_ID

# 以前と同じように、メッセージの重複を防ぐための変数
msged_content = "Save_content"
DIS_API_KEY = settings.DIS_API_KEY
map_list = {"Kings Canyon": {"name": "キングスキャニオン"}, "World's Edge": {"name": "ワールズエッジ"},
				"Olympus": {"name": "オリンパス"}, "Storm Point": {"name": "ストームポイント"}, 'Broken Moon': {"name": "ブロークンムーン"}}

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

active_channels = []  # ONにしたチャンネルのリスト

async def send_map_every_30_seconds():
	await client.wait_until_ready()
	while True:
		try:
			# マップローテーションの取得
			url_map = "https://api.mozambiquehe.re/maprotation?version=2&auth="
			als_api_key = settings.ALS_API_KEY
			res_map = requests.get(url_map + als_api_key)
			json_map = json.loads(res_map.text)
			if res_map.status_code == 200:
				print("(ALS)Request succeeded")
			else:
				print("(ALS)Request failed with " + str(res_map.status_code))
		except Exception as e:
			print(f"エラーが発生しました: {e}")
			continue  # 最初からやり直す

		# カジュアルのマップローテーションを取得
		battle_royale_current_map = json_map['battle_royale']['current']['map']
		battle_royale_current_map_start = json_map['battle_royale']['current']['readableDate_start']
		battle_royale_current_map_end = json_map['battle_royale']['current']['readableDate_end']
		battle_royale_next_map = json_map['battle_royale']['next']['map']
		battle_royale_next_map_start = json_map['battle_royale']['next']['readableDate_start']
		battle_royale_next_map_end = json_map['battle_royale']['next']['readableDate_end']
		# ランクのマップローテーションを取得
		ranked_current_map = json_map['ranked']['current']['map']
		ranked_current_map_start = json_map['ranked']['current']['readableDate_start']
		ranked_current_map_end = json_map['ranked']['current']['readableDate_end']
		ranked_next_map = json_map['ranked']['next']['map']
		ranked_next_map_start = json_map['ranked']['next']['readableDate_start']
		ranked_next_map_end = json_map['ranked']['next']['readableDate_end']

		# カジュアルをJSTに変換
		battle_royale_current_map_start_jst = datetime.strptime(
			battle_royale_current_map_start, '%Y-%m-%d %H:%M:%S')
		battle_royale_current_map_start_jst = battle_royale_current_map_start_jst + timedelta(hours=9)
		battle_royale_current_map_end_jst = datetime.strptime(
			battle_royale_current_map_end, '%Y-%m-%d %H:%M:%S')
		battle_royale_current_map_end_jst = battle_royale_current_map_end_jst + timedelta(hours=9)
		battle_royale_next_map_start_jst = datetime.strptime(
			battle_royale_next_map_start, '%Y-%m-%d %H:%M:%S')
		battle_royale_next_map_start_jst = battle_royale_next_map_start_jst + timedelta(hours=9)
		battle_royale_next_map_end_jst = datetime.strptime(
			battle_royale_next_map_end, '%Y-%m-%d %H:%M:%S')
		battle_royale_next_map_end_jst = battle_royale_next_map_end_jst + timedelta(hours=9)

		# ランクをJSTに変換
		ranked_current_map_start_jst = datetime.strptime(
			ranked_current_map_start, '%Y-%m-%d %H:%M:%S')
		ranked_current_map_start_jst = ranked_current_map_start_jst + timedelta(hours=9)
		ranked_current_map_end_jst = datetime.strptime(
			ranked_current_map_end, '%Y-%m-%d %H:%M:%S')
		ranked_current_map_end_jst = ranked_current_map_end_jst + timedelta(hours=9)
		ranked_next_map_start_jst = datetime.strptime(
			ranked_next_map_start, '%Y-%m-%d %H:%M:%S')
		ranked_next_map_start_jst = ranked_next_map_start_jst + timedelta(hours=9)
		ranked_next_map_end_jst = datetime.strptime(
			ranked_next_map_end, '%Y-%m-%d %H:%M:%S')
		ranked_next_map_end_jst = ranked_next_map_end_jst + timedelta(hours=9)


		# メッセージ内容
		msg_content = (
		"[カジュアル]\n"
		+ "現在("
		+ battle_royale_current_map_start_jst.strftime('%H:%M')
		+ "～"
		+ battle_royale_current_map_end_jst.strftime('%H:%M')
		+ ")⇒"
		+ map_list[battle_royale_current_map]['name']
		+ "\n"
		+ "次("
		+ battle_royale_next_map_start_jst.strftime('%H:%M')
		+ "～"
		+ battle_royale_next_map_end_jst.strftime('%H:%M')
		+ ")⇒"
		+ map_list[battle_royale_next_map]['name']
		+ "\n\n"
		+ "[ランク] ("
		+ ranked_next_map_start_jst.strftime('%H:%M')
		+ "切り替わり)\n"
		+ "現在⇒"
		+ map_list[ranked_current_map]['name']
		+ "\n"
		+ "次⇒"
		+ map_list[ranked_next_map]['name']
		)

		global msged_content

		if msged_content == msg_content:
			print('既にメッセージを送信済みです')
		else:
			# メッセージを送信(まだmsg_contentを送っていないとき)
			for channel in active_channels:
				target_channel = client.get_channel(channel)
				if target_channel:
					await target_channel.send(msg_content)
				# 送信済メッセージの内容を保存
				msged_content = msg_content
				print('メッセージを送信しました')
		await asyncio.sleep(30)  # 30秒待つ

@client.event
async def on_ready():
    print("起動完了")
    await tree.sync()  # スラッシュコマンドを同期
    client.loop.create_task(send_map_every_30_seconds())  # 30秒ごとにマップを送るタスクを作る

@tree.command(name="togglemap", description="マップローテーションの送信をON/OFFします。")
async def toggle_command(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    if channel_id in active_channels:
        active_channels.remove(channel_id)
        await interaction.response.send_message("このチャンネルでのマップローテーションの送信を停止します。", ephemeral=True)
    else:
        active_channels.append(channel_id)
        await interaction.response.send_message("このチャンネルでマップローテーションを送ります。", ephemeral=True)

@tree.command(name="myid", description="SteamIDを送信します。")
async def myid_command(interaction: discord.Interaction):
	url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={STEAM_ID}"
	response = requests.get(url)
	data = response.json()
	username = data['response']['players'][0]['personaname']
	await interaction.response.send_message(f"ID: {username}")

client.run(DIS_API_KEY)
