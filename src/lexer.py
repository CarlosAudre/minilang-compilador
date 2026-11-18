"""Analisador léxico da MiniLang (item b).

O lexer é um autômato finito escrito à mão: cada ramo do `if/elif` do laço
principal corresponde a um estado/transição da tabela em docs/gramatica.md.
"""
from dataclasses import dataclass


class LexerError(Exception):
    """Erro léxico: caractere ou lexema que não pertence à linguagem."""

    def __init__(self, mensagem, linha, coluna):
        super().__init__(f"Erro léxico (linha {linha}, coluna {coluna}): {mensagem}")
        self.linha = linha
        self.coluna = coluna


@dataclass
class Token:
    tipo: str      # classe do token, ex.: "T_num"
    valor: object  # lexema guardado só nas classes CA (T_num, T_id); senão None
    linha: int
    coluna: int


# Palavras reservadas: casam com o padrão de T_id, mas têm classe própria.
PALAVRAS_RESERVADAS = {
    "true": "T_true", "false": "T_false", "while": "T_while", "for": "T_for",
    "if": "T_if", "else": "T_else", "print": "T_print",
}

# Símbolos de um caractere só, sem ambiguidade.
SIMBOLOS = {
    "+": "T_mais", "-": "T_menos", "*": "T_mult",
    "(": "T_apar", ")": "T_fpar", "{": "T_ach", "}": "T_fch", ";": "T_ptvg",
}

# Símbolos que podem ganhar um "=" depois: (sem "=", com "=").
COM_IGUAL = {
    "<": ("T_menor", "T_menorig"),
    ">": ("T_maior", "T_maiorig"),
    "=": ("T_atrib", "T_igual"),
}


def eh_digito(c):
    return "0" <= c <= "9"


def eh_letra(c):
    return "a" <= c <= "z" or "A" <= c <= "Z"


def tokenizar(codigo: str) -> list:
    """Recebe o código-fonte e devolve a lista de tokens."""
    tokens = []
    n = len(codigo)
    i, linha, coluna = 0, 1, 1

    def avancar():
        """Consome um caractere e atualiza linha e coluna."""
        nonlocal i, linha, coluna
        c = codigo[i]
        i += 1
        if c == "\n":
            linha += 1
            coluna = 1
        else:
            coluna += 1

    while i < n:                                   # estado inicial q0
        c = codigo[i]
        l0, c0 = linha, coluna                     # posição de início do lexema

        if c in " \t\r\n":                         # espaço: descartado
            avancar()

        elif eh_digito(c):                         # q0 -> q1 (T_num)
            inicio = i
            while i < n and eh_digito(codigo[i]):
                avancar()
            if i < n and eh_letra(codigo[i]):      # q1 + letra -> erro (ex.: 1x)
                raise LexerError(
                    f"número seguido de letra: '{codigo[inicio:i + 1]}'", l0, c0)
            tokens.append(Token("T_num", int(codigo[inicio:i]), l0, c0))

        elif eh_letra(c):                          # q0 -> q2 (T_id)
            inicio = i
            while i < n and (eh_letra(codigo[i]) or eh_digito(codigo[i])):
                avancar()
            lexema = codigo[inicio:i]
            tipo = PALAVRAS_RESERVADAS.get(lexema, "T_id")
            valor = lexema if tipo == "T_id" else None
            tokens.append(Token(tipo, valor, l0, c0))

        elif c == "/":                             # q0 -> q_barra
            prox = codigo[i + 1] if i + 1 < n else ""
            if prox == "/":                        # comentário de linha
                while i < n and codigo[i] != "\n":
                    avancar()
            elif prox == "*":                      # comentário de bloco
                avancar()
                avancar()
                fechado = False
                while i < n:
                    if codigo[i] == "*" and i + 1 < n and codigo[i + 1] == "/":
                        avancar()
                        avancar()
                        fechado = True
                        break
                    avancar()
                if not fechado:                    # chegou ao fim sem "*/"
                    raise LexerError("comentário de bloco não fechado", l0, c0)
            else:                                  # divisão
                avancar()
                tokens.append(Token("T_div", None, l0, c0))

        elif c in COM_IGUAL:                       # <, >, = (e <=, >=, ==)
            avancar()
            simples, composto = COM_IGUAL[c]
            if i < n and codigo[i] == "=":
                avancar()
                tokens.append(Token(composto, None, l0, c0))
            else:
                tokens.append(Token(simples, None, l0, c0))

        elif c == "!":                             # só existe como "!="
            avancar()
            if i < n and codigo[i] == "=":
                avancar()
                tokens.append(Token("T_dif", None, l0, c0))
            else:
                raise LexerError("'!' deve ser seguido de '='", l0, c0)

        elif c in SIMBOLOS:                        # ( ) { } ; + - *
            avancar()
            tokens.append(Token(SIMBOLOS[c], None, l0, c0))

        else:                                      # nenhum estado reconhece
            raise LexerError(f"caractere inválido: {c!r}", l0, c0)

    return tokens


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python -m src.lexer <arquivo.ml>")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        for t in tokenizar(f.read()):
            print(t.tipo, "" if t.valor is None else t.valor)
