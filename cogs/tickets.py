import discord
from discord.ext import commands
from discord import app_commands  # إضافة ضرورية للسلاش كوماند
import asyncio
from datetime import datetime

# 1. نموذج شكوى على إداري
class StaffComplaintModal(discord.ui.Modal, title="شكوى على إداري"):
    staff_name = discord.ui.TextInput(label="يوزر أو مينشن الإداري", placeholder="مثال: @Admin", required=True)
    reason = discord.ui.TextInput(label="السبب", style=discord.TextStyle.paragraph, placeholder="اكتب سبب الشكوى بالتفصيل...", required=True)
    proof = discord.ui.TextInput(label="الدليل", placeholder="رابط الدليل (صورة أو فيديو)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_channel(interaction, "شكوى على إداري", {
            "الإداري المشتكى عليه": self.staff_name.value,
            "السبب": self.reason.value,
            "الدليل": self.proof.value
        })

# 2. نموذج شكوى على عضو
class MemberComplaintModal(discord.ui.Modal, title="شكوى على عضو"):
    member_name = discord.ui.TextInput(label="يوزر أو مينشن العضو", placeholder="مثال: @Member", required=True)
    reason = discord.ui.TextInput(label="السبب", style=discord.TextStyle.paragraph, placeholder="اكتب سبب الشكوى بالتفصيل...", required=True)
    proof = discord.ui.TextInput(label="الدليل", placeholder="رابط الدليل (صورة أو فيديو)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_channel(interaction, "شكوى على عضو", {
            "العضو المشتكى عليه": self.member_name.value,
            "السبب": self.reason.value,
            "الدليل": self.proof.value
        })

