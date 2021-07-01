# import stuff
import discord, asyncio, math, random
from cogs.games.gacha.helperFunctions import *
from discord.ext import commands


class AnimeRPG(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["i"])
    async def inventory(self, ctx):
        """ Shows user's iventory """

        # Check for desired user
        player = await getDesiredUser(ctx, self.client)
        if player == False:
            await ctx.send(f"{ctx.author.mention} that user was not found!")
            return
        uid = str(player.id)

        # Get invenotry from file
        inv = getFromFile1("cogs/inventory.txt", uid, ",")

        # Check if user has any items
        if inv == False:
            await ctx.send(f"{player} has no items!")

        else:
            # Format inventory
            items = ""
            for item in inv[1:]:
                items += item + "\n"

            # Display inventory
            invEmbed = discord.Embed(title="Inventory")
            invEmbed.add_field(name=f"{player}'s items", value=items)
            invEmbed.set_thumbnail(url=player.avatar_url)
            await ctx.send(embed=invEmbed)

    @commands.command(aliases=["c"])
    async def collection(self, ctx):
        """ Shows user's collection """
        def getSummon(code):
            """ Format summon """
            readFile = open("cogs/generatedCards.txt", "r")
            for line in readFile:
                if code in line:
                    desc = list(map(str.strip, line.split(',')))
                    break
            readFile.close()

            return f"{desc[0]} · {desc[3]} · {desc[1]} {getGenderSymbols(desc[2])}"

        # Check for desired user
        player = await getDesiredUser(ctx, self.client)
        if player == False:
            await ctx.send(f"{ctx.author.mention} that user was not found!")
            return
        uid = str(player.id)

        # Get user collection
        collection = getFromFile1("cogs/collections.txt", uid, ",")

        # Check collection exists
        if collection == False:
            await ctx.send(f"{player} has no summons!")
        else:
            totalCharacters = len(collection) - 1

            # Initial display
            collectionEmbed = discord.Embed(title="Summon Collection")
            characters = "\u200b"
            page = 1
            if collection != False:
                characters = ""
                if totalCharacters < 11:
                    for code in collection[page:]:
                        characters += getSummon(code) + "\n"
                else:
                    for code in collection[1:11]:
                        characters += getSummon(code) + "\n"

            # Show collection
            collectionEmbed = discord.Embed(title="Summon Collection")
            collectionEmbed.set_footer(
                text=
                f"Showing page {page} out of {math.ceil(totalCharacters/10)}")
            collectionEmbed.add_field(name=f"{player}'s Summons",
                                      value=characters)
            collectionEmbed.set_thumbnail(url=player.avatar_url)
            message = await ctx.send(embed=collectionEmbed)
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")

            # Persistent display
            timeRemaining = True
            while timeRemaining:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", check=lambda reaction, reactor: reactor == ctx.author and \
                        (str(reaction.emoji) == "⬅️" or str(reaction.emoji) == "➡️") and reaction.message == message, timeout = 300.0)
                except asyncio.TimeoutError:
                    timeRemaining = False
                    break

                # Move pages
                characters = ""
                if str(reaction.emoji) == "⬅️":
                    if page != 1:
                        page -= 1
                        for code in collection[page * 10 - 9:page * 10 + 1]:
                            characters += getSummon(code) + "\n"
                else:
                    if page * 10 < totalCharacters:
                        page += 1
                        if page * 10 > totalCharacters:
                            for code in collection[page * 10 - 9:]:
                                characters += getSummon(code) + "\n"
                        else:
                            for code in collection[page * 10 - 9:page * 10 +
                                                   1]:
                                characters += getSummon(code) + "\n"

                # Redisplay collection
                if characters != "":
                    newEmbed = discord.Embed(title="Summon Collection")
                    newEmbed.set_footer(
                        text=
                        f"Showing page {page} out of {math.ceil(totalCharacters/10)}"
                    )
                    newEmbed.add_field(name=f"{player}'s Summons",
                                       value=characters)
                    newEmbed.set_thumbnail(url=player.avatar_url)
                    await message.edit(embed=newEmbed)

    @commands.command(aliases=["v"])
    async def view(self, ctx):
        """ Displays the specified summon, or defaults to the last summon the user acquired """

        # Default viewing
        if ctx.message.content.strip() == ".v":
            summons = getFromFile1("cogs/collections.txt", str(ctx.author.id),
                                   ",")
            if summons == False:
                await ctx.send(f"{ctx.author} you have no cards to view!")
            else:
                character = getFromFile1("cogs/generatedCards.txt",
                                         summons[-1], ",")

        # Specified card viewing
        else:
            message = ctx.message.content.split()
            code = message[1]
            character = getFromFile1("cogs/generatedCards.txt", code, ",")

        # Display Card
        if character == False:
            await ctx.send("Invalid code!")
        else:
            charEmbed = discord.Embed(
                title=f"{character[1]} {getGenderSymbols(character[2])}",
                description=f"{character[3]}")
            charEmbed.add_field(
                name="\u200b",
                value=
                f"{character[0]} --- :crossed_swords:: {character[4]} --- :green_heart:: {character[5]}"
            )
            charEmbed.set_image(url=character[6])
            await ctx.send(embed=charEmbed)

    @commands.command(aliases=["s"])
    async def summon(self, ctx):
        """ Summons a anime character """
        def generateUniqueCode():
            """ Get a unique code """
            while True:
                # Pick possible code
                row, col = random.randrange(8788), random.randrange(52)

                # Get the code
                codeLine = getFromFile2("cogs/possibleCodes.txt", row, " ")
                code = codeLine[col]

                # Check if code is unique
                if getFromFile1("cogs/generatedCards.txt", code, " ") == False:
                    return code

        def getRandomCharacter():
            """ Picks a random character and assigns it random base stats """
            # Get character from characterList
            totalCharacters = 545

            img = False
            while not img:
                count = random.randrange(totalCharacters)
                character = getFromFile2("cogs/characterList.txt", count, ",")
                if len(character) == 4:
                    img = True

            # Assign it a unique code
            character.insert(0, generateUniqueCode())

            # Add random stats
            character.insert(1, random.randint(40, 100))  # Attack
            character.insert(2, random.randint(40, 100))  # Hp

            # Return final character
            return character

        uid = str(ctx.author.id)
        character = getRandomCharacter()

        # Display Summoned Character
        charEmbed = discord.Embed(
            title=f"{character[3]} {getGenderSymbols(character[4])}",
            description=f"{character[5]}")
        charEmbed.add_field(
            name="\u200b",
            value=
            f"{character[0]} --- :crossed_swords:: {character[1]} --- :green_heart:: {character[2]}"
        )
        charEmbed.set_image(url=character[6])
        await ctx.send(embed=charEmbed)

        # Save character to collection
        saveToCollection(uid, [character[0]])

        # Add character to generatedCards
        appendFile = open("cogs/generatedCards.txt", "a")
        appendFile.write(
            f"\n{character[0]}, {character[3]}, {character[4]}, {character[5]}, {character[1]}, {character[2]}, {character[6]}"
        )
        appendFile.close()


def setup(client):
    client.add_cog(AnimeRPG(client))