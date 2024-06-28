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

color = 0x89cff0

ownerid = 1190392666991636680
adminid = 1201213737013628980

@bot.event
async def on_ready():
    print(f"[@{bot.user.name}] is up")
    bot.db = await aiosqlite.connect('data.db')
    async with bot.db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS warns(member_id INTEGER, amount INTEGER, reason TEXT)")
        await bot.db.commit()
    print(f"[@{bot.user.name}] connected to database")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"carti.bio"))


commands_description = {
    'ban': f'{prefix}ban [user] > ban a user',
    'kick': '{prefix}kick [user] > kick a user',
    'warn': f'{prefix}warn [user] [reason] > warn a user',
    'cwarns': f'{prefix}cwarns [user] > get a users warns',
    'mc': f'{prefix}mc > shows the membercount',
    'lookup': f'{prefix}lookup [user] > lookup a user',
    'snipe': f'{prefix}snipe > get the last deleted message',
    'usage': f'{prefix}usage [command] > show the usage of a command',
    'help': f'{prefix}help > show the help',
    'to': f'{prefix}to [user] [days] [hours] [minutes] [seconds] > timeout the person',
    'unt': f'{prefix}unt [user] > untimeout the user',
    'ping': f'{prefix}ping > get the bots ping',
    'play': f'{prefix}play [text] > change the bots status',
    'listen': f'{prefix}listen [text] > change the bots status to listen',
    'watch': f'{prefix}watch [text] > change the bots status to watch',
    'role': f'{prefix}role [user] [role] > give a user a role',
    'img': f'{prefix}img [user] > give a user the pic perms'
}


@bot.command()
async def usage(ctx, command_name: str):
    description = commands_description.get(command_name.lower())
    if description:
        embed = discord.Embed(
            title=f'Usage for `{command_name}`',
            description=description,
            color=color
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            description=f'Command `{command_name}` not found.',
            color=color
        )
        await ctx.send(embed=embed)


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="**knives.lol commands**",
        description="Prefix: `,` [] = required, () = optional",
        color=color
    )

    embed.add_field(name="community commands", value="`cwarns [user]`, `mc`, `lookup [user]`, `snipe`", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    embed = discord.Embed(
        description=f" my latency is {round(bot.latency * 1000)}ms",
        color=color
    )
    await ctx.send(embed=embed)

@bot.command()
@commands.has_role(ownerid)
async def ban(ctx, user: discord.User):
    await ctx.guild.ban(user)
    embed = discord.Embed(
        title=f"Successfully banned {user}",
        color=color
    )
    await ctx.send(embed=embed)

@bot.command()
@commands.has_role(ownerid)
async def kick(ctx, user: discord.User):
    await ctx.guild.kick(user)
    embed = discord.Embed(
        title=f"Successfully kicked {user}",
        color=color
    )
    await ctx.send(embed=embed)





@bot.command()
async def mc(ctx):
    embed = discord.Embed(
        title="Member Count",
        description=f"{ctx.guild.member_count} members",
        color=color
    )
    await ctx.send(embed=embed)




servers = []

from datetime import timedelta

@bot.command()
@commands.has_role(adminid)
@commands.has_permissions(moderate_members=True)
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

    await ctx.send(embed=embed)


@bot.command()
@commands.has_role(adminid)
async def unt(ctx, member: discord.Member):
    await member.remove_timeout()
    embed = discord.Embed(
        title=f"Successfully removed timeout from {member}",
        color=color
    )

    await ctx.send(embed=embed)


@bot.command()
@commands.has_role(ownerid)
async def play(ctx, text):
    game = discord.Game(
        name=text
    )
    await bot.change_presence(activity=game)

    embed = discord.Embed(
        title="Playing",
        description=f"knives.lol is playing `{text}`",
        color=color
    )
    await ctx.send(embed=embed)


@bot.command()
@commands.has_role(ownerid)
async def listen(ctx, text):
    game = discord.Activity(
        type=discord.ActivityType.listening,
        name=text
    )
    await bot.change_presence(activity=game)

    embed = discord.Embed(
        title="Listening",
        description=f"knives.lol is listening to `{text}`",
        color=color
    )
    await ctx.send(embed=embed)

@bot.command()
@commands.has_role(ownerid)
async def watch(ctx, text):
    game = discord.Activity(
        type=discord.ActivityType.watching,
        name=text
    )
    await bot.change_presence(activity=game)

    embed = discord.Embed(
        title="Watching",
        description=f"knives.lol is watching `{text}`",
        color=color
    )
    await ctx.send(embed=embed)



@bot.event
async def on_member_join(member):

    channel = bot.get_channel(1193235676779528232)
    
    embed = discord.Embed(
        title="Welcome",
        description=f"Welcome {member.mention} to knives.lol",
        color=color
    )

    if channel:
        await channel.send(embed=embed)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "pic perm" in message.content or "pic perms" in message.content or "picperm" in message.content or "picperms" in message.content:

        embed = discord.Embed(
            title="want pic perm?",
            description="To get pic perm put `knives.lol | discord.gg/QsBFxhedSZ` in your activity.",
            color=color

        )
        await message.channel.send(embed=embed)


    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    global deleted_message
    global deleted_message_author
    deleted_message=message.content
    deleted_message_author=message.author.id    
    
    
@bot.command()
async def snipe(ctx):
    embed = discord.Embed(title="Sniped Message", description=f"User: <@{deleted_message_author}>\ncontent: {deleted_message}", color=color)
    await ctx.reply(embed=embed)




    
@bot.command()
@commands.has_role(ownerid)
async def role(ctx, member: discord.Member, *, role_name: str):
    if ctx.author.guild_permissions.manage_roles:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        
        if not role:
            embed = discord.Embed(
                description=f"Role '{role_name}' not found.",
                color=color
            )
            await ctx.send(embed=embed)
            return
        
        if role in member.roles:
            embed = discord.Embed(
                description=f"{member.mention} already has the {role.name} role.",
                color=color
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description=f"Added {role.name} role to {member.mention}.",
                color=color
            )
            await member.add_roles(role)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            description="You do not have permission to manage roles.",
            color=color
        )
        await ctx.send(embed=embed)

