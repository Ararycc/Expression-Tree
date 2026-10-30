"""Example input generator used by Tree Studio."""
import random

_NUMERIC_EXAMPLES = [
    '8 3 10 1 6 14 4 7 13',
    '42, 21, 64, 9, 32, 50, 78, 5, 12, 27, 36',
    '15 8 23 4 11 19 31 2 6 9 13',
    '12 5 18 2 9 15 22 7 10 13 17',
]
_ALPHA_EXAMPLES = [
    'maple oak pine birch cedar willow ash elm',
    'mango apple banana orange grape lemon cherry',
    'fern moss ivy rose lotus daisy orchid tulip',
]
_EXPR_EXAMPLES = {
    'Infix': ['( 8 + 2 ) * ( 9 - 4 )', '12 / ( 2 + 1 ) + 7 * 2', '( 3 + 5 ) ^ 2 - 4 * 6', '18 / 3 + 4 * 2'],
    'Prefix': ['* + 8 2 - 9 4', '+ / 12 + 2 1 * 7 2', '- ^ + 3 5 2 * 4 6'],
    'Postfix': ['8 2 + 9 4 - *', '12 2 1 + / 7 2 * +', '3 5 + 2 ^ 4 6 * -'],
}


def random_example(kind='Numerical', expression=False, notation='Infix', previous=''):
    if expression:
        choices = _EXPR_EXAMPLES.get(notation, _EXPR_EXAMPLES['Infix'])
    elif kind == 'Alphabetical':
        choices = _ALPHA_EXAMPLES
    else:
        choices = _NUMERIC_EXAMPLES
    available = [item for item in choices if item != previous]
    return random.choice(available or choices)
