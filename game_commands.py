from discord.ext import commands
from game import SubstrGame

class GameCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.substr_game = SubstrGame()
        self.started = False

    @commands.command()
    async def start(self, ctx):
        if not self.started:
            #self.substr_game.start()
            self.started = True
        else:
            await ctx.send("The game is already running!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.started:
            await message.channel.send("The game is currently running.")
        else:
            await message.channel.send("The game is not currently running.")
