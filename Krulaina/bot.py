# import stuff
import discord, os
from discord.ext import commands

#prefix
intents = discord.Intents().all()
client = commands.Bot(command_prefix = ";", case_insensitive = True, intents=intents)
    
@client.event
async def on_ready():
    print("Krulaina is online!")
    
#loading commands
@client.command()
async def load(ctx, extension):
    if ctx.author.id == 198224062512758784:
        client.load_extension(f"cogs.{extension}") 
        await ctx.send("Successfully loaded")
    else:
        await ctx.send("You don't have permission to do that!")
    
@client.command()
async def unload(ctx, extension):
    if ctx.author.id == 198224062512758784:
        client.unload_extension(f"cogs.{extension}") 
        await ctx.send("Successfully unloaded")
    else:
        await ctx.send("You don't have permission to do that!")
    
@client.command()
async def reload(ctx, extension):
    if ctx.author.id == 198224062512758784:
        client.reload_extension(f"cogs.{extension}") 
        await ctx.send("Successfully reloaded")
    else:
        await ctx.send("You don't have permission to do that!")
    
# load all cogs on start
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        if filename != "helperFunctions.py":
            client.load_extension(f"cogs.{filename[:-3]}")


# run client
client.run("")
