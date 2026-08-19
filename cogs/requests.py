import discord
from discord.ext import commands
from discord import app_commands
import rando
import string
import os

# آيديات الرومات والرتب
LOG_CHANNEL_ID = 1538837244381634590
PANEL_CHANNEL_ID = 1537196905766068297

STAFF_ROLE_IDS = [
    1538498863890173952,
    1536685496619630722,
    1536685263894347887
]

# دالة لإنشاء رقم طلب متصاعد من 4 أرقام
def get_req_number():
    counter_file = "request_counter.txt"
    num = 1000
    if os.path.exists(counter_file):
        try:
            with open(counter_file, "r") as f:
                num = int(f.read().strip())
        except:
            num = 1000
    num += 1
    with open(counter_file, "w") as f:
        f.write(str(num))
    return f"{num:04d}"

# 1. نموذج طلب روم
class RoomModal(discord.ui.Modal, title="طلب روم جديد"):
    room_type = discord.ui.TextInput(label="نوع الروم (شات ولا فويس)", placeholder="اكتب شات أو فويس", required=True)
    room_name = discord.ui.TextInput(label="اسم الروم المطلوبة", placeholder="اكتب اسم الروم", required=True)
    allowed_role = discord.ui.TextInput(label="الرتبة المسموحة للروم", placeholder="يوزر أو مينشن الرتبة", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        req_num = get_req_number()
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        
        embed = discord.Embed(title="╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n✦ 🏠 طــلــب رُوْم جــديــد ✦\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯", color=discord.Color.blue())
        embed.add_field(name="「👤」 صـاحـب الـطـلـب", value=f"「 {interaction.user.mention} 」", inline=False)
        embed.add_field(name="「🆔」 رقـم الـطـلـب", value=f"「 #{req_num} 」", inline=False)
        embed.add_field(name="「📂」 نـوع الـروم", value=f"「 {self.room_type.value} 」", inline=False)
        embed.add_field(name="「🏷️」 اسـم الـروم", value=f"「 {self.room_name.value} 」", inline=False)
        embed.add_field(name="「🛡️」 الـرثـبـة المـسـمـوحـة", value=f"「 {self.allowed_role.value} 」", inline=False)

        view = RequestActionView(interaction.user, "روم", {"type": self.room_type.value, "name": self.room_name.value}, req_num)
        
        if log_channel:
            await log_channel.send(embed=embed, view=view)
        
        await interaction.response.send_message("✅ تم إرسال طلب الروم بنجاح إلى الإدارة!", ephemeral=True)

# 2. نموذج توثيق البنات
class VerificationModal(discord.ui.Modal, title="توثيق البنات"):
    name_info = discord.ui.TextInput(label="اسمك الحقيقي أو المستعار أو لقبك", placeholder="اكتب اسمك أو لقبك هنا", required=True)
    age = discord.ui.TextInput(label="عمرك", placeholder="اكتب عمرك هنا", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        req_num = get_req_number()
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        
        embed = discord.Embed(title="╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n✦ 🌸 تــوثــيــق بــنــات ✦\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯", color=discord.Color.purple())
        embed.add_field(name="「👤」 صـاحـبـة الـطـلـب", value=f"「 {interaction.user.mention} 」", inline=False)
        embed.add_field(name="「🆔」 رقـم الـطـلـب", value=f"「 #{req_num} 」", inline=False)
        embed.add_field(name="「📝」 الاسـم أو الـلـقـب", value=f"「 {self.name_info.value} 」", inline=False)
        embed.add_field(name="「🎂」 الـعـمـر", value=f"「 {self.age.value} 」", inline=False)

        view = RequestActionView(interaction.user, "توثيق", {"name": self.name_info.value, "age": self.age.value}, req_num)
        
        if log_channel:
            await log_channel.send(embed=embed, view=view)
        
        await interaction.response.send_message("✅ تم إرسال طلب التوثيق بنجاح إلى الإدارة!", ephemeral=True)

# 3. نموذج اقتراحات
class SuggestionModal(discord.ui.Modal, title="تقديم اقتراح"):
    suggestion_text = discord.ui.TextInput(label="اقتراحك", style=discord.TextStyle.paragraph, placeholder="اكتب اقتراحك بالتفصيل...", required=True)
    color_text = discord.ui.TextInput(label="اللون (باي لون تبيه)", placeholder="اكتب اللون المطلوب", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        req_num = get_req_number()
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        
        embed = discord.Embed(title="╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n✦ 💡 اقــتــراح جــديــد ✦\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯", color=discord.Color.gold())
        embed.add_field(name="「👤」 صـاحـب الـاقـتـراح", value=f"「 {interaction.user.mention} 」", inline=False)
        embed.add_field(name="「🆔」 رقـم الـطـلـب", value=f"「 #{req_num} 」", inline=False)
        embed.add_field(name="「💬」 الـاقـتـراح", value=f"「 {self.suggestion_text.value} 」", inline=False)
        embed.add_field(name="「🎨」 الـلـون الـمـطـلـوب", value=f"「 {self.color_text.value} 」", inline=False)

        view = RequestActionView(interaction.user, "اقتراح", {"suggestion": self.suggestion_text.value}, req_num)
        
        if log_channel:
            await log_channel.send(embed=embed, view=view)
        
        await interaction.response.send_message("✅ تم إرسال اقتراحك بنجاح إلى الإدارة!", ephemeral=True)

# أزرار اللوحة الرئيسية (بدون وقت انتهاء)
class RequestPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="طلب روم", style=discord.ButtonStyle.primary, emoji="🏠", custom_id="req_room_button")
    async def req_room(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RoomModal())

    @discord.ui.button(label="توثيق البنات", style=discord.ButtonStyle.success, emoji="🌸", custom_id="req_verification_button")
    async def req_verification(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VerificationModal())

    @discord.ui.button(label="اقتراحات", style=discord.ButtonStyle.secondary, emoji="💡", custom_id="req_suggestion_button")
    async def req_suggestion(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SuggestionModal())

# أزرار الإدارة في سجل الطلبات (بدون وقت انتهاء)
class RequestActionView(discord.ui.View):
    def __init__(self, target_user: discord.Member = None, req_type: str = None, data: dict = None, req_num: str = None):
        super().__init__(timeout=None)
        self.target_user = target_user
        self.req_type = req_type
        self.data = data
        self.req_num = req_num

    @discord.ui.button(label="قبول", style=discord.ButtonStyle.green, emoji="✅", custom_id="accept_request_action")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        has_role = any(role.id in STAFF_ROLE_IDS for role in interaction.user.roles)
        if not (has_role or interaction.user.guild_permissions.administrator):
            return await interaction.response.send_message("هذا الزر مخصص للإدارة فقط!", ephemeral=True)

        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        if self.req_type == "اقتراح":
            try:
                await self.target_user.send("✅ تم قبول إقتراحك.")
            except:
                pass
            await interaction.response.send_message(f"تم قبول الاقتراح بواسطة {interaction.user.mention}.", ephemeral=True)

        elif self.req_type == "روم":
            try:
                await self.target_user.send("✅ تم قبول وصنع رومك.")
            except:
                pass
            
            try:
                guild = interaction.guild
                r_type = self.data['type'].lower()
                r_name = self.data['name']
                if "فويس" in r_type or "voice" in r_type:
                    await guild.create_voice_channel(name=r_name)
                else:
                    await guild.create_text_channel(name=r_name)
            except Exception as e:
                print(f"Error creating room: {e}")

            await interaction.response.send_message(f"تم قبول طلب الروم وصنعه بواسطة {interaction.user.mention}.", ephemeral=True)

        elif self.req_type == "توثيق":
            verify_code = ''.join(random.choices(string.ascii_letters + string.digits, k=9))
            try:
                dm_text = (
                    f"🎉 **تم قبول طلب توثيق البنات الخاص بك!**\n\n"
                    f"🔑 **كود التوثيق:** `{verify_code}`\n"
                    f"🆔 **رقم الطلب:** `#{self.req_num}`\n\n"
                    f"⚠️ **ملاحظة هامة:**\n"
                    f"الكود ذا افتحي دعم فني ووريهم صوره للكود ورقم الطلب، لكن والله لو كنت ولد وجاي تستهبل لا أصفقك باند وتايم 🚫."
                )
                await self.target_user.send(dm_text)
            except:
                pass
            await interaction.response.send_message(f"تم قبول طلب التوثيق وإرسال الكود في الخاص بواسطة {interaction.user.mention}.", ephemeral=True)

    @discord.ui.button(label="رفض", style=discord.ButtonStyle.danger, emoji="❌", custom_id="reject_request_action")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        has_role = any(role.id in STAFF_ROLE_IDS for role in interaction.user.roles)
        if not (has_role or interaction.user.guild_permissions.administrator):
            return await interaction.response.send_message("هذا الزر مخصص للإدارة فقط!", ephemeral=True)

        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        if self.req_type == "اقتراح":
            try:
                await self.target_user.send("❌ عذراً، تم رفض إقتراحك.")
            except:
                pass
        elif self.req_type == "روم":
            try:
                await self.target_user.send("❌ عذراً، تم رفض طلب الروم الخاص بك.")
            except:
                pass
        elif self.req_type == "توثيق":
            try:
                await self.target_user.send(f"❌ عذراً، تم رفض طلب توثيق البنات الخاص بك (رقم الطلب: #{self.req_num}).")
            except:
                pass

        await interaction.response.send_message(f"تم رفض الطلب بواسطة {interaction.user.mention}.", ephemeral=True)

class Requests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='requests', description='إرسال لوحة الطلبات في الروم المحدد')
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_requests(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(PANEL_CHANNEL_ID)
        if not channel:
            return await interaction.response.send_message("لم يتم العثور على روم الطلبات المحدد!", ephemeral=True)

        embed = discord.Embed(
            title="╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n✦ 🎫 نــظــام الــطــلــبــات ✦\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯",
            description="اختر القسم المناسب من الأزرار بالأسفل لتقديم طلبك:",
            color=discord.Color.blue()
        )
        embed.set_footer(text="يرجى استخدام الأزرار الجادة فقط.")
        
        await channel.send(embed=embed, view=RequestPanelView())
        await interaction.response.send_message("تم إرسال لوحة الطلبات بنجاح!", ephemeral=True)

async def setup(bot):
    bot.add_view(RequestPanelView())
    await bot.add_cog(Requests(bot))
