import discord
from discord.ext import commands
from discord import app_commands

# آيديات الرومات المحدثة حسب طلبك
EVAL_PANEL_CHANNEL_ID = 1538838112564944926   # روم إرسال لوحة التقييم
EVAL_LOG_CHANNEL_ID = 1538837810407145512     # روم استقبال التقييمات

# 1. القائمة الأولى (التحذير + زر بدء التقييم - دائم)
class EvaluationStartView(discord.ui.View):
    def __init__(self):.
        super().__init__(timeout=None)

    @discord.ui.button(label="ابدأ التقييم", style=discord.ButtonStyle.primary, emoji="⭐", custom_id="start_eval_button_perm")
    async def start_eval(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EvaluationModal())

# 2. نافذة أسئلة التقييم
class EvaluationModal(discord.ui.Modal, title="تقييم الإدارة"):
    staff_username = discord.ui.TextInput(
        label="يوزر الإداري المراد تقييمه",
        placeholder="اكتب يوزر أو منشن الإداري هنا...",
        required=True
    )
    
    reason = discord.ui.TextInput(
        label="السبب",
        style=discord.TextStyle.paragraph,
        placeholder="اكتب سبب التقييم بالتفصيل...",
        required=True
    )
    
    stars = discord.ui.TextInput(
        label="التقييم بالنجوم (من 1 إلى 6)",
        placeholder="اكتب رقماً فقط من 1 إلى 6...",
        min_length=1,
        max_length=1,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        star_val = self.stars.value.strip()
        if not star_val.isdigit() or not (1 <= int(star_val) <= 6):
            return await interaction.response.send_message("❌ عذراً، يجب أن يكون التقييم بالنجوم رقماً صحيحاً من **1 إلى 6** فقط!", ephemeral=True)

        rating_num = int(star_val)
        stars_display = "⭐" * rating_num

        # إرسال التقييم إلى روم الاستقبال المحدد
        log_channel = None
        for guild in interaction.client.guilds:
            ch = guild.get_channel(EVAL_LOG_CHANNEL_ID)
            if ch:
                log_channel = ch
                break

        if log_channel:
            embed = discord.Embed(
                title="╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n✦ ⭐ تــقــيــم إداري جــديــد ✦\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯",
                color=discord.Color.gold()
            )
            embed.add_field(name="「👤」 العضو المقيّم", value=f"「 {interaction.user.mention} 」", inline=False)
            embed.add_field(name="「👮‍♂️」 يوزر الإداري", value=f"「 {self.staff_username.value} 」", inline=False)
            embed.add_field(name="「📊」 التقييم", value=f"「 {stars_display} ({rating_num}/6) 」", inline=False)
            embed.add_field(name="「📝」 السبب", value=f"「 {self.reason.value} 」", inline=False)

            await log_channel.send(embed=embed)

        # إرسال رسالة شكر في الخاص للعضو
        try:
            await interaction.user.send(
                "🌟 **شكراً لك على تقييمك!**\n"
                "نحن نقدر حرصك ومساهمتك في تحسين جودة طاقم الإدارة ومصداقية العمل في السيرفر."
            )
        except:
            pass # في حال كان الخاص مغلقاً

        await interaction.response.send_message("✅ شكراً لك، تم إرسال تقييمك بنجاح وتفقد رسائل الخاص!", ephemeral=True)

# 3. الكوج الخاص بنظام التقييم وإرسال اللوحة
class Evaluation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='setup_evaluation', description='إرسال لوحة تقييم الإدارة')
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_evaluation(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(EVAL_PANEL_CHANNEL_ID)
        if not channel:
            return await interaction.response.send_message("لم يتم العثور على روم إرسال اللوحة المحدد!", ephemeral=True)

        embed = discord.Embed(
            title="╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n✦ ⚠️ تــقــيــم طــاقــم الإدارة ✦\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯",
            description=(
                "⚠️ **لا تحاول تكسب إداري بصفك من التقييم!**\n\n"
                "اضغط على الزر بالأسفل لتقييم أي إداري بمصداقية وعدالة:"
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="كن مصيباً وعادلاً في تقييمك.")
        
        await channel.send(embed=embed, view=EvaluationStartView())
        await interaction.response.send_message("تم إرسال لوحة التقييم بنجاح!", ephemeral=True)

async def setup(bot):
    bot.add_view(EvaluationStartView())
    await bot.add_cog(Evaluation(bot))
