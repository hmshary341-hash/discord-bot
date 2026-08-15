import os
import asyncio
import discord
from discord.ext import commands
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

# إعدادات البوت والأوامر
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'تم تسجيل الدخول بنجاح باسم: {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'تم مزامنة {len(synced)} أمر سلاش بنجاح.')
    except Exception as e:
        print(f'خطأ في مزامنة الأوامر: {e}')

# دالة لتحميل جميع الأقسام من مجلد cogs تلقائياً
async def load_extensions():
    if not os.path.exists('./cogs'):
        os.makedirs('./cogs')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'تم تحميل القسم: {filename}')

async def main():
    keep_alive()
    async with bot:
        await load_extensions()
        token = os.getenv('TOKEN')
        if not token:
            print("خطأ: لم يتم العثور على التوكن!")
        else:
            await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())
