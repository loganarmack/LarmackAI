from game import SubstrGame
from multi_game import MultiSubstrGame

class GameManager:
    def __init__(self, user_id, channel_id, other_user_ids, open_game=False, versus=False):
        self.channel_id = channel_id
        self.user_list = [str(user_id)] + list(other_user_ids)
        self.host_id = user_id
        self.versus = versus
        self.open_game = open_game
        if versus:
            self.game = MultiSubstrGame(self.user_list)
        else:
            self.game = SubstrGame()

    def _includes_user(self, user_id):
        return self.open_game \
            or str(user_id) in self.user_list

    async def start(self, on_round_end, on_wrong_answer):
        await self.game.start(on_round_end, on_wrong_answer)

    async def submit_word(self, user_id, word):
        if (
            self.versus and self.game.get_current_player() == str(user_id)
            or not self.versus and self._includes_user(user_id)
        ):
            await self.game.submit_word(word)
