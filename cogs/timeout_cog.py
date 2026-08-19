import discord
from discord import app_commands
from discord.ext import commands


class TimeoutModal(discord.ui.Modal, title="استبيان الإسكات (Timeout)"):
  user_input = discord.ui.TextInput(
      label="يوزر العضو أو الأيدي",
      placeholder="اكتب اسم العضو أو الأيدي الخاص به هنا...",
  )
  reason_input = discord.ui.TextInput(
      label="سبب العقوبة",
      style=discord.TextStyle.paragraph,
      placeholder="اكتب سبب التايم والمدة المقترحة...",
  )

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.send_message(
        "✅ **تم إرسال استبيان التايم بنجاح.**\n📎 *الدليل ارسله بعد ماترفع"
        " الاستبيان في قناة الإدارة المخصصة.*",
        ephemeral=True,
    )


class TimeoutView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="بدء الاستبيان",
      style=discord.ButtonStyle.secondary,
      custom_id="persistent_timeout_btn",
  )
  async def start_form(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_modal(TimeoutModal())


class TimeoutCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(
      name="setup_timeout", description="نشر لوحة استبيان الإسكات (Timeout)"
  )
  @app_commands.checks.has_permissions(administrator=True)
  async def setup_timeout(self, interaction: discord.Interaction):
    embed = discord.Embed(
        title="⏳ لوحة نظام الإسكات (Timeout)",
        description=(
            "مرحباً بك في لوحة نظام الإسكات الإداري.\n\n"
            "• **العقوبات والتايمات المعتمدة (حسب مهام الإدارة):**\n"
            "  - `10 دقائق`: للسبام البسيط أو الإزعاج الخفيف.\n"
            "  - `ساعة واحدة`: للشتم اللفظي أو سوء الأدب المحدود.\n"
            "  - `6 ساعات إلى 24 ساعة`: لتكرار المخالفات أو الاستفزاز"
            " المستمر.\n"
            "  - `أكثر من ذلك`: للمخالفات الجسيمة المتاحة.\n\n"
            "اضغط على الزر أدناه لبدء تقديم استبيان التايم 👇"
        ),
        color=discord.Color.gold(),
    )
    await interaction.response.send_message(embed=embed, view=TimeoutView())


async def setup(bot):
  bot.add_view(TimeoutView())
  await bot.add_cog(TimeoutCog(bot))
