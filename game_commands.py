from discord.ext import commands
from game import SubstrGame
import constant

class GameCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.substr_game = SubstrGame()
        self.started = False

    @commands.command()
    async def start(self, ctx):
        if not self.started:
            substr = self.substr_game.start()
            self.started = True
            await ctx.send(self.__game_update_message('', substr))
        else:
            await ctx.send("The game is already running!")

    @commands.command()
    async def stop(self, ctx):
        if not self.started:
            await ctx.send("No game is currently running!")
        else:
            self.started = False
            self.substr_game.end()
            await ctx.send("Game stopped.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.content[0] == '!': #TODO: get prefix programmatically
            return

        if self.started:
            result, substr = self.substr_game.submit_word(message.content.lower())
            await message.channel.send(content=self.__game_update_message(result, substr))

        else:
            await message.channel.send("The game is not currently running.")

    def __game_update_message(self, result, substr):
        message = "```"
        message += f"Remaining letters: {self.substr_game.get_remaining_letters()}\n"
        message += f"Lives: Lives: {self.substr_game.lives}\n"
        message += f"{result}\n"
        message += f"Score: {self.substr_game.points}\n"

        if self.substr_game.lives > 0:
            message += f"Enter a word containing {substr}\n"
        else:
            self.substr_game.end()
            self.started = False
            message += "GAME OVER\n"

        return message + "```"
