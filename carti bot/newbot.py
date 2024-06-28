import discord
import random
import asyncio
import aiosqlite
import os
import colorama

from colorama import Fore

from discord.ext import commands
from discord.commands import Option
from discord.ui import Button, View
from discord.ui import Select
from discord.ext import commands


prefix = ","

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)

color = 0x2b2d31

ownerid = 1192640390474518584
adminid = 1194110052647313428

@bot.event
async def on_ready():
    print(f"[@{bot.user.name}] is up")
    bot.db = await aiosqlite.connect('data.db')
    async with bot.db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS warns(member_id INTEGER, amount INTEGER, reason TEXT)")
        await bot.db.commit()
    print(f"[@{bot.user.name}] connected to database")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"carti.bio"))



class SelectMenuTestView(discord.ui.View):
    def __init__(self):
        super().__init__()


    @discord.ui.select(
        placeholder="Please select a category",
        options = [
            discord.SelectOption(
                label="home",
                emoji="<:cartiii:1193568305504587837>",
                value="home_option",
            )
                ],
        select_type=discord.ComponentType.select,
    )
    async def select_callback(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ):
        selected_option = select.values[0]

        if selected_option == "home_option":
            embed = discord.Embed(
                title="Help",
                description="",
                color=color,
            )

        await interaction.response.edit_message(content=None, embed=embed, view=self)

@bot.slash_command(name="help")
async def help(ctx):
    embed = discord.Embed(
        title="Help",
        description="Please select one of the following categories for commands",
        color=color,
    )
    view = SelectMenuTestView()
    await ctx.respond(embed=embed, view=view)


@bot.slash_command(name="ban", description="Ban a user")
@commands.has_role(adminid)
async def ban(ctx, user: discord.User):
    await ctx.guild.ban(user)
    embed = discord.Embed(
        title=f"Successfully banned {user}",
        color=color
    )
    await ctx.respond(embed=embed)


@bot.slash_command(name="kick", description="Kick a user")
@commands.has_role(adminid)
async def kick(ctx, user: discord.User):
    await ctx.guild.kick(user)
    embed = discord.Embed(
        title=f"Successfully kicked {user}",
        color=color
    )
    await ctx.respond(embed=embed)

servers = []

from datetime import timedelta

@bot.slash_command(name="timeout", description="Timeout a user")
@commands.has_role(adminid)
async def to(ctx, member: discord.Member, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0):
    if member.id == ctx.author.id:
        await ctx.send("You can't timeout yourself!")
        return
    if member.guild_permissions.moderate_members:
        await ctx.send("You can't do this, this person is a moderator!")
        return
    duration = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    if duration >= timedelta(days=28):
        await ctx.send("I can't mute someone for more than 28 days!")
        return
    await member.timeout_for(duration)
    embed = discord.Embed(
        title=f"Successfully timed out {member}",
        description=f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds",
        color=color
    )

    await ctx.respond(embed=embed)


@bot.slash_command(name="untimeout", description="Un-timeout a user")
@commands.has_role(adminid)
async def unt(ctx, member: discord.Member):
    await member.remove_timeout()
    embed = discord.Embed(
        title=f"Successfully removed timeout from {member}",
        color=color
    )

    await ctx.respond(embed=embed)


bot.run("MTE5MzE5NDcxMjAzNTc1ODA4MA.GCiQx5.gEuXausjaq2zxxBUcD7tcY_VLriwqaSRjzXtok")