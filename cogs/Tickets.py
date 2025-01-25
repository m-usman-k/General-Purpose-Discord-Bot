import discord
from discord.ext import commands
from discord.ui import Button, View
import os, aiofiles

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_roles = {}
        self.user_tickets = {}
        self.ticket_logs = "ticket_logs"  # Directory to store ticket logs

        # Ensure the logs directory exists
        if not os.path.exists(self.ticket_logs):
            os.makedirs(self.ticket_logs)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ticket(self, ctx):
        """Command to start the ticket creation process."""
        if ctx.author.id in self.user_tickets:
            await ctx.send("You already have an open ticket. Please close it before creating a new one.")
            return

        embed = discord.Embed(
            title="Create a Ticket",
            description="Click the button below to create a ticket.",
            color=discord.Color.blue()
        )
        button = Button(label="Create Ticket", style=discord.ButtonStyle.primary)

        async def button_callback(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            if interaction.user != ctx.author:
                await interaction.response.send_message("Only the command initiator can use this button.", ephemeral=True)
                return

            guild = interaction.guild
            ticket_category = discord.utils.get(guild.categories, name="Tickets")
            if not ticket_category:
                ticket_category = await guild.create_category("Tickets")

            # Check if user already has a ticket
            if ctx.author.id in self.user_tickets:
                await interaction.response.send_message("You already have an open ticket. Please close it first.", ephemeral=True)
                return

            # Create ticket channel
            ticket_channel = await guild.create_text_channel(
                name=f"ticket-{interaction.user.name}",
                category=ticket_category
            )

            # Create a role for the ticket
            ticket_role = await guild.create_role(name=f"Ticket-{interaction.user.name}")
            self.ticket_roles[ticket_channel.id] = ticket_role.id
            self.user_tickets[ctx.author.id] = ticket_channel.id

            # Assign role permissions
            await ticket_channel.set_permissions(guild.default_role, read_messages=False)
            await ticket_channel.set_permissions(ticket_role, read_messages=True, send_messages=True)
            await interaction.user.add_roles(ticket_role)

            embed = discord.Embed(
                title="Ticket Created",
                description=f"Your ticket has been created: {ticket_channel.mention}",
                color=discord.Color.green()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)

            # Send admin controls embed
            admin_embed = discord.Embed(
                title="Admin Controls",
                description="Use the buttons below to manage this ticket.",
                color=discord.Color.red()
            )
            close_button = Button(label="Close Ticket", style=discord.ButtonStyle.danger)
            delete_button = Button(label="Delete Ticket", style=discord.ButtonStyle.danger)

            async def close_callback(interaction2: discord.Interaction):
                if not interaction2.user.guild_permissions.administrator:
                    await interaction2.response.send_message("You do not have permission to use this button.", ephemeral=True)
                    return
                
                # Create or get the "Closed Tickets" category
                closed_category = discord.utils.get(interaction2.guild.categories, name="Closed Tickets")
                if not closed_category:
                    closed_category = await interaction2.guild.create_category("Closed Tickets")
                
                # Move the ticket channel to the "Closed Tickets" category
                await ticket_channel.edit(category=closed_category)
                
                # Set the ticket role permissions to prevent further messages
                await ticket_channel.set_permissions(ticket_role, read_messages=False)
                await interaction2.response.send_message("Ticket closed and moved to 'Closed Tickets'.", ephemeral=True)

                # Remove the ticket role from the user
                await interaction2.user.remove_roles(ticket_role)


            async def delete_callback(interaction3: discord.Interaction):
                if not interaction3.user.guild_permissions.administrator:
                    await interaction3.response.send_message("You do not have permission to use this button.", ephemeral=True)
                    return

                # Remove role from the user
                if ticket_role in interaction3.user.roles:
                    await interaction3.user.remove_roles(ticket_role)

                # Delete the ticket channel and role
                await ticket_channel.delete()
                if ticket_role:
                    await ticket_role.delete()

                # Clean up data
                self.ticket_roles.pop(ticket_channel.id, None)
                self.user_tickets.pop(ctx.author.id, None)

            close_button.callback = close_callback
            delete_button.callback = delete_callback

            admin_view = View()
            admin_view.add_item(close_button)
            admin_view.add_item(delete_button)

            await ticket_channel.send(embed=admin_embed, view=admin_view)

        button.callback = button_callback
        view = View(timeout=None)
        view.add_item(button)
        await ctx.send(embed=embed, view=view)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_user(self, ctx, member: discord.Member):
        """Add a user to the ticket by giving them the ticket role."""
        ticket_role_id = self.ticket_roles.get(ctx.channel.id)
        if not ticket_role_id:
            await ctx.send("This command can only be used in a ticket channel.")
            return

        ticket_role = ctx.guild.get_role(ticket_role_id)
        await member.add_roles(ticket_role)
        await ctx.send(f"{member.mention} has been added to the ticket.")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Log messages sent in ticket channels."""
        if message.channel.id in self.ticket_roles:
            log_entry = f"{message.author}: {message.content}"
            log_file_path = os.path.join(self.ticket_logs, f"ticket-{message.channel.id}.txt")
            async with aiofiles.open(log_file_path, mode="a") as log_file:
                await log_file.write(log_entry + "\n")

async def setup(bot):
    await bot.add_cog(Tickets(bot))
