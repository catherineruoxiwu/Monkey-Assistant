import discord
import time
import random
import asyncio
import json
import os
import sqlite3
from discord.ext import commands

id = 721857311655723059
messages = joined = 0
dic = {"Leeds#0925": 1}

token = "NzIxODU2NDY3Mzk2ODUzODUz.Xubalw.USaE4n2W1J4Sz_Xh2XDttTHwvu8"
client = commands.Bot(command_prefix='.')


@client.event
async def on_ready():
    db = sqlite3.connect('main.sqlite')
    print('Bot online')
    return await client.change_presence(activity=discord.Activity(type=1, name='with your feelings'))


@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.channel.send(f"""{ctx.author.mention} has reloaded the {extension}.py extension""")


@client.command()
async def hello(ctx):
    await ctx.channel.send(f"""Helloijarejo, {ctx.author.mention}""")
# -----------------------------------------------------------------------------
@client.command()
async def hello2(ctx):
    await ctx.channel.send(f"""Hello, {ctx.author.mention}""")
# -----------------------------------------------------------------------------


@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)


@client.command()
async def users(ctx):
    await ctx.channel.send(f"""Number of users: {client.get_guild(id).member_count}""")

'''
@client.command()
async def ping(ctx):
    await ctx.send(f"""{ctx.author.mention} stop pinging!""")
'''



@client.command()
async def magic8(ctx, *arg):
    choices = ["It is certain",
               "It is definitely so",
               "Without a doubt",
               "Yes - definitely",
               "You may rely on it",
               "As I see it, yes",
               "Most likely",
               "Outlook good",
               "Yes",
               "Signs point to yes",
               "Reply hazy, try again",
               "Ask again later",
               "Better not tell you now",
               "Cannot predict now",
               "Concentrate and ask again",
               "Don't sure on it",
               "My reply is no",
               "My sources say no",
               "Outlook not so good",
               "Very doubtful"]
    randchoice = random.choice(choices)

    response = discord.Embed(title=" ".join(arg), description=randchoice, color=0x2ECC71)
    await ctx.send(content=None, embed=response)


# -----------------------------------------------------------------------------
@client.command()
async def pic(ctx):
    await ctx.channel.send(file=discord.File('cat.jpg'))
    
@client.command()
async def pic1(ctx):
    await ctx.channel.send(file=discord.File('1.jpg'))

@client.command()
async def pic2(ctx):
    await ctx.channel.send(file=discord.File('2.jpg'))
    
@client.command()
async def pic3(ctx):
    await ctx.channel.send(file=discord.File('3.jpg'))
    
@client.command()
async def pic4(ctx):
    await ctx.channel.send(file=discord.File('4.jpg'))

# -----------------------------------------------------------------------------

@client.command()
async def options(ctx):
    help_command = discord.Embed(title="Help on BOT", description="Some useful commands", color=0xC0392B)
    help_command.add_field(name="hello", value="Greets the user")
    help_command.add_field(name="user", value="prints the number of users")
    help_command.add_field(name="magic8", value="ask the magic 8 ball a question")
    help_command.add_field(name="coinflip", value="flip a coin. Heads or tails?")
    help_command.add_field(name="work", value="work and earn 2 coins")
    help_command.add_field(name="money", value="see how much you have")
    help_command.add_field(name="ping", value="get mentioned")
    await ctx.send(content=None, embed=help_command)


async def update_stats():
    await client.wait_until_ready()
    global messages, joined

    while not client.is_closed():
        try:
            with open("stats.txt", "a") as f:
                f.write(f"Time: {int(time.time())}, Messages: {messages}, Members Joined: {joined}\n")

                messages = joined = 0

                await asyncio.sleep(5)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)



'''
@client.event
async def on_member_update(before, after):
    print("changing")
    n = after.nick
    if n: #checks if n is null
        if n.lower().count("leeds") > 0:
            print("name change attempt")
            last = before.nick
            if last:
                await after.edit(nick=last)
            else:
                await after.edit(nick="no, stop that!")
'''

@client.event
async def on_member_join(member):
    global joined
    joined += 1
    for channel in member.guild.channels:
        if str(channel) == "general":
            await channel.send(f"""Welcome to the server {member.mention}""")

    #updates data
    with open('users.json', 'r') as f:
        docs = json.load(f)
    await update_data(docs, member)
    with open('users.json', 'w') as f:
        json.dump(docs, f)


@client.event
async def on_message(message):
    global messages
    messages += 1
    if str(message.author) != "testbot#4215":

        with open('users.json', 'r') as f:
            users = json.load(f)

        await update_data(users, message.author)
        await add_experience(users, message.author, 5)
        await level_up(users, message.author, message.channel)

        with open('users.json', 'w') as f:
            json.dump(users, f)

        await client.process_commands(message)


async def update_data(users, user):
    if str(user.id) not in users:
        users[str(user.id)] = {}
        users[str(user.id)]['experience'] = 0
        users[str(user.id)]['level'] = 1
        users[str(user.id)]['money'] = 0


async def add_experience(users, user, exp):
    users[str(user.id)]['experience'] += exp


async def add_money(money, user, amount):
    money[str(user.id)]['money'] += amount


async def level_up(users, user, channel):
    experience = users[str(user.id)]['experience']
    lvl_start = users[str(user.id)]['level']
    lvl_end = int(experience ** (1/4))

    if lvl_start < lvl_end:
        await channel.send('{} has leveled up to level {}'.format(user.mention, lvl_end))
        users[str(user.id)]['level'] = lvl_end

client.loop.create_task(update_stats())
client.run(token)
