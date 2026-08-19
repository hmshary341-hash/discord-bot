import re
import discord
from discord import app_commands
from discord.ext import commands

REVIEW_CHANNEL_ID = 1539593111439941633


class BanModal(discord.ui.Modal, title="استبيان الباند"):
  user_input = discord.ui.TextInput(label="يوزر العضو أو الأيدي", placeholder="أيدي العضو المراد تبنيده")
  reason_input = discord.ui.TextInput(label="سبب الباند", style=discord.TextStyle.paragraph, placeholder="اكتب سبب الحظر بالتفصيل...")
  duration_input = discord.ui.TextInput(label="مدة الباند", placeholder="مثال: دائم أو 7 أيام")
  evidence_input = discord.ui.TextInput(label="الدليل (الصورة أو الرابط)", placeholder="ألصق الصورة أو رابط الدليل هنا مباشرة...", style=discord.TextStyle.paragraph)

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild

    match = re.search(r"\d+", self.user_input.value)
    if not match:
      return await interaction.followup.send("❌ يرجى إدخال أيدي صحيح للعضو.", ephemeral=True)
    
    member_id = int(match.group())
    member = guild.get_member(member_id)
    
    # محاولة تبنيد العضو
    try:
      if member:
        await member.ban(reason=self.reason_input.value)
      else:
        user_obj = await self.bot.fetch_user(member_id)
        await guild.ban(user_obj, reason=self.reason_input.value)
    except Exception as e:
      return await interaction.followup.send(f"❌ حدث خطأ أثناء تنفيذ الباند: {e}", ephemeral=True)

    review_channel = guild.get_channel(REVIEW_CHANNEL_ID)
    if review_channel:
      target_mention = f"<@{member_id}>"
      embed_text = (
          f"╭・𓆩 اســتــبــيــان الــبــانــد 𓆪・╮\n\n"
          f"👤 اســم الــعــضــو: {target_mention} (`{member_id}`)\n\n"
          f"🛡️ صــاحــب الــبــانــد: {interaction.user.mention}\n\n"
          f"⚔️ ســبــب الــبــانــد: {self.reason_input.value}\n\n"
          f"⏳ مــدة الــبــانــد: {self.duration_input.value}\n\n"
          f"📅 تــاريــخ انــتــهــاء الــعــقــوبــة: {self.duration_input.value}\n\n"
          f"📎 الدليل:\n{self.evidence_input.value}"
      )
      await review_channel.send(embed_text)

    await interaction.followup.send("✅ **تم تنفيذ الباند وإرسال الاستبيان للإدارة بنجاح.**", ephemeral=True)


class UnBanModal(discord.ui.Modal, title="إلغاء عقوبة الباند"):
  user_input = discord.ui.TextInput(label="أيدي العضو (User ID)", placeholder="أيدي الشخص لفك الباند عنه")
  reason_input = discord.ui.TextInput(label="سبب إلغاء العقوبة", style=discord.TextStyle.paragraph, placeholder="اكتب سبب إلغاء الباند...")

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild

    match = re.search(r"\d+", self.user_input.value)
    if not match:
      return await interaction.followup.send("❌ يرجى إدخال أيدي صحيح.", ephemeral=True)
    
    user_id = int(match.group())
    try:
      user_obj = await self.bot.fetch_user(user_id)
      await guild.unban(user_obj, reason=self.reason_input.value)
    except Exception as e:
      return await interaction.followup.send(f"❌ لم يتم العثور على العضو المحظور أو حدث خطأ: {e}", ephemeral=True)

    review_channel = guild.get_channel(REVIEW_CHANNEL_ID)
    if review_channel:
      await review_channel.send(f"🔓 **تم إلغاء الباند عن العضو:** <@{user_id}>\n👤 **بواسطة:** {interaction.user.mention}\n📝 **السبب:** {self.reason_input.value}")

    await interaction.followup.send("✅ **تم فك الباند بنجاح.**", ephemeral=True)


class BanView(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(label="بدء الاستبيان", style=discord.ButtonStyle.danger, custom_id="persistent_ban_btn")
  async def start_form(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(BanModal())

  @discord.ui.button(label="إلغاء العقوبة", style=discord.ButtonStyle.secondary, custom_id="persistent_unban_btn")
  async def cancel_form(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(UnBanModal())


class BanCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="setup_ban", description="نشر لوحة استبيان الباند")
  @app_commands.checks.has_permissions(administrator=True)
  async def setup_ban(self, interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚖️ لوحة نظام الحظر (Ban)",
        description="اضغط على **بدء الاستبيان** لتقديم طلب باند وتطبيقه، أو **إلغاء العقوبة** لفك الباند.",
        color=discord.Color.red(),
    )
    await interaction.response.send_message(embed=embed, view=BanView())


async def setup(bot):
  bot.add_view(BanView())
  await bot.add_cog(BanCog(bot))
