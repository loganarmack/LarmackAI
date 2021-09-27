from music_player.YTDLSource import YTDLSource
import discord
from collections import deque


class AudioController:
    def __init__(self, bot, guild, tc, vc):
        self.bot = bot
        self.guild = guild
        self.tc = tc
        self.vc = vc
        self.voice_client = None

        self.queue = deque()

    def next_song(self, error):
        if error:
            print(error)
            return

        if len(self.queue) <= 1:
            self.queue.clear()
            return

        self.queue.popleft()

        play_next_coro = self.play_song(self.queue[-1])

        self.bot.loop.create_task(play_next_coro)

    async def play_song(self, song):
        try:
            if not self.voice_client:
                self.voice_client = await self.vc.connect()

            self.voice_client.play(discord.FFmpegPCMAudio(
                song[0]), after=lambda e: self.next_song(e))
            await self.tc.send(f"**Now Playing:** {song[1]} {song[2]}")

        except Exception as e:
            print(f"{repr(e)}: {e}")
            await self.tc.send("An error occurred trying to play the song.")

    async def add_song(self, url):
        await self._add_song(url, False)

    async def add_song_next(self, url):
        await self._add_song(url, True)

    async def _add_song(self, url, play_next):
        title = await self._get_title(url)
        await self.tc.send(f"**Adding** {title} to the queue.")

        filename = await self._download_song(url)
        if play_next:
            self.queue.appendLeft((filename, title, url))
        else:
            self.queue.append((filename, title, url))

        if not (self.voice_client and self.voice_client.is_playing()):
            await self.play_song(self.queue[-1])

    async def _get_title(self, url):
        title = "Unknown"
        if 'youtube' in url:
            title = await YTDLSource.get_title(url, loop=self.bot.loop)
        else:
            print("Error fetching song title.")

        return title

    async def _download_song(self, url):
        filename = ""

        if 'youtube' in url:
            filename = await YTDLSource.from_url(url, loop=self.bot.loop)
        else:
            print("Url not supported.")

        return filename

    async def display_queue(self):
        if len(self.queue) == 0:
            await self.tc.send("The queue is empty.")
        else:
            msg = "**Queue:**\n"
            for i, song in enumerate(self.queue):
                msg += f"{i + 1}: {song[1]} {song[2]}\n"

            await self.tc.send(msg)

    async def now_playing(self):
        if not self.voice_client or len(self.queue) == 0:
            await self.tc.send("There's no music playing.")
        else:
            song = self.queue[-1]
            await self.tc.send(f"**Now Playing:** {song[1]} {song[2]}")

    async def skip(self):
        if not self.voice_client or len(self.queue) == 0:
            await self.tc.send("There's no music playing.")
        else:
            self.voice_client.stop()

    async def pause(self):
        if not self.voice_client or not self.voice_client.is_playing():
            await self.tc.send("There's no music playing.")
        else:
            self.voice_client.pause()

    async def resume(self):
        if not self.voice_client or not self.voice_client.is_paused():
            await self.tc.send("The music isn't paused.")
        else:
            self.voice_client.resume()

    async def stop(self):
        if not self.voice_client:
            await self.tc.send("There's no music playing.")
        else:
            self.queue.clear()
            self.voice_client.stop()

    async def connect(self):
        if self.voice_client:
            await self.tc.send("I'm already in a call.")
        else:
            self.voice_client = await self.vc.connect()

    async def disconnect(self):
        if not self.voice_client:
            await self.tc.send("I'm not in any call.")

        else:
            self.queue.clear()
            await self.voice_client.disconnect()
