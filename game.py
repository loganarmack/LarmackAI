from word_counter import get_pair_levels, get_triplet_levels, export_levels, load_words
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
            try:
                f = open("levels.json", "r")
                SubstrGame.levels = json.load(f)
            except FileNotFoundError:
                export_levels(constant.LEVELS)
                SubstrGame.levels = {
                    '2': get_pair_levels(constant.LEVELS),
                    '3': get_triplet_levels(constant.LEVELS),
                }

        self.__reset()

    def __reset(self):
        self.points = 0
        self.lives = 3
        self.used_words = set()
        self.used_letters = set()
        self.level_weights = {0: 1000, 1: 0, 2: 0, 3: 0, 4: 0}
        self.length_weights = {2: 100, 3: 0}
        self.substr = "ng"
        self.possible_word = "ping"
        self.substr_level = 0
        self.substr_length = 2
        self.guess_time = 15
        self.timer = None
        self.timeout_callback = None

    def __choose_substr(self):
        self.substr_level = self.weighted_random(self.level_weights)
        self.substr_length = self.weighted_random(self.length_weights)
        self.substr = choice(list(SubstrGame.levels[str(self.substr_length)][self.substr_level].keys()))
        self.possible_word = choice(SubstrGame.levels[str(self.substr_length)][self.substr_level][self.substr])

    def __check_word(self, user_word): 
        correct = True
        reason = None
        if not user_word:
            correct = False
            reason = "You didn't enter a word!"

        elif user_word in self.used_words:
            correct = False
            reason = "You've already used that word!"

        elif self.substr not in user_word:
            correct = False
            reason = f"Your word doesn't use {self.substr}!"

        elif user_word not in SubstrGame.levels[str(self.substr_length)][self.substr_level][self.substr]:
            correct = False
            reason = "That's not a real word!"
        
        return [correct, reason]

    def __score_word(self, word):
        base = 100  # default for valid word
        base += 10 * len(word)  # bonus for making longer words
        if word[:2] != self.substr and word[:3] != self.substr:
            base += 20  # bonus for not starting word with substring
        bonus_mult = self.substr_level / 4.0  # substr difficulty multiplier
        bonus_mult += (self.substr_length - 2) / 2.0  # substr length multiplier
        total = base * (bonus_mult + 1)
        self.points += total
        return total

    def __increment_weights(self):
        for level in self.level_weights:
            if level != constant.LEVELS - 1:
                self.level_weights[level + 1] += floor(self.level_weights[level] / 10.0)
                self.level_weights[level] = floor(self.level_weights[level] * 9 / 10.0)

        self.length_weights[3] += floor(self.length_weights[2] / 10.0)
        self.length_weights[2] = floor(self.length_weights[2] * 9 / 10.0)
        #self.guess_time = max(constant.MIN_TIME_SECONDS, self.guess_time * 9 / 10.0)

    def __update_used_letters(self, user_word):
        for letter in user_word.lower():
            self.used_letters.add(letter)
        
        if len(self.used_letters) == 26:
            self.used_letters = set()

            if self.lives < constant.MAX_LIVES:
                self.lives += 1
                print("You've gained a life from using each letter at least once!")
                print(f"New lives: {self.lives}")

    def get_remaining_letters(self):
        return sorted(SubstrGame.letter_set - self.used_letters)

    def __next_round(self):
        if self.lives <= 0:
            return "Game Over"
        else:
            self.timer = Timer(self.guess_time, self.__on_timeout)
            self.__choose_substr()
            return self.substr

    async def __on_timeout(self):
        self.lives -= 1
        result = f"You're out of time! \nA possible word for this was {self.possible_word}"
        if self.lives > 0:
            self.__choose_substr()
            await self.timeout_callback(result, self.substr)
            self.timer = Timer(self.guess_time, self.__on_timeout)
        else:
            await self.timeout_callback(result, "Game Over")

    def submit_word(self, user_word):
        if self.timer:
            self.timer.cancel()

        result = ''

        correct, reason = self.__check_word(user_word)
        if correct:
            word_value = self.__score_word(user_word)
            self.__increment_weights()
            self.used_words.add(user_word)
            self.__update_used_letters(user_word)

            result = f"Nice job! You earned {word_value} points."
        
        else:
            self.lives -= 1

            result = reason + f"\nA possible word for this was {self.possible_word}"

        return result, self.__next_round()

    def start(self, timeout_callback):
        self.__reset()
        self.timeout_callback = timeout_callback

        self.__next_round()
        return self.substr

    def game_over(self):
        return self.lives <= 0      

    @staticmethod
    def weighted_random(weights):
        total = sum(weights[level] for level in weights)
        r = randint(1, total)
        for level in weights:
            r -= weights[level]
            if r <= 0:
                return level
