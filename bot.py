import os
import discord
from game import SubstrGame
from dotenv import load_dotenv
from discord.ext import commands
from game_commands import GameCommands

class LarmackBot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix, case_insensitive=True)
    
        self.add_cog(GameCommands(self))
        SubstrGame.load()
        
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if 'pog' in message.content.lower():
            await message.channel.send("PogChamp!!")

        if 210819098274299904 in message.raw_mentions:
            larmad = next((emoji for emoji in message.guild.emojis if "larmad" in emoji.name or emoji.name == "log"), None)
            emoji = str(larmad) or "\N{smiling face with sunglasses}"
            await message.add_reaction(emoji)

        await self.process_commands(message)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = LarmackBot("!")
bot.run(TOKEN)
