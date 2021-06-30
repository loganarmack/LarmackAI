from discord.ext import commands
from game_manager import GameManager

class GameCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_list = {}

    @commands.command()
    async def start(self, ctx):
        user_id = ctx.message.author.id
        if user_id in self.game_list:
            await ctx.send("You already have a game running!")
        else:
            self.game_list[user_id] = GameManager(user_id, ctx.channel.id)
            substr = self.game_list[user_id].game.start(lambda r, s: self.__timeout(user_id, r, s))
            await ctx.send(self.__game_update_message(user_id, '', substr))

    @commands.command()
    async def stop(self, ctx):
        user_id = ctx.message.author.id
        if user_id not in self.game_list:
            await ctx.send("No game is currently running!")
        else:
            self.game_list[user_id].stop()
            self.game_list.pop(user_id)
            await ctx.send("Game stopped.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.content and message.content[0] == '!': #TODO: get prefix programmatically
            return

        user_id = message.author.id
        if user_id in self.game_list and message.channel.id == self.game_list[user_id].channel_id:
            result, substr = self.game_list[user_id].game.submit_word(message.content.lower())
            await message.channel.send(content=self.__game_update_message(user_id, result, substr))

            if self.game_list[user_id].game.game_over():
                self.game_list[user_id].stop()
                self.game_list.pop(user_id)

    def __game_update_message(self, user_id, result, substr):
        message = "```ml\n"
        if result:
            message += f"{result}\n"
        message += f"Remaining letters: {self.game_list[user_id].game.get_remaining_letters()}\n"
        message += f"Lives: {self.game_list[user_id].game.lives}\n"
        message += f"Score: {self.game_list[user_id].game.points}\n"

        if not self.game_list[user_id].game.game_over():
            message += f"Enter a word containing '{substr}' (time: {self.game_list[user_id].game.guess_time}s)\n"
        else:
            message += "GAME OVER\n"

        return message + "```"

    async def __timeout(self, user_id, result, substr):
        channel = self.bot.get_channel(self.game_list[user_id].channel_id)
        await channel.send(self.__game_update_message(user_id, result, substr))
        
        if self.game_list[user_id].game.game_over():
            self.game_list[user_id].stop()
            self.game_list.pop(user_id)
