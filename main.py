import os
import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'تم تسجيل الدخول بنجاح باسم: {client.user}')

token = os.getenv('TOKEN')
client.run(token)
