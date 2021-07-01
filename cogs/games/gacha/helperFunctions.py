import discord, asyncio


def getFromFile1(fileName, flag, whitespace):
    """ Reads fileName and returns a list of the specified 
    line, denoted by flag, split by the specified whitespace. 
    Returns False if it dosen't exist in the file """

    readFile = open(fileName, "r")
    for line in readFile:
        if flag in line:
            readFile.close()
            return list(map(str.strip, line.split(whitespace)))

    return False


def getFromFile2(fileName, count, whitespace):
    """ Reads fileName and returns a list of at 
    line count, split by the specified whitespace. """

    readFile = open(fileName, "r")
    for line in readFile:
        if count == 0:
            readFile.close()
            return list(map(str.strip, line.split(whitespace)))
        else:
            count -= 1


def getFromFile3(path, whitespace):
    """ Returns the entire specified file in a list, 
    split by the specified whitespace """

    readFile = open(path, "r")
    data = readFile.readlines()
    readFile.close()
    return list(map(lambda x: list(map(str.strip, x.split(whitespace))), data))


def getGenderSymbols(gender):
    """ Gets the appropriate gender symbol for displaying in discord """

    if gender == "M":
        return ":male_sign:"
    elif gender == "F":
        return ":female_sign:"
    else:
        return ":male_sign::female_sign:"


def saveToCollection(uid, codes):
    """ Adds the code/s of a summon/s to a player's collection """
    # Get data
    readFile = open("collections.txt", "r")
    data = readFile.readlines()
    readFile.close()

    # String form of codes
    adding = ""
    for code in codes:
        adding += f", {code}"

    # Add code to existing player
    exists = False
    for i in range(len(data)):
        if uid in data[i]:
            if "\n" in data[i]:
                data[i] = data[i][:-1] + adding + "\n"
            else:
                data[i] = data[i] + adding
            exists = True
            break

    # Add code to new player
    if not exists:
        data.append(f"\n{uid}{adding}")

    # Write back to file
    writeFile = open("collections.txt", "w")
    writeFile.writelines(data)
    writeFile.close()


async def getDesiredUser(ctx, bot):
    initialMessage = ctx.message.content.split()
    mentions = ctx.message.mentions
    if len(initialMessage) == 1:
        user = ctx.author
    elif len(mentions) != 0:
        user = mentions[0]
    else:
        try:
            user = await bot.fetch_user(int(initialMessage[1]))
        except:
            await ctx.send(f"{ctx.author.mention} that user was not found!")
            user = False

    return user
