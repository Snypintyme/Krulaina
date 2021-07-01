import discord, asyncio, random, math
from discord.ext import commands


class Games(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["rps"])
    async def rockPaperScissors(self, ctx):
        """ Play a game of rock paper scissors with the bot """

        # Unicode emojis
        choices = ("🪨", "📰", "✂️")

        rpsInitial = discord.Embed(title="Rock Paper Scissors")
        rpsInitial.add_field(name=":question:     :vs:     :question:",
                             value="Click on a reaction to make your choice.")
        message = await ctx.send(embed=rpsInitial)

        # Add reactions
        for reaction in choices:
            await message.add_reaction(reaction)

        # Get response
        try:
            reaction, user = await self.client.wait_for("reaction_add", check=lambda reaction, reactor: reactor == ctx.author and \
                str(reaction.emoji) in choices and reaction.message == message, timeout = 60.0)
        except asyncio.TimeoutError:
            await ctx.send(
                f"{ctx.author.mention} you took too long to respond, not playing with you :rage:"
            )
        else:
            computerChoice = random.choice(choices)

            # Determine result
            if (str(reaction.emoji) == "🪨" and computerChoice == "✂️") or \
            (str(reaction.emoji) == "📰" and computerChoice == "🪨") or \
            (str(reaction.emoji) == "✂️" and computerChoice == "📰"):
                result = "win"
            elif (str(reaction.emoji) == "🪨" and computerChoice == "📰") or \
            (str(reaction.emoji) == "📰" and computerChoice == "✂️") or \
            (str(reaction.emoji) == "✂️" and computerChoice == "🪨"):
                result = "lose"
            else:
                result = "tied"

            # Show result
            rpsFinal = discord.Embed(title="Rock Paper Scissors\n")
            rpsFinal.add_field(
                name=f"{reaction}     :vs:     {computerChoice}",
                value=f"You {result}!")
            await ctx.send(embed=rpsFinal)

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
            readFile = open("8ball.txt", "r")
            messages = readFile.readlines()
            readFile.close()
            await ctx.send(random.choice(messages))


def setup(client):
    client.add_cog(Games(client))
