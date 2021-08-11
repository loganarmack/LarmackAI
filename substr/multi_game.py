from substr.substr_game import SubstrGame
import substr.constant as const
from timer import Timer

class MultiSubstrGame(SubstrGame):

    def __init__(self, users): 
        super().__init__()

        self._whos_turn = 0
        self._users = [
            {
                'id': user_id,
                'lives': const.STARTING_LIVES,
                'used_letters': set()
            } 
            for user_id in users
        ]
        self._substr_rep_max = len(self._users)
        self._substr_rep_curr = 0

    def _current_user(self):
        return self._users[self._whos_turn]

    def _make_data(self):
        return {
            'lives': self._users[self._whos_turn]['lives'],
            'remaining_letters': self._get_remaining_letters(),
            'substr': self._substr,
            'guess_time': self._guess_time,
            'turn': self.get_current_player()
        }

    def _get_remaining_letters(self):
        return sorted(SubstrGame.letter_set - self._current_user()['used_letters'])

    def _update_used_letters(self, user_word):
        for letter in user_word.lower():
            self._current_user()['used_letters'].add(letter)
        
        if len(self._current_user()['used_letters']) == 26:
            self._current_user()['used_letters'] = set()
            self._current_user()['lives'] += 1
            
            return True

        return False

    def _increment_weights(self):
        self._guess_time = max(const.MIN_TIME_SECONDS, self._guess_time * 9 / 10.0)
        super()._increment_weights()
    
    def _choose_substr(self):
        self._substr_rep_curr = 0
        self._substr_rep_max = len(self._users)
        super()._choose_substr()

    async def _round_end(self, user_word, timeout):
        delta_lives = 0
        result = ''
        if not timeout:
            self._timer.cancel()

            self._increment_weights()
            self._used_words.add(user_word)
            used_all_letters = self._update_used_letters(user_word)
            
            result = f"Nice job!"

            if used_all_letters:
                result += "\nYou've gained a life from using each letter at least once!"
                delta_lives = 1

            self._choose_substr()

        else:
            self._current_user()['lives'] -= 1
            result = f"You're out of time!"
            delta_lives = -1

            self._substr_rep_curr += 1

            if self._substr_rep_curr == self._substr_rep_max:
                self._choose_substr()

        data = {
            'result': result,
        }

        if delta_lives != 0:
            data['delta_lives'] = delta_lives
            data['lives'] = self._current_user()['lives']

        if self._current_user()['lives'] <= 0:
            data['eliminated'] = self._current_user()['id']
            del self._users[self._whos_turn]
            self._whos_turn -= 1

            if len(self._users) == 1:
                data['winner'] = self._users[0]['id']

        #update previous user about their turn
        await self._round_end_callback(data)

        #start next round if people are still alive
        self._whos_turn = (self._whos_turn + 1) % len(self._users)
        if len(self._users) >= 2:
            data = self._make_data()
            await self._round_end_callback(data)
            self._timer = Timer(self._guess_time, self._on_timeout)

    def get_current_player(self):
        return self._users[self._whos_turn]['id']
