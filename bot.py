import discord, os, webserver
from discord.ext import commands

# Prefix = ;
intents = discord.Intents().all()
client = commands.Bot(command_prefix=";",
                      case_insensitive=True,
                      intents=intents)


@client.event
async def on_ready():
    print("Krulaina is online!")


# Loading commands
@client.command()
async def load(ctx, extension):
    if ctx.author.id == 198224062512758784:
        client.load_extension(extension)
        await ctx.send("Successfully loaded")
    else:
        await ctx.send("You don't have permission to do that!")


@client.command()
async def unload(ctx, extension):
    if ctx.author.id == 198224062512758784:
        client.unload_extension(extension)
        await ctx.send("Successfully unloaded")
    else:
        await ctx.send("You don't have permission to do that!")


@client.command()
async def reload(ctx, extension):
    if ctx.author.id == 198224062512758784:
        client.reload_extension(extension)
        await ctx.send("Successfully reloaded")
    else:
        await ctx.send("You don't have permission to do that!")


# Load all cogs on start
client.load_extension(f"cogs.admin.admin")
client.load_extension(f"cogs.games.adventure.cyoa")
client.load_extension(f"cogs.games.dungeon.dungeonAdventure")
client.load_extension(f"cogs.games.gacha.animeRPG")
client.load_extension(f"cogs.games.other.connect4")
client.load_extension(f"cogs.games.other.games")
client.load_extension(f"cogs.games.other.tic tac toe")

# Run client
webserver.keepAlive()
TOKEN = os.environ.get("SECRET_KEY")
client.run(TOKEN)
