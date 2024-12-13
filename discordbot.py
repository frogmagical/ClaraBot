import discord
import boto3
import json
import asyncio
from datetime import date, datetime, time

ssm = boto3.client("ssm")

# 環境変数からトークンを取得
response = ssm.get_parameter(
    Name="DISCORD_TOKEN",
    WithDecryption=False
)
DISCORD_TOKEN = response["Parameter"]["Value"]

# Intentsの設定
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# BOTへ接続するオブジェクトを定義
client = discord.Client(intents=intents)

with open("animal.json", "r", encoding="utf-8") as f:
    animal_dict = json.load(f)
    animal_names = animal_dict["animals"]

async def send_event_notifications():
    await client.wait_until_ready()
    channel_id = 981151248499769406 # 告知先チャンネルID
    channel = client.get_channel(channel_id)
    if channel is None:
        print("チャンネルが見つからなかった！")
        return

    while not client.is_closed():
        now = datetime.now()
        # 水曜日22:00のイベント
        if now.weekday() == 2 and now.time() >= time(22, 0) and now.time() < time(22, 1): 
            await channel.send("📢今日は水曜日！22時からチームオーダー消化会をするよ！")
        # 日曜日20:00のイベント
        elif now.weekday() == 6 and now.time() >= time(20, 0) and now.time() < time(20, 1):
            await channel.send("📢今日は日曜日！20時からみんなでエステで遊ぶよ！よかったらきてね！")
        # 1分ごとにチェックする
        await asyncio.sleep(60)

# スクリプト起動時処理
@client.event
async def on_ready():
    print("Botログインしました")

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return

    # どうぶつが辞書内で合致したら鳴き声が返る処理
    if message.content in animal_names:
        animal_cry = animal_names[(message.content)]
        await message.channel.send(animal_cry)

    # 「/tree」と発言したら「今日のツリーID」が返る処理
    if message.content == "/tree":
        # 今日のday値を確認
        tree_criterion_date = int(739160)
        serial_value_date = int(date.today().toordinal())
        tree_date_diff = serial_value_date - tree_criterion_date
        tree_day_diff = tree_date_diff % 28

        # 今日の日付を生成
        today_date = date.today().strftime("%m月%d日")

        # ツリー情報を取得
        with open("treeDate.json", "r") as f:
            tree_dict = json.load(f)
            today_detail = next((item for item in tree_dict["treeDate"] if item["day"] == str(tree_day_diff)), None)
            today_id = today_detail["data"]["id"]
            today_treeType = today_detail["data"]["treeType"]
            today_point = today_detail["data"]["point"]

            # メッセージ成形
            tree_message_body = str("今日は" + today_date + "だね！\nGPIDが" + today_id + "の人の" + today_treeType + "色ツリー\ud83c\udf33から" + today_point + "ポイントもらえるよー！\u2728")

        await message.channel.send(tree_message_body)

# 定期タスクの登録
client.loop.create_task(send_event_notifications())

# Botの起動とDiscordサーバーへの接続
client.run(DISCORD_TOKEN)
