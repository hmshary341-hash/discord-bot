import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# Flask (keep as is)
app = Flask('')
@app.route('/')
def home(): return "Bot is alive!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())

    async def setup_hook(self):
        # 1. تحميل الملفات
        if os.path.exists('./cogs'):
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    await self.load_extension(f'cogs.{filename[:-3]}')
        
        # 2. كاشف الأخطاء: اطبع الأوامر التي يراها البوت قبل المزامنة
        commands_found = self.tree.get_commands()
        print(f"DEBUG: الأوامر الموجودة حالياً في الـ Tree هي: {[c.name for c in commands_found]}")

        # 3. محاولة المزامنة
        try:
            MY_GUILD = discord.Object(id=1536684342154109019)
            # تجربة مزامنة السيرفر الخاص
            synced = await self.tree.sync(guild=MY_GUILD)
            print(f'تمت المزامنة بنجاح لـ {len(synced)} أمر.')
        except Exception as e:
            print(f'خطأ في المزامنة: {e}')

bot = MyBot()
@bot.event
async def on_ready():
    print(f'تم تسجيل الدخول: {bot.user}')

keep_alive()
bot.run(os.getenv('TOKEN'))
