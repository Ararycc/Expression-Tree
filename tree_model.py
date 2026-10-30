"""Tree construction, traversal and arithmetic evaluation for Tree Studio."""
from collections import deque
import ast
import operator
import re


class Node:
    __slots__ = ('value', 'left', 'right')

    def __init__(self, value, left=None, right=None):
        self.value = str(value)
        self.left = left
        self.right = right


def number(value):
    """Convert a displayed numeric token to float, accepting integer forms."""
    try:
        return float(str(value))
    except (TypeError, ValueError):
        raise ValueError(f"'{value}' is not a valid number.")


def format_number(value):
    if abs(value) < 1e-12:
        value = 0
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.10g}"


def _numeric_token(token):
    try:
        v = float(token)
        return format_number(v)
    except ValueError:
        raise ValueError(f"'{token}' is not a valid number.")


def _split_values(text):
    values = [part for part in re.split(r'[\s,]+', text.strip()) if part]
    if not values:
        raise ValueError('Enter at least one value to build a tree.')
    return values


def build_values(text, kind='Numerical', layout='Binary search tree'):
    values = _split_values(text)
    if len(values) > 250:
        raise ValueError('Please use 250 values or fewer.')
    if kind == 'Numerical':
        values = [_numeric_token(v) for v in values]
    else:
        if any(not v for v in values):
            raise ValueError('Alphabetical values cannot be empty.')
        values = [v.strip() for v in values]

    if layout == 'Level-filled tree':
        nodes = [Node(v) for v in values]
        for i, node in enumerate(nodes):
            left, right = 2 * i + 1, 2 * i + 2
            if left < len(nodes): node.left = nodes[left]
            if right < len(nodes): node.right = nodes[right]
        return nodes[0]

    # A binary search tree; duplicate values are ignored to keep ordering unique.
    root = Node(values[0])
    keys = {values[0] if kind != 'Numerical' else number(values[0])}
    for value in values[1:]:
        key = value if kind != 'Numerical' else number(value)
        if key in keys:
            continue
        keys.add(key)
        node = root
        while True:
            node_key = node.value if kind != 'Numerical' else number(node.value)
            goes_left = key < node_key if kind == 'Numerical' else key.casefold() < node_key.casefold()
            if goes_left:
                if node.left is None:
                    node.left = Node(value); break
                node = node.left
            else:
                if node.right is None:
                    node.right = Node(value); break
                node = node.right
    return root


OPS = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv, '^': operator.pow}
PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}


def _tokenize_infix(text):
    # Accept decimals, integers, operators and parentheses. Unary minus is folded into numbers where possible.
    raw = re.findall(r'\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?|[()+\-*/^]', text.replace('−', '-'))
    compact = re.sub(r'\s+', '', text.replace('−', '-'))
    if ''.join(raw) != compact:
        raise ValueError('Infix expression contains an unsupported character or token.')
    if not raw:
        raise ValueError('Enter an arithmetic expression.')
    tokens = []
    for token in raw:
        if token == '-' and (not tokens or tokens[-1] in OPS or tokens[-1] == '('):
            tokens.append('u-')
        else:
            tokens.append(token)
    # Convert unary minus before a numeric token to a signed number.
    normalized = []
    i = 0
    while i < len(tokens):
        if tokens[i] == 'u-' and i + 1 < len(tokens) and _is_num(tokens[i+1]):
            normalized.append('-' + tokens[i+1]); i += 2
        else:
            normalized.append(tokens[i]); i += 1
    return normalized


def _is_num(token):
    try: float(token); return True
    except (ValueError, TypeError): return False


def _infix_to_postfix(tokens):
    output, stack = [], []
    for token in tokens:
        if _is_num(token):
            output.append(token)
        elif token in OPS:
            while stack and stack[-1] in OPS and (
                PRECEDENCE[stack[-1]] > PRECEDENCE[token] or
                (PRECEDENCE[stack[-1]] == PRECEDENCE[token] and token != '^')
            ):
                output.append(stack.pop())
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if not stack:
                raise ValueError('Mismatched parentheses in infix expression.')
            stack.pop()
        else:
            raise ValueError(f"Unsupported token '{token}'.")
    if any(t in ('(', ')') for t in stack):
        raise ValueError('Mismatched parentheses in infix expression.')
    output.extend(reversed(stack))
    return output


def _make_from_postfix(tokens):
    stack = []
    for token in tokens:
        if token in OPS:
            if len(stack) < 2:
                raise ValueError(f"Operator '{token}' needs two operands.")
            right, left = stack.pop(), stack.pop()
            stack.append(Node(token, left, right))
        elif _is_num(token):
            stack.append(Node(format_number(float(token))))
        else:
            raise ValueError(f"Invalid operand '{token}'. Use numbers and +, -, *, /, ^.")
    if len(stack) != 1:
        raise ValueError('Expression is incomplete or has too many operands.')
    return stack[0]


def build_expression(text, notation='Infix'):
    if not text.strip():
        raise ValueError('Enter an arithmetic expression.')
    if notation == 'Infix':
        tokens = _infix_to_postfix(_tokenize_infix(text))
    else:
        tokens = text.split()
        if not tokens:
            raise ValueError('Enter an arithmetic expression.')
        if notation == 'Prefix':
            stack = []
            for token in reversed(tokens):
                if token in OPS:
                    if len(stack) < 2:
                        raise ValueError(f"Operator '{token}' needs two operands.")
                    left, right = stack.pop(), stack.pop()
                    stack.append(Node(token, left, right))
                elif _is_num(token):
                    stack.append(Node(format_number(float(token))))
                else:
                    raise ValueError(f"Invalid token '{token}'. Separate tokens with spaces.")
            if len(stack) != 1:
                raise ValueError('Expression is incomplete or has too many operands.')
            return stack[0]
        if notation != 'Postfix':
            raise ValueError(f"Unknown notation '{notation}'.")
    return _make_from_postfix(tokens)


def traversals(root):
    result = {'Preorder': [], 'Inorder': [], 'Postorder': [], 'Level order': []}
    def pre(node):
        if node:
            result['Preorder'].append(node); pre(node.left); pre(node.right)
    def ino(node):
        if node:
            ino(node.left); result['Inorder'].append(node); ino(node.right)
    def post(node):
        if node:
            post(node.left); post(node.right); result['Postorder'].append(node)
    pre(root); ino(root); post(root)
    if root:
        queue = deque([root])
        while queue:
            node = queue.popleft(); result['Level order'].append(node)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
    return result


def evaluate(root):
    if root is None:
        raise ValueError('Cannot evaluate an empty tree.')
    if root.value in OPS:
        if root.left is None or root.right is None:
            raise ValueError(f"Operator '{root.value}' needs two operands.")
        left, right = evaluate(root.left), evaluate(root.right)
        try:
            value = OPS[root.value](left, right)
        except ZeroDivisionError:
            raise ValueError('Cannot divide by zero.')
        except (OverflowError, ValueError) as exc:
            raise ValueError(f'Expression cannot be evaluated: {exc}')
        if isinstance(value, complex) or not (-1e300 < value < 1e300):
            raise ValueError('Expression result is outside the supported numeric range.')
        return float(value)
    return number(root.value)
