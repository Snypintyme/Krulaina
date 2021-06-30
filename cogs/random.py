import discord, random
from discord.ext import commands

class Random(commands.Cog):
    def  __init__(self, client):
        self.client = client

    @commands.command() 
    async def typeWords(self, ctx):
        """ Makes Krulaina type whatever you specify """
        await ctx.send(ctx.message.content[10:])


    @commands.command(aliases=["8ball"]) 
    async def eightBall(self, ctx):
        """ Magic 8ball """

        if ctx.message.content == ".8ball" or ctx.message.content == ".eightBall":
            await ctx.send("You didn't ask anything!")
        else:
            readFile = open("cogs/8ball.txt", "r")
            messages = readFile.readlines()
            readFile.close()
            await ctx.send(random.choice(messages))


def setup(client):
    client.add_cog(Random(client))
