import discord
from discord.ext import commands, tasks
import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_stats.start()  # Start the background task to update stats periodically

    def cog_unload(self):
        self.update_stats.cancel()  # Cancel the task if the cog is unloaded

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_stats(self, ctx):
        """Create statistics channels for the server."""
        try:
            # Create the statistics category if it doesn't exist
            category = discord.utils.get(ctx.guild.categories, name="Server Stats")
            if not category:
                category = await ctx.guild.create_category("Server Stats")
                logger.info(f"Created new category: Server Stats")

            # Create channels for each stat (if they don't exist)
            await self._create_or_get_channel(ctx, category, "total-members", "Total Members: 0")
            await self._create_or_get_channel(ctx, category, "actual-users", "Actual Users: 0")
            await self._create_or_get_channel(ctx, category, "total-bots", "Total Bots: 0")
            await self._create_or_get_channel(ctx, category, "active-tickets", "Active Tickets: 0")
            await self._create_or_get_channel(ctx, category, "total-tickets", "Total Tickets: 0")
            await self._create_or_get_channel(ctx, category, "members-joined-this-month", "Members Joined This Month: 0")

            await ctx.send("Server statistics channels have been created successfully!")
            logger.info("Statistics channels have been created.")

        except Exception as e:
            await ctx.send(f"An error occurred while creating statistics channels: {e}")
            logger.error(f"Unexpected error while creating statistics channels: {e}")

    async def _create_or_get_channel(self, ctx, category, channel_name, default_name):
        """Create a channel or get the existing one."""
        existing_channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
        if not existing_channel:
            try:
                existing_channel = await ctx.guild.create_text_channel(channel_name, category=category)
                logger.info(f"Created new channel: {channel_name}")
            except discord.Forbidden:
                logger.error(f"Permission error creating channel {channel_name}")
                await ctx.send(f"Permission error: Cannot create channel {channel_name}. Please ensure I have the correct permissions.")
                return
            except Exception as e:
                logger.error(f"Unexpected error creating channel {channel_name}: {e}")
                await ctx.send(f"An unexpected error occurred while creating channel {channel_name}: {e}")
                return

        # Update the channel with the correct stats (without doubling the name)
        if not existing_channel.name.startswith(channel_name):
            await existing_channel.edit(name=f"{channel_name}: {default_name}")
            logger.info(f"Updated channel {channel_name} with default name: {default_name}")

    @tasks.loop(seconds=3)
    async def update_stats(self):
        """Periodically update the statistics channels."""
        guild = self.bot.get_guild(1251412440566992977)  # Replace with your server ID
        if not guild:
            logger.error("Unable to find the guild. Make sure the bot is in the server.")
            return

        try:
            # Get the total number of members, bots, and actual users
            total_members = len(guild.members)
            total_bots = len([member for member in guild.members if member.bot])
            actual_users = total_members - total_bots

            # Get the "Tickets" and "Closed Tickets" categories
            tickets_category = discord.utils.get(guild.categories, name="Tickets")
            closed_tickets_category = discord.utils.get(guild.categories, name="Closed Tickets")

            # Calculate active tickets (channels under "Tickets" category with members)
            active_tickets = 0
            if tickets_category:
                active_tickets = len([channel for channel in tickets_category.text_channels if len(channel.members) > 0])

            # Calculate total tickets (channels under both "Tickets" and "Closed Tickets" categories)
            total_tickets = 0
            if tickets_category:
                total_tickets += len(tickets_category.text_channels)
            if closed_tickets_category:
                total_tickets += len(closed_tickets_category.text_channels)

            # Calculate how many members joined this month
            current_month = datetime.datetime.now().month
            members_joined_this_month = len([member for member in guild.members if member.joined_at and member.joined_at.month == current_month])

            # Update channel names with the statistics
            total_members_channel = discord.utils.get(guild.text_channels, name="total-members")
            if total_members_channel:
                await total_members_channel.edit(name=f"Total Members: {total_members}")

            actual_users_channel = discord.utils.get(guild.text_channels, name="actual-users")
            if actual_users_channel:
                await actual_users_channel.edit(name=f"Actual Users: {actual_users}")

            total_bots_channel = discord.utils.get(guild.text_channels, name="total-bots")
            if total_bots_channel:
                await total_bots_channel.edit(name=f"Total Bots: {total_bots}")

            active_tickets_channel = discord.utils.get(guild.text_channels, name="active-tickets")
            if active_tickets_channel:
                await active_tickets_channel.edit(name=f"Active Tickets: {active_tickets}")

            total_tickets_channel = discord.utils.get(guild.text_channels, name="total-tickets")
            if total_tickets_channel:
                await total_tickets_channel.edit(name=f"Total Tickets: {total_tickets}")

            joined_this_month_channel = discord.utils.get(guild.text_channels, name="members-joined-this-month")
            if joined_this_month_channel:
                await joined_this_month_channel.edit(name=f"Members Joined This Month: {members_joined_this_month}")

            logger.info("Updated server statistics channels.")

        except Exception as e:
            logger.error(f"Error updating stats: {e}")

async def setup(bot):
    await bot.add_cog(Statistics(bot))
