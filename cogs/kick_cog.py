import re
import discord
from discord import app_commands
from discord.ext import commands

REVIEW_CHANNEL_ID = 1539593111439941633


class KickModal(discord.ui.Modal, title="استبيان الكك"):
  user_input = discord.ui.TextInput(label="يوزر العضو أو الأيدي", placeholder="أيدي العضو المراد طرده")
  reason_input = discord.ui.TextInput(label="سبب الكك", style=discord.TextStyle.paragraph, placeholder="اكتب سبب الطرد بالتفصيل...")
  evidence_input = discord.ui.TextInput(label="الدليل (الصورة أو الرابط)", placeholder="ألصق الصورة أو رابط الدليل هنا مباشرة...", style=discord.TextStyle.paragraph)

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild

    match = re.search(r"\d+", self.user_input.value)
    if not match:
      return await interaction.followup.send("❌ يرجى إدخال أيدي صحيح للعضو.", ephemeral=True)
    
    member_id = int(match.group())
    member = guild.get_member(member_id)
    if not member:
      try:
        member = await guild.fetch_member(member_id)
      except:
        return await interaction.followup.send("❌ لم يتم العثور على العضو داخل السيرفر.", ephemeral=True)

    try:
      await member.kick(reason=self.reason_input.value)
    except Exception as e:
      return await interaction.followup.send(f"❌ حدث خطأ أثناء تنفيذ الطرد: {e}", ephemeral=True)

    review_channel = guild.get_channel(REVIEW_CHANNEL_ID)
    if review_channel:
      embed_text = (
          f"╭・𓆩 اســتــبــيــان الــكــك 𓆪・╮\n\n"
          f"👤 اســم الــعــضــو: {member.mention} (`{member.id}`)\n\n"
          f"🛡️ صــاحــب الــكــك: {interaction.user.mention}\n\n"
          f"⚔️ ســبــب الــكــك: {self.reason_input.value}\n\n"
          f"📅 تــاريــخ انــتــهــاء الــعــقــوبــة: تم التنفيذ فوريًا (طرد)\n\n"
          f"📎 الدليل:\n{self.evidence_input.value}"
      )
      await review_channel.send(embed_text)

    await interaction.followup.send("✅ **تم تنفيذ الطرد وإرسال الاستبيان للإدارة بنجاح.**", ephemeral=True)


class KickView(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(label="بدء الاستبيان", style=discord.ButtonStyle.primary, custom_id="persistent_kick_btn")
  async def start_form(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(KickModal())


class KickCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="setup_kick", description="نشر لوحة استبيان الطرد (الكك)")
  @app_commands.checks.has_permissions(administrator=True)
  async def setup_kick(self, interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚠️ لوحة نظام الطرد (Kick)",
        description="اضغط على **بدء الاستبيان** لتقديم طلب طرد وتطبيقه مباشرة.",
        color=discord.Color.orange(),
    )
    await interaction.response.send_message(embed=embed, view=KickView())


async def setup(bot):
  bot.add_view(KickView())
  await bot.add_cog(KickCog(bot))
