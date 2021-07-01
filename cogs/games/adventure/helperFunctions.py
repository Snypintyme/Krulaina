import discord, asyncio, math, random


def getAdventure(filePath):
    """ Loads the given adventure """
    readFile = open(filePath, "r")
    story = readFile.readlines()
    readFile.close()

    for i in range(1, len(story)):
        story[i] = story[i].split("//")
        for j in range(len(story[i])):
            story[i][j] = story[i][j].split("->")
            for k in range(len(story[i][j])):
                story[i][j][k] = story[i][j][k].strip()

    return story


async def sendReactions(message, newReactions):
    """ Clears all old reactions and adds the given reactions """
    # Clear old reactions
    await message.clear_reactions()

    # Add new reactions
    for r in newReactions:
        await message.add_reaction(r)


async def changeEmbedColour(ctx, newTitle, message, desc, newColour):
    """ Edits the embed message with the new colour """
    newEmbed = discord.Embed(title=newTitle,
                             description=desc,
                             colour=newColour)
    await message.edit(embed=newEmbed)


def getReactionNumber(reactionList, reaction):
    """ Returns the number associated with the reaction """
    count = 1
    for r in reactionList:
        if reaction == r:
            return count
        count += 1


async def confirmIntention(ctx, client, header, desc, endMessage, reactions,
                           desiredColour, footer):
    """ Confirms if the user wanted to use a certain command """
    # Display embed
    if desiredColour:
        myEmbed = discord.Embed(title=header,
                                description=desc,
                                colour=desiredColour)
    else:
        myEmbed = discord.Embed(title=header, description=desc)
    if footer:
        myEmbed.set_footer(text=footer)
    message = await ctx.send(embed=myEmbed)
    await sendReactions(message, reactions)

    # Get response
    try:
        reaction, user = await client.wait_for("reaction_add", check=lambda reaction, reactor: reactor == ctx.author and \
            str(reaction.emoji) in reactions and reaction.message == message, timeout = 60.0)
    except asyncio.TimeoutError:
        await changeEmbedColour(ctx, header, message, "Command timed out",
                                discord.Colour.red())
        return False, message

    if str(reaction.emoji) == "❌":
        await changeEmbedColour(ctx, header, message, endMessage,
                                discord.Colour.red())
        return False, message

    return str(reaction.emoji), message
