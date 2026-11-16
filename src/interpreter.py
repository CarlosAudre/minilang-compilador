"""Interpretador e tabela de símbolos da MiniLang (item e)."""
import sys


class SemanticError(Exception):
    """Erro semântico (variável indefinida, divisão por zero, tipo incompatível)."""


# TODO: TabelaSimbolos (inserir, buscar)
# TODO: Interpretador que percorre a AST


def executar(codigo: str) -> None:
    """Pipeline completo: lexer -> parser -> interpretador."""
    raise NotImplementedError


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python -m src.interpreter <arquivo.ml>")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        executar(f.read())