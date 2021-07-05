from discord.ext import commands
from game_manager import GameManager
import constant
import re
import psycopg2
from config import config


class GameCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_list = {}

        #setup db for highscores
        params = config()
        self.conn = psycopg2.connect(**params)
        self.cur = self.conn.cursor()

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS leaderboards (
                guild_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                score REAL NOT NULL,
                PRIMARY KEY (guild_id, user_id)
            );""")


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
            print(f"Stopped game in channel {channel_id} by host {user_id}")
            await ctx.send("Game stopped.")

    @commands.command(name='leaderboard', aliases=['leaderboards', 'highscores']) #TODO: http://dreamlo.com/lb/vtbGDimszEqVQtUNKWmojgR-stxw8_1020Kryey3UTnw
    async def leaderboard(self, ctx):
        guild_id = ctx.guild.id

        try:
            self.cur.execute(f"SELECT user_id, score FROM leaderboards WHERE guild_id = {guild_id} ORDER BY score DESC")
            leaderboard = self.cur.fetchall()

            message = ""
            if not leaderboard:
                message = f"There are currently no scores stored for {ctx.guild.name}."
            
            else:
                message = f"The current leaderboards for {ctx.guild.name}:\n"
                for i, row in enumerate(leaderboard):
                    user = self.bot.get_user(row[0])
                    username = user.name + '#' + user.discriminator if user else "Unknown"
                    message += f"{i + 1}: {username} with {row[1]} points\n"

            await ctx.send(message)

        except Exception as e:
            print(e)
            await ctx.send("There was an error retrieving the leaderboard.")

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
            guild_id = channel.guild.id
            user_id = self.game_list[channel_id].host_id

            self.game_list.pop(channel_id)

            try:
                #Insert score if it doesn't exist
                self.cur.execute(f"""
                    INSERT INTO leaderboards (guild_id, user_id, score) 
                    VALUES ({guild_id}, {user_id}, {data['points']})
                    ON CONFLICT (guild_id, user_id)
                    DO UPDATE SET score = GREATEST(EXCLUDED.score, {data['points']});""")

                self.conn.commit()

            except Exception as e:
                print(f"Error updating score for user {user_id}: {e}")


            

    
