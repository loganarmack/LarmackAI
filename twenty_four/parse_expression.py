import twenty_four.constant as const

class InvalidExpressionException(Exception):
    # Raised when a mathematical expression is invalid
    def __init__(self, reason, expression):
        self.reason = reason
        self.expression = expression
        super().__init__(f"Invalid expression: {expression}")


def parse_expression(expression): #can't use eval since string isn't trusted
    # return number value of expression
    # throw InvalidExpressionException if expression is not valid

    # trim spaces
    expression = expression.replace(' ', '')

    add = lambda a,b: a + b
    sub = lambda a,b: a - b
    mul = lambda a,b: a * b
    div = lambda a,b: a / b

    negative_op = False
    seen_two_operators = False
    curr_operand = None
    operands = []
    operators = []
    open_bracket = None
    capture_group = ''

    for char in expression:
        if char not in const.VALID_CHARS:
            raise InvalidExpressionException("Invalid character in expression", expression)

        elif char in ')]}' and char == _return_closing_bracket(open_bracket): # close bracket
            curr_operand = parse_expression(capture_group)
            open_bracket = None
            capture_group = ''

        elif open_bracket:
            capture_group += char
        
        elif char in '([{': # open bracket
            if curr_operand:
                operators.append(mul)
                operands.append(curr_operand)
                curr_operand = None
            open_bracket = char
        
        elif char.isdigit():
            if curr_operand is None:
                curr_operand = int(char)

            else:
                curr_operand = curr_operand * 10 + int(char)

        elif char in '*/+-':
            if curr_operand is None:
                if char in '*/':
                    raise InvalidExpressionException("*/ without preceding operand", expression)
                elif char in '+=':
                    if seen_two_operators:
                        raise InvalidExpressionException("More than two +- operators in a row", expression)

                    negative_op = char == '-'
                    seen_two_operators = True # can't have more than two +/- operators in a row
                    continue
            
            if char == '+':
                operators.append(add)
            elif char == '-':
                operators.append(sub)
            elif char == '*':
                operators.append(mul)
            elif char == '/':
                operators.append(div)

            operands.append(curr_operand)
            curr_operand = None
            negative_op = False
            seen_two_operators = False
    
    if open_bracket:
        raise InvalidExpressionException("Unclosed bracket", expression)
    elif curr_operand is None:
        raise InvalidExpressionException("Trailing operator", expression)
    else:
        operands.append(curr_operand)

    for i in range(len(operators) - 1, -1, -1):
        #resolve all mult/div first
        if operators[i] == mul or operators[i] == div:
            if operators[i] == div and operands[i] == 0:
                raise InvalidExpressionException("Division by zero", expression)

            val = operators[i](operands[i], operands[i+1])
            operands[i] = val
            operands.pop(i+1)
            operators.pop(i)

    for i in range(len(operators)):
        operands[0] = operators[i](operands[0], operands[i+1])
    
    return operands[0]

def _return_closing_bracket(open_bracket):
    if open_bracket == '(':
        return ')'
    elif open_bracket == '[':
        return ']'
    elif open_bracket == '{':
        return '}'
    else:
        raise Exception("Invalid bracket")
