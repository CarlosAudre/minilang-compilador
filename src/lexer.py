"""Analisador léxico da MiniLang (item b)."""


class LexerError(Exception):
    """Erro léxico: caractere ou lexema que não pertence à linguagem."""


# TODO: definir TokenType (palavras reservadas, operadores, literais, delimitadores)
# TODO: definir Token (tipo, lexema, linha, coluna)
# TODO: implementar o lexer conforme o autômato de docs/gramatica.md


def tokenizar(codigo: str) -> list:
    """Recebe o código-fonte e devolve a lista de tokens."""
    raise NotImplementedError