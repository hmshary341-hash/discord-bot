import discord
from discord.ext import commands


class BanModal(discord.ui.Modal, title="استبيان الحظر (Ban)"):.
  user_input = discord.ui.TextInput(
      label="يوزر العضو أو الأيدي",
      placeholder="اكتب اسم العضو أو الأيدي الخاص به هنا...",
  )
  reason_input = discord.ui.TextInput(
      label="سبب العقوبة",
      style=discord.TextStyle.paragraph,
      placeholder="اكتب سبب الحظر بالتفصيل...",
  )

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.send_message(
        "✅ **تم إرسال استبيان الباند بنجاح.**\n📎 *الدليل ارسله بعد ماترفع"
        " الاستبيان في قناة الإدارة المخصصة.*",
        ephemeral=True,
    )


class BanView(discord.ui.View):

  def __init__(self):
    super().__init__(
        timeout=None
    )  # هذا يمنع انتهاء صلاحية الزر نهائياً

  @discord.ui.button(
      label="بدء الاستبيان",
      style=discord.ButtonStyle.danger,
      custom_id="persistent_ban_btn",  # معرف ثابت لضمان استمرارية الزر
  )
  async def start_form(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_modal(BanModal())


class BanCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="setup_ban")
  @commands.has_permissions(administrator=True)
  async def setup_ban(self, ctx):
    embed = discord.Embed(
        title="⚖️ لوحة نظام الحظر (Ban)",
        description=(
            "مرحباً بك في نظام العقوبات الصارمة.\n\n"
            "• **شروط الباند:** يُستخدم هذا الإجراء بحق المخالفين خطراً جسيماً"
            " على أمان السيرفر أو المخترقين أو المخالفين المتكررين بشدة.\n"
            "• يرجى تحري الدقة ورفع الأدلة الموثوقة بعد إرسال الاستبيان.\n\n"
            "اضغط على الزر أدناه لبدء تقديم استبيان الحظر 👇"
        ),
        color=discord.Color.red(),
    )
    await ctx.send(embed=embed, view=BanView())


async def setup(bot):
  bot.add_view(
      BanView()
  )  # تسجيل الزر ليبقى يعمل حتى لو تم إعادة تشغيل البوت
  await bot.add_cog(BanCog(bot))
