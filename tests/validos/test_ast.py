"""Testes da AST (item d).

Resultado esperado: os nós são construídos com os campos corretos, o parser
gera a AST esperada (precedência, associatividade, while e for com as três
cláusulas) e a AST elimina só o que não é necessário para a execução
(parênteses, ";", chaves, palavras-chave), sem perder informação.
"""
from dataclasses import fields
from pathlib import Path

from src.ast_nodes import (
    Atribuicao, Bloco, Booleano, For, If, Numero, OpBinaria, Print, Programa,
    Variavel, While, formatar,
)
from src.lexer import tokenizar
from src.parser import parse

EXEMPLOS = Path(__file__).resolve().parents[2] / "exemplos"


def arvore(codigo):
    return parse(tokenizar(codigo))


def expressao(codigo):
    return arvore(f"x = {codigo};").comandos[0].expressao


def nomes_dos_campos(classe):
    return [f.name for f in fields(classe) if f.name != "linha"]


# ---------- Definição dos nós ----------
def test_campos_dos_nos_de_laco():
    assert nomes_dos_campos(While) == ["condicao", "corpo"]
    assert nomes_dos_campos(For) == ["inicializacao", "condicao", "atualizacao", "corpo"]


def test_campos_dos_demais_nos():
    assert nomes_dos_campos(Numero) == ["valor"]
    assert nomes_dos_campos(Booleano) == ["valor"]
    assert nomes_dos_campos(Variavel) == ["nome"]
    assert nomes_dos_campos(OpBinaria) == ["operador", "esquerda", "direita"]
    assert nomes_dos_campos(Atribuicao) == ["nome", "expressao"]
    assert nomes_dos_campos(Print) == ["expressao"]
    assert nomes_dos_campos(Bloco) == ["comandos"]
    assert nomes_dos_campos(If) == ["condicao", "entao", "senao"]
    assert nomes_dos_campos(Programa) == ["comandos"]


def test_construcao_manual_de_um_for():
    no = For(
        inicializacao=Atribuicao("i", Numero(0)),
        condicao=OpBinaria("<", Variavel("i"), Numero(3)),
        atualizacao=Atribuicao("i", OpBinaria("+", Variavel("i"), Numero(1))),
        corpo=Bloco([Print(Variavel("i"))]),
    )
    assert no.inicializacao.nome == "i"
    assert no.condicao.operador == "<"
    assert no.atualizacao.expressao.operador == "+"
    assert no.corpo.comandos == [Print(Variavel("i"))]


# ---------- AST de 1 + 2 * 3 ----------
def test_ast_de_1_mais_2_vezes_3():
    raiz = expressao("1 + 2 * 3")
    # A raiz é o "+": ele é resolvido por último.
    assert raiz.operador == "+"
    assert raiz.esquerda == Numero(1)
    # O "*" fica mais fundo, então é resolvido primeiro.
    assert raiz.direita == OpBinaria("*", Numero(2), Numero(3))


def test_ast_de_parenteses_nao_tem_no_de_parenteses():
    # (1 + 2) * 3: os parênteses só mudam a forma da árvore.
    raiz = expressao("(1 + 2) * 3")
    assert raiz == OpBinaria("*", OpBinaria("+", Numero(1), Numero(2)), Numero(3))


def test_parenteses_redundantes_geram_a_mesma_ast():
    assert expressao("((1 + 2))") == expressao("1 + 2")
    assert expressao("1 + (2 * 3)") == expressao("1 + 2 * 3")


def test_associatividade_a_esquerda_na_ast():
    assert expressao("10 - 4 - 3") == OpBinaria(
        "-", OpBinaria("-", Numero(10), Numero(4)), Numero(3))


