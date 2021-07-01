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

    @commands.command(aliases=["ttt"])
    async def ticTacToe(self, ctx):
        """ Plays tic tac toe with the bot """
        def checkWinner(board):
            """ Check for a winner """

            # Check rows for winner
            for row in range(3):
                if board[row][0] == board[row][1] == board[row][2]:
                    return board[row][0]

            # Check columns for winner
            for col in range(3):
                if board[0][col] == board[1][col] == board[2][col]:
                    return board[0][col]

            # Check diagonal (top-left to bottom-right) for winner
            if board[0][0] == board[1][1] == board[2][2]:
                return board[0][0]

            # Check diagonal (bottom-left to top-right) for winner
            if board[2][0] == board[1][1] == board[0][2]:
                return board[2][0]

            # No winner
            return ""

        def getBoard(board):
            """ Returns a string representing the current ttt board """

            return f"{board[0][0]}   |   {board[0][1]}   |   {board[0][2]}\
            \n----+----+----\
            \n{board[1][0]}   |   {board[1][1]}   |   {board[1][2]}\
            \n----+----+----\
            \n{board[2][0]}   |   {board[2][1]}   |   {board[2][2]}"

        def minimax(board, computerTurn):
            """ Minimax for hard mode """
            # Check winner
            if checkWinner(board) == ":o:":
                return 1
            elif checkWinner(board) == ":x:":
                return -1

            # Loop through all possible moves
            scores = []
            moveTaken = False
            for row in range(3):
                for col in range(3):
                    if board[row][col] != ":o:" and board[row][col] != ":x:":
                        prevSym = board[row][col]
                        if computerTurn:
                            board[row][col] = ":o:"
                        else:
                            board[row][col] = ":x:"
                        moveTaken = True
                        scores.append(minimax(board, not computerTurn))
                        board[row][col] = prevSym

            if moveTaken:
                if computerTurn:
                    return max(scores)
                else:
                    return min(scores)
            else:
                return 0

        # Variables
        freeCells = 9
        usersTurn = True
        tttBoard = [[":one:", ":two:", ":three:"],
                    [":four:", ":five:", ":six:"],
                    [":seven:", ":eight:", ":nine:"]]
        validPositions = ("1", "2", "3", "4", "5", "6", "7", "8", "9")
        winner = ""

        # Select difficulty
        tttEmbed = discord.Embed(title="Tic Tac Toe",
                                 description="Select a difficulty")
        message = await ctx.send(embed=tttEmbed)
        await message.add_reaction("🙂")
        await message.add_reaction("💀")

        # Get response
        try:
            reaction, user = await self.client.wait_for("reaction_add", check=lambda reaction, reactor: reactor == ctx.author and \
                (str(reaction.emoji) == "🙂" or str(reaction.emoji) == "💀") and reaction.message == message, timeout = 60.0)
        except asyncio.TimeoutError:
            await ctx.send(
                f"Holy {ctx.author.mention} you took too long to respond, not playing with you :rage:"
            )

        if str(reaction) == "🙂":
            hardMode = False
        else:
            hardMode = True

        # Game loop
        while not winner and freeCells > 0:
            # Show Board
            tttEmbed = discord.Embed(title="Tic Tac Toe",
                                     description=getBoard(tttBoard))
            await ctx.send(embed=tttEmbed)

            # User move
            if usersTurn:
                validMove = False
                while not validMove:
                    try:
                        await ctx.send(
                            "Which square do you want to move to (1-9)?")
                        msg = await self.client.wait_for(
                            'message',
                            check=lambda msg: msg.author == ctx.author and msg.
                            content in validPositions,
                            timeout=60.0)
                    except asyncio.TimeoutError:
                        return

                    move = int(msg.content)
                    row = math.floor((move - 1) / 3)
                    col = (move + 2) % 3

                    if tttBoard[row][col] == ":x:" or tttBoard[row][
                            col] == ":o:":
                        continue
                    else:
                        tttBoard[row][col] = ":x:"
                        validMove = True
                        usersTurn = not usersTurn

            # Computer move
            else:
                if hardMode:
                    score = -math.inf
                    for row in range(3):
                        for col in range(3):
                            if tttBoard[row][col] != ":o:" and tttBoard[row][
                                    col] != ":x:":
                                prevSym = tttBoard[row][col]
                                tttBoard[row][col] = ":o:"
                                newScore = minimax(tttBoard, False)
                                if newScore > score:
                                    score = newScore
                                    bestRow = row
                                    bestCol = col
                                tttBoard[row][col] = prevSym

                    tttBoard[bestRow][bestCol] = ":o:"
                    usersTurn = not usersTurn
                else:
                    validMove = False
                    while not validMove:
                        row = random.randrange(0, 3)
                        col = random.randrange(0, 3)

                        if tttBoard[row][col] == ":x:" or tttBoard[row][
                                col] == ":o:":
                            continue
                        else:
                            tttBoard[row][col] = ":o:"
                            validMove = True
                            usersTurn = not usersTurn

            freeCells -= 1
            winner = checkWinner(tttBoard)

        # Show Board
        tttEmbed = discord.Embed(title="Tic Tac Toe",
                                 description=getBoard(tttBoard))
        await ctx.send(embed=tttEmbed)

        # Game end message
        if winner == ":x:":
            await ctx.send(f"{ctx.author.mention} you won!")
        elif winner == ":o:":
            await ctx.send(f"{ctx.author.mention} you lost!")
        else:
            await ctx.send(f"{ctx.author.mention} you tied!")

    @commands.command(aliases=["c4", "cf"])
    async def connectFour(self, ctx):
        """ Connect Four """
        def checkWinner(board):
            """ Checks for a winner """

            background = ":blue_square:"

            # Check horizontal win
            for row in range(6):
                for col in range(4):
                    if board[row][col] == board[row][col+1] == board[row][col+2] == board[row][col+3] \
                        and board[row][col] != background:
                        return board[row][col]

            # Check vertical win
            for row in range(3):
                for col in range(7):
                    if board[row][col] == board[row+1][col] == board[row+2][col] == board[row+3][col] \
                        and board[row][col] != background:
                        return board[row][col]

            # check \ diagonal win
            for row in range(3):
                for col in range(4):
                    if board[row][col] == board[row+1][col+1] == board[row+2][col+2] == board[row+3][col+3] \
                        and board[row][col] != background:
                        return board[row][col]

            # check / diagonal win
            for row in range(3):
                for col in range(3, 7):
                    if board[row][col] == board[row+1][col-1] == board[row+2][col-2] == board[row+3][col-3] \
                        and board[row][col] != background:
                        return board[row][col]

            # No winner
            return ""

        def getBoard(c4Board):
            """ Returns a string representing the current c4 board """

            board = ""
            for row in range(6):
                line = ""
                for col in range(7):
                    if col != 6:
                        line += " | " + c4Board[row][col]
                    else:
                        line += " | " + c4Board[row][col] + " | "
                board += (line + "\n")
                if row == 5:\
                    board += "========================"

            return board

        def getCol(reaction, choices):
            """ Returns the desired column based on the reaction """
            for num in range(7):
                if str(reaction.emoji) == choices[num]:
                    return num

        # Find a mention that indicates the other player, otherwise play the bot
        player1 = ctx.author
        mentions = ctx.message.mentions
        if len(mentions) != 0:
            if mentions[0] == player1:
                await ctx.send("You can't play with yourself!")
            else:
                player2 = mentions[
                    0]  # Small chance it won't take the first mention, discord limitation
        else:
            player2 = "Krulaina"

        # Make board
        c4Board = []
        for row in range(6):
            makeRow = []
            for col in range(7):
                makeRow.append(":blue_square:")
            c4Board.append(makeRow)

        # Unicode emojis (1-7)
        choices = [
            "{}\N{COMBINING ENCLOSING KEYCAP}".format(num)
            for num in range(1, 8)
        ]

        # Show board
        c4Embed = discord.Embed(title="Connect 4",
                                description=getBoard(c4Board),
                                colour=discord.Colour.red())
        c4Embed.set_footer(text="Click on a reaction to place a piece")
        message = await ctx.send(embed=c4Embed)

        # Add reactions
        for reaction in choices:
            await message.add_reaction(reaction)

        # Variables
        freeCells = 42
        player1Turn = True
        winner = ""

        # Game loop
        while not winner and freeCells > 0:

            # Player 1 move
            if player1Turn:

                # Change embed colour to indicate turn
                newEmbed = discord.Embed(title="Connect 4",
                                         description=getBoard(c4Board),
                                         colour=discord.Colour.red())
                newEmbed.set_footer(
                    text="Click on a reaction to place a piece")
                await message.edit(embed=newEmbed)

                validMove = False
                while not validMove:
                    # Get response
                    try:
                        reaction, user = await self.client.wait_for("reaction_add", check=lambda reaction, reactor: reactor == player1 and \
                            str(reaction.emoji) in choices and reaction.message == message, timeout = 60.0)
                    except asyncio.TimeoutError:
                        await ctx.send(
                            f"{player1} you took too long to respond, quitting game."
                        )
                        newEmbed = discord.Embed(title="Connect 4",
                                                 description=getBoard(c4Board))
                        newEmbed.set_footer(text="Game timed out")
                        await message.edit(embed=newEmbed)
                        return

                    col = getCol(reaction, choices)
                    # Check for full column
                    if c4Board[0][col] != ":blue_square:":
                        continue

                    # Dropping animation
                    row = 0
                    dropping = True
                    while dropping:
                        c4Board[row][col] = ":red_circle:"
                        if row != 0:
                            c4Board[row - 1][col] = ":blue_square:"
                        newEmbed = discord.Embed(title="Connect 4",
                                                 description=getBoard(c4Board),
                                                 colour=discord.Colour.red())
                        newEmbed.set_footer(
                            text="Click on a reaction to place a piece")
                        await message.edit(embed=newEmbed)
                        await asyncio.sleep(0.5)
                        if row == 5:
                            dropping = False
                        elif c4Board[row + 1][col] != ":blue_square:":
                            dropping = False
                        else:
                            row += 1

                    validMove = True
                    player1Turn = not player1Turn

            else:

                # Change embed colour to indicate turn
                newEmbed = discord.Embed(title="Connect 4",
                                         description=getBoard(c4Board),
                                         colour=discord.Colour.gold())
                newEmbed.set_footer(
                    text="Click on a reaction to place a piece")
                await message.edit(embed=newEmbed)

                # Player 2 move
                if player2 != "Krulaina":
                    validMove = False
                    while not validMove:
                        # Get response
                        try:
                            reaction, user = await self.client.wait_for("reaction_add", check=lambda reaction, reactor: reactor == player2 and \
                                str(reaction.emoji) in choices and reaction.message == message, timeout = 60.0)
                        except asyncio.TimeoutError:
                            await ctx.send(
                                f"{player2} you took too long to respond, quitting game."
                            )
                            newEmbed = discord.Embed(
                                title="Connect 4",
                                description=getBoard(c4Board))
                            newEmbed.set_footer(text="Game timed out")
                            await message.edit(embed=newEmbed)
                            return

                        col = getCol(reaction, choices)
                        # Check for full column
                        if c4Board[0][col] != ":blue_square:":
                            continue

                        # Dropping animation
                        row = 0
                        dropping = True
                        while dropping:
                            c4Board[row][col] = ":yellow_circle:"
                            if row != 0:
                                c4Board[row - 1][col] = ":blue_square:"
                            newEmbed = discord.Embed(
                                title="Connect 4",
                                description=getBoard(c4Board),
                                colour=discord.Colour.gold())
                            newEmbed.set_footer(
                                text="Click on a reaction to place a piece")
                            await message.edit(embed=newEmbed)
                            await asyncio.sleep(0.5)
                            if row == 5:
                                dropping = False
                            elif c4Board[row + 1][col] != ":blue_square:":
                                dropping = False
                            else:
                                row += 1

                        validMove = True
                        player1Turn = not player1Turn

                # Computer move
                else:
                    validMove = False
                    await asyncio.sleep(1)
                    while not validMove:
                        col = random.randrange(0, 7)

                        # Check for full column
                        if c4Board[0][col] != ":blue_square:":
                            continue

                        # Dropping animation
                        row = 0
                        dropping = True
                        while dropping:
                            c4Board[row][col] = ":yellow_circle:"
                            if row != 0:
                                c4Board[row - 1][col] = ":blue_square:"
                            newEmbed = discord.Embed(
                                title="Connect 4",
                                description=getBoard(c4Board),
                                colour=discord.Colour.gold())
                            newEmbed.set_footer(
                                text="Click on a reaction to place a piece")
                            await message.edit(embed=newEmbed)
                            await asyncio.sleep(0.5)
                            if row == 5:
                                dropping = False
                            elif c4Board[row + 1][col] != ":blue_square:":
                                dropping = False
                            else:
                                row += 1

                        validMove = True
                        player1Turn = not player1Turn

            freeCells -= 1
            winner = checkWinner(c4Board)

        # Game end message
        finalEmbed = discord.Embed(title="Connect 4",
                                   description=getBoard(c4Board),
                                   colour=discord.Colour.green())
        if winner == ":red_circle:":
            finalEmbed.set_footer(text=f"🎉 {player1} Won! 🎉")
        elif winner == ":yellow_circle:":
            finalEmbed.set_footer(text=f"🎉 {player2} Won! 🎉")
        else:
            finalEmbed.set_footer(text=f"🎉 Tie Game! 🎉")
        await message.edit(embed=finalEmbed)


def setup(client):
    client.add_cog(Games(client))
