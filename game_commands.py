from discord.ext import commands
from game_manager import GameManager
import substr.constant as const
from constant import GameType
import re
import psycopg2
import os
from dotenv import load_dotenv


class GameCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_list = {}

        # setup db for highscores
        load_dotenv()
        DATABASE_URL = os.getenv('DATABASE_URL')
        self.conn = psycopg2.connect(DATABASE_URL)
        self.cur = self.conn.cursor()

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS leaderboards (
                guild_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                score REAL NOT NULL,
                PRIMARY KEY (guild_id, user_id)
            );""")

    @commands.command(
        help="Starts a game in the current channel. "
        + "You must mention the game type (substr or 24) "
        + "You can metion specific users after the command to add "
        + "them to your game, or allow anyone to pitch in using the keyword 'any'.",
        brief="Starts a game in the current channel."
    )
    async def start(self, ctx, game, *other_users):
        open_game = other_users and other_users[0].lower() in [
            "any", "open", "all"]

        if not game:
            await ctx.send("You must specify a game type.")

        game_type = None
        if game.lower() in ["substr", "word"]:
            game_type = GameType.substr
        elif game.lower() in ["24", "twenty_four", "24game", "twenty"]:
            game_type = GameType.twenty_four
        else:
            await ctx.send("Invalid game type.")
            return

        args = {
            'game_type': game_type,
            'open_game': open_game,
            'other_users': other_users
        }
        await self._start_game(ctx, args)

    @commands.command(
        help="Starts a versus word game in the current channel. "
        + "Mention any users who you'd like to include in the game.",
        brief="Starts a versus word game in the current channel.",
        name="start-vs"
    )
    async def start_versus(self, ctx, *other_users):
        args = {
            'game_type': GameType.substr_vs,
            'other_users': other_users,
        }
        await self._start_game(ctx, args)

    async def _start_game(self, ctx, data):
        user_id = ctx.message.author.id
        channel_id = ctx.channel.id
        if channel_id in self.game_list:
            await ctx.send("There's already a game running in this channel!")
            return

        extra_users = set()
        if data.get('other_users'):
            for user in data['other_users']:
                search_id = re.search('^<@!(.*)>$', user)
                if search_id:
                    extra_users.add(search_id.group(1))

        if data['game_type'] == GameType.substr_vs and (not extra_users or len(extra_users) == 1 and str(user_id) in extra_users):
            await ctx.send("You have to mention at least one other player.")
            return

        game_data = {
            'channel_id': channel_id,
            'user_id': user_id,
            'game_type': data['game_type'],
            'open_game': data.get('open_game'),
            'other_users': extra_users
        }

        self.game_list[channel_id] = GameManager(
            ctx, game_data, self._on_game_end)
        print(
            f"Starting {data['game_type']} game in channel {channel_id} by host {user_id} with extra users {extra_users}")
        await self.game_list[channel_id].start()

    @commands.command(
        help="Quits the word game in the current channel. "
        + "You must have been the one to start the lobby to be able to end it.",
        brief="Quits the word game in the current channel."
    )
    async def quit(self, ctx):
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

    @commands.command(
        name='leaderboard',
        aliases=['leaderboards', 'highscores'],
        help="Displays the word game high scores for the current server.",
        brief="Displays the word game high scores for the current server."
    )
    async def leaderboard(self, ctx):
        guild_id = ctx.guild.id

        try:
            self.cur.execute(
                f"SELECT user_id, score FROM leaderboards WHERE guild_id = {guild_id} ORDER BY score DESC")
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

    @commands.command(
        name='rules',
        aliases=['howtoplay'],
        help="A quick breakdown of the rules of the game.",
        brief="A quick breakdown of the rules of the game.",
    )
    async def rules(self, ctx):
        try:
            file_path = os.path.abspath(__file__)
            dir_path = os.path.dirname(file_path)
            rules_path = os.path.join(dir_path, 'game_rules.txt')
            with open(rules_path, 'r') as f:
                replacements = {
                    'starting_lives': const.STARTING_LIVES, 'guess_time': const.GUESS_TIME}
                message = f.read().replace('\n', '').replace('\\', '\n').format(**replacements)
                await ctx.send(message)

        except FileNotFoundError:
            print("Error: could not find rules file.")

    @commands.Cog.listener()
    async def on_message(self, message):
        # TODO: get prefix programmatically
        if message.author == self.bot.user or message.content and message.content[0] == '!':
            return

        channel_id = message.channel.id
        user_id = message.author.id
        if channel_id in self.game_list:
            await self.game_list[channel_id].submit(user_id, message.content.lower())

    def _on_game_end(self, ctx, data):
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id
        user_id = self.game_list[channel_id].host_id
        game_type = self.game_list[channel_id].game_type
        solo = len(self.game_list[channel_id].user_list) == 1

        self.game_list.pop(channel_id)

        if game_type == GameType.substr and solo:  # update highscore
            try:
                self.cur.execute(f"""
                    INSERT INTO leaderboards (guild_id, user_id, score) 
                    VALUES ({guild_id}, {user_id}, {data['points']})
                    ON CONFLICT (guild_id, user_id)
                    DO UPDATE SET score = GREATEST(EXCLUDED.score, leaderboards.score);""")

                self.conn.commit()
            except Exception as e:
                print(f"Error updating score for user {user_id}: {e}")
