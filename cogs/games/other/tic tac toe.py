import discord, asyncio, random, math
from discord.ext import commands


class TicTacToe(commands.Cog):
    def __init__(self, client):
        self.client = client

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
                f"{ctx.author.mention} you took too long to respond, not playing with you :rage:"
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


def setup(client):
    client.add_cog(TicTacToe(client))
