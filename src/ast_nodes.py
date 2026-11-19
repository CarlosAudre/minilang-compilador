"""Nós da árvore sintática abstrata (item d).

Cada classe é um tipo de nó. Os campos guardam só o que é necessário para
executar o programa; os símbolos que servem apenas para guiar a análise
sintática (parênteses, ";", "{", "}", palavras-chave) não viram nós.

Todo nó tem também o campo `linha` (linha do código-fonte onde o nó começa),
usado nas mensagens de erro semântico. Ele não entra na comparação (`==`):
duas árvores são iguais quando têm a mesma estrutura, independentemente de
onde estavam no arquivo.
"""
from dataclasses import dataclass, field, fields, is_dataclass
from typing import List, Optional, Union


@dataclass
class No:
    """Base de todos os nós."""
    linha: int = field(default=0, compare=False, repr=False, kw_only=True)


# ---------- Expressões (produzem um valor) ----------
@dataclass
class Numero(No):
    """Literal inteiro. Ex.: 42"""
    valor: int


@dataclass
class Booleano(No):
    """Literal booleano: true ou false."""
    valor: bool


@dataclass
class Variavel(No):
    """Uso de uma variável dentro de uma expressão. Ex.: x"""
    nome: str


@dataclass
class OpBinaria(No):
    """Operação com dois operandos. Ex.: 1 + 2, x < 10

    A precedência e a associatividade ficam na forma da árvore: a operação
    mais funda é avaliada primeiro.
    """
    operador: str          # "+", "-", "*", "/", "<", ">", "<=", ">=", "==", "!="
    esquerda: "Expressao"
    direita: "Expressao"


Expressao = Union[Numero, Booleano, Variavel, OpBinaria]


# ---------- Comandos (executam uma ação) ----------
@dataclass
class Atribuicao(No):
    """nome = expressao;"""
    nome: str
    expressao: Expressao


@dataclass
class Print(No):
    """print(expressao);"""
    expressao: Expressao


@dataclass
class Bloco(No):
    """{ comandos }"""
    comandos: List["Comando"]


@dataclass
class If(No):
    """if (condicao) entao [else senao]"""
    condicao: Expressao
    entao: Bloco
    senao: Optional[Bloco]  # None quando não há else


@dataclass
class While(No):
    """while (condicao) corpo"""
    condicao: Expressao
    corpo: Bloco


@dataclass
class For(No):
    """for (inicializacao; condicao; atualizacao) corpo"""
    inicializacao: Atribuicao
    condicao: Expressao
    atualizacao: Atribuicao
    corpo: Bloco


Comando = Union[Atribuicao, Print, Bloco, If, While, For]


@dataclass
class Programa(No):
    """Raiz da árvore: a sequência de comandos do arquivo."""
    comandos: List[Comando]


# ---------- Utilitário: imprime a árvore com indentação ----------
def _eh_no(v):
    return is_dataclass(v) or isinstance(v, list)


def _campos(no):
    """Campos estruturais do nó (sem `linha`)."""
    return [f for f in fields(no) if f.name != "linha"]


def formatar(no, nivel=0):
    """Devolve a árvore como texto indentado (útil para o relatório)."""
    pad = "  " * nivel
    if not is_dataclass(no):
        return f"{pad}{no!r}"
    simples = [f"{f.name}={getattr(no, f.name)!r}"
               for f in _campos(no) if not _eh_no(getattr(no, f.name))]
    linhas = [f"{pad}{type(no).__name__}({', '.join(simples)})"]
    for f in _campos(no):
        v = getattr(no, f.name)
        if is_dataclass(v):
            linhas.append(f"{pad}  {f.name}:")
            linhas.append(formatar(v, nivel + 2))
        elif isinstance(v, list):
            linhas.append(f"{pad}  {f.name}:")
            linhas.extend(formatar(x, nivel + 2) for x in v)
    return "\n".join(linhas)
