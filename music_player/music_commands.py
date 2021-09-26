from discord.ext import commands
import discord
from music_player.YTDLSource import YTDLSource
import path


class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief="Joins the voice channel."
    )
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("You're not connected to a voice channel.")
        else:
            channel = ctx.message.author.voice.channel
            await channel.connect()

    @commands.command(
        brief="Leaves the voice channel."
    )
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client

        if not voice_client.is_connected():
            await ctx.send("I'm not in a voice channel.")
        else:
            await voice_client.disconnect()

    @commands.command(
        help="Plays a song in the current voice channel. "
        + "You must be connected to a voice channel to run this command.",
        brief="Plays a song in the current voice channel."
    )
    async def play(self, ctx, song):
        if not ctx.message.author.voice:
            await ctx.send("You're not connected to a voice channel.")
            return

        # TODO: allow getting songs from soundcloud, spotify, musescore

        channel = ctx.message.author.voice.channel
        voice_client = ctx.message.guild.voice_client

        if not voice_client:
            await channel.connect()
            voice_client = ctx.message.guild.voice_client

        try:
            async with ctx.typing():
                file_path = path.abspath(__file__)
                dir_path = path.dirname(file_path)
                ffmpeg_path = path.join(dir_path, 'ffmpeg.exe')

                filename, title = await YTDLSource.from_url(song, loop=self.bot.loop)
                voice_client.play(discord.FFmpegPCMAudio(
                    executable=ffmpeg_path, source=filename))
                await ctx.send(f"**Now Playing:** {title}")

        except Exception as e:
            print(e)
            await ctx.send("I couldn't find that song.")

    @commands.command(
        brief="Plays a song in the current voice channel."
    )
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(
        brief="Resumes playing a song."
    )
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send("The bot was not playing anything before this. Use play_song command")

    @commands.command(
        brief="Stops playing a song."
    )
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")
