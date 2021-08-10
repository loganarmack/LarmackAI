from substr.substr_game import SubstrGame
from substr.multi_game import MultiSubstrGame
from twenty_four.twenty_four_game import TwentyFourGame
from constant import GameType
import substr.constant as const

class GameManager:
    def __init__(self, ctx, data):
        self._ctx = ctx
        self.channel_id = data['channel_id']
        self.user_list = [str(data['user_id'])] + list(data['other_users'])
        self.host_id = data['user_id']
        self.game_type = data['game_type']
        self.open_game = data['open_game']
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
        round_end_callback = lambda info: self._on_round_end(info)
        wrong_answer_callback = lambda reason: self._on_wrong_answer(reason)
        await self.game.start(round_end_callback, wrong_answer_callback)

    async def submit_word(self, user_id, word):
        if (
            self.game_type == GameType.substr_vs and self.game.get_current_player() == str(user_id)
            or not self.game_type == GameType.substr_vs and self._includes_user(user_id)
        ):
            await self.game.submit(word)

    
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

    async def _on_round_end(self, data):
        await self._ctx.send(self._game_update_message(data))
        
        if data.get('winner'):
            self.game_list.pop(channel_id)

        elif data.get('substr') == const.GAME_OVER:
            guild_id = self._ctx.guild.id
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

    async def _on_wrong_answer(self, reason):
        await self._ctx.send(reason)
