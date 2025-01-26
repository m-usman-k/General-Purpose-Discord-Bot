import discord
from discord.ext import commands
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kick a member from the server."""
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="Member Kicked",
                description=f"{member.mention} has been kicked from the server. Reason: {reason}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

            # Log the kick action
            logger.info(f"{ctx.author} kicked {member} from the server. Reason: {reason}")

        except discord.Forbidden:
            await ctx.send("I do not have permission to kick this member.")
            logger.error(f"Failed to kick {member}: Insufficient permissions.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred: {e}")
            logger.error(f"Error during kick of {member}: {e}")
        except Exception as e:
            await ctx.send(f"An unexpected error occurred: {e}")
            logger.error(f"Unexpected error while kicking {member}: {e}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Ban a member from the server."""
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="Member Banned",
                description=f"{member.mention} has been banned from the server. Reason: {reason}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

            # Log the ban action
            logger.info(f"{ctx.author} banned {member} from the server. Reason: {reason}")

        except discord.Forbidden:
            await ctx.send("I do not have permission to ban this member.")
            logger.error(f"Failed to ban {member}: Insufficient permissions.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred: {e}")
            logger.error(f"Error during ban of {member}: {e}")
        except Exception as e:
            await ctx.send(f"An unexpected error occurred: {e}")
            logger.error(f"Unexpected error while banning {member}: {e}")
            
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User, *, reason=None):
        """Unban a member from the server."""
        try:
            # Unban the member
            await ctx.guild.unban(user, reason=reason)
            embed = discord.Embed(
                title="Member Unbanned",
                description=f"{user.mention} has been unbanned from the server. Reason: {reason}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

            # Log the unban action
            logger.info(f"{ctx.author} unbanned {user} from the server. Reason: {reason}")

        except discord.Forbidden:
            await ctx.send("I do not have permission to unban this member.")
            logger.error(f"Failed to unban {user}: Insufficient permissions.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred: {e}")
            logger.error(f"Error during unban of {user}: {e}")
        except Exception as e:
            await ctx.send(f"An unexpected error occurred: {e}")
            logger.error(f"Unexpected error while unbanning {user}: {e}")


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: int, *, reason=None):
        """Mute a member for a specified duration in minutes."""
        try:
            # Create a mute role if it doesn't exist
            mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if not mute_role:
                mute_role = await ctx.guild.create_role(name="Muted")
                for channel in ctx.guild.text_channels:
                    await channel.set_permissions(mute_role, speak=False, send_messages=False, read_messages=True)

            # Add the mute role to the member
            await member.add_roles(mute_role, reason=reason)
            embed = discord.Embed(
                title="Member Muted",
                description=f"{member.mention} has been muted for {duration} minutes. Reason: {reason}",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)

            # Log the mute action
            logger.info(f"{ctx.author} muted {member} for {duration} minutes. Reason: {reason}")

            # Wait for the specified duration (in seconds)
            await asyncio.sleep(duration * 60)

            # Remove the mute role after the duration
            await member.remove_roles(mute_role)
            embed = discord.Embed(
                title="Member Unmuted",
                description=f"{member.mention} has been unmuted after {duration} minutes.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

            # Log the unmute action
            logger.info(f"{ctx.author} unmuted {member} after {duration} minutes.")

        except discord.Forbidden:
            await ctx.send("I do not have permission to mute this member.")
            logger.error(f"Failed to mute {member}: Insufficient permissions.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred: {e}")
            logger.error(f"Error during mute of {member}: {e}")
        except Exception as e:
            await ctx.send(f"An unexpected error occurred: {e}")
            logger.error(f"Unexpected error while muting {member}: {e}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, *, reason=None):
        """Unmute a member."""
        try:
            mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if mute_role in member.roles:
                await member.remove_roles(mute_role, reason=reason)
                embed = discord.Embed(
                    title="Member Unmuted",
                    description=f"{member.mention} has been unmuted. Reason: {reason}",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)

                # Log the unmute action
                logger.info(f"{ctx.author} unmuted {member}. Reason: {reason}")
            else:
                await ctx.send(f"{member.mention} is not muted.")
        except discord.Forbidden:
            await ctx.send("I do not have permission to unmute this member.")
            logger.error(f"Failed to unmute {member}: Insufficient permissions.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred: {e}")
            logger.error(f"Error during unmute of {member}: {e}")
        except Exception as e:
            await ctx.send(f"An unexpected error occurred: {e}")
            logger.error(f"Unexpected error while unmuting {member}: {e}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
