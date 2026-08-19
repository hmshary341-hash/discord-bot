import discord
from discord import app_commands
from discord.ext import commands


class KickModal(discord.ui.Modal, title="استبيان الطرد (Kick)"):
  user_input = discord.ui.TextInput(
      label="يوزر العضو أو الأيدي",
      placeholder="اكتب اسم العضو أو الأيدي الخاص به هنا...",
  )
  reason_input = discord.ui.TextInput(
      label="سبب العقوبة",
      style=discord.TextStyle.paragraph,
      placeholder="اكتب سبب الطرد بالتفصيل...",
  )

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.send_message(
        "✅ **تم إرسال استبيان الكك بنجاح.**\n📎 *الدليل ارسله بعد ماترفع"
        " الاستبيان في قناة الإدارة المخصصة.*",
        ephemeral=True,
    )


class KickView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="بدء الاستبيان",
      style=discord.ButtonStyle.primary,
      custom_id="persistent_kick_btn",
  )
  async def start_form(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_modal(KickModal())


class KickCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="setup_kick", description="نشر لوحة استبيان الطرد")
  @app_commands.checks.has_permissions(administrator=True)
  async def setup_kick(self, interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚠️ لوحة نظام الطرد (Kick)",
        description=(
            "مرحباً بك في نظام الطرد المؤقت من السيرفر.\n\n"
            "• **شروط الكك:** يُستخدم بحق الأعضاء الذين يتجاوزون الحدود"
            " ويتجاهلون التحذيرات البسيطة، مع إمكانية عودتهم برابط دعوة"
            " جديد.\n"
            "• يرجى الالتزام بالأنظمة ورفع الإثباتات المطلوبة.\n\n"
            "اضغط على الزر أدناه لبدء تقديم استبيان الطرد 👇"
        ),
        color=discord.Color.orange(),
    )
    await interaction.response.send_message(embed=embed, view=KickView())


async def setup(bot):
  bot.add_view(KickView())
  await bot.add_cog(KickCog(bot))
