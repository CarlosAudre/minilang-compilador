"""Parser descendente recursivo da MiniLang (item c)."""


class ParserError(Exception):
    """Erro sintático."""


# TODO: uma função por não-terminal da gramática (docs/gramatica.md)


def parse(tokens: list):
    """Recebe a lista de tokens e devolve a AST (Programa)."""
    raise NotImplementedError