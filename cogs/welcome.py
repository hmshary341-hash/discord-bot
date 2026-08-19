import discord
from discord.ext import commands

# آيديات الرومات
WELCOME_CHANNEL_ID = 1536708856695226408.
LEAVE_CHANNEL_ID = 1536709079706378331

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # حدث دخول عضو جديد
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return

        # جلب جميع الرتب (مع استثناء رتبة الجميع)
        roles = [role.mention for role in member.roles if role != member.guild.default_role]
        roles_text = " ".join(roles) if roles else "لا توجد رتب"

        embed = discord.Embed(color=discord.Color.blue())
        
        # التصميم
        embed.title = "╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n✦ 𓆩 تـرحـيـب بـعـضـو جـديـد 𓆪 ✦\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
        
        embed.add_field(name="ـ", value=f"『 👤 』نـورتـنـا يـا {member.mention}", inline=False)
        embed.add_field(name="ـ", value=f"╭──────────────────────────────╮\n✦ نـسـعـد بـانـضـمـامـك لـنـا ✦\n✦ اجـعـل وجـودك بـيـنـنـا مـمـيـزًا ✦\n✦ نـتـمـنـى لـك أوقـاتـًا مـمـتـعـة ✦\n╰──────────────────────────────╯", inline=False)
        embed.add_field(name="ـ", value=f"『 🏛️ 』أهـلًا وسـهـلًا بـك فـي مـجـتـمـعـنـا\n\n**رتبك في السيرفر:**\n{roles_text}", inline=False)
        embed.add_field(name="ـ", value="⚜️ نتمنى لك إقامة تليق بمقامك ⚜️", inline=False)
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        await channel.send(content=f"{member.mention}", embed=embed)

    # حدث خروج عضو
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = self.bot.get_channel(LEAVE_CHANNEL_ID)
        if not channel:
            return

        embed = discord.Embed(color=discord.Color.red())
        
        # التصميم
        embed.title = "╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n✦ 𓆩 وداعـًا لـعـضـو غـادر 𓆪 ✦\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
        
        embed.add_field(name="ـ", value=f"『 👤 』غـادرنـا {member.name}", inline=False)
        embed.add_field(name="ـ", value=f"╭──────────────────────────────╮\n✦ كـان وجـودك بـيـنـنـا جـمـيـلًا ✦\n✦ لـن نـنـسـى أثـرك بـيـنـنـا ✦\n✦ نـتـمـنـى لـك الـتـوفـيـق والـخـيـر ✦\n╰──────────────────────────────╯", inline=False)
        embed.add_field(name="ـ", value="『 🏛️ 』سـتـبـقـى ذكـراك حـاضـرة بـيـنـنـا\n\n⚜️ فـي أمـان الـلـه، وإلـى لـقـاء آخـر ⚜️", inline=False)
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
