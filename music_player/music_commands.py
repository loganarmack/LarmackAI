from discord.ext import commands
import discord
import re
from music_player.audio_controller import AudioController
from youtube_search import YoutubeSearch
from datetime import datetime


class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_to_audio_controller = {}

    @commands.command(
        brief="Joins the voice channel."
    )
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("You are not in a voice channel.")
            return

        audiocontroller = self._get_audio_controller(ctx, make_new=True)
        await audiocontroller.connect()

    @commands.command(
        brief="Leaves the voice channel."
    )
    async def leave(self, ctx):
        audiocontroller = self._get_audio_controller(ctx)

        if audiocontroller:
            await audiocontroller.disconnect()
            del self.guild_to_audio_controller[ctx.message.guild.id]
        else:
            await ctx.send("I'm not in any call.")

    @commands.command(
        help="Plays a song in the current voice channel. "
        + "You must be connected to a voice channel to run this command.",
        brief="Plays a song in the current voice channel."
    )
    async def play(self, ctx, *song):
        await self._play(ctx, song, False)

    @commands.command(
        name="play-next",
        help="Plays a song in the current voice channel. "
        + "You must be connected to a voice channel to run this command.",
        brief="Adds a song to the front of the queue."
    )
    async def play_next(self, ctx, *song):
        await self._play(ctx, song, True)

    async def _play(self, ctx, song, play_next):
        if not ctx.message.author.voice:
            await ctx.send("You're not connected to a voice channel.")
            return

        audiocontroller = self._get_audio_controller(ctx, make_new=True)
        if not audiocontroller.voice_client:
            audiocontroller.voice_client = await audiocontroller.vc.connect()

        song_url = await self._song_to_url(ctx, song)
        if not song_url:
            return

        if play_next:
            await audiocontroller.add_song_next(song_url)
        else:
            await audiocontroller.add_song(song_url)

    async def _song_to_url(self, ctx, song):
        if self._is_url(song[0]):
            return song[0]

        search_query = " ".join(song)
        results = YoutubeSearch(search_query, max_results=10).to_dict()

        link = "https://www.youtube.com"
        for result in results:
            try:
                # duration shouldn't have hour specified
                datetime.strptime(result["duration"], "%M:%S")
                link += result['url_suffix']
                break
            except ValueError:
                continue

        if link == "https://www.youtube.com":
            await ctx.send("All results found were too long. Maximum video length is 1 hour.")
            return None

        return link

    @commands.command(
        brief="Pauses the song in the current voice channel."
    )
    async def pause(self, ctx):
        audiocontroller = self._get_audio_controller(ctx)

        if audiocontroller:
            await audiocontroller.pause()
        else:
            await ctx.send("I'm not playing anything.")

    @commands.command(
        brief="Resumes playing a song."
    )
    async def resume(self, ctx):
        audiocontroller = self._get_audio_controller(ctx)

        if audiocontroller:
            await audiocontroller.resume()
        else:
            await ctx.send("I'm not in call.")

    @commands.command(
        brief="Stops the current song."
    )
    async def stop(self, ctx):
        audiocontroller = self._get_audio_controller(ctx)

        if audiocontroller:
            await audiocontroller.stop()
        else:
            await ctx.send("I'm not playing anything.")

    @commands.command(
        brief="Skips to the next song in queue."
    )
    async def skip(self, ctx):
        audiocontroller = self._get_audio_controller(ctx)

        if audiocontroller:
            await audiocontroller.skip()
        else:
            await ctx.send("I'm not playing anything.")

    @commands.command(
        brief="Lists the songs in queue."
    )
    async def queue(self, ctx):
        audiocontroller = self._get_audio_controller(ctx)

        if audiocontroller:
            await audiocontroller.display_queue()
        else:
            await ctx.send("There's nothing in queue.")

    @commands.command(
        name='song',
        aliases=['current', 'now-playing'],
        brief="Gives info on the current song"
    )
    async def now_playing(self, ctx):
        audiocontroller = self._get_audio_controller(ctx)

        if audiocontroller:
            await audiocontroller.now_playing()
        else:
            await ctx.send("I'm not playing anything right now.")

    def _get_audio_controller(self, ctx, make_new=False):
        guild = ctx.message.guild
        audiocontroller = self.guild_to_audio_controller.get(guild.id)
        if not audiocontroller and make_new:
            audiocontroller = AudioController(
                self.bot, guild, ctx.message.channel, ctx.message.author.voice.channel)
            self.guild_to_audio_controller[guild.id] = audiocontroller

        return audiocontroller

    @staticmethod
    def _is_url(s):
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            # domain...
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return re.match(regex, s) is not None
