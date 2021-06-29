from word_counter import get_pair_levels, get_triplet_levels, export_levels
from nltk.corpus import words
from random import randint, choice
import constant
import json
from pathlib import Path
from math import floor
from pprint import pprint


class Game:
    word_list = words.words()
    levels = {}

    def __init__(self):
        try:
            f = open("levels.json", "r")
            Game.levels = json.load(f)
        except FileNotFoundError:
            export_levels(constant.LEVELS)
            Game.levels = {
                '2': get_pair_levels(constant.LEVELS),
                '3': get_triplet_levels(constant.LEVELS),
            }
        self.__reset()

    def choose_substr(self):
        self.substr_level = self.weighted_random(self.level_weights)
        self.substr_length = self.weighted_random(self.length_weights)
        self.substr = choice(Game.levels[str(self.substr_length)][self.substr_level])

    @staticmethod
    def weighted_random(weights):
        total = sum(weights[level] for level in weights)
        r = randint(1, total)
        for level in weights:
            r -= weights[level]
            if r <= 0:
                return level

    def start(self):
        self.__reset()

        while self.lives > 0:
            self.choose_substr()

            user_word = input(
                "Enter a word containing %s (level = %s):\n"
                % (self.substr, self.substr_level)
            ).lower()

            if (
                user_word
                and user_word not in self.used_words
                and user_word in Game.word_list
                and self.substr in user_word
            ):
                self.score_word(user_word)
                print("New score:", self.points)
                self.used_words.append(user_word)
                self.__increment_weights()

            elif user_word in self.used_words:
                print("You've already used this word!")
                self.lives -= 1

            else:
                print("Invalid word")
                self.lives -= 1

        print("Game over. Your score is", self.points)

    def score_word(self, word):
        base = 100  # default for valid word
        base += 10 * len(word)  # bonus for making longer words
        if word[:2] != self.substr and word[:3] != self.substr:
            base += 50  # bonus for not starting word with substring
        bonus_mult = self.substr_level / 4.0  # substr difficulty multiplier
        bonus_mult += (self.substr_length - 2) / 2.0  # substr length multiplier
        self.points += base * (bonus_mult + 1)

    def __increment_weights(self):
        for level in self.level_weights:
            if level != constant.LEVELS - 1:
                self.level_weights[level + 1] += floor(self.level_weights[level] / 10.0)
                self.level_weights[level] = floor(self.level_weights[level] * 9 / 10.0)

        self.length_weights[3] += floor(self.length_weights[2] / 10.0)
        self.length_weights[2] = floor(self.length_weights[2] * 9 / 10.0)

    def __reset(self):
        self.points = 0
        self.lives = 3
        self.used_words = []
        self.level_weights = {0: 1000, 1: 0, 2: 0, 3: 0, 4: 0}
        self.length_weights = {2: 100, 3: 0}
        self.substr = "ng"
        self.substr_level = 0
        self.substr_length = 2


game = Game()
game.start()
