import discord, asyncio, math, random, psycopg2, os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

""" File handling functions """

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


"""  AnimeRPG functions """
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
    readFile = open("cogs/collections.txt", "r")
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
    writeFile = open("cogs/collections.txt", "w")
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


""" Adventure functions """
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
    newEmbed = discord.Embed(title=newTitle, description=desc, colour=newColour)
    await message.edit(embed=newEmbed)


def getReactionNumber(reactionList, reaction):
    """ Returns the number associated with the reaction """
    count = 1
    for r in reactionList:
        if reaction == r:
            return count
        count += 1


async def confirmIntention(ctx, client, header, desc, endMessage, reactions, desiredColour, footer):
    """ Confirms if the user wanted to use a certain command """
    # Display embed
    if desiredColour:
        myEmbed = discord.Embed(title=header, description=desc, colour=desiredColour)
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
        await changeEmbedColour(ctx, header, message, "Command timed out", discord.Colour.red())
        return False, message

    if str(reaction.emoji) == "❌":
        await changeEmbedColour(ctx, header, message, endMessage, discord.Colour.red())
        return False, message

    return str(reaction.emoji), message


""" Dungeon functions """

class Creature():
    """ Parent of player and monster """
    def  __init__(self, hp, name):
        self.name = name
        self.hp = int(hp)
        self.maxHp = self.hp

    def isDead(self):
        """ Check if creature is dead """
        if self.hp <= 0:
            self.hp = 0
            return True
        else:
            return False

    def getName(self):
        """ Returns the name of the creature """
        return self.name

    def getHP(self):
        """ Returns hp """
        return self.hp

    def changeHP(self, modifier):
        """ Changes hp value """
        self.hp += modifier

        if self.hp < 0:
            self.hp = 0
        elif self.hp > self.maxHp:
            self.hp = self.maxHp


class Player(Creature):
    """ The user's player """
    def  __init__(self, name):
        super().__init__(10, name)
        self.attack = 1
        self.weapons = []
        self.weaponCount = 0
        self.items = []
        self.money = 1000

    def getAttack(self):
        """ Returns the player's current attack value """
        return self.attack

    def changeAttack(self, modifier):
        """ Changes the player's current attack value """
        if -modifier > self.attack:
            self.attack = 0
        else:
            self.attack += modifier

    def addWeapon(self, weapon):
        """ Adds a weapon to the player's inventory """
        self.weapons.append(weapon)
        self.weaponCount += 1
    
    def removeWeapon(self, index):
        """ Removes the weapon from the player's inventory """
        del self.weapons[index]
        self.weaponCount -= 1

    def countWeapons(self):
        """ Returns the number of weapons the player has """
        return self.weaponCount

    def getWeaponIndex(self, index):
        """ Returns the weapon at the specified index """
        return self.weapons[index]

    def getWeapons(self):
        """ Gets a string representation of all the weapons in the player's inventory """
        if self.weapons:
            strRep = ""
            for w in self.weapons:
                strRep += f"{w}\n"

            return strRep
        else:
            return "\u200b"

    def formatWeapons(self):
        """ Returns a list of weapons the player can use for displaying """
        lst = [["Bare Hands", "1 :crossed_swords:"]]
        for w in self.weapons:
            lst.append([w.getName(), f"{w.getAttack()} :crossed_swords:"])
        return lst

    def addItem(self, item):
        """ Adds an item to the player's inventory """
        self.items.append(item)

    def removeItem(self, index):
        """ Removes the item from the player's inventory """
        del self.items[index]

    def getItems(self):
        """ Gets a string representation of all the items in the player's inventory """
        if self.items:
            strRep = ""
            count = 1
            for i in self.items:
                strRep += f"{count}. {i}\n"
                count += 1
            return strRep
        else:
            return "\u200b"

    def getItemList(self):
        """ Returns the list of items the player has """
        return self.items

    def changeMoney(self, amount):
        """ Changes the amount of money the player currently has """
        self.money += amount

    def getMoney(self):
        """ Returns the amount of money the player currently has """
        return self.money

    def __str__(self):
        return f"{self.hp} 💚 | {self.attack} ⚔️ | {self.money} 💰"


