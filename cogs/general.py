import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # أمر بينج التجريبي
    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send('Pong! 🏓 السيرفر شغال وزي الفل.')

async def setup(bot):
    await bot.add_cog(General(bot)).
