"""Testes inválidos do interpretador (item e): erros semânticos.

Resultado esperado: todos os programas abaixo passam pelo lexer e pelo
parser (são sintaticamente válidos), mas a execução é interrompida com
SemanticError, cuja mensagem tem o formato
    "Erro semântico (linha N): <descrição>".

Casos cobertos:
- variável não definida (inclusive a variável de controle de laços);
- divisão por zero;
- tipo incompatível (operação aritmética/relacional com bool, == entre
  int e bool, variável que muda de tipo);
- condição não booleana em if, while e for;
- laço que passa do limite de iterações.
"""
import subprocess
import sys
from pathlib import Path

import pytest

from src.interpreter import LimiteIteracoesError, SemanticError, executar
from src.lexer import tokenizar
from src.parser import parse

RAIZ = Path(__file__).resolve().parents[2]


def erro_semantico(codigo):
    """Confirma que o programa é sintaticamente válido e que a execução falha."""
    parse(tokenizar(codigo))  # não pode lançar erro léxico nem sintático
    with pytest.raises(SemanticError) as info:
        executar(codigo, escrever=lambda _: None)
    return info.value


# ---------- Variável não definida ----------
def test_variavel_nao_definida():
    e = erro_semantico("print(y);")
    assert "variável 'y' não definida" in str(e)


def test_variavel_usada_na_propria_definicao():
    assert "'x' não definida" in str(erro_semantico("x = x + 1;"))


def test_variavel_de_controle_do_while_nao_definida():
    e = erro_semantico("while (i < 10) { i = i + 1; }")
    assert "'i' não definida" in str(e)


def test_variavel_de_controle_do_for_nao_definida_na_condicao():
    # A inicialização define i, mas a condição usa j.
    e = erro_semantico("for (i = 0; j < 10; i = i + 1) { print(i); }")
    assert "'j' não definida" in str(e)


def test_variavel_nao_definida_na_atualizacao_do_for():
    e = erro_semantico("for (i = 0; i < 10; i = k + 1) { print(i); }")
    assert "'k' não definida" in str(e)


# ---------- Divisão por zero ----------
def test_divisao_por_zero_literal():
    assert "divisão por zero" in str(erro_semantico("x = 10 / 0;"))


def test_divisao_por_zero_calculada():
    assert "divisão por zero" in str(erro_semantico("z = 2 - 2; print(1 / z);"))


# ---------- Tipo incompatível ----------
def test_soma_de_int_com_bool():
    e = erro_semantico("x = 1 + true;")
    assert "tipo incompatível" in str(e) and "int e bool" in str(e)


def test_comparacao_relacional_com_bool():
    assert "tipo incompatível" in str(erro_semantico("x = true < false;"))


def test_igualdade_entre_int_e_bool():
    e = erro_semantico("x = 1 == true;")
    assert "compara int com bool" in str(e)


def test_variavel_nao_pode_mudar_de_tipo():
    e = erro_semantico("x = 1;\nx = true;")
    assert "variável 'x' é int" in str(e)
    assert e.linha == 2


# ---------- Condição não booleana ----------
def test_while_com_condicao_inteira():
    e = erro_semantico("x = 10;\nwhile (x) {\n  x = x - 1;\n}")
    assert "condição do while deve ser booleana, mas é int" in str(e)
    assert e.linha == 2


def test_for_com_condicao_inteira():
    e = erro_semantico("for (i = 0; i + 1; i = i + 1) { print(i); }")
    assert "condição do for deve ser booleana" in str(e)


def test_if_com_condicao_inteira():
    assert "condição do if deve ser booleana" in str(erro_semantico("if (1) { }"))


# ---------- Limite de iterações ----------
def test_laco_acima_do_limite_e_interrompido():
    with pytest.raises(LimiteIteracoesError) as info:
        executar("x = 0; while (true) { x = x + 1; }",
                 escrever=lambda _: None, limite_iteracoes=50)
    assert "limite de 50 iterações" in str(info.value)


# ---------- Mensagem e posição ----------
def test_mensagem_tem_formato_e_linha():
    e = erro_semantico("a = 1;\nb = 2;\nprint(a / (b - 2));")
    assert str(e) == "Erro semântico (linha 3): divisão por zero"


def test_saida_anterior_ao_erro_e_mantida():
    saida = []
    with pytest.raises(SemanticError):
        executar("print(1); print(2); print(y);", escrever=saida.append)
    assert saida == ["1", "2"]


def test_linha_de_comando_mostra_erro_e_sai_com_codigo_1():
    r = subprocess.run(
        [sys.executable, "-m", "src.interpreter", "exemplos/programa_invalido.ml"],
        cwd=RAIZ, capture_output=True, text=True)
    assert r.returncode == 1
    assert r.stderr.startswith("Erro sintático (linha 2")