class Monster(Creature):
    """ A generic monster """
    def __init__(self, name, hp, minAttack, maxAttack):
        super().__init__(hp, name)
        self.minAttack = int(minAttack)
        self.maxAttack = int(maxAttack)

    def getAttack(self):
        """ Returns a random value between the minAttack and maxAttack inclusive """
        return random.randint(self.minAttack, self.maxAttack)

    def getAttackRange(self):
        """ Returns the possible attack range of this monster """
        return f"{self.minAttack} - {self.maxAttack}"

    def getDisplay(self):
        """ Returns a string representing the monster and it's current stats for displaying """
        return f"{self.getName()} | {self.getHP()} :green_heart: | {self.getAttackRange()} :crossed_swords:"


class Goods():
    """ A generic purchasable good """
    def  __init__(self, name, price):
        self.name = name
        self.price = price

    def getName(self):
        """ Returns the name of the good """
        return self.name

    def getPrice(self):
        """ Returns the price of the good """
        return self.price


class Weapon(Goods):
    """ A generic weapon """
    def  __init__(self, name, minAttack, maxAttack, durability, price):
        super().__init__(name, price)
        self.minAttack = int(minAttack)
        self.maxAttack = int(maxAttack)
        self.maxDurability = int(durability)
        self.durability = int(durability)
        self.condition = 4

    def getAttack(self):
        """ Returns the weapons attack in a string format """
        return f"{self.minAttack} - {self.maxAttack}"

    def randomAttack(self):
        """ Returns a random attack value between minAttack and maxAttack """
        return random.randint(self.minAttack, self.maxAttack)

    def changeDurability(self, modifier):
        """ Changes the durability value and condition of the weapon """
        self.durability += durability

        if self.durability == self.maxDurability:
            self.setCondition(4)
        elif self.durability >= math.ceil(self.maxDurability/2):
            self.setCondition(3)
        elif self.durability >= math.ceil(self.maxDurability/5):
            self.setCondition(2)
        elif self.durability <= 0:
            self.setCondition(0)
        else:
            self.setCondition(1)

    def getCondition(self):
        """ Returns the condition of the weapon """
        return self.condition

    def setCondition(self, condition):
        """ Changes the condition of the weapon """
        self.condition = condition

    def __str__(self):
        return f"{self.name} | {self.getAttack()} :crossed_swords:"


class Item(Goods):
    """ A generic item """
    def  __init__(self, name, desc, price):
        super().__init__(name, price)
        self.description = desc

    def __str__(self):
        return f"{self.name} | {self.description}"


async def displayDungeon(ctx, client, message, desc, footer, reactions, *args):
    """ Shows the current floor the player is on and gets the desired action """

    # Update Embed
    dungeonEmbed = discord.Embed(title="Dungeon crawler", description=desc, colour=discord.Colour.orange())
    if footer: dungeonEmbed.set_footer(text=footer)
    count = 1
    for item in args:
        dungeonEmbed.add_field(name=f"{count}. {item[0]}", value=item[1])
        count += 1
    await message.edit(embed=dungeonEmbed)
    if reactions: 
        await sendReactions(message, reactions)

        # Get response
        try:
            reaction, user = await client.wait_for("reaction_add", check=lambda reaction, reactor: reactor == ctx.author and \
                (str(reaction.emoji) in reactions) and reaction.message == message, timeout = 60.0)
        except asyncio.TimeoutError:
            await changeEmbedColour(ctx, "Dungeon crawler", message, "Command timed out", discord.Colour.red())
            await sendReactions(message, [])
            return False

        return str(reaction.emoji)
    return True


