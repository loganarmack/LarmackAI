from discord.ext import commands
from game_manager import GameManager
import constant
import re
import json

class GameCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_list = {}

    @commands.command()
    async def start(self, ctx, *args):
        user_id = ctx.message.author.id
        channel_id = ctx.channel.id
        if channel_id in self.game_list:
            await ctx.send("There's already a game running in this channel!")

        else:
            open_game = args and args[0].lower() == "any"
            extra_users = []
            for arg in args:
                search_id = re.search('^<@!(.*)>$', arg)
                if search_id:
                    extra_users.append(search_id.group(1))

            self.game_list[channel_id] = GameManager(user_id, channel_id, extra_users, open_game)
            print(f"Starting game in channel {channel_id} by host {user_id} with extra users {extra_users}")
            await self.game_list[channel_id].start(lambda data: self._on_round_end(channel_id, data))

    @commands.command()
    async def stop(self, ctx):
        user_id = ctx.message.author.id
        channel_id = ctx.channel.id
        if channel_id not in self.game_list:
            await ctx.send("There aren't any games running in this channel!")
        elif self.game_list[channel_id].host_id != user_id:
            await ctx.send("You don't have permission to stop this game!")
        else:
            self.game_list[channel_id].game.stop()
            self.game_list.pop(channel_id)
            await ctx.send("Game stopped.")

    @commands.command()
    async def leaderboards(self, ctx):
        guild_id = str(ctx.guild.id)
        with open("leaderboards.json", "r") as f:
            leaderboards = json.load(f)
            
            message = f"The current leaderboards for {ctx.guild.name}:\n"
            for i, user_id in enumerate(leaderboards[guild_id]):
                user = self.bot.get_user(int(user_id))
                username = user.name + '#' + user.discriminator if user else "Unknown"
                message += f"{i + 1}: {username} with {leaderboards[guild_id][user_id]} points\n"

            await ctx.send(message)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.content and message.content[0] == '!': #TODO: get prefix programmatically
            return

        channel_id = message.channel.id
        user_id = message.author.id
        if (channel_id in self.game_list
            and self.game_list[channel_id].includes_user(user_id)
        ):
            await self.game_list[channel_id].submit_word(message.content.lower())

    def _game_update_message(self, data):
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

    async def _on_round_end(self, channel_id, data):
        channel = self.bot.get_channel(channel_id)
        await channel.send(self._game_update_message(data))
        
        if data['substr'] == constant.GAME_OVER:

            try:
                f = open("leaderboards.json", "r+")

                leaderboards = json.load(f)
                guild_id = str(channel.guild.id)
                user_id = str(self.game_list[channel_id].host_id)

                changed = False
                if not leaderboards[guild_id]:
                    leaderboards[guild_id] = {user_id: data['points']}
                    changed = True

                elif user_id not in leaderboards[guild_id] or leaderboards[guild_id][user_id] < data['points']:
                    leaderboards[guild_id][user_id] = data['points']
                    changed = True

                if changed:
                    leaderboards[guild_id] = {
                        k: v for k, v in sorted(leaderboards[guild_id].items(), key=lambda item: item[1])
                    }
                    f.seek(0)
                    f.write(json.dumps(leaderboards))
                    f.truncate()

                f.close()
            
            except FileNotFoundError:
                guild_id = channel.guild.id
                user_id = self.game_list[channel_id].host_id
                leaderboards = {guild_id: { user_id: data['points']}}

                with open("leaderboards.json", "w") as f:
                    f.write(json.dumps(leaderboards))

            self.game_list.pop(channel_id)
