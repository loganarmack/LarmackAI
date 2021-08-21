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
        if len(self._deck) < const.NUM_CARDS:
            self._deck = self._starting_deck
            
        self._cards = set(sample(self._deck, const.NUM_CARDS))
        self._deck = self._deck - self._cards
        self._possible_answers = self._find_answers()

    def _check_answer(self, answer):
        correct = True
        reason = None

        # Check if answer is impossible, and there are no possible answers
        if answer.lower() == const.IMPOSSIBLE:
            is_answer = len(self._possible_answers) != 0
            if is_answer:
                correct = False
                reason = "It's not impossible."
            else:
                correct = True
        
        else:
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
            
        if not correct:
            random_answer = 'impossible' if len(self._possible_answers) == 0 else choice(self._possible_answers)
            reason += f"\nA possible answer for this was {random_answer}."

        return correct, reason

    async def _round_end(self, message):
        self._choose_cards()
        message += f"\nYour new cards are {self._cards}"
        await self._round_end_callback(message)

    async def submit(self, expression):
        correct, reason = self._check_answer(expression)

        if not correct:
            await self._wrong_answer_callback(reason)
            await self._round_end("")
        else:
            await self._round_end(f"Correct!")

    async def start(self, round_end_callback, wrong_answer_callback):
        self._reset()
        self._choose_cards()
        self._round_end_callback = round_end_callback
        self._wrong_answer_callback = wrong_answer_callback

        await round_end_callback(f"Your cards are {self._cards}")

    def _find_answers(self):
        #TODO: this doesn't find solutions of the form (a-b)(c-d)
        # will need to rethink this algorithm
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
                    break

        return answers

    async def stop(self):
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
