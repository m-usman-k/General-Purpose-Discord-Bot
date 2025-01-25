import discord
from discord.ext import commands
import logging
import os, dotenv

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

    await bot.load_extension("cogs.Tickets")
    await bot.tree.sync()

bot.run(BOT_TOKEN)
