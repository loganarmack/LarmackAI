from discord.ext import commands
from game_manager import GameManager
import constant

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
            await self.game_list[user_id].game.start(lambda data: self._on_round_end(user_id, data))

    @commands.command()
    async def stop(self, ctx):
        user_id = ctx.message.author.id
        if user_id not in self.game_list:
            await ctx.send("No game is currently running!")
        else:
            self.game_list[user_id].game.stop()
            self.game_list.pop(user_id)
            await ctx.send("Game stopped.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.content and message.content[0] == '!': #TODO: get prefix programmatically
            return

        user_id = message.author.id
        if user_id in self.game_list and message.channel.id == self.game_list[user_id].channel_id:
            await self.game_list[user_id].game.submit_word(message.content.lower())

    def _game_update_message(self, user_id, data):
        message = "```ml\n"

        #previous round result
        if data.get('result'):
            message += f"{data['result']}\n"
        message += f"Letters to bonus: {data['remaining_letters']}\n"

        #lives
        if data.get('delta_lives'):
            message += f"Lives: {data['lives'] - data['delta_lives']} -> {data['lives']}\n"
        else:
            message += f"Lives: {data['lives']}\n"

        #score
        message += f"Score: {data['points']}\n"

        #substr/game over
        if data['substr'] != constant.GAME_OVER:
            message += f"Enter a word containing '{data['substr']}' (time: {data['guess_time']}s)\n"
        else:
            message += "GAME OVER\n"

        return message + "```"

    async def _on_round_end(self, user_id, data):
        channel = self.bot.get_channel(self.game_list[user_id].channel_id)
        await channel.send(self._game_update_message(user_id, data))
        
        if data['substr'] == constant.GAME_OVER:
            self.game_list.pop(user_id)
