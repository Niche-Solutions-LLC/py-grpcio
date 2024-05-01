class MethodSignatureException(Exception):
    def __init__(self: 'MethodSignatureException', text: str):
        self.text: str = text

    def __str__(self: 'MethodSignatureException') -> str:
        return f'{self.__class__.__name__} | {self.text}'

    __repr__ = __str__
