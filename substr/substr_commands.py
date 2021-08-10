from discord.ext import commands
from substr.substr_manager import SubstrManager
import substr.constant as const
import re
import psycopg2
import os
from dotenv import load_dotenv


class SubstrCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_list = {}

        #setup db for highscores
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
        help="Starts a word game in the current channel. "
            +"You can metion specific users after the command to add "
            +"them to your game, or allow anyone to pitch in using the keyword 'any'.",
        brief="Starts a word game in the current channel."

    )
    async def start(self, ctx, *other_users):
        open_game = other_users and other_users[0].lower() in ["any", "open", "all"]
        await self._start_game(ctx, other_users, open_game=open_game)

    @commands.command(
        help="Starts a versus word game in the current channel. "
            +"Mention any users who you'd like to include in the game.",
        brief="Starts a versus word game in the current channel.",
        name="start-vs"
    )
    async def start_versus(self, ctx, *other_users):
        await self._start_game(ctx, other_users, versus=True)

    async def _start_game(self, ctx, other_users, open_game=False, versus=False):
        user_id = ctx.message.author.id
        channel_id = ctx.channel.id
        if channel_id in self.game_list:
            await ctx.send("There's already a game running in this channel!")

        else:
            extra_users = set()
            for user in other_users:
                search_id = re.search('^<@!(.*)>$', user)
                if search_id:
                    extra_users.add(search_id.group(1))

            if versus and (not extra_users or len(extra_users) == 1 and str(user_id) in extra_users):
                await ctx.send("You have to mention at least one other player.")
                return

            self.game_list[channel_id] = SubstrManager(user_id, channel_id, extra_users, open_game, versus)
            print(f"Starting game in channel {channel_id} by host {user_id} with extra users {extra_users} (Versus = {versus})")
            await self.game_list[channel_id].start(
                lambda data: self._on_round_end(channel_id, data),
                lambda reason: self._on_wrong_answer(channel_id, reason)
            )

    @commands.command(
        help="Stops the word game in the current channel. "
            +"You must have been the one to start the lobby to be able to stop it.",
        brief="Stops the word game in the current channel."
    )
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

    @commands.command(
        name='leaderboard',
        aliases=['leaderboards', 'highscores'],
        help="Displays the word game high scores for the current server.",
        brief="Displays the word game high scores for the current server."
    )
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
                replacements = {'starting_lives': const.STARTING_LIVES, 'guess_time': const.GUESS_TIME}
                message = f.read().replace('\n', '').replace('\\', '\n').format(**replacements)
                await ctx.send(message)

        except FileNotFoundError:
            print("Error: could not find rules file.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.content and message.content[0] == '!': #TODO: get prefix programmatically
            return

        channel_id = message.channel.id
        user_id = message.author.id
        if channel_id in self.game_list:
            await self.game_list[channel_id].submit_word(user_id, message.content.lower())

    def _game_update_message(self, data):
        message = "```ml\n"

        #previous round result
        if data.get('result'):
            message += f"{data['result']}\n"

        if data.get('remaining_letters'):
            message += f"Letters to bonus: {data['remaining_letters']}\n"

        #lives
        if data.get('lives') is not None and data.get('delta_lives'):
            message += f"Lives: {data['lives'] - data['delta_lives']} -> {data['lives']}\n"
        elif data.get('lives') is not None:
            message += f"Lives: {data['lives']}\n"

        #score
        if data.get('points'):
            message += f"Score: {data['points']}\n"

        #substring
        if data.get('substr') and data['substr'] != const.GAME_OVER:
            message += f"Enter a word containing '{data['substr']}' (time: {data['guess_time']}s)\n"
        elif data.get('substr'):
            message += "GAME OVER\n"

        message += "```"

        if data.get('turn'):
            message += f"<@{data['turn']}>"

        if data.get('eliminated'):
            message += f"<@{data['eliminated']}> has been eliminated."

        if data.get('winner'):
            message += f"\nGG, the winner is <@{data['winner']}>!"


        return message

    async def _on_round_end(self, channel_id, data):
        channel = self.bot.get_channel(channel_id)
        await channel.send(self._game_update_message(data))
        
        if data.get('winner'):
            self.game_list.pop(channel_id)

        elif data.get('substr') == const.GAME_OVER:
            guild_id = channel.guild.id
            user_id = self.game_list[channel_id].host_id
            solo = len(self.game_list[channel_id].user_list) == 1

            self.game_list.pop(channel_id)

            if not solo: #only store single player high scores
                return

            try:
                #Insert score if it doesn't exist
                self.cur.execute(f"""
                    INSERT INTO leaderboards (guild_id, user_id, score) 
                    VALUES ({guild_id}, {user_id}, {data['points']})
                    ON CONFLICT (guild_id, user_id)
                    DO UPDATE SET score = GREATEST(EXCLUDED.score, leaderboards.score);""")

                self.conn.commit()

            except Exception as e:
                print(f"Error updating score for user {user_id}: {e}")

    async def _on_wrong_answer(self, channel_id, reason):
        channel = self.bot.get_channel(channel_id)
        await channel.send(reason)

            

    