async def displayInventory(ctx, client, message, player, floor):
    """ Shows the player's current stats and inventory """

    # Update Embed
    itemList = player.getItemList()
    reactions = ["<:inventory:797167772366536714>" if num == 0 else f"{num}\N{COMBINING ENCLOSING KEYCAP}" for num in range(0, len(itemList)+1)]
    desc = f"{player.getName()} | {player.__str__()}"

    while True:
        dungeonEmbed = discord.Embed(title="Dungeon crawler", description=desc, colour=discord.Colour.orange())
        dungeonEmbed.set_footer(text=f"Floor {floor}")
        dungeonEmbed.add_field(name="Items", value=player.getItems())
        dungeonEmbed.add_field(name="Weapons", value=player.getWeapons())
        await message.edit(embed=dungeonEmbed)
        await sendReactions(message, reactions)

        # Get response
        try:
            reaction, user = await client.wait_for("reaction_add", check=lambda reaction, reactor: reactor == ctx.author and \
                str(reaction.emoji) in reactions and reaction.message == message, timeout = 60.0)
        except asyncio.TimeoutError:
            await changeEmbedColour(ctx, "Dungeon crawler", message, "Command timed out", discord.Colour.red())
            await sendReactions(message, [])
            return False

        for i in range(0, len(reactions)):
            if str(reaction) == reactions[i]:

                # Exit out of inventory
                if i == 0:
                    return True

                # Hard coded potions for now, maybe use currying in the future
                else:
                    item = itemList[i-1]
                    if "Small" in item.getName():
                        value = 2
                    elif "Medium" in item.getName():
                        value = 5
                    else:
                        value = 10

                    player.changeHP(value)
                    reactions = reactions[:-1]
                    player.removeItem(i-1)
                    desc = f"{player.getName()} | {player.__str__()}\n\nYou drank a {item.getName()}!"
                    

async def showHighScores(ctx, client, message):
    """ Shows the top scores achieved by the user """

    # Get data
    con = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
    cur = con.cursor()

    try:
        cur.execute('SELECT * FROM dungeon_scores WHERE id = %s LIMIT 10', (ctx.author.id, ))
        playerScores = cur.fetchall()

        cur.execute('''SELECT * 
                       FROM dungeon_scores 
                       ORDER BY floor DESC 
                       LIMIT 10''')
        globalScores = cur.fetchall()

    except Exception as e: 
        print ("Exception: ", e)
        sendErrorMessage(ctx)
    finally:
        con.commit()
        cur.close()
        con.close()

    # # Get highscores
    # serverMembers = [[member.name, str(member.id)] for member in ctx.guild.members]
    # playerScoreExists = False
    # serverScores = []
    # for line in data:
    #     if str(ctx.author.id) in line:
    #         playerScores = line.split(",")
    #         playerScoreExists = True
    #     for member in serverMembers:
    #         if member[1] in line:
    #             scores = list(map(lambda x: x.split("|"), line.split(",")))
    #             for score in scores[1:]:
    #                 if "\n" in score[1]:
    #                     serverScores.append([member[0], score[0], score[1][:-2]])
    #                 else:   
    #                     serverScores.append([member[0], score[0], score[1]])

    # if playerScoreExists:
    #     # User's most recent scores
    #     playerScores = list(map(lambda x: x.split("|"), playerScores))
    #     playerScores[-1][-1] = playerScores[-1][-1][:-2]
    #     recentScores = ""
    #     counter = 1
    #     for i in range(len(playerScores)-1, 0, -1):
    #         if counter <= 10:
    #             recentScores += f"{counter}. {ctx.author} | Floor {playerScores[i][0]} | {playerScores[i][1]}\n"
    #             counter += 1
    #         else: 
    #             break

    #     # User's top scores
    #     playerScores = sorted(playerScores[1:], key=lambda x: x[0], reverse=True)
    #     topScores = ""
    #     counter = 1
    #     for i in range(0, len(playerScores)):
    #         if counter <= 10:
    #             topScores += f"{counter}. {ctx.author} | Floor {playerScores[i][0]} | {playerScores[i][1]}\n"
    #             counter += 1
    #         else: 
    #             break

    #     # Guild's top scores
    #     if serverScores:
    #         serverScores = sorted(serverScores, key=lambda x: x[1], reverse=True)
    #         topServerScores = ""
    #         counter = 1
    #         for i in range(0, len(serverScores)):
    #             if counter <= 10:
    #                 topServerScores += f"{counter}. {serverScores[i][0]} | Floor {serverScores[i][1]} | {serverScores[i][2]}\n"
    #                 counter += 1
    #             else: 
    #                 break
    #     else:
    #         topServerScores = topScores

    # elif serverScores:
    #     topScores = f"{ctx.author} has never survived the dungeon"
    #     recentScores = f"{ctx.author} has never survived the dungeon"
    #     serverScores = sorted(serverScores, key=lambda x: x[1], reverse=True)
    #     counter = 1
    #     topServerScores = ""
    #     for i in range(0, len(serverScores)):
    #         if counter <= 10:
    #             topServerScores += f"{counter}. {serverScores[i][0]} | Floor {serverScores[i][1]} | {serverScores[i][2]}\n"
    #             counter += 1
    #         else: 
    #             break
    
    # # No recorded scores
    # else:
    #     topScores = f"{ctx.author} has never survived the dungeon"
    #     recentScores = f"{ctx.author} has never survived the dungeon"
    #     topServerScores = f"Nobody from {ctx.guild.name} has ever survived the dungeon"

    topScores = ""
    for i in range(len(playerScores)):
        topScores += f"{i + 1}. {playerScores[i][1]} | Floor {playerScores[i][2]} | {playerScores[i][3]}\n"

    globalTopScores = ""
    for i in range(len(globalScores)):
        globalTopScores += f"{i + 1}. {globalScores[i][1]} | Floor {globalScores[i][2]} | {globalScores[i][3]}\n"

    scoreEmbed = discord.Embed(title=f"{ctx.author}'s high scores", description=topScores, colour=discord.Colour.orange())
    showTopScores = True
    while True:
        # Show high scores
        await message.edit(embed=scoreEmbed)
        reactions = ["👑", "🔁"] 
        await sendReactions(message, reactions)

        # Get response
        try:
            reaction, user = await client.wait_for("reaction_add", check=lambda reaction, reactor: reactor == ctx.author and \
                (str(reaction.emoji) in reactions) and reaction.message == message, timeout = 60.0)
        except asyncio.TimeoutError:
            await changeEmbedColour(ctx, "High Scores", message, "Command timed out", discord.Colour.red())
            await sendReactions(message, [])
            return 

        if str(reaction.emoji) == "👑":
            return
        else:
            if showTopScores:
                scoreEmbed = discord.Embed(title=f"{ctx.author}'s high scores", description=globalTopScores, colour=discord.Colour.orange())
            else:
                scoreEmbed = discord.Embed(title=f"Global high scores", description=topScores, colour=discord.Colour.orange())
            showTopScores = not showTopScores


