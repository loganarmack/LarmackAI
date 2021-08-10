from random import sample, choice
from twenty_four.parse_expression import parse_expression, InvalidExpressionException
import twenty_four.constant as const
import re
from itertools import permutations
from base_game import BaseGame

class TwentyFourGame(BaseGame):
    _starting_deck = []
    _operator_permutations = []

    def __init__(self):
        if not TwentyFourGame._starting_deck:
            TwentyFourGame._starting_deck = set([(num + 1, suit) for suit in const.SUITS for num in range(const.MAX_NUM)])
        if not TwentyFourGame._operator_permutations:
            TwentyFourGame._operator_permutations = TwentyFourGame._generate_operator_permutations(const.NUM_CARDS - 1)
        self._reset()

    def _reset(self):
        self._deck = self._starting_deck.copy()
        self._choose_cards()

    def _choose_cards(self):
        self._cards = set(sample(self._deck, const.NUM_CARDS))
        self._deck = self._deck - self._cards

    def submit_answer(self, answer):
        correct = True
        reason = None

        # Check that answer contains the right amount of numbers
        answer_nums = re.findall(r'\d+', answer)
        if len(answer_nums) != const.NUM_CARDS:
            correct = False
            reason = "Your answer must use each card exactly once."

        # Check that each number is from the cards
        else:
            for card in self._cards:
                if str(card[0]) not in answer_nums:
                    correct = False
                    reason = "Your answer must use each card exactly once."
                    break
                else:
                    answer_nums.remove(str(card[0]))
        
        # If numbers are correct, check that expression is valid and sums to 24
        if correct: 
            try:
                if parse_expression(answer) != const.TARGET_SUM:
                    correct = False
                    reason = f"Your answer doesn't equal {const.TARGET_SUM}"
            except InvalidExpressionException as e:
                correct = False
                reason = "That's not a valid expression!"

        possible_answers = self._find_answers()
        random_answer = 'impossible' if len(possible_answers) == 0 else choice(possible_answers)

        return correct, reason, random_answer

    def start(self, round_end_callback, wrong_answer_callback):
        self._reset()
        self._choose_cards()

    def _find_answers(self):
        answers = []
        # Check all possible permutations of cards
        for permutation in permutations([card[0] for card in self._cards]):
            # Check all permutations of operators
            for op_permutation in self._operator_permutations:
                val = permutation[0]
                for i in range(len(op_permutation)):
                    operation = self._symbol_to_operation(op_permutation[i])
                    val = operation(val, permutation[i+1])

                if val == const.TARGET_SUM:
                    answer = ""
                    prev_op = None
                    for i in range(len(op_permutation)):
                        if op_permutation[i] in '*/' and prev_op and prev_op in '+-':
                            answer = f"({answer}{permutation[i]}) {op_permutation[i]} "
                        else:
                            answer += f"{permutation[i]} {op_permutation[i]} "
                        prev_op = op_permutation[i]
                    answer += f"{permutation[-1]}"

                    answers.append(answer)
                    print(val, answer)
                    break

        return answers

    def stop(self):
        pass
        
            
    @staticmethod
    def _generate_operator_permutations(remaining_loops):
        permutations = []
        operators = '+-*/'
        if remaining_loops == 1:
            for op in operators:
                permutations.append(op)

            return permutations
        
        else: 
            for op in operators:
                for perm in TwentyFourGame._generate_operator_permutations(remaining_loops - 1):
                    permutations.append(op + perm)

            return permutations

    @staticmethod
    def _symbol_to_operation(symb):
        if symb == '+':
            return lambda a,b: a + b
        elif symb == '-':
            return lambda a,b: a - b
        elif symb == '*':
            return lambda a,b: a * b
        elif symb == '/':
            return lambda a,b: a / b
