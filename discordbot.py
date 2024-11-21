import discord
import openai
from discord.ext import commands

# 環境変数からトークンを取得
DISCORD_TOKEN = "DiscordToken"
OPENAI_API_KEY = "OpenAIAPIKEY"

# OpenAI APIキーを設定
openai.api_key = OPENAI_API_KEY

# Discordのインテント設定
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Discord Botの初期化
bot = commands.Bot(command_prefix="!", intents=intents)

# 会話履歴を保持する辞書
conversation_history = {}

# ChatGPT APIを呼び出す関数
async def ask_chatgpt(user_id, user_message):
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # ユーザーのメッセージを履歴に追加
    conversation_history[user_id].append({"role": "user", "content": user_message})

    try:
        # ChatGPT APIを非同期で呼び出し
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=conversation_history[user_id],
        )
    except openai.error.OpenAIError as e:
        return f"OpenAI APIでエラーが発生しました: {e}"
    except Exception as e:
        return f"その他のエラーが発生しました: {e}"

    try:
        # ChatGPTの応答を取得
        bot_response = response["choices"][0]["message"]["content"]
    except KeyError as e:
        return f"応答の形式が不正です: {e}"
    except Exception as e:
        return f"応答の処理中にエラーが発生しました: {e}"

    # 応答を履歴に追加
    conversation_history[user_id].append({"role": "assistant", "content": bot_response})

    # 履歴が多すぎる場合、古い履歴を削除
    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]

    return bot_response

# メッセージ受信イベント
@bot.event
async def on_message(message):
    if message.author.bot:  # Botのメッセージは無視
        return
    print(message)

    # ユーザーIDを取得
    user_id = str(message.author.id)
    user_message = message.content
    print(user_id)
    print(user_message)

    # ChatGPTに質問
    bot_response = await ask_chatgpt(user_id, user_message)
    print(bot_response)

    # 応答を送信
    await message.channel.send(bot_response)

# Botの起動
bot.run(DISCORD_TOKEN)
