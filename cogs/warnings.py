import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import asyncio

# رتب الإدارة
STAFF_ROLE_IDS = [
    1538498863890173952,
    1536685496619630722,
    1536685263894347887
]

# رومات اللوق الخاصة بالتحذيرات والإجراءات
MOD_ROOMS = {
    "بان / كيك": 1538837356348444712,  # روم البان والكيك
    "تايم آوت": 1538837520329080872,   # روم التايم آوت
    "تحذير": 1538837627967512646     # روم التحذيرات
}

async def check_staff_permission(interaction: discord.Interaction):
    has_role = any(role.id in STAFF_ROLE_IDS for role in interaction.user.roles)
    is_admin = interaction.user.guild_permissions.administrator
    if not (has_role or is_admin):
        await interaction.response.send_message("❌ أنت لست مخولاً لاستخدام هذا الاستبيان!", ephemeral=True)
        return False
    return True

# استبيان النصوص (يوزر الشخص، السبب، المدة)
class ModTextModal(discord.ui.Modal):
    def __init__(self, action_type: str, bot):
        super().__init__(title=f"استبيان الإجراء: {action_type}")
        self.action_type = action_type
        self.bot = bot

        self.target_user = discord.TextInput(
            label="يوزر أو مينشن الشخص",
            placeholder="@User أو اسم المستخدم",
            required=True
        )
        self.reason = discord.TextInput(
            label="السبب",
            style=discord.TextStyle.paragraph,
            placeholder="اكتب سبب العقوبة بالتفصيل...",
            required=True
        )
        
        if action_type in ["بان / كيك", "تايم آوت"]:
            self.duration = discord.TextInput(
                label="المدة (مثال: يوم، ساعة، دائم)",
                placeholder="اكتب المدة المطلوبة هنا...",
                required=True
            )
        else:
            self.duration = None

        self.add_item(self.target_user)
        self.add_item(self.reason)
        if self.duration:
            self.add_item(self.duration)

    async def on_submit(self, interaction: discord.Interaction):
        target = self.target_user.value
        reason = self.reason.value
        duration_val = self.duration.value if self.duration else "غير محدد"
        
        # رسالة مؤقتة تطلب رفع الصورة من الشات
        await interaction.response.send_message(
            f"📸 **تم حفظ البيانات بنجاح!**\n"
            f"الرجاء إرسال **صورة الدليل** الآن في الشات (باستخدام زر **+** من جهازك) خلال **60 ثانية**...",
            ephemeral=True
        )

        # انتظار إرسال الصورة من نفس العضو وفي نفس الروم
        def check(m: discord.Message):
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id and len(m.attachments) > 0

        try:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            proof_attachment = msg.attachments[0]
            image_url = proof_attachment.url
            
            # محاولة حذف رسالة الصورة لترتيب الشات
            try:
                await msg.delete()
            except:
                pass

        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ انتهى الوقت ولم تقم بإرسال صورة الدليل. تم إلغاء العملية.", ephemeral=True)
            return

        # تحديد روم اللوق المناسب
        target_room_id = MOD_ROOMS.get(self.action_type)
        log_channel = interaction.guild.get_channel(target_room_id)
        if not log_channel:
            await interaction.followup.send("⚠️ عذراً، روم اللوق الخاص بهذا الإجراء غير موجود أو خطأ في الآيدي!", ephemeral=True)
            return

        # بناء التقرير وإرفاق الصورة بشكل مباشر
        embed = discord.Embed(
            title=f"╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n✦ تقرير إجراء إداري: {self.action_type} ✦\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯",
            color=discord.Color.red() if "بان" in self.action_type or "كيك" in self.action_type else discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.add_field(name="👤 العضو المخالف", value=f"「 {target} 」", inline=False)
        embed.add_field(name="🛡️ الإداري المسؤول", value=f"「 {interaction.user.mention} 」", inline=False)
        embed.add_field(name="📂 نوع الإجراء", value=f"「 {self.action_type} 」", inline=True)
        
        if self.duration:
            embed.add_field(name="⏱️ المدة", value=f"「 {duration_val} 」", inline=True)
            
        embed.add_field(name="📝 السبب", value=f"``` {reason} ```", inline=False)
        
        # عرض الصورة المرفوعة داخل الإيمبد مباشرة
        embed.set_image(url=image_url)

        await log_channel.send(embed=embed)
        await interaction.followup.send(f"✅ تم إرسال تقرير ({self.action_type}) بنجاح إلى الروم المخصص مع صورة الدليل!", ephemeral=True)

# قائمة اختيار نوع العقوبة
class ModSelectView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot

    @discord.ui.select(
        placeholder="📌 اختر نوع الإجراء أو التحذير المطلوب...",
        options=[
            discord.SelectOption(label="تحذير (Warning)", value="تحذير", emoji="⚠️", description="إرسال تحذير رسمي للعضو"),
            discord.SelectOption(label="تايم آوت (Timeout)", value="تايم آوت", emoji="⏳", description="إسكات العضو لفترة محددة"),
            discord.SelectOption(label="بان / كيك (Ban / Kick)", value="بان / كيك", emoji="🔨", description="طرد أو حظر العضو من السيرفر")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if not await check_staff_permission(interaction):
            return
        
        selected_type = select.values[0]
        await interaction.response.send_modal(ModTextModal(selected_type, self.bot))

# لوحة التحذيرات الرئيسية
class ModMainView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="أبدا استبيان", style=discord.ButtonStyle.danger, emoji="📋", custom_id="start_mod_survey")
    async def start_survey(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_staff_permission(interaction):
            return
        
        view = ModSelectView(self.bot)
        await interaction.response.send_message("🔍 **اختر نوع العقوبة أو الإجراء الذي تريد تسجيله:**", view=view, ephemeral=True)

class Warnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='warnings_panel', description='إرسال لوحة إدارة التحذيرات والإجراءات')
    @app_commands.checks.has_permissions(administrator=True)
    async def warnings_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n✦ لــوحــة نــظــام الــتــحــذيرات ✦\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯",
            description="هذه اللوحة مخصصة للإدارة لتسجيل وإرسال تقارير العقوبات والإجراءات بدقة.\n\n"
                        "• **التحذيرات:** لتسجيل المخالفات العادية.\n"
                        "• **التايم آوت:** لإسكات الأعضاء المخالفين.\n"
                        "• **الكيك / البان:** للطرد أو الحظر النهائي.\n\n"
                        "اضغط على الزر بالأسفل لبدء الاستبيان المخصص:",
            color=discord.Color.dark_red()
        )
        embed.set_footer(text="نظام الحماية والإدارة الآلي")
        
        await interaction.response.send_message(embed=embed, view=ModMainView(self.bot))

async def setup(bot):
    bot.add_view(ModMainView(bot))
    await bot.add_cog(Warnings(bot))
