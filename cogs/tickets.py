import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime
import os

# آيدي رتب الإدارة الثلاثة
STAFF_ROLE_IDS = [
    1538498863890173952,
    1536685496619630722,
    1536685263894347887
]

# آيدي رتبة النائب (استبدله بالآيدي الحقيقي إن وجد، أو اتركه 0)
DEPUTY_ROLE_ID = 0  

# آيدي روم اللوق لإرسال نسخة التكتات المغلقة
LOG_CHANNEL_ID = 1539139378222202942

def get_next_ticket_number():
    counter_file = "ticket_counter.txt"
    num = 0
    if os.path.exists(counter_file):
        try:
            with open(counter_file, "r") as f:
                num = int(f.read().strip())
        except:
            num = 0
    num += 1
    with open(counter_file, "w") as f:
        f.write(str(num))
    return f"#{num:04d}", f"{num}"

class StaffComplaintModal(discord.ui.Modal, title="شكوى على إداري"):
    staff_name = discord.ui.TextInput(label="يوزر أو مينشن الإداري", required=True)
    reason = discord.ui.TextInput(label="السبب", style=discord.TextStyle.paragraph, required=True)
    proof = discord.ui.TextInput(label="الدليل", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_channel(interaction, "شكوى على إداري", {
            "الإداري المشتكى عليه": self.staff_name.value,
            "السبب": self.reason.value,
            "الدليل": self.proof.value
        })

class MemberComplaintModal(discord.ui.Modal, title="شكوى على عضو"):
    member_name = discord.ui.TextInput(label="يوزر أو مينشن العضو", required=True)
    reason = discord.ui.TextInput(label="السبب", style=discord.TextStyle.paragraph, required=True)
    proof = discord.ui.TextInput(label="الدليل", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_channel(interaction, "شكوى على عضو", {
            "العضو المشتكى عليه": self.member_name.value,
            "السبب": self.reason.value,
            "الدليل": self.proof.value
        })

class PromotionModal(discord.ui.Modal, title="طلب ترقية"):
    old_rank = discord.ui.TextInput(label="رتبتك القديمة", required=True)
    new_rank = discord.ui.TextInput(label="رتبتك الجديدة المطلوبة", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_channel(interaction, "ترقية", {
            "رتبتك القديمة": self.old_rank.value,
            "رتبتك الجديدة": self.new_rank.value
        })

class AddUserModal(discord.ui.Modal, title="إضافة عضو"):
    user_input = discord.ui.TextInput(label="مينشن أو يوزر العضو", placeholder="@User أو اسم المستخدم")
    async def on_submit(self, interaction: discord.Interaction):
        try:
            query = self.user_input.value.strip()
            member = None
            if query.startswith("<@") and query.endswith(">"):
                member_id = int(query.replace("<@", "").replace("!", "").replace(">", ""))
                member = interaction.guild.get_member(member_id)
            else:
                member = discord.utils.get(interaction.guild.members, name=query) or discord.utils.get(interaction.guild.members, global_name=query)

            if member:
                await interaction.channel.set_permissions(member, view_channel=True, send_messages=True)
                await interaction.response.send_message(f"تمت إضافة {member.mention} للتكت بنجاح!", ephemeral=True)
            else:
                await interaction.response.send_message("لم يتم العثور على العضو، تأكد من اليوزر أو المنشن!", ephemeral=True)
        except:
            await interaction.response.send_message("حدث خطأ، تأكد من كتابة اسم المستخدم بشكل صحيح.", ephemeral=True)

class RemoveUserModal(discord.ui.Modal, title="إزالة عضو"):
    user_input = discord.ui.TextInput(label="مينشن أو يوزر العضو", placeholder="@User أو اسم المستخدم")
    async def on_submit(self, interaction: discord.Interaction):
        try:
            query = self.user_input.value.strip()
            member = None
            if query.startswith("<@") and query.endswith(">"):
                member_id = int(query.replace("<@", "").replace("!", "").replace(">", ""))
                member = interaction.guild.get_member(member_id)
            else:
                member = discord.utils.get(interaction.guild.members, name=query) or discord.utils.get(interaction.guild.members, global_name=query)

            if member:
                await interaction.channel.set_permissions(member, view_channel=False)
                await interaction.response.send_message(f"تمت إزالة {member.mention} من التكت.", ephemeral=True)
            else:
                await interaction.response.send_message("لم يتم العثور على العضو!", ephemeral=True)
        except:
            await interaction.response.send_message("حدث خطأ، تأكد من البيانات المدخلة.", ephemeral=True)

class RenameModal(discord.ui.Modal, title="تغيير اسم التكت"):
    new_name = discord.ui.TextInput(label="الاسم الجديد")
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.channel.edit(name=self.new_name.value)
        await interaction.response.send_message("تم تغيير الاسم بنجاح!", ephemeral=True)

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

    @discord.ui.button(label="ترقية", style=discord.ButtonStyle.primary, emoji="⭐", custom_id="ticket_promotion")
    async def promotion(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PromotionModal())

# أزرار تأكيد إغلاق التكت مع حفظ النسخة (Transcript) وإرسالها لروم اللوق
class CloseConfirmView(discord.ui.View):
    def __init__(self, ticket_user, ticket_type, ticket_number):
        super().__init__(timeout=60)
        self.ticket_user = ticket_user
        self.ticket_type = ticket_type
        self.ticket_number = ticket_number

    @discord.ui.button(label="نعم", style=discord.ButtonStyle.green, emoji="✅")
    async def confirm_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 جاري حفظ النسخة وإغلاق التذكرة...", ephemeral=True)
        
        channel = interaction.channel
        messages_history = []
        async for message in channel.history(limit=None, oldest_first=True):
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            messages_history.append(f"[{timestamp}] {message.author}: {message.content}")
            for att in message.attachments:
                messages_history.append(f"  [مرفق: {att.url}]")
        
        transcript_text = "\n".join(messages_history)
        filename = f"transcript-{channel.name}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(transcript_text)
            
        # إرسال النسخة والتقرير لروم اللوق المحدد
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="📁 أرشيف تذكرة مغلقة",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            embed.add_field(name="رقم التذكرة", value=self.ticket_number, inline=True)
            embed.add_field(name="نوع التذكرة", value=self.ticket_type, inline=True)
            embed.add_field(name="صاحب التذكرة", value=self.ticket_user.mention, inline=True)
            embed.add_field(name="أُغلق بواسطة", value=interaction.user.mention, inline=True)
            
            file = discord.File(filename, filename=filename)
            await log_channel.send(embed=embed, file=file)
            
        if os.path.exists(filename):
            os.remove(filename)

        await asyncio.sleep(2)
        await channel.delete()

    @discord.ui.button(label="لا", style=discord.ButtonStyle.red, emoji="❌")
    async def confirm_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="تم إلغاء إغلاق التذكرة.", view=None)

class TicketControlView(discord.ui.View):
    def __init__(self, user, open_time, ticket_type, ticket_number):
        super().__init__(timeout=None)
        self.user = user
        self.open_time = open_time
        self.ticket_type = ticket_type
        self.ticket_number = ticket_number
        self.claimed_by = None
        self.claim_time = None

    async def check_permissions(self, interaction: discord.Interaction):
        has_role = any(role.id in STAFF_ROLE_IDS for role in interaction.user.roles)
        is_admin = interaction.user.guild_permissions.administrator
        if not (has_role or is_admin):
            await interaction.response.send_message("❌ أنت لست مخولاً لذلك!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="استلام التكت", style=discord.ButtonStyle.green, emoji="🙋‍♂️", custom_id="claim_ticket", row=0)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_permissions(interaction): return
        
        if self.claimed_by:
            await interaction.response.send_message(f"⚠️ هذه التذكرة مستلمة بالفعل من الإداري: {self.claimed_by.mention}", ephemeral=True)
            return
        
        self.claimed_by = interaction.user
        self.claim_time = datetime.now().strftime("%I:%M %p")
        
        embed = create_ticket_embed(self.user, self.ticket_type, self.open_time, self.claimed_by, self.claim_time, "مستلمة", self.ticket_number)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"استلم التكت: {interaction.user.mention}")

    @discord.ui.button(label="إغلاق التذكرة", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket_btn", row=0)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_permissions(interaction): return
        
        view = CloseConfirmView(self.user, self.ticket_type, self.ticket_number)
        await interaction.response.send_message("❓ **هل تم حل المشكلة؟**", view=view, ephemeral=False)

    @discord.ui.button(label="منشن الإدارة الكامل", style=discord.ButtonStyle.blurple, emoji="📢", custom_id="ping_all_admin", row=1)
    async def ping_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_permissions(interaction): return
        
        staff_mentions = " ".join([f"<@&{r_id}>" for r_id in STAFF_ROLE_IDS])
        owner_mention = f"<@{interaction.guild.owner_id}>"
        deputy_mention = f"<@&{DEPUTY_ROLE_ID}>" if DEPUTY_ROLE_ID != 0 else ""
        
        await interaction.channel.send(f"📢 **تنبيه هام للإدارة:**\n{staff_mentions} {owner_mention} {deputy_mention}")
        await interaction.response.send_message("تم منشن الإدارة وصاحب السيرفر والنائب.", ephemeral=True)

    @discord.ui.select(placeholder="⚙️ خيارات التكت", options=[
        discord.SelectOption(label="استدعاء صاحب التذكرة", value="come", emoji="📣"),
        discord.SelectOption(label="إضافة عضو", value="add", emoji="➕"),
        discord.SelectOption(label="إزالة عضو", value="remove", emoji="➖"),
        discord.SelectOption(label="تغيير اسم التذكرة", value="rename", emoji="📝"),
        discord.SelectOption(label="إلغاء الاستلام (Unclaim)", value="unclaim", emoji="❌"),
        discord.SelectOption(label="إغلاق التذكرة", value="close", emoji="🔒")
    ], row=2)
    async def select_option(self, interaction: discord.Interaction, select: discord.ui.Select):
        if not await self.check_permissions(interaction): return

        val = select.values[0]
        if val == "come":
            await interaction.channel.send(f"{self.user.mention}، الإدارة تطلب حضورك.")
            await interaction.response.send_message("تم استدعاء العضو.", ephemeral=True)
        elif val == "add":
            await interaction.response.send_modal(AddUserModal())
        elif val == "remove":
            await interaction.response.send_modal(RemoveUserModal())
        elif val == "rename":
            await interaction.response.send_modal(RenameModal())
        elif val == "unclaim":
            self.claimed_by = None
            embed = create_ticket_embed(self.user, self.ticket_type, self.open_time, None, None, "مفتوح", self.ticket_number)
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.response.send_message("تم إلغاء الاستلام.", ephemeral=True)
        elif val == "close":
            view = CloseConfirmView(self.user, self.ticket_type, self.ticket_number)
            await interaction.response.send_message("❓ **هل تم حل المشكلة؟**", view=view, ephemeral=False)

def create_ticket_embed(user, ticket_type, open_time, claimer=None, claim_time=None, status="مفتوح", ticket_number="#0001"):
    embed = discord.Embed(title="╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n✦ 𝗧𝗜𝗖𝗞𝗘𝗧 𝗦𝗬𝗦𝗧𝗘𝗠 ✦\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯", color=discord.Color.blue())
    
    embed.add_field(name="👤 فــاتــح الــتــكــت", value=f" {user.mention} ", inline=False)
    embed.add_field(name="🛡️ مــســتــلــم الــتــكــت", value=f" {claimer.mention if claimer else 'لا يوجد'} ", inline=False)
    embed.add_field(name="📂 نــوع الــتــكــت", value=f" {ticket_type} ", inline=False)
    embed.add_field(name="🕐 وقــت فــتــح الــتــكــت", value=f" {open_time} ", inline=False)
    embed.add_field(name="🆔 رقــم الــتــكــت", value=f" {ticket_number} ", inline=False)
    embed.add_field(name="📌 حــالــة الــتــكــت", value=f" 🟢 {status} ", inline=False)
    
    role_user = user.top_role.mention if hasattr(user, 'top_role') else "@عضو"
    role_claimer = claimer.top_role.mention if claimer and hasattr(claimer, 'top_role') else "لا يوجد"
    
    embed.add_field(name="\n╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n✦ حــالــة الــتــكــت ✦\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯", value="", inline=False)
    embed.add_field(name="🔓 فــتــح الــتــكــت بــواســطــة", value=f" {role_user} ", inline=False)
    embed.add_field(name="🎫 اســتــلام الــتــكــت بــواســطــة", value=f" {role_claimer} ", inline=False)
    
    return embed

async def create_ticket_channel(interaction: discord.Interaction, ticket_type: str, details: dict):
    guild = interaction.guild
    category = discord.utils.get(guild.categories, id=1536706404176633866)
    
    ticket_number, ticket_num_clean = get_next_ticket_number()

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    }
    
    mentions = []
    for r_id in STAFF_ROLE_IDS:
        role = guild.get_role(r_id)
        if role:
            overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
            mentions.append(role.mention)

    channel = await guild.create_text_channel(
        name=f"ticket-{ticket_num_clean}",
        category=category,
        overwrites=overwrites
    )

    open_time = datetime.now().strftime("%I:%M %p | %d/%m/%Y")
    embed = create_ticket_embed(interaction.user, ticket_type, open_time, ticket_number=ticket_number)
    
    view = TicketControlView(interaction.user, open_time, ticket_type, ticket_number)
    
    role_mentions_text = " ".join(mentions) if mentions else ""
    await channel.send(content=role_mentions_text, embed=embed, view=view)
    await interaction.response.send_message(f"تم فتح التكت: {channel.mention}", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='tickets', description='فتح مركز التكتات والمساعدة')
    async def ticket(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="مركز التكتات والمساعدة 🎫",
            description="اختر القسم المناسب من الأزرار بالأسفل:",
            color=discord.Color.blue()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1536682727531745291/1538123383462436884/file_00000000876482468a3bff92f21e3939.png?ex=6a818887&is=6a803707&hm=d216e646dc54fb9eee3ee9b3a99d1838fe96619fe3447150d094d03f9cf22964&")
        await interaction.response.send_message(embed=embed, view=TicketMainView())

async def setup(bot):
    bot.add_view(TicketMainView())
    await bot.add_cog(Tickets(bot))
