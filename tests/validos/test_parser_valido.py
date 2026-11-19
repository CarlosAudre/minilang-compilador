"""Testes válidos do parser. Resultado esperado: a AST correta é construída."""
from pathlib import Path

from src.ast_nodes import (
    Atribuicao, Bloco, Booleano, For, If, Numero, OpBinaria, Print, Programa,
    Variavel, While,
)
from src.lexer import tokenizar
from src.parser import parse

EXEMPLOS = Path(__file__).resolve().parents[2] / "exemplos"


def arvore(codigo):
    return parse(tokenizar(codigo))


def expressao(codigo):
    """AST da expressão de `x = <codigo>;`."""
    return arvore(f"x = {codigo};").comandos[0].expressao


def test_programa_vazio():
    assert arvore("") == Programa([])


def test_atribuicao_simples():
    assert arvore("x = 10;") == Programa([Atribuicao("x", Numero(10))])


def test_booleanos_e_variaveis():
    assert expressao("true") == Booleano(True)
    assert expressao("false") == Booleano(False)
    assert expressao("y") == Variavel("y")


def test_precedencia_multiplicacao_sobre_soma():
    # 1 + 2 * 3  ->  1 + (2 * 3)
    assert expressao("1 + 2 * 3") == OpBinaria(
        "+", Numero(1), OpBinaria("*", Numero(2), Numero(3)))


def test_parenteses_mudam_a_arvore():
    # (1 + 2) * 3  ->  (1 + 2) * 3
    assert expressao("(1 + 2) * 3") == OpBinaria(
        "*", OpBinaria("+", Numero(1), Numero(2)), Numero(3))


def test_arvores_de_1_mais_2_vezes_3_sao_diferentes():
    assert expressao("1 + 2 * 3") != expressao("(1 + 2) * 3")


def test_subtracao_associa_a_esquerda():
    # 10 - 4 - 3  ->  (10 - 4) - 3
    assert expressao("10 - 4 - 3") == OpBinaria(
        "-", OpBinaria("-", Numero(10), Numero(4)), Numero(3))


def test_divisao_associa_a_esquerda():
    # 8 / 2 / 2  ->  (8 / 2) / 2
    assert expressao("8 / 2 / 2") == OpBinaria(
        "/", OpBinaria("/", Numero(8), Numero(2)), Numero(2))


def test_comparacao_tem_precedencia_menor_que_aritmetica():
    # a + 1 < b * 2  ->  (a + 1) < (b * 2)
    assert expressao("a + 1 < b * 2") == OpBinaria(
        "<",
        OpBinaria("+", Variavel("a"), Numero(1)),
        OpBinaria("*", Variavel("b"), Numero(2)))


def test_todos_os_operadores_de_comparacao():
    for op in ["<", ">", "<=", ">=", "==", "!="]:
        assert expressao(f"a {op} b") == OpBinaria(op, Variavel("a"), Variavel("b"))


def test_print():
    assert arvore("print(x + 1);") == Programa(
        [Print(OpBinaria("+", Variavel("x"), Numero(1)))])


def test_if_sem_else():
    assert arvore("if (x > 0) { print(x); }") == Programa([
        If(OpBinaria(">", Variavel("x"), Numero(0)),
           Bloco([Print(Variavel("x"))]),
           None)])


def test_if_com_else():
    no = arvore("if (x) { y = 1; } else { y = 2; }").comandos[0]
    assert no.entao == Bloco([Atribuicao("y", Numero(1))])
    assert no.senao == Bloco([Atribuicao("y", Numero(2))])


def test_while():
    assert arvore("while (x > 0) { x = x - 1; }") == Programa([
        While(OpBinaria(">", Variavel("x"), Numero(0)),
              Bloco([Atribuicao("x", OpBinaria("-", Variavel("x"), Numero(1)))]))])


def test_for_com_as_tres_clausulas():
    no = arvore("for (i = 0; i < 5; i = i + 1) { soma = soma + i; }").comandos[0]
    assert isinstance(no, For)
    assert no.inicializacao == Atribuicao("i", Numero(0))
    assert no.condicao == OpBinaria("<", Variavel("i"), Numero(5))
    assert no.atualizacao == Atribuicao(
        "i", OpBinaria("+", Variavel("i"), Numero(1)))
    assert no.corpo == Bloco(
        [Atribuicao("soma", OpBinaria("+", Variavel("soma"), Variavel("i")))])


def test_lacos_aninhados():
    codigo = "while (a) { for (i = 0; i < 2; i = i + 1) { print(i); } }"
    externo = arvore(codigo).comandos[0]
    assert isinstance(externo.corpo.comandos[0], For)


def test_bloco_vazio_e_bloco_solto():
    assert arvore("{ }") == Programa([Bloco([])])
    assert arvore("while (a) { }").comandos[0].corpo == Bloco([])


def test_programa_valido_do_exemplo():
    codigo = (EXEMPLOS / "programa_valido.ml").read_text(encoding="utf-8")
    programa = arvore(codigo)
    tipos = [type(c).__name__ for c in programa.comandos]
    assert tipos == ["Atribuicao", "Atribuicao", "While",
                     "Atribuicao", "For", "If"]
