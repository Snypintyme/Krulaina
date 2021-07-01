import discord, asyncio, random
from cogs.games.adventure.helperFunctions import *
from discord.ext import commands


class ChooseYourOwnAdventure(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["a"])
    async def adventure(self, ctx):
        """ Choose your own adventure """

        # Load story
        story = getAdventure("cogs/games/adventure/adventure1.txt")

        # Confirm intention
        answer, message = await confirmIntention(ctx, self.client, f"{ctx.author}'s adventure", f"{story[0]}\nDo you wish to go on this adventure?", \
            "You did not go on this adventure", ["❌", "✅"], False, False)
        if answer == False:
            return

        # Main storyline
        line = 2
        allChoices = [
            "{}\N{COMBINING ENCLOSING KEYCAP}".format(num)
            for num in range(1, 10)
        ]
        while True:
            # Check for end of story
            if story[line - 1][1][0] == "C":
                await changeEmbedColour(ctx, f"{ctx.author}'s adventure",
                                        message, story[line - 1][0][0].strip(),
                                        discord.Colour.green())
                break
            elif story[line - 1][1][0] == "D":
                await changeEmbedColour(ctx, f"{ctx.author}'s adventure",
                                        message, story[line - 1][0][0].strip(),
                                        discord.Colour.red())
                break

            # Show next sections
            for i in range(len(story[line - 1][0]) - 1):
                storyEmbed = discord.Embed(title=f"{ctx.author}'s adventure",
                                           description=story[line - 1][0][i])
                await message.edit(embed=storyEmbed)
                await sendReactions(message, ["➡️"])

                try:
                    reaction, user = await self.client.wait_for("reaction_add", check=lambda reaction, reactor: reactor == ctx.author and \
                        str(reaction.emoji) == "➡️" and reaction.message == message, timeout = 60.0)
                except asyncio.TimeoutError:
                    await changeEmbedColour(ctx, f"{ctx.author}'s adventure",
                                            message, "Command timed out",
                                            discord.Colour.red())
                    break

            storyEmbed = discord.Embed(
                title=f"{ctx.author}'s adventure",
                description=story[line - 1][0][len(story[line - 1][0]) - 1])
            for i in range(2, len(story[line - 1])):
                storyEmbed.add_field(name=f"{i-1}. {story[line-1][i][0]}",
                                     value="\u200b")
            await message.edit(embed=storyEmbed)

            # Reload reactions
            choices = allChoices[:len(story[line - 1]) - 2]
            await sendReactions(message, choices)

            # Get response
            try:
                reaction, user = await self.client.wait_for("reaction_add", check=lambda reaction, reactor: reactor == ctx.author and \
                    str(reaction.emoji) in choices and reaction.message == message, timeout = 60.0)
            except asyncio.TimeoutError:
                await changeEmbedColour(ctx, f"{ctx.author}'s adventure",
                                        message, "Command timed out",
                                        discord.Colour.red())
                break

            # Next line in story
            index = getReactionNumber(choices, str(reaction.emoji)) + 1
            line = int(story[line - 1][index][1])

        await sendReactions(message, [])


def setup(client):
    client.add_cog(ChooseYourOwnAdventure(client))
