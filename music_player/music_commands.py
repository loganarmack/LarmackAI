from discord.ext import commands
import discord
from music_player.YTDLSource import YTDLSource
from music_player.audio_controller import AudioController


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
    async def play(self, ctx, song):
        if not ctx.message.author.voice:
            await ctx.send("You're not connected to a voice channel.")
            return

        audiocontroller = self._get_audio_controller(ctx, make_new=True)

        await audiocontroller.add_song(song)

    @commands.command(
        name="play-next",
        help="Plays a song in the current voice channel. "
        + "You must be connected to a voice channel to run this command.",
        brief="Adds a song to the front of the queue."
    )
    async def play_next(self, ctx, song):
        if not ctx.message.author.voice:
            await ctx.send("You're not connected to a voice channel.")
            return

        audiocontroller = self._get_audio_controller(ctx, make_new=True)

        await audiocontroller.add_song_next(song)

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

    def _get_audio_controller(self, ctx, make_new=False):
        guild = ctx.message.guild
        audiocontroller = self.guild_to_audio_controller.get(guild.id)
        if not audiocontroller and make_new:
            audiocontroller = AudioController(
                self.bot, guild, ctx.message.channel, ctx.message.author.voice.channel)
            self.guild_to_audio_controller[guild.id] = audiocontroller

        return audiocontroller
