from substr.substr_game import SubstrGame
from substr.multi_game import MultiSubstrGame
from twenty_four.twenty_four_game import TwentyFourGame
from constant import GameType
import substr.constant as const
import substr.bot_interface as substr_interface
import twenty_four.bot_interface as twenty_four_interface

class GameManager:
    def __init__(self, ctx, data, game_end_callback):
        self._ctx = ctx
        self.channel_id = data['channel_id']
        self.user_list = [str(data['user_id'])] + list(data['other_users'])
        self.host_id = data['user_id']
        self.game_type = data['game_type']
        self.open_game = data['open_game']
        self._game_end_callback = game_end_callback
        if self.game_type == GameType.substr_vs:
            self.game = MultiSubstrGame(self.user_list)
        elif self.game_type == GameType.substr:
            self.game = SubstrGame()
        elif self.game_type == GameType.twenty_four:
            self.game = TwentyFourGame()
        else:
            raise ValueError('Invalid game type')

    def _includes_user(self, user_id):
        return self.open_game \
            or str(user_id) in self.user_list

    async def start(self):
        on_round_end = None
        on_wrong_answer = None

        if self.game_type in (GameType.substr_vs, GameType.substr):
            on_round_end = substr_interface.on_round_end
            on_wrong_answer = substr_interface.on_wrong_answer
        elif self.game_type == GameType.twenty_four:
            on_round_end = twenty_four_interface.on_round_end
            on_wrong_answer = twenty_four_interface.on_wrong_answer

        round_end_callback = lambda info: on_round_end(self._ctx, info, self._game_end_callback)
        wrong_answer_callback = lambda reason: on_wrong_answer(self._ctx, reason)

        await self.game.start(round_end_callback, wrong_answer_callback)

    async def submit(self, user_id, message):
        if (
            self.game_type == GameType.substr_vs and self.game.get_current_player() == str(user_id)
            or self.game_type != GameType.substr_vs and self._includes_user(user_id)
        ):
            await self.game.submit(message)
    
    