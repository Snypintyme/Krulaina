import discord, asyncio, cogs.helperFunctions, random
from discord.ext import commands

class ChooseYourOwnAdventure(commands.Cog):
    def  __init__(self, client):
        self.client = client


    @commands.command(aliases=["d"]) 
    async def dungeon(self, ctx):
        """ Dungeon adventure """

        # Confirm intention
        answer, message = await cogs.helperFunctions.confirmIntention(ctx, self.client, "Dungeon crawler", "Do you wish to go into the dungeon?", \
                "You did not go into the dungeon", ["❌", "✅", "<:highscore:797647096119164928>"], discord.Colour.orange(), False)
        if answer == False:
            return
        elif answer == "<:highscore:797647096119164928>":
            await cogs.helperFunctions.showHighScores(ctx, self.client, message)
            while True:
                action = await cogs.helperFunctions.displayDungeon(ctx, self.client, message, "Do you wish to go into the dungeon?", False, ["❌", "✅", "<:highscore:797647096119164928>"])
                if action == False:
                    return
                elif action == "<:highscore:797647096119164928>":
                    await cogs.helperFunctions.showHighScores(ctx, self.client, message)
                else:
                    break

        # Main loop
        player = cogs.helperFunctions.Player(ctx.author)
        floor = 1
        dead = False
        dead, exitDungeon = False, False
        emojis = ["<:inventory:797167772366536714>", "<:exit:797173266002870352>", "<:nextFloor:797180937125101568>"] # Custom emojis for inventory, exit, and nextFloor
        while True:
            event = random.choice(["Nothing", "Battle", "Merchant"])

            # Empty Floor
            if event == "Nothing":
                while True:
                    action = await cogs.helperFunctions.displayDungeon(ctx, self.client, message, "You find not a single soul here other than yourself, must be a free pass to the next floor.", \
                        f"{floor}{cogs.helperFunctions.getSuffix(floor)} Floor | {player.__str__()}", [emojis[1], emojis[0], emojis[2]])
                    if action == False:
                        return
                    elif action == emojis[0]:
                        action = await cogs.helperFunctions.displayInventory(ctx, self.client, message, player, floor)
                        if action == False:
                            return
                    elif action == emojis[1]:
                        await cogs.helperFunctions.leaveDungeon(ctx, message, floor)
                        exitDungeon = True
                        break
                    else:
                        break
                
            # Merchant Floor
            elif event == "Merchant":
                reactions = [emojis[1] if num == -2 else emojis[0] if num == -1 else emojis[2] if num == 0 else f"{num}\N{COMBINING ENCLOSING KEYCAP}" for num in range(-2, 4)]
                goods = cogs.helperFunctions.generateMerchantGoods()
                formattedGoods = list(cogs.helperFunctions.formatGoods(goods))
                desc = "You find a merchant's shop on this floor with a variety of stuff for sale."
                while True:
                    action = await cogs.helperFunctions.displayDungeon(ctx, self.client, message, desc, \
                        f"{floor}{cogs.helperFunctions.getSuffix(floor)} Floor | {player.__str__()}", reactions, *formattedGoods)
                    if action == False:
                        return
                    elif action == emojis[0]:
                        action = await cogs.helperFunctions.displayInventory(ctx, self.client, message, player, floor)
                        if action == False:
                            return
                    elif action == emojis[2]:
                        break
                    elif action == emojis[1]:
                        await cogs.helperFunctions.leaveDungeon(ctx, message, floor)
                        exitDungeon = True
                        break
                    else:
                        for num in range(len(reactions)-3):
                            if action == f"{num+1}\N{COMBINING ENCLOSING KEYCAP}":
                                if player.getMoney() >= int(goods[num][-1]):
                                    desc = f"You find a merchant's shop on this floor with a variety of stuff for sale.\n\nYou purchased a {goods[num][0]}!"
                                    if len(goods[num]) == 5:
                                        player.addWeapon(cogs.helperFunctions.Weapon(*goods[num]))
                                    else:
                                        player.addItem(cogs.helperFunctions.Item(*goods[num]))
                                    player.changeMoney(-int(goods[num][-1]))
                                    del goods[num]
                                    formattedGoods = list(cogs.helperFunctions.formatGoods(goods))
                                    del reactions[-1]
                                else:
                                    desc = f"You find a merchant's shop on this floor with a variety of stuff for sale.\nYou don't have enough money to buy that!"
            
            # Battle
            else:
                monster = cogs.helperFunctions.spawnMonster()
                reactions = [emojis[0] if num == 0 else f"{num}\N{COMBINING ENCLOSING KEYCAP}" for num in range(0, player.countWeapons()+2)]
                desc = f"You have encountered a {monster.getDisplay()} , you prepare to attack..."
                monsterTurn = False
                while True:
                    if emojis[1] in reactions:
                        action = await cogs.helperFunctions.displayDungeon(ctx, self.client, message, desc, \
                            f"{floor}{cogs.helperFunctions.getSuffix(floor)} Floor | {player.__str__()}", reactions)
                    elif monsterTurn:
                        action = await cogs.helperFunctions.displayDungeon(ctx, self.client, message, desc, \
                            f"{floor}{cogs.helperFunctions.getSuffix(floor)} Floor | {player.__str__()}", [])
                        await asyncio.sleep(2.0)
                        damage = monster.getAttack()
                        player.changeHP(-damage)
                        desc += f"\n\nThe monster hits back and deals {damage} damage to you"
                        if player.isDead():
                            desc += f"\nUnfortunately you succumb to your injuries and have died on Floor {floor}" 
                            await cogs.helperFunctions.changeEmbedColour(ctx, "Dungeon crawler", message, desc, discord.Colour.red())
                            await cogs.helperFunctions.sendReactions(message, [])
                            return
                        else:
                            action = await cogs.helperFunctions.displayDungeon(ctx, self.client, message, desc, \
                                f"{floor}{cogs.helperFunctions.getSuffix(floor)} Floor | {player.__str__()}", ["➡️"])
                    else:
                        action = await cogs.helperFunctions.displayDungeon(ctx, self.client, message, desc, \
                            f"{floor}{cogs.helperFunctions.getSuffix(floor)} Floor | {player.__str__()}", reactions, *player.formatWeapons())
                    if action == False:
                        return
                    elif action == emojis[0]:
                        action = await cogs.helperFunctions.displayInventory(ctx, self.client, message, player, floor)
                        if action == False:
                            return
                    elif action == emojis[1]:
                        await cogs.helperFunctions.leaveDungeon(ctx, message, floor)
                        exitDungeon = True
                        break
                    elif action == emojis[2]:
                        break
                    elif action == "➡️":
                        desc = f"You prepare to attack the {monster.getDisplay()} again..."
                        monsterTurn = False #REmove react8ions when weapon breaks
                    else:
                        for i in range(0, len(reactions)):
                            if action == reactions[i]:

                                # Hit with bare hands
                                if i == 1:
                                    weapon = "bare hands"
                                    damage = 1
                                    monster.changeHP(-damage)
                                    desc = f"You hit the {monster.getDisplay()} with your bare hands and deal 1 damage"

                                # Hit with weapon
                                else:
                                    weapon = player.getWeaponIndex(i-2)
                                    damage = weapon.randomAttack()
                                    monster.changeHP(-damage)
                                    desc = f"You hit the {monster.getDisplay()} with your {weapon.getName()} and deal {damage} damage"

                                # Check dead monster
                                if monster.isDead():
                                    desc += f"\n\nYou have slain the {monster.getName()}!"
                                    reactions = [emojis[1], emojis[0], emojis[2]]
                                monsterTurn = True

            # Check exit
            if exitDungeon:
                cogs.helperFunctions.saveScore(str(ctx.author.id), floor)
                break
            elif dead:
                break
            else:
                floor += 1


    @commands.command(aliases=["a"]) 
    async def adventure(self, ctx):
        """ Choose your own adventure """

        # Load story
        story = cogs.helperFunctions.getAdventure("cogs/adventure1.txt")

        # Confirm intention
        answer, message = await cogs.helperFunctions.confirmIntention(ctx, self.client, f"{ctx.author}'s adventure", f"{story[0]}\nDo you wish to go on this adventure?", \
            "You did not go on this adventure", ["❌", "✅"], False, False)
        if answer == False:
            return

        # Main storyline
        line = 2
        allChoices = ["{}\N{COMBINING ENCLOSING KEYCAP}".format(num) for num in range(1, 10)]
        while True:
            # Check for end of story
            if story[line-1][1][0] == "C":
                await cogs.helperFunctions.changeEmbedColour(ctx, f"{ctx.author}'s adventure", message, story[line-1][0][0].strip(), discord.Colour.green())
                break
            elif story[line-1][1][0] == "D":
                await cogs.helperFunctions.changeEmbedColour(ctx, f"{ctx.author}'s adventure", message, story[line-1][0][0].strip(), discord.Colour.red())
                break

            # Show next sections
            for i in range(len(story[line-1][0])-1):
                storyEmbed = discord.Embed(title=f"{ctx.author}'s adventure", description=story[line-1][0][i])
                await message.edit(embed=storyEmbed)
                await cogs.helperFunctions.sendReactions(message, ["➡️"])

                try:
                    reaction, user = await self.client.wait_for("reaction_add", check=lambda reaction, reactor: reactor == ctx.author and \
                        str(reaction.emoji) == "➡️" and reaction.message == message, timeout = 60.0)
                except asyncio.TimeoutError:
                    await cogs.helperFunctions.changeEmbedColour(ctx, f"{ctx.author}'s adventure", message, "Command timed out", discord.Colour.red())
                    break

            storyEmbed = discord.Embed(title=f"{ctx.author}'s adventure", description=story[line-1][0][len(story[line-1][0])-1])
            for i in range(2, len(story[line-1])):
                storyEmbed.add_field(name=f"{i-1}. {story[line-1][i][0]}", value="\u200b")
            await message.edit(embed=storyEmbed)

            # Reload reactions
            choices = allChoices[:len(story[line-1])-2]
            await cogs.helperFunctions.sendReactions(message, choices)

            # Get response
            try:
                reaction, user = await self.client.wait_for("reaction_add", check=lambda reaction, reactor: reactor == ctx.author and \
                    str(reaction.emoji) in choices and reaction.message == message, timeout = 60.0)
            except asyncio.TimeoutError:
                await cogs.helperFunctions.changeEmbedColour(ctx, f"{ctx.author}'s adventure", message, "Command timed out", discord.Colour.red())
                break

            # Next line in story
            index = cogs.helperFunctions.getReactionNumber(choices, str(reaction.emoji)) + 1
            line = int(story[line-1][index][1])

        await cogs.helperFunctions.sendReactions(message, [])



def setup(client):
    client.add_cog(ChooseYourOwnAdventure(client))
