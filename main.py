import os
import discord
from flask import Flask
from threading import Thread

# إعداد سيرفر الويب المصغر لمنع البوت من النوم
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# إعدادات ديسكورد الأساسية
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'تم تسجيل الدخول بنجاح باسم: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '!ping':
        await message.channel.send('Pong!')

# تشغيل سيرفر الويب أولاً ثم تشغيل البوت
keep_alive()

token = os.getenv('TOKEN')
client.run(token)