# ---------- AST dos laços ----------
def test_ast_do_for_com_as_tres_clausulas():
    no = arvore("for (i = 0; i < 10; i = i + 1) { print(i); }").comandos[0]
    assert no == For(
        Atribuicao("i", Numero(0)),
        OpBinaria("<", Variavel("i"), Numero(10)),
        Atribuicao("i", OpBinaria("+", Variavel("i"), Numero(1))),
        Bloco([Print(Variavel("i"))]),
    )
    # As cláusulas de inicialização e atualização são atribuições.
    assert isinstance(no.inicializacao, Atribuicao)
    assert isinstance(no.atualizacao, Atribuicao)


def test_ast_do_while():
    no = arvore("while (x > 0) { x = x - 1; }").comandos[0]
    assert no == While(
        OpBinaria(">", Variavel("x"), Numero(0)),
        Bloco([Atribuicao("x", OpBinaria("-", Variavel("x"), Numero(1)))]),
    )


def test_for_e_while_equivalentes_tem_as_mesmas_partes():
    # for (i = 0; i < 3; i = i + 1) { print(i); }
    # equivale a  i = 0; while (i < 3) { print(i); i = i + 1; }
    f = arvore("for (i = 0; i < 3; i = i + 1) { print(i); }").comandos[0]
    ini, w = arvore("i = 0; while (i < 3) { print(i); i = i + 1; }").comandos
    assert f.inicializacao == ini
    assert f.condicao == w.condicao
    assert f.corpo.comandos + [f.atualizacao] == w.corpo.comandos


# ---------- O que a AST elimina sem perder informação ----------
def test_ast_nao_guarda_tokens_de_pontuacao():
    no = arvore("print((x));").comandos[0]
    assert no == Print(Variavel("x"))


def test_if_sem_else_tem_senao_none():
    assert arvore("if (true) { }").comandos[0].senao is None


def test_linha_e_guardada_mas_nao_muda_a_igualdade():
    programa = arvore("x = 1;\n\nwhile (x < 3) {\n  x = x + 1;\n}")
    atrib, laco = programa.comandos
    assert atrib.linha == 1
    assert laco.linha == 3
    assert laco.corpo.comandos[0].linha == 4
    # A mesma árvore, sem informação de linha, é considerada igual.
    assert laco == While(
        OpBinaria("<", Variavel("x"), Numero(3)),
        Bloco([Atribuicao("x", OpBinaria("+", Variavel("x"), Numero(1)))]))


# ---------- Programa completo com laço ----------
def test_ast_do_programa_valido():
    codigo = (EXEMPLOS / "programa_valido.ml").read_text(encoding="utf-8")
    programa = arvore(codigo)
    assert len(programa.comandos) == 6
    laco_while = programa.comandos[2]
    laco_for = programa.comandos[4]
    assert laco_while.condicao == OpBinaria(">", Variavel("x"), Numero(0))
    assert laco_for.inicializacao == Atribuicao("i", Numero(0))
    assert laco_for.condicao == OpBinaria("<", Variavel("i"), Numero(5))
    assert laco_for.atualizacao == Atribuicao(
        "i", OpBinaria("+", Variavel("i"), Numero(1)))


def test_formatar_mostra_a_arvore_indentada():
    texto = formatar(arvore("for (i = 0; i < 2; i = i + 1) { print(i); }"))
    assert texto == "\n".join([
        "Programa()",
        "  comandos:",
        "    For()",
        "      inicializacao:",
        "        Atribuicao(nome='i')",
        "          expressao:",
        "            Numero(valor=0)",
        "      condicao:",
        "        OpBinaria(operador='<')",
        "          esquerda:",
        "            Variavel(nome='i')",
        "          direita:",
        "            Numero(valor=2)",
        "      atualizacao:",
        "        Atribuicao(nome='i')",
        "          expressao:",
        "            OpBinaria(operador='+')",
        "              esquerda:",
        "                Variavel(nome='i')",
        "              direita:",
        "                Numero(valor=1)",
        "      corpo:",
        "        Bloco()",
        "          comandos:",
        "            Print()",
        "              expressao:",
        "                Variavel(nome='i')",
    ])
