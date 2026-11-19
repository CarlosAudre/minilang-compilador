"""Testes inválidos do parser.

Resultado esperado: toda entrada abaixo levanta ParserError (erro sintático),
com linha e coluna do primeiro token que não pertence à gramática. Os tokens
são todos válidos; o que falha é a ordem deles em relação às regras da EBNF.
"""
from pathlib import Path

import pytest

from src.lexer import tokenizar
from src.parser import ParserError, parse

EXEMPLOS = Path(__file__).resolve().parents[2] / "exemplos"


def arvore(codigo):
    return parse(tokenizar(codigo))


def test_laco_for_mal_formado_sem_atualizacao():
    # for exige três cláusulas: atribuicao ";" expressao ";" atribuicao
    with pytest.raises(ParserError) as erro:
        arvore("for (i = 0; i < 10) { print(i); }")
    assert "esperado ';'" in str(erro.value)
    assert (erro.value.linha, erro.value.coluna) == (1, 19)


def test_exemplo_programa_invalido_do_enunciado():
    codigo = (EXEMPLOS / "programa_invalido.ml").read_text(encoding="utf-8")
    with pytest.raises(ParserError):
        arvore(codigo)


@pytest.mark.parametrize("codigo", [
    "for (i = 0; ; i = i + 1) { }",             # for sem condição
    "for (i = 0; i < 3; i = i + 1) print(i);",  # for sem bloco
    "for i = 0; i < 3; i = i + 1 { }",          # for sem parênteses
    "for (0; i < 3; i = i + 1) { }",            # inicialização não é atribuição
])
def test_outros_lacos_for_mal_formados(codigo):
    with pytest.raises(ParserError):
        arvore(codigo)


@pytest.mark.parametrize("codigo", [
    "while (x) x = 1;",        # while sem bloco
    "while x { }",             # while sem parênteses
    "while () { }",            # while sem condição
    "while (x) { x = 1;",      # bloco não fechado
])
def test_while_mal_formado(codigo):
    with pytest.raises(ParserError):
        arvore(codigo)


@pytest.mark.parametrize("codigo", [
    "x = (1 + ;",              # operando faltando e parêntese aberto
    "x = 1 + ;",               # operando faltando
    "x = (1 + 2;",             # parêntese não fechado
    "x = 1 + 2);",             # parêntese a mais
    "x = ;",                   # atribuição sem expressão
    "x = * 2;",                # operador sem operando
])
def test_expressoes_mal_formadas(codigo):
    with pytest.raises(ParserError):
        arvore(codigo)


@pytest.mark.parametrize("codigo", [
    "x = 5",                   # falta ";"
    "print(1)",                # falta ";" no print
    "print 1;",                # print sem parênteses
    "x 5;",                    # falta "="
    "= 5;",                    # sem identificador
    "5 = x;",                  # lado esquerdo não é ID
])
def test_comandos_mal_formados(codigo):
    with pytest.raises(ParserError):
        arvore(codigo)


def test_comparacao_nao_encadeia():
    # comparacao usa [ ] (no máximo uma vez): a < b < c é rejeitado
    with pytest.raises(ParserError):
        arvore("x = 1 < 2 < 3;")


def test_menos_unario_nao_existe():
    with pytest.raises(ParserError):
        arvore("x = -5;")


@pytest.mark.parametrize("codigo", [
    "if (x) y = 1;",                       # if sem bloco
    "if x { }",                            # if sem parênteses
    "if (x) { } else y = 2;",              # else sem bloco
    "if (x) { } else if (y) { }",          # else if não existe na gramática
    "else { }",                            # else sem if
])
def test_condicional_mal_formado(codigo):
    with pytest.raises(ParserError):
        arvore(codigo)


def test_chave_solta():
    with pytest.raises(ParserError):
        arvore("}")


def test_mensagem_traz_posicao_em_outra_linha():
    with pytest.raises(ParserError) as erro:
        arvore("x = 1;\ny = ;")
    assert (erro.value.linha, erro.value.coluna) == (2, 5)
