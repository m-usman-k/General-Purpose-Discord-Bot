import discord
from discord.ext import commands
import logging
import os, dotenv
from discord import app_commands

# Load environment variables
dotenv.load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Logging setup
if not os.path.exists("logs"):
    os.mkdir("logs")
logging.basicConfig(
    filename="logs/ticket_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    await bot.load_extension("cogs.Moderation")
    await bot.load_extension("cogs.Tickets")
    await bot.load_extension("cogs.Statistics")
    await bot.tree.sync()
    
@bot.tree.command(name="sendembed", description="Send an embed to a specified channel (Admin only)")
@app_commands.describe(channel="The channel to send the embed to", title="The title of the embed", description="The description of the embed")
async def send_embed(interaction: discord.Interaction, channel: discord.TextChannel, title: str, description: str):
    """
    Sends an embed message to a specified channel.
    Parameters:
      - channel: The channel to send the embed message to (mention or ID).
      - title: The title of the embed.
      - description: The description of the embed.
    """
    # Check if the user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have the required permissions to use this command.", ephemeral=True)
        return

    embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
    embed.set_footer(text=f"Sent by {interaction.user}")

    try:
        await channel.send(embed=embed)
        await interaction.response.send_message(f"Embed sent to {channel.mention}!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to send embed: {e}", ephemeral=True)

bot.run(BOT_TOKEN)