async def displayHelp(ctx, client, message):
    """ Shows the help message on how to play the game """


def generateMerchantGoods():
    """ Picks a random selection of 3 weapons or items for the merchant to sell """

    # Get data
    weapons = getFromFile3("cogs/weaponList.txt", "|")
    items = getFromFile3("cogs/itemList.txt", "|")
    choices = weapons + items

    return [random.choice(choices) for i in range(3)]
    

def formatGoods(goods):
    """ Format the merchants goods for displaying """

    names = [f"{x[0]} | {x[-1]} :moneybag:" for x in goods]
    desc = [f"{x[1]} - {x[2]} :crossed_swords:" if len(x) == 5 else x[1] for x in goods]
    return zip(names, desc)


def saveScore(uid, name, floor):
    """ Saves the highest floor the player achieved that run """

    con = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
    cur = con.cursor()

    try:
        cur.execute("SET TIMEZONE='US/Eastern';")
        cur.execute('INSERT INTO dungeon_scores VALUES (%s, %s, %s, NOW());', (uid, name, floor))
    except Exception as e: 
        print ("Exception: ", e)
    finally:
        con.commit()
        cur.close()
        con.close()


def spawnMonster():
    """ Spawns a random monster from monsterList """

    numOfMonsters = 4
    monster = getFromFile2("cogs/monsterList.txt", random.randrange(0, numOfMonsters), "|")
    return Monster(*monster)


def getSuffix(floor):
    """ Returns the appropriate suffix for the floor """
    if floor == 1:
        return "st"
    elif floor == 2:
        return "nd"
    elif floor == 2:
        return "rd"
    else:
        return "th"


async def leaveDungeon(ctx, message, floor):
    """ Tells the user that they left the dungeon """

    await changeEmbedColour(ctx, "Dungeon crawler", message, f"{ctx.author}, you managed to make it all the way to the {floor}{getSuffix(floor)} floor without dying!", discord.Colour.green())
    await sendReactions(message, [])



async def sendErrorMessage(ctx):
    """ Send an error message """
    await ctx.send("An error occured, if this problem persists, contact Snypintyme#9303")

