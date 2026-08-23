import o
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# Flask
app = Flask('')
@app.route('/')
def home(): return "Bot is alive!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

class MyBot(commands.Bot):
    def __init__(self):
        # تفعيل الصلاحيات (Intents) وخصوصاً الأعضاء للترحيب
        intents = discord.Intents.default()
        intents.members = True  # ضروري جداً لكي يعمل الترحيب والمغادرة
        intents.message_content = True
        
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # 1. تحميل الملفات
        if os.path.exists('./cogs'):
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    await self.load_extension(f'cogs.{filename[:-3]}')
        
        # 2. مزامنة فورية ونسخ الأمر للسيرفر الخاص بك
        try:
            MY_GUILD = discord.Object(id=1536684342154109019)
            self.tree.copy_global_to(guild=MY_GUILD)  # السطر السحري لنسخ الأمر للسيرفر
            synced = await self.tree.sync(guild=MY_GUILD)
            print(f'تمت المزامنة بنجاح لـ {len(synced)} أمر في السيرفر.')
        except Exception as e:
            print(f'خطأ في المزامنة: {e}')

bot = MyBot()
@bot.event
async def on_ready():
    print(f'تم تسجيل الدخول: {bot.user}')

keep_alive()
bot.run(os.getenv('TOKEN'))
