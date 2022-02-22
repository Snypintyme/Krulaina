# import stuff
import discord, os
from discord.ext import commands
from dotenv import load_dotenv
from constants import SNYPINTYME_ID

load_dotenv()

# Prefix
intents = discord.Intents().all()
client = commands.Bot(command_prefix = ";", case_insensitive = True, intents=intents)
    
@client.event
async def on_ready():
    print("Krulaina is online!")
    
# Loading commands
@client.command()
async def load(ctx, extension):
    if ctx.author.id == SNYPINTYME_ID:
        client.load_extension(f"cogs.{extension}") 
        await ctx.send("Successfully loaded")
    else:
        await ctx.send("You don't have permission to do that!")
    
@client.command()
async def unload(ctx, extension):
    if ctx.author.id == SNYPINTYME_ID:
        client.unload_extension(f"cogs.{extension}") 
        await ctx.send("Successfully unloaded")
    else:
        await ctx.send("You don't have permission to do that!")
    
@client.command()
async def reload(ctx, extension):
    if ctx.author.id == SNYPINTYME_ID:
        client.reload_extension(f"cogs.{extension}") 
        await ctx.send("Successfully reloaded")
    else:
        await ctx.send("You don't have permission to do that!")
    
# Load all cogs on start
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        if filename != "helperFunctions.py":
            client.load_extension(f"cogs.{filename[:-3]}")


# Run client
TOKEN = os.getenv("TOKEN")
client.run(TOKEN)
