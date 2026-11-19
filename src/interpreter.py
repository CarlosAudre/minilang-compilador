"""Interpretador e tabela de símbolos da MiniLang (item e).

O interpretador percorre a AST (src/ast_nodes.py):
- `avaliar(expressao)` devolve um valor (int ou bool);
- `executar(comando)` muda o estado (tabela de símbolos) ou a saída.

Tipos da MiniLang: `int` e `bool`. As verificações semânticas são feitas
durante a execução, no momento em que cada nó é visitado.
"""
import sys
from dataclasses import dataclass

from src.ast_nodes import (
    Atribuicao, Bloco, Booleano, For, If, Numero, OpBinaria, Print, Programa,
    Variavel, While,
)
from src.lexer import LexerError, tokenizar
from src.parser import ParserError, parse

# Limite padrão de iterações de UM laço, para que um laço infinito não trave.
LIMITE_ITERACOES = 100_000


class SemanticError(Exception):
    """Erro semântico (variável indefinida, divisão por zero, tipo incompatível)."""

    def __init__(self, mensagem, linha=0):
        super().__init__(f"Erro semântico (linha {linha}): {mensagem}")
        self.linha = linha


class LimiteIteracoesError(SemanticError):
    """Laço passou do limite de iterações (provável laço infinito)."""


def nome_tipo(valor):
    """Nome do tipo MiniLang de um valor Python.

    Cuidado: em Python, bool é subclasse de int (True == 1). Por isso a
    comparação é com `type(...) is`, e não com isinstance.
    """
    return "bool" if type(valor) is bool else "int"


def formatar_valor(valor):
    """Como o print mostra um valor: booleanos em minúsculas."""
    if type(valor) is bool:
        return "true" if valor else "false"
    return str(valor)


# ---------- Tabela de símbolos ----------
@dataclass
class Simbolo:
    nome: str
    tipo: str    # "int" ou "bool", fixado na primeira atribuição
    valor: object
    linha: int   # linha da primeira atribuição (definição)


class TabelaSimbolos:
    """Tabela de símbolos de escopo único (global).

    Estrutura: dicionário nome -> Simbolo (tabela hash).
    Inserção e busca custam O(1) em média.
    A MiniLang não tem funções nem escopo aninhado, então um único
    dicionário basta: uma variável criada dentro de um bloco continua
    existindo depois dele.
    """

    def __init__(self):
        self._simbolos = {}

    def inserir(self, nome, valor, linha):
        """Define a variável ou atualiza o seu valor.

        Na primeira atribuição o tipo é fixado. Uma atribuição posterior
        com valor de outro tipo é erro de tipo incompatível.
        """
        tipo = nome_tipo(valor)
        simbolo = self._simbolos.get(nome)
        if simbolo is None:
            self._simbolos[nome] = Simbolo(nome, tipo, valor, linha)
            return
        if simbolo.tipo != tipo:
            raise SemanticError(
                f"tipo incompatível: variável '{nome}' é {simbolo.tipo} "
                f"(definida na linha {simbolo.linha}) e recebeu {tipo}", linha)
        simbolo.valor = valor

    def buscar(self, nome, linha):
        """Devolve o valor da variável; erro se ela não foi definida."""
        simbolo = self._simbolos.get(nome)
        if simbolo is None:
            raise SemanticError(f"variável '{nome}' não definida", linha)
        return simbolo.valor

    def __contains__(self, nome):
        return nome in self._simbolos

    def simbolo(self, nome):
        """Entrada completa da tabela (para testes e depuração)."""
        return self._simbolos[nome]

    def valores(self):
        """Cópia nome -> valor (para testes)."""
        return {n: s.valor for n, s in self._simbolos.items()}


# ---------- Interpretador ----------
ARITMETICOS = {"+", "-", "*", "/"}
RELACIONAIS = {"<", ">", "<=", ">="}
IGUALDADE = {"==", "!="}


