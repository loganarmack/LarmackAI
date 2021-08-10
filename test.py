from twenty_four.game import TwentyFourGame
from twenty_four.parse_expression import parse_expression

game = TwentyFourGame()

game.start()
print(game._cards)
print(game.submit_answer(input("Enter an expression: ")))
