# import stuff
import discord, os, random, asyncio
from discord.ext import commands

class Admin(commands.Cog):
    def  __init__(self, client):
        self.client = client
        
    # Commands
    @commands.command()
    async def purge(self, ctx):
        """ Deletes the specified amount of previous messages, or last massage if nothing is specified """
        if ctx.author.guild_permissions.administrator:
            number = 0
            if len(ctx.message.content) == 6:
                number = 1
            else:
                try:
                    number = int(ctx.message.content[6:].strip())
                except:
                    await ctx.send('Invalid syntax, must be ".purge <number>"')

            if number:
                await ctx.channel.purge(limit=number+1)
                message = await ctx.send(f"{number} messages purged")
                await asyncio.sleep(2)
                await message.delete()


    @commands.command()
    async def kick(self, ctx, user : discord.Member, *, reason=None):
        """ Kicks the specified member for the specified reason """
        if ctx.author.guild_permissions.administrator:
            name = user.name
            await user.kick(reason=reason)
            await ctx.send(f"Successfully kicked {name}")
        else:
            await ctx.send(f"{ctx.author} you dont have permission to kick someone!")

    
    @commands.command()
    async def ban(self, ctx, user : discord.Member, *, reason=None):
        """ Bans the specified member for the specified reason """
        if ctx.author.guild_permissions.administrator:
            name = user.name
            await user.ban(reason=reason)
            await ctx.send(f"Successfully banned {name}")
        else:
            await ctx.send(f"{ctx.author} you dont have permission to ban someone!")


    @commands.command()
    async def unban(self, ctx, uid : int):
        """ Unbans the specified member """
        if ctx.author.guild_permissions.administrator:
            user = await self.client.fetch_user(uid)
            await ctx.guild.unban(user)
            await ctx.send(f"Successfully unbanned {uid}")
        else:
            await ctx.send(f"{ctx.author} you dont have permission to unban someone!")


    @commands.command()
    async def generateCodes(self, ctx):
        if ctx.author.id == 198224062512758784:
            characters = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z")
            f = open("cogs/possibleCodes.txt", "w")

            line = ""
            count = 0
            for letter1 in range(26):
                for letter2 in range(26):
                    for letter3 in range(26):
                        for letter4 in range(26):

                            code = characters[letter1] + characters[letter2] + characters[letter3] + characters[letter4] + " "

                            if count == 52:
                                line += "\n"
                                f.write(line)
                                count = 1
                                line = code
                            else:
                                line += code
                                count += 1

            f.write(line)

            f.close()
            print("Successfully generated!")
        else: 
            ctx.send("You don't have permission to do that!")


    @commands.command()
    async def sortCharacters(self, ctx):
        """ Sorts the character list in alphabetical order using series name then character name """

        def combine(lst):
            line = ""
            for item in lst:
                line += item + ", "

            line = line[:-2] + "\n"
            return line  

        if ctx.author.id == 198224062512758784:
            readFile = open("cogs/characterList.txt", "r")
            data = readFile.readlines()
            readFile.close()
            
            for i in range(len(data)):
                data[i] = list(map(str.strip, data[i].split(",")))

            # Remove urls
            '''for i in range(len(data)):
                if len(data[i]) == 4:
                    data[i] = data[i][:3]'''

            for i in range(len(data)):
                data[i].insert(0, data[i][2] + data[i][0])
            data.sort(key=lambda x: x[0])
            data = list(map(lambda x: x[1:], data))
            data = list(map(lambda x: combine(x), data))

            writeFile = open("cogs/characterList.txt", "w")
            writeFile.writelines(data)
            writeFile.close()

            await ctx.send("Successfully sorted!")
        else: 
            ctx.send("You don't have permission to do that!")


    @commands.command()
    async def resetGame(self, ctx):
        """ Resets all summons and inventory """
        if ctx.author.id == 198224062512758784:
            try:
                await ctx.send("Are you sure you want to reset the game? (yes, no)")
                msg = await self.client.wait_for('message', check=lambda msg: msg.author==ctx.author and (msg.content.lower()=="y" or \
                    msg.content.lower()=="yes" or msg.content.lower()=="n" or msg.content.lower()=="no"), timeout = 60.0)
            except asyncio.TimeoutError:
                await ctx.send("Timed out, game not reset")

            if msg.content.lower() == "y" or  msg.content.lower() == "yes":
                os.remove("cogs/collections.txt")
                os.remove("cogs/generatedCards.txt")
                os.remove("cogs/inventory.txt")
                f = open("cogs/collections.txt", "w")
                f.close()
                f = open("cogs/generatedCards.txt", "w")
                f.close()
                f = open("cogs/inventory.txt", "w")
                f.close()
                await ctx.send("Successfully reset")
            else:
                await ctx.send("Game has not been reset")
        else:
            ctx.send("You don't have permission to do that!")


    @commands.command()
    async def resetRecords(self, ctx):
        """ Resets all dungeon high scores """
        if ctx.author.id == 198224062512758784:
            try:
                await ctx.send("Are you sure you want to reset records? (yes, no)")
                msg = await self.client.wait_for('message', check=lambda msg: msg.author==ctx.author and (msg.content.lower()=="y" or \
                    msg.content.lower()=="yes" or msg.content.lower()=="n" or msg.content.lower()=="no"), timeout = 60.0)
            except asyncio.TimeoutError:
                await ctx.send("Timed out, game not reset")

            if msg.content.lower() == "y" or  msg.content.lower() == "yes":
                os.remove("cogs/dungeonScores.txt")
                f = open("cogs/dungeonScores.txt", "w")
                f.close()
                await ctx.send("Successfully reset")
            else:
                await ctx.send("Game has not been reset")
        else:
            ctx.send("You don't have permission to do that!")

        
def setup(client):
    client.add_cog(Admin(client))
