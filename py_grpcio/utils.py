from re import findall, sub
from types import FunctionType


def is_method(method: FunctionType) -> bool:
    return isinstance(method, FunctionType) and not (method.__name__.startswith('__') or method.__name__.endswith('__'))


def camel_to_snake(string: str) -> str:
    words: list[str] = findall(pattern=r'[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+', string=string)
    return '_'.join(map(lambda word: word.lower(), words))


def snake_to_camel(string: str) -> str:
    return sub(pattern=r'_([a-zA-Z])', repl=lambda match: match.group(1).upper(), string=string.title())
