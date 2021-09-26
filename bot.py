import os
import discord
import re
import constant
from substr.substr_game import SubstrGame
from dotenv import load_dotenv
from discord.ext import commands
from game_commands import GameCommands
from music_player.music_commands import MusicCommands


class LarmackBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, case_insensitive=True, intents=intents)

        self.add_cog(GameCommands(self))
        self.add_cog(MusicCommands(self))
        SubstrGame.load()

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        msg = message.content.lower()

        if re.search('(^|\s)pog+(gers)?(champ)?(gies)?!*(\s|$)', msg):
            await message.channel.send("PogChamp!!")

        # If I'm mentioned
        if 210819098274299904 in message.raw_mentions and constant.REACT_ON_MENTION:
            await message.add_reaction("<:larmad:859893602917810217>")

        await self.process_commands(message)


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = LarmackBot("!", intents)
bot.run(TOKEN)
