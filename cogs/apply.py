import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import random
import strin

# آيديات الرومات والرتب المطلوبة
APPLY_PANEL_CHANNEL_ID = 1537196996668956682  # روم لوحة التقديم
APPLY_LOG_CHANNEL_ID = 1538837953881837589    # روم سجلات التقديم

STAFF_ROLE_IDS = [
    1538498863890173952,
    1536685496619630722,
    1536685263894347887
]

# قاعدة البيانات (ملف الحفظ)
DATABASE_FILE = "database.json"

def load_database():
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"pending": {}, "accepted": {}}
    return {"pending": {}, "accepted": {}}

def save_database(data):
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 1. الاستمارة الأولى (البيانات الأساسية)
class FirstApplicationModal(discord.ui.Modal, title="استمارة التقديم الإداري"):
    real_name = discord.ui.TextInput(label="اسمك الحقيقي", placeholder="اكتب اسمك الحقيقي هنا", required=True)
    username = discord.ui.TextInput(label="يوزرك", placeholder="اكتب يوزرك في الديسكورد", required=True)
    age = discord.ui.TextInput(label="عمرك", placeholder="اكتب عمرك هنا", required=True)
    experience = discord.ui.TextInput(label="خبراتك", style=discord.TextStyle.paragraph, placeholder="اكتب خبراتك السابقة بالتفصيل...", required=True)
    benefit = discord.ui.TextInput(label="وش بنستفيد منك", style=discord.TextStyle.paragraph, placeholder="اكتب ماذا ستقدم للسيرفر...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        db = load_database()
        db["pending"][user_id] = {
            "real_name": self.real_name.value,
            "username": self.username.value,
            "age": self.age.value,
            "experience": self.experience.value,
            "benefit": self.benefit.value
        }
        save_database(db)
        
        try:
            view = ScenarioButtonView()
            await interaction.user.send(
                "📌 **ملاحظة هامة وتكملة التقديم:**\n"
                "يرجى الضغط على الزر بالأسفل لفتح خانة السيناريو والإجابة على السؤال لإكمال تقديمك:",
                view=view
            )
            await interaction.response.send_message("✅ تم إرسال خطوة السيناريو إلى الخاص لديك، يرجى إكمالها هناك!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ عذراً، خاصك مغلق! يرجى فتح الخاص وإعادة المحاولة.", ephemeral=True)

# زر دائم في الخاص يفتح نافذة السيناريو
class ScenarioButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إجابة سؤال السيناريو", style=discord.ButtonStyle.primary, emoji="✍️", custom_id="open_scenario_modal_persistent")
    async def open_scenario(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        db = load_database()
        if user_id not in db["pending"]:
            return await interaction.response.send_message("❌ عذراً، لا يوجد تقديم معلق أو انتهت الصلاحية. يرجى إعادة التقديم من السيرفر.", ephemeral=True)
        await interaction.response.send_modal(ScenarioModal())

# خانة إجابة السيناريو
class ScenarioModal(discord.ui.Modal, title="سؤال السيناريو"):
    scenario_answer = discord.ui.TextInput(
        label="تصرفك لو خويك خالف قوانين السيرفر؟",
        style=discord.TextStyle.paragraph,
        placeholder="اكتب تصرفك بالتفصيل هنا...",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        db = load_database()
        if user_id not in db["pending"]:
            return await interaction.response.send_message("❌ عذراً، حدث خطأ أو انتهت الجلسة.", ephemeral=True)
        
        data = db["pending"].pop(user_id)
        save_database(db)
        
        data["scenario"] = self.scenario_answer.value
        
        log_channel = None
        for guild in interaction.client.guilds:
            ch = guild.get_channel(APPLY_LOG_CHANNEL_ID)
            if ch:
                log_channel = ch
                break

        if log_channel:
            embed = discord.Embed(
                title="╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n✦ 📋 تــقــديــم إداري جــديــد ✦\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯",
                color=discord.Color.blue()
            )
            embed.add_field(name="「👤」 المتقدم", value=f"「 {interaction.user.mention} 」", inline=False)
            embed.add_field(name="「📝」 الاسم الحقيقي", value=f"「 {data['real_name']} 」", inline=False)
            embed.add_field(name="「🏷️」 اليوزر", value=f"「 {data['username']} 」", inline=False)
            embed.add_field(name="「🎂」 العمر", value=f"「 {data['age']} 」", inline=False)
            embed.add_field(name="「🛠️」 الخبرات", value=f"「 {data['experience']} 」", inline=False)
            embed.add_field(name="「💡」 وش بنستفيد منك", value=f"「 {data['benefit']} 」", inline=False)
            embed.add_field(name="「⚖️」 إجابة السيناريو", value=f"「 {data['scenario']} 」", inline=False)

            view = ApplicationActionView(interaction.user)
            await log_channel.send(embed=embed, view=view)

        await interaction.response.send_message("✅ تم إكمال تقديمك وإرساله إلى الإدارة بنجاح!", ephemeral=True)

# أزرار لوحة التقديم الرئيسية (دائمة)
class ApplicationPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="تقديم", style=discord.ButtonStyle.primary, emoji="📝", custom_id="main_apply_button_permanent")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FirstApplicationModal())

# أزرار الإدارة في سجل التقديمات (قبول / رفض - دائمة)
class ApplicationActionView(discord.ui.View):
    def __init__(self, target_user: discord.User):
        super().__init__(timeout=None)
        self.target_user = target_user

    @discord.ui.button(label="قبول", style=discord.ButtonStyle.green, emoji="✅", custom_id="accept_apply_action_perm")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        has_role = any(role.id in STAFF_ROLE_IDS for role in interaction.user.roles)
        if not (has_role or interaction.user.guild_permissions.administrator):
            return await interaction.response.send_message("هذا الزر مخصص للإدارة فقط!", ephemeral=True)

        # توليد كود من 11 حرف ورقم طلب عشوائي
        auth_code = ''.join(random.choices(string.ascii_letters + string.digits, k=11))
        request_id = random.randint(1000, 9999)

        # حفظ البيانات المقبولة في قاعدة البيانات
        db = load_database()
        db["accepted"][str(self.target_user.id)] = {
            "auth_code": auth_code,
            "request_id": request_id,
            "rank": "إداري جديد"
        }
        save_database(db)

        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        success_message = (
            f"🎉 **مبروك! تم قبول طلب انضمامك لطاقم الإدارة.**\n\n"
            f"🏷️ **الرتبة:** إداري جديد\n"
            f"🆔 **رقم الطلب:** `#{request_id}`\n"
            f"🔑 **كود التوثيق:** `{auth_code}`\n\n"
            f"📌 **ملاحظة هامة:**\n"
            f"يرجى فتح تكت دعم فني وإرسال صورة للكود ورقم الطلب داخل التكت!"
        )

        try:
            await self.target_user.send(success_message)
        except:
            pass

        await interaction.response.send_message(f"تم قبول التقديم بواسطة {interaction.user.mention} وإرسال بيانات التوثيق للمتقدم.", ephemeral=True)

    @discord.ui.button(label="رفض", style=discord.ButtonStyle.danger, emoji="❌", custom_id="reject_apply_action_perm")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        has_role = any(role.id in STAFF_ROLE_IDS for role in interaction.user.roles)
        if not (has_role or interaction.user.guild_permissions.administrator):
            return await interaction.response.send_message("هذا الزر مخصص للإدارة فقط!", ephemeral=True)

        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        try:
            await self.target_user.send("❌ عذراً، تم رفض طلب انضمامك لطاقم الإدارة.")
        except:
            pass

        await interaction.response.send_message(f"تم رفض التقديم بواسطة {interaction.user.mention}.", ephemeral=True)

class Apply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='apply', description='إرسال لوحة التقديمات')
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_apply(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(APPLY_PANEL_CHANNEL_ID)
        if not channel:
            return await interaction.response.send_message("لم يتم العثور على روم لوحة التقديم المحدد!", ephemeral=True)

        embed = discord.Embed(
            title="╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n✦ 📋 نــظــام الــتــقــديــمات الإداريــة ✦\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯",
            description="اضغط على زر **تقديم** بالأسفل لفتح استمارة التقديم:",
            color=discord.Color.blue()
        )
        embed.set_footer(text="يرجى كتابة معلومات جادة وصحيحة.")
        
        await channel.send(embed=embed, view=ApplicationPanelView())
        await interaction.response.send_message("تم إرسال لوحة التقديم بنجاح!", ephemeral=True)

async def setup(bot):
    bot.add_view(ApplicationPanelView())
    bot.add_view(ScenarioButtonView())
    await bot.add_cog(Apply(bot))
