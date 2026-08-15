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

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # تحميل جميع الأقسام (Cogs) تلقائياً
        if not os.path.exists('./cogs'):
            os.makedirs('./cogs')
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f'تم تحميل القسم: {filename}')
                except Exception as e:
                    print(f'خطأ في تحميل {filename}: {e}')

        # مزامنة الأوامر فورياً للسيرفر الخاص بك
        try:
            guild = discord.Object(id=1536684342154109019)
            synced = await self.tree.sync(guild=guild)
            print(f'تمت المزامنة بنجاح لـ {len(synced)} أمر في السيرفر.')
        except Exception as e:
            print(f'خطأ أثناء المزامنة: {e}')

bot = MyBot()

@bot.event
async def on_ready():
    print(f'تم تسجيل الدخول بنجاح باسم: {bot.user}')

async def main():
    keep_alive()
    token = os.getenv('TOKEN')
    if not token:
        print("خطأ: لم يتم العثور على التوكن!")
    else:
        await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())
