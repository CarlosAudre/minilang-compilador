"""Testes de laço infinito com limite de iterações (item g).

Resultado esperado: todo laço que não termina é interrompido pelo limite de
iterações com LimiteIteracoesError (subclasse de SemanticError), mensagem
    "Erro semântico (linha N): laço passou do limite de L iterações
     (possível laço infinito)"
em que N é a linha do while/for. A suíte nunca trava: o limite é passado
como parâmetro (pequeno) nos testes e vale 100.000 por padrão.
"""
import pytest

from src.interpreter import (
    LIMITE_ITERACOES, LimiteIteracoesError, SemanticError, executar,
)


def rodar(codigo, limite):
    saida = []
    executar(codigo, escrever=saida.append, limite_iteracoes=limite)
    return saida


def test_while_true_e_interrompido():
    with pytest.raises(LimiteIteracoesError) as info:
        rodar("while (true) { }", limite=100)
    assert "limite de 100 iterações" in str(info.value)
    assert "possível laço infinito" in str(info.value)


def test_while_cuja_condicao_nunca_muda():
    with pytest.raises(LimiteIteracoesError):
        rodar("x = 1; while (x > 0) { print(x); }", limite=10)


def test_while_que_se_afasta_da_condicao_de_parada():
    with pytest.raises(LimiteIteracoesError):
        rodar("x = 1; while (x > 0) { x = x + 1; }", limite=50)


def test_for_com_atualizacao_que_nao_progride():
    with pytest.raises(LimiteIteracoesError):
        rodar("for (i = 0; i < 5; i = i) { }", limite=20)


def test_for_com_atualizacao_na_direcao_errada():
    with pytest.raises(LimiteIteracoesError):
        rodar("for (i = 0; i < 5; i = i - 1) { }", limite=20)


def test_for_com_condicao_sempre_verdadeira():
    with pytest.raises(LimiteIteracoesError):
        rodar("for (i = 0; true; i = i + 1) { }", limite=30)


def test_erro_informa_a_linha_do_laco():
    with pytest.raises(LimiteIteracoesError) as info:
        rodar("x = 0;\ny = 1;\nwhile (true) { x = x + 1; }", limite=5)
    assert info.value.linha == 3
    assert str(info.value).startswith("Erro semântico (linha 3)")


def test_saida_ate_o_limite_e_mantida():
    saida = []
    with pytest.raises(LimiteIteracoesError):
        executar("while (true) { print(1); }", escrever=saida.append,
                 limite_iteracoes=4)
    assert saida == ["1"] * 4


def test_laco_com_exatamente_o_limite_nao_e_erro():
    # 5 voltas com limite 5: permitido. A volta de número 6 é que estoura.
    assert rodar("for (i = 0; i < 5; i = i + 1) { }", limite=5) == []
    with pytest.raises(LimiteIteracoesError):
        rodar("for (i = 0; i < 6; i = i + 1) { }", limite=5)


def test_limite_vale_por_laco_e_nao_para_o_programa_inteiro():
    # Dois laços de 5 voltas cada, com limite 5: cada um tem o seu contador.
    codigo = ("for (i = 0; i < 5; i = i + 1) { } "
              "for (j = 0; j < 5; j = j + 1) { }")
    assert rodar(codigo, limite=5) == []


def test_laco_interno_infinito_dentro_de_laco_finito():
    with pytest.raises(LimiteIteracoesError):
        rodar("for (i = 0; i < 3; i = i + 1) { while (true) { } }", limite=10)


def test_limite_padrao_interrompe_sem_travar():
    assert LIMITE_ITERACOES == 100_000
    with pytest.raises(LimiteIteracoesError) as info:
        executar("while (true) { }", escrever=lambda _: None)
    assert "limite de 100000 iterações" in str(info.value)


def test_erro_de_limite_e_um_erro_semantico():
    assert issubclass(LimiteIteracoesError, SemanticError)
