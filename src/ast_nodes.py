"""Nós da árvore sintática abstrata (item d)."""
from dataclasses import dataclass, fields, is_dataclass
from typing import List, Optional, Union


# ---------- Expressões ----------
@dataclass
class Numero:
    valor: int


@dataclass
class Booleano:
    valor: bool


@dataclass
class Variavel:
    nome: str


@dataclass
class OpBinaria:
    operador: str          # "+", "-", "*", "/", "<", ">", "<=", ">=", "==", "!="
    esquerda: "Expressao"
    direita: "Expressao"


Expressao = Union[Numero, Booleano, Variavel, OpBinaria]


# ---------- Comandos ----------
@dataclass
class Atribuicao:
    nome: str
    expressao: Expressao


@dataclass
class Print:
    expressao: Expressao


@dataclass
class Bloco:
    comandos: List["Comando"]


@dataclass
class If:
    condicao: Expressao
    entao: Bloco
    senao: Optional[Bloco]  # None quando não há else


@dataclass
class While:
    condicao: Expressao
    corpo: Bloco


@dataclass
class For:
    inicializacao: Atribuicao
    condicao: Expressao
    atualizacao: Atribuicao
    corpo: Bloco


Comando = Union[Atribuicao, Print, Bloco, If, While, For]


@dataclass
class Programa:
    comandos: List[Comando]


# ---------- Utilitário: imprime a árvore com indentação ----------
def _eh_no(v):
    return is_dataclass(v) or isinstance(v, list)


def formatar(no, nivel=0):
    """Devolve a árvore como texto indentado (útil para o relatório)."""
    pad = "  " * nivel
    if not is_dataclass(no):
        return f"{pad}{no!r}"
    simples = [f"{f.name}={getattr(no, f.name)!r}"
               for f in fields(no) if not _eh_no(getattr(no, f.name))]
    linhas = [f"{pad}{type(no).__name__}({', '.join(simples)})"]
    for f in fields(no):
        v = getattr(no, f.name)
        if is_dataclass(v):
            linhas.append(f"{pad}  {f.name}:")
            linhas.append(formatar(v, nivel + 2))
        elif isinstance(v, list):
            linhas.append(f"{pad}  {f.name}:")
            linhas.extend(formatar(x, nivel + 2) for x in v)
    return "\n".join(linhas)
