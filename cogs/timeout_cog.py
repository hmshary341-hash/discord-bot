from datetime import datetime, timedelta, timezone
import re
import discord
from discord import app_commands
from discord.ext import commands

REVIEW_CHANNEL_ID = 1539593111439941633


def parse_duration(duration_str):
  duration_str = duration_str.strip()
  match = re.search(r"(\d+)\s*(دقيقة|دقيقتين|ساعة|ساعات|يوم|أيام|m|h|d)?", duration_str, re.IGNORECASE)
  if not match:
    return timedelta(minutes=10)
  val = int(match.group(1))
  unit = match.group(2)
  if unit in ["ساعة", "ساعات", "h", "H"]:
    return timedelta(hours=val)
  elif unit in ["يوم", "أيام", "d", "D"]:
    return timedelta(days=val)
  else:
    return timedelta(minutes=val)


class TimeoutModal(discord.ui.Modal, title="استبيان التايم"):
  user_input = discord.ui.TextInput(label="يوزر العضو أو الأيدي", placeholder="مثال: @user أو الأيدي")
  reason_input = discord.ui.TextInput(label="سبب التايم", style=discord.TextStyle.paragraph, placeholder="اكتب سبب العقوبة هنا...")
  duration_input = discord.ui.TextInput(label="مدة التايم", placeholder="مثال: 30 دقيقة أو 2 ساعة أو 1 يوم")
  evidence_input = discord.ui.TextInput(label="الدليل (الصورة أو الرابط)", placeholder="ألصق الصورة أو رابط الدليل هنا مباشرة...", style=discord.TextStyle.paragraph)

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild

    # البحث عن العضو
    match = re.search(r"\d+", self.user_input.value)
    if not match:
      return await interaction.followup.send("❌ يرجى إدخال أيدي أو يوزر صحيح للعضو.", ephemeral=True)
    
    member_id = int(match.group())
    member = guild.get_member(member_id)
    if not member:
      try:
        member = await guild.fetch_member(member_id)
      except:
        return await interaction.followup.send("❌ لم يتم العثور على العضو في السيرفر.", ephemeral=True)

    delta = parse_duration(self.duration_input.value)
    expiry_time = datetime.now(timezone.utc) + delta
    expiry_timestamp = int(expiry_time.timestamp())

    try:
      await member.timeout(delta, reason=self.reason_input.value)
    except Exception as e:
      return await interaction.followup.send(f"❌ حدث خطأ أثناء تطبيق التايم على العضو: {e}", ephemeral=True)

    review_channel = guild.get_channel(REVIEW_CHANNEL_ID)
    if review_channel:
      embed_text = (
          f"╭・𓆩 اســتــبــيــان الــتــايــم 𓆪・╮\n\n"
          f"👤 اســم الــعــضــو: {member.mention} (`{member.id}`)\n\n"
          f"🛡️ صــاحــب الــتــايــم: {interaction.user.mention}\n\n"
          f"⚔️ ســبــب الــتــايــم: {self.reason_input.value}\n\n"
          f"⏳ مــدة الــتــايــم: {self.duration_input.value}\n\n"
          f"📅 تــاريــخ انــتــهــاء الــعــقــوبــة: <t:{expiry_timestamp}:F>\n\n"
          f"📎 الدليل:\n{self.evidence_input.value}"
      )
      await review_channel.send(embed_text)

    await interaction.followup.send("✅ **تم تنفيذ التايم بنجاح وإرسال الاستبيان للإدارة العليا.**", ephemeral=True)


class UnTimeoutModal(discord.ui.Modal, title="إلغاء عقوبة التايم"):
  user_input = discord.ui.TextInput(label="يوزر العضو أو الأيدي", placeholder="أيدي العضو لفك التايم عنه")
  reason_input = discord.ui.TextInput(label="سبب إلغاء العقوبة", style=discord.TextStyle.paragraph, placeholder="اكتب سبب إلغاء التايم...")

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild

    match = re.search(r"\d+", self.user_input.value)
    if not match:
      return await interaction.followup.send("❌ يرجى إدخال أيدي صحيح.", ephemeral=True)
    
    member = guild.get_member(int(match.group()))
    if not member:
      try:
        member = await guild.fetch_member(int(match.group()))
      except:
        return await interaction.followup.send("❌ لم يتم العثور على العضو.", ephemeral=True)

    try:
      await member.timeout(None, reason=self.reason_input.value)
    except Exception as e:
      return await interaction.followup.send(f"❌ لم يتم إزالة التايم: {e}", ephemeral=True)

    review_channel = guild.get_channel(REVIEW_CHANNEL_ID)
    if review_channel:
      await review_channel.send(f"🔓 **تم إلغاء التايم عن العضو:** {member.mention}\n👤 **بواسطة:** {interaction.user.mention}\n📝 **السبب:** {self.reason_input.value}")

    await interaction.followup.send("✅ **تم إلغاء التايم بنجاح.**", ephemeral=True)


class TimeoutView(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(label="بدء الاستبيان", style=discord.ButtonStyle.secondary, custom_id="persistent_timeout_btn")
  async def start_form(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(TimeoutModal())

  @discord.ui.button(label="إلغاء العقوبة", style=discord.ButtonStyle.danger, custom_id="persistent_untimeout_btn")
  async def cancel_form(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(UnTimeoutModal())


class TimeoutCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="setup_timeout", description="نشر لوحة استبيان التايم")
  @app_commands.checks.has_permissions(administrator=True)
  async def setup_timeout(self, interaction: discord.Interaction):
    embed = discord.Embed(
        title="⏳ لوحة نظام الإسكات (Timeout)",
        description="اضغط على **بدء الاستبيان** لتقديم طلب تايم وتطبيقه، أو **إلغاء العقوبة** لفك التايم.",
        color=discord.Color.gold(),
    )
    await interaction.response.send_message(embed=embed, view=TimeoutView())


async def setup(bot):
  bot.add_view(TimeoutView())
  await bot.add_cog(TimeoutCog(bot))
