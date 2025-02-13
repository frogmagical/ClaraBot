import discord
import boto3
import json
import asyncio
import re
import random
from datetime import date, datetime, time

ssm = boto3.client("ssm")

# 環境変数からトークンを取得
response = ssm.get_parameter(
    Name="DISCORD_TOKEN",
    WithDecryption=False
)
DISCORD_TOKEN = response["Parameter"]["Value"]

response = ssm.get_parameter(
    Name="DISCORD_NOTIFICATE_CHANNEL_ID",
    WithDecryption=False
)
DISCORD_NOTIFICATE_CHANNEL_ID = response["Parameter"]["Value"]

# 動物の名前辞書を事前定義
with open("animal.json", "r", encoding="utf-8") as f:
    animal_dict = json.load(f)
    animal_names = animal_dict["animals"]

# サイコロ用の正規表現パターン定義
dicePattern = r"^!\d+d\d+$"

# Intentsの設定
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# 定期タスクの登録をsetup_hookに移動
class MyClient(discord.Client):
    async def setup_hook(self):
        self.loop.create_task(send_event_notifications())

# BOTへ接続するオブジェクトを定義
client = MyClient(intents=intents)

async def send_event_notifications():
    # ログイン処理
    await client.wait_until_ready()
    channel_id = int(DISCORD_NOTIFICATE_CHANNEL_ID)
    channel = client.get_channel(channel_id)
    print(f"Success loggin to Channel: {channel}!")
    if channel is None:
        print("Not found Notificate Channel.")
        return

    # チムイベ告知タイマー
    while not client.is_closed():
        now = datetime.now()
        if now.weekday() == 2 and now.time() >= time(21, 0) and now.time() < time(21, 1):  # 水曜日22:00
            # メッセージ候補を生成
            wedMessages = [
                f"📢今日は水曜日！22時からチームイベント消化をやるよ！\nよかったら手伝ってー＞＜！",
                f"📢水曜日の22時といったらチムオダ消化の会だよね！？\nチムマグ維持とかに大助かりなので…ぜひ来てほしいな～！",
                f"📢Today is Wednesday! We'll have a team event at 10pm! :)\n…つまり水曜日なのでチームオーダー消化の日だよ！ってこと～！",
            ]
            # ランダムに選択
            wed_message_body = random.choice(wedMessages)
            await channel.send(wed_message_body)
            
        elif now.weekday() == 6 and now.time() >= time(19, 0) and now.time() < time(19, 1):  # 日曜日20:00
            # メッセージ候補を生成
            sunMessages = [
                f"📢今日は日曜日！20時からエステでコーデを作るイベントをやるよ！\n気軽に遊びに来てね！",
                f"📢みんなエステパスは持った？\n今日は20時からエステイベントの日なんだよ！忘れちゃだめだよー！！",
                f"📢にちようびーのーにじゅうじはーエーステーのひー！\n今日は一体どんなお題がでるんだろう…？？",
            ]
            # ランダムに選択
            sun_message_body = random.choice(sunMessages)
            await channel.send(sun_message_body)
        await asyncio.sleep(60)  # 1分ごとにチェック

# スクリプト起動時処理
@client.event
async def on_ready():
    print("Success loggin to your Discord Server!")

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return

    # トリセツ
    if message.content == "!torisetu":
        function01 = ("!tree: 今日のクリスペツリーのIDをお答えするよ！")
        function02 = ("!omikuji: 今日のあなたの運勢を占うよ！")
        function03 = ("!neko: 私が鳴いちゃう！…ちょっ…なんの機能よこれー！？")
        function04 = ("!2d6: とりあえず2d6振っちゃう？ダイスの種類と個数は自由な数字でも大丈夫！")
        torisetu_message_body = (f"いま私ができることはこんなかんじだよ！\n{function01}\n{function02}\n{function03}\n{function04}")
        await message.channel.send(torisetu_message_body)

    # どうぶつ名が辞書内で合致したら鳴き声が返る処理
    if message.content in animal_names:
            animal_cry = animal_names[(message.content)]
            await message.channel.send(animal_cry)
    
    # おみくじの時間
    if message.content == "!omikuji":
        with open("omikuji.json", "r", encoding="utf-8") as f:
            omikuji_data = json.load(f)
            omikuji_num = str(random.randint(0,99)).zfill(3)
            result = omikuji_data[omikuji_num]
            omikuji_user = message.author.name
            omikuji_message = (f"今日の{omikuji_user}ちゃんの運勢は…{result['Unsei']}\n{result['Comment']}")
            await message.channel.send(omikuji_message)
    
    # サイコロを振ってみよう
    if re.match(dicePattern, message.content):
        text_body = message.content
        dice_user = message.author.name
        dice = text_body.lstrip("!")
        dice_data = dice.split('d')
        dice_count = dice_data[0]
        dice_type = dice_data[1]
        dice_sum = 0
        for i in range(int(dice_count)):
            dice_num = random.randint(1, int(dice_type))
            dice_sum = dice_sum + dice_num
        dice_messages = [
            f"{dice_user} は {dice} を振った！ {dice_sum} だった！",
            f"{dice_user}：{dice} => {dice_sum}",
            f"{dice}の結果は…{dice_sum}！"
        ]
        dice_message_body = random.choice(dice_messages)
        await message.channel.send(dice_message_body)

    # 「!tree」と発言したら「今日のツリーID」が返る処理
    if message.content == "!tree":
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

            # メッセージ候補を生成
            tree_messages = [
                f"今日は{today_date}だね！\nGPIDが{today_id}の人の{today_treeType}色ツリー🌳から{today_point}ポイントもらえるよー！✨",
                f"むにゃむにゃ…今日のツリー…？今日は{today_date}だよね…\nGPIDは{today_id}で…{today_treeType}色じゃない…？もう起こさないでね…( ˘ω˘ )",
                f"もい！今日はGPID{today_id}の人の{today_treeType}色ツリー🌳から{today_point}ポイントを回収するのよ！"
            ]
            # ランダムに選択
            tree_message_body = random.choice(tree_messages)

        await message.channel.send(tree_message_body)

# Botの起動とDiscordサーバーへの接続
client.run(DISCORD_TOKEN)