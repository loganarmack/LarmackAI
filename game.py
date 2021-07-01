from word_counter import get_pair_levels, get_triplet_levels, export_levels
from random import randint, choice
import constant
import json
from math import floor
from timer import Timer

class SubstrGame:
    levels = {}
    letter_set = set([chr(i) for i in range(ord('a'), ord('a') + 26)])

    def __init__(self):
        if not SubstrGame.levels:
            SubstrGame.load()

        self._reset()

    def _reset(self):
        self._points = 0
        self._lives = 3
        self._used_words = set()
        self._used_letters = set()
        self._level_weights = {0: 1000, 1: 0, 2: 0, 3: 0, 4: 0}
        self._length_weights = {2: 100, 3: 0}
        self._substr = "ng"
        self._possible_word = "ping"
        self._substr_level = 0
        self._substr_length = 2
        self._guess_time = 15
        self._timer = None
        self._timeout_callback = None

    def _choose_substr(self):
        self._substr_level = SubstrGame.weighted_random(self._level_weights)
        self._substr_length = SubstrGame.weighted_random(self._length_weights)
        self._substr = choice(list(SubstrGame.levels[str(self._substr_length)][self._substr_level].keys()))
        self._possible_word = choice(SubstrGame.levels[str(self._substr_length)][self._substr_level][self._substr])

    def _check_word(self, user_word, timeout): 
        correct = True
        reason = None
        if timeout:
            correct = False
            reason = "You're out of time!"

        elif not user_word:
            correct = False
            reason = "You didn't enter a word!"

        elif user_word in self._used_words:
            correct = False
            reason = "You've already used that word!"

        elif self._substr not in user_word:
            correct = False
            reason = f"Your word doesn't use '{self._substr}'!"

        elif user_word not in SubstrGame.levels[str(self._substr_length)][self._substr_level][self._substr]:
            correct = False
            reason = "That's not a real word!"
        
        return correct, reason

    def _score_word(self, word):
        base = 100  # default for valid word

        # bonus for making longer words p(l) = (l-5)^2 + 10l
        base += 10 * len(word) + (len(word) - 5) ** 2

        # bonus for not starting word with substring
        if word[:self._substr_length] != self._substr:
            base += 25  

        # substr difficulty multiplier
        bonus_mult = self._substr_level / 4.0  

        # substr length multiplier (might not be worth keeping)
        bonus_mult += (self._substr_length - 2) / 2.0  

        total = base * (bonus_mult + 1)
        self._points += total
        return total

    def _increment_weights(self):
        for level in self._level_weights:
            if level != constant.LEVELS - 1:
                self._level_weights[level + 1] += floor(self._level_weights[level] / 10.0)
                self._level_weights[level] = floor(self._level_weights[level] * 9 / 10.0)

        self._length_weights[3] += floor(self._length_weights[2] / 10.0)
        self._length_weights[2] = floor(self._length_weights[2] * 9 / 10.0)

        #self.guess_time = max(constant.MIN_TIME_SECONDS, self.guess_time * 9 / 10.0)
        #minimum word length scaling?

    def _update_used_letters(self, user_word):
        for letter in user_word.lower():
            self._used_letters.add(letter)
        
        if len(self._used_letters) == 26:
            self._used_letters = set()
            self._lives += 1
            
            return True

        return False

    async def _round_end(self, user_word, timeout):
        if not timeout:
            self._timer.cancel()

        result = ''
        delta_lives = 0
        correct, reason = self._check_word(user_word, timeout)
        if correct:
            word_value = self._score_word(user_word)
            self._increment_weights()
            self._used_words.add(user_word)
            used_all_letters = self._update_used_letters(user_word)

            result = f"Nice job! You earned {word_value} points."

            if used_all_letters:
                result += "You've gained a life from using each letter at least once!\n"
                delta_lives = 1
        
        else:
            self._lives -= 1
            result = reason + f"\nA possible word for this was {self._possible_word}"
            delta_lives = -1

        if self._lives <= 0:
            self._substr = constant.GAME_OVER
        else:
            self._choose_substr()

        data = {
            'result': result,
            'lives': self._lives, 
            'points': self._points, 
            'remaining_letters': self._get_remaining_letters(), 
            'substr': self._substr, 
            'guess_time': self._guess_time
        }

        if delta_lives != 0:
            data['delta_lives'] = delta_lives

        await self._round_end_callback(data)

        if self._lives > 0:
            self._timer = Timer(self._guess_time, self._on_timeout)

    async def _on_timeout(self):
        await self._round_end(None, True)

    async def submit_word(self, user_word):
        await self._round_end(user_word, False)

    async def start(self, round_end_callback):
        self._reset()
        self._round_end_callback = round_end_callback
        self._choose_substr()

        data = {
            'lives': self._lives, 
            'points': self._points, 
            'remaining_letters': self._get_remaining_letters(), 
            'substr': self._substr, 
            'guess_time': self._guess_time
        }
        await round_end_callback(data)

        self._timer = Timer(self._guess_time, self._on_timeout)

    def stop(self):
        if self._timer:
            self._timer.cancel()  

    def _get_remaining_letters(self):
        return sorted(SubstrGame.letter_set - self._used_letters) 

    @staticmethod
    def weighted_random(weights):
        total = sum(weights[level] for level in weights)
        r = randint(1, total)
        for level in weights:
            r -= weights[level]
            if r <= 0:
                return level

    @staticmethod
    def load():
        try:
            f = open("levels.json", "r")
            SubstrGame.levels = json.load(f)
        except FileNotFoundError:
            export_levels(constant.LEVELS)
            SubstrGame.levels = {
                '2': get_pair_levels(constant.LEVELS),
                '3': get_triplet_levels(constant.LEVELS),
            }
