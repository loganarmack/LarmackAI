from game import SubstrGame
from datetime import datetime
import constant

class GameManager:
    def __init__(self, user_id, channel_id, other_user_ids, open_game):
        self.game = SubstrGame()
        self.channel_id = channel_id
        self.host_id = user_id
        self.other_user_ids = other_user_ids
        self.open_game = open_game

    def includes_user(self, user_id):
        return self.open_game \
            or user_id == self.host_id \
            or str(user_id) in self.other_user_ids

    async def start(self, on_round_end, on_wrong_answer):
        await self.game.start(on_round_end, on_wrong_answer)

    async def submit_word(self, word):
        await self.game.submit_word(word)