# 3. نموذج ترقية
class PromotionModal(discord.ui.Modal, title="طلب ترقية"):
    old_rank = discord.ui.TextInput(label="رتبتك القديمة", placeholder="مثال: عضو / مراقب", required=True)
    new_rank = discord.ui.TextInput(label="رتبتك الجديدة المطلوبة", placeholder="مثال: إداري", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_channel(interaction, "ترقية", {
            "رتبتك القديمة": self.old_rank.value,
            "رتبتك الجديدة": self.new_rank.value
        })

# الأزرار الرئيسية في قائمة التكتات
class TicketMainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="دعم فني", style=discord.ButtonStyle.primary, emoji="🛠️", custom_id="ticket_support")
    async def support(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket_channel(interaction, "دعم فني", {"نوع التكت": "دعم فني عام"})

    @discord.ui.button(label="شكوى على إداري", style=discord.ButtonStyle.danger, emoji="⚠️", custom_id="ticket_staff_complaint")
    async def staff_complaint(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(StaffComplaintModal())

    @discord.ui.button(label="شكوى على عضو", style=discord.ButtonStyle.secondary, emoji="👤", custom_id="ticket_member_complaint")
    async def member_complaint(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MemberComplaintModal())

    @discord.ui.button(label="إستفسار", style=discord.ButtonStyle.success, emoji="❓", custom_id="ticket_inquiry")
    async def inquiry(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket_channel(interaction, "إستفسار", {"نوع التكت": "استفسار عام"})

    @discord.ui.button(label="ترقية", style=discord.ButtonStyle.primary, emoji="⭐", custom_id="ticket_promotion")
    async def promotion(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PromotionModal())

# نموذج سؤال الإغلاق (هل انحلت المشكلة؟)
class CloseReasonModal(discord.ui.Modal, title="إغلاق التكت"):
    is_solved = discord.ui.TextInput(label="هل انحلت المشكلة؟", placeholder="اكتب نعم أو لا مع ذكر التفاصيل باختصار", required=True)

    def __init__(self, user, open_time, claim_time, claimed_by):
        super().__init__()
        self.user = user
        self.open_time = open_time
        self.claim_time = claim_time
        self.claimed_by = claimed_by

    async def on_submit(self, interaction: discord.Interaction):
        close_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        closed_by = interaction.user

        summary_embed = discord.Embed(
            title="🔒 تقرير إغلاق التكت",
            color=discord.Color.red()
        )
        summary_embed.add_field(name="صاحب التكت", value=self.user.mention, inline=False)
        summary_embed.add_field(name="المشرف الذي استلم التكت", value=self.claimed_by.mention if self.claimed_by else "لم يتم الاستلام", inline=False)
        summary_embed.add_field(name="المشرف الذي أغلق التكت", value=closed_by.mention, inline=False)
        summary_embed.add_field(name="وقت الفتح", value=self.open_time, inline=True)
        summary_embed.add_field(name="وقت الاستلام", value=self.claim_time if self.claim_time else "غير مطبق", inline=True)
        summary_embed.add_field(name="وقت الإغلاق", value=close_time, inline=True)
        summary_embed.add_field(name="هل انحلت المشكلة؟", value=self.is_solved.value, inline=False)

        await interaction.response.send_message(embed=summary_embed)
        await asyncio.sleep(5)
        await interaction.channel.delete()

# أزرار التحكم داخل تكت القناة (استلام + إغلاق)
class TicketControlView(discord.ui.View):
    def __init__(self, user, open_time):
        super().__init__(timeout=None)
        self.user = user
        self.open_time = open_time
        self.claimed_by = None
        self.claim_time = None

    @discord.ui.button(label="استلام التكت", style=discord.ButtonStyle.green, emoji="🙋‍♂️", custom_id="claim_ticket")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("هذا الزر مخصص للإدارة فقط!", ephemeral=True)
            return

        if self.claimed_by:
            await interaction.response.send_message(f"تم استلام هذا التكت مسبقاً بواسطة {self.claimed_by.mention}", ephemeral=True)
            return

        self.claimed_by = interaction.user
        self.claim_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        button.disabled = True
        button.label = f"استلمه: {interaction.user.name}"

        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"قام الإداري {interaction.user.mention} باستلام التكت بنجاح.")

    @discord.ui.button(label="إغلاق التكت", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket_button")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("هذا الزر مخصص للإدارة فقط!", ephemeral=True)
            return

        modal = CloseReasonModal(
            user=self.user,
            open_time=self.open_time,
            claim_time=self.claim_time,
            claimed_by=self.claimed_by
        )
        await interaction.response.send_modal(modal)

# دالة موحدة لإنشاء روم التكت
async def create_ticket_channel(interaction: discord.Interaction, ticket_type: str, details: dict):
    guild = interaction.guild
    user = interaction.user

    existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{user.name.lower()}")
    if existing_channel:
        if interaction.response.is_done():
            await interaction.followup.send(f"لديك تكت مفتوح مسبقاً: {existing_channel.mention}", ephemeral=True)
        else:
            await interaction.response.send_message(f"لديك تكت مفتوح مسبقاً: {existing_channel.mention}", ephemeral=True)
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    category = discord.utils.get(guild.categories, name="Tickets")
    if not category:
        category = await guild.create_category("Tickets")

    channel = await guild.create_text_channel(
        name=f"ticket-{user.name}",
        category=category,
        overwrites=overwrites
    )

    open_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    embed = discord.Embed(
        title=f"تكت جديد: {ticket_type}",
        description=f"مرحباً {user.mention}!\nتم فتح التكت بنجاح، يرجى انتظار رد الإدارة.",
        color=discord.Color.blue()
    )
    embed.add_field(name="صاحب التكت", value=user.mention, inline=True)
    embed.add_field(name="وقت الفتح", value=open_time, inline=True)

    for key, value in details.items():
        embed.add_field(name=key, value=value, inline=False)

    view = TicketControlView(user=user, open_time=open_time)

    if not interaction.response.is_done():
        await interaction.response.send_message(f"تم إنشاء التكت الخاص بك: {channel.mention}", ephemeral=True)
    else:
        await interaction.followup.send(f"تم إنشاء التكت الخاص بك: {channel.mention}", ephemeral=True)

    await channel.send(embed=embed, view=view)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # التعديل هنا: تحويل الأمر إلى Slash Command
    @app_commands.command(name='ticket', description='فتح مركز التكتات والمساعدة')
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="مركز التكتات والمساعدة 🎫",
            description="اختر القسم المناسب من الأزرار بالأسفل لفتح تكت جديد وتعبئة التفاصيل:",
            color=discord.Color.blue()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1536682727531745291/1538123383462436884/file_00000000876482468a3bff92f21e3939.png?ex=6a818887&is=6a803707&hm=d216e646dc54fb9eee3ee9b3a99d1838fe96619fe3447150d094d03f9cf22964&")
        await interaction.response.send_message(embed=embed, view=TicketMainView())

async def setup(bot):
    await bot.add_cog(Tickets(bot))
