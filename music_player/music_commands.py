from discord.ext import commands
import youtube_dl


class MusicComands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        ytdl_format_options = {
            'format': 'bestaudio/best',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            # bind to ipv4 since ipv6 addresses cause issues sometimes
            'source_address': '0.0.0.0'
        }

        self.ffmpeg_options = {
            'options': '-vn'
        }

        self.ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

    @commands.command(
        help="Starts a game in the current channel. "
        + "You must mention the game type (substr or 24) "
        + "You can metion specific users after the command to add "
        + "them to your game, or allow anyone to pitch in using the keyword 'any'.",
        brief="Starts a game in the current channel."
    )
    async def play(self, ctx, game, *other_users):
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
