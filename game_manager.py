from game import SubstrGame
from datetime import date, datetime
import constant

class GameManager:
    def __init__(self, user_id, channel_id, other_user_ids, open_game):
        self.game = SubstrGame()
        self.channel_id = channel_id
        self.host_id = user_id
        self.other_user_ids = other_user_ids
        self.open_game = open_game
        self.prompt_time = datetime.now().second

    def includes_user(self, user_id):
        return self.open_game \
            or user_id == self.host_id \
            or str(user_id) in self.other_user_ids

    async def submit_word(self, word):
        curr_time = datetime.now().second
        if curr_time - self.prompt_time > constant.GUESS_DELAY:
            self.prompt_time = curr_time
            await self.game.submit_word(word)

        else:
            print("Guessed too fast!")