@bot.command()
@commands.has_role(adminid)
async def img(ctx, member: discord.Member):
    roleid = 1201213737013628980
    role = discord.utils.get(ctx.guild.roles, id=roleid)

    await member.add_roles(role)

    embed = discord.Embed(
        description=f"{member.mention} has been given pic perms",
        color=color
    )

    await ctx.send(embed=embed)


@bot.command()
@commands.has_role(adminid)
async def warn(ctx, member: discord.Member, *, reason=None):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM warns WHERE member_id = ?", (member.id,))
        existing_warn = await cursor.fetchone()

        if existing_warn:
            new_warn_count = existing_warn[1] + 1
            await cursor.execute("UPDATE warns SET amount = ?, reason = ? WHERE member_id = ?", (new_warn_count, reason, member.id))
        else:
            await cursor.execute("INSERT INTO warns VALUES (?, ?, ?)", (member.id, 1, reason))
        
        await bot.db.commit()

    embed = discord.Embed(
        title="Warned",
        description=f"{member.mention} has been warned",
        color=color
    )
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_role(adminid)
async def cwarns(ctx, member: discord.Member):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM warns WHERE member_id = ?", (member.id,))
        result = await cursor.fetchone()

        if result:
            embed = discord.Embed(
                title="Warns",
                description=f"{member.mention} has {result[1]} warns",
                color=color
            )
            if result[2]:
                embed.add_field(name="Reason", value=result[2], inline=False)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Warns",
                description=f"{member.mention} has no warns",
                color=color
            )
            await ctx.send(embed=embed)







bot.run("MTIxMjgwMDE2MDgwNDExMDQxNg.GSLSfK.FvzoPfZ5MWEl9aN_sH_QWsgoSWzrum-ySbp4us")