class Interpretador:
    def __init__(self, escrever=print, limite_iteracoes=LIMITE_ITERACOES):
        self.tabela = TabelaSimbolos()
        self.escrever = escrever        # para onde vai a saída do print
        self.limite_iteracoes = limite_iteracoes

    # ---------- comandos ----------
    def executar(self, no):
        if isinstance(no, Programa):
            for comando in no.comandos:
                self.executar(comando)
        elif isinstance(no, Atribuicao):
            # Avalia primeiro, insere depois: em `x = x + 1;` o x da direita
            # precisa já existir.
            self.tabela.inserir(no.nome, self.avaliar(no.expressao), no.linha)
        elif isinstance(no, Print):
            self.escrever(formatar_valor(self.avaliar(no.expressao)))
        elif isinstance(no, Bloco):
            for comando in no.comandos:
                self.executar(comando)
        elif isinstance(no, If):
            if self.condicao(no.condicao, "if"):
                self.executar(no.entao)
            elif no.senao is not None:
                self.executar(no.senao)
        elif isinstance(no, While):
            iteracoes = 0
            while self.condicao(no.condicao, "while"):
                iteracoes = self.contar(iteracoes, no)
                self.executar(no.corpo)
        elif isinstance(no, For):
            self.executar(no.inicializacao)
            iteracoes = 0
            while self.condicao(no.condicao, "for"):
                iteracoes = self.contar(iteracoes, no)
                self.executar(no.corpo)
                self.executar(no.atualizacao)
        else:
            raise TypeError(f"nó desconhecido: {type(no).__name__}")

    def condicao(self, expr, comando):
        """Avalia a condição de if/while/for, que tem de ser bool."""
        valor = self.avaliar(expr)
        if type(valor) is not bool:
            raise SemanticError(
                f"a condição do {comando} deve ser booleana, mas é {nome_tipo(valor)}",
                expr.linha)
        return valor

    def contar(self, iteracoes, no):
        iteracoes += 1
        if iteracoes > self.limite_iteracoes:
            raise LimiteIteracoesError(
                f"laço passou do limite de {self.limite_iteracoes} iterações "
                f"(possível laço infinito)", no.linha)
        return iteracoes

    # ---------- expressões ----------
    def avaliar(self, no):
        if isinstance(no, (Numero, Booleano)):
            return no.valor
        if isinstance(no, Variavel):
            return self.tabela.buscar(no.nome, no.linha)
        if isinstance(no, OpBinaria):
            return self.operacao(no)
        raise TypeError(f"expressão desconhecida: {type(no).__name__}")

    def operacao(self, no):
        a = self.avaliar(no.esquerda)
        b = self.avaliar(no.direita)
        op = no.operador
        ta, tb = nome_tipo(a), nome_tipo(b)

        if op in ARITMETICOS or op in RELACIONAIS:
            if ta != "int" or tb != "int":
                raise SemanticError(
                    f"tipo incompatível: '{op}' exige int e int, recebeu {ta} e {tb}",
                    no.linha)
        elif ta != tb:  # == e !=
            raise SemanticError(
                f"tipo incompatível: '{op}' compara {ta} com {tb}", no.linha)

        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            if b == 0:
                raise SemanticError("divisão por zero", no.linha)
            return dividir(a, b)
        if op == "<":
            return a < b
        if op == ">":
            return a > b
        if op == "<=":
            return a <= b
        if op == ">=":
            return a >= b
        if op == "==":
            return a == b
        return a != b  # "!="


def dividir(a, b):
    """Divisão inteira truncada em direção a zero (como em C e Java).

    O `//` do Python arredonda para baixo: -7 // 2 == -4. Aqui -7 / 2 == -3.
    """
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b > 0) else -q


def executar(codigo: str, escrever=print, limite_iteracoes=LIMITE_ITERACOES):
    """Pipeline completo: lexer -> parser -> interpretador.

    Devolve a tabela de símbolos final (útil nos testes).
    """
    programa = parse(tokenizar(codigo))
    interpretador = Interpretador(escrever, limite_iteracoes)
    interpretador.executar(programa)
    return interpretador.tabela


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python -m src.interpreter <arquivo.ml>")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        codigo = f.read()
    try:
        executar(codigo)
    except (LexerError, ParserError, SemanticError) as erro:
        print(erro, file=sys.stderr)
        sys.exit(1)
