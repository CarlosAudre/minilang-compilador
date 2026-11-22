"""Testes de while e for: casos válidos e de borda (item g).

Resultado esperado: cada programa executa até o fim, sem erro, e produz a
saída (lista de linhas do print) ou o estado final indicado em cada teste.

Casos cobertos, para while e para for:
- laço que não executa (condição falsa na entrada);
- laço que executa uma vez;
- laço que executa N vezes;
- for cuja atualização altera a variável de controle de forma diferente de +1;
- equivalência entre for e (inicialização; while com corpo + atualização).
"""
from src.interpreter import executar


def rodar(codigo):
    """Executa o programa e devolve (saída do print, valores finais das variáveis)."""
    saida = []
    tabela = executar(codigo, escrever=saida.append)
    return saida, tabela.valores()


# ---------- while ----------
def test_while_nao_executa_com_condicao_falsa_na_entrada():
    saida, vars_ = rodar("x = 0; while (x > 0) { print(x); x = x - 1; }")
    assert saida == []
    assert vars_["x"] == 0


def test_while_com_false_literal_nao_executa():
    saida, _ = rodar("while (false) { print(1); }")
    assert saida == []


def test_while_executa_uma_vez():
    saida, vars_ = rodar("x = 1; while (x > 0) { print(x); x = x - 1; }")
    assert saida == ["1"]
    assert vars_["x"] == 0


def test_while_executa_n_vezes():
    saida, vars_ = rodar("x = 5; while (x > 0) { print(x); x = x - 1; }")
    assert saida == ["5", "4", "3", "2", "1"]
    assert vars_["x"] == 0


def test_while_acumulador():
    _, vars_ = rodar("i = 1; s = 0; while (i <= 100) { s = s + i; i = i + 1; }")
    assert vars_["s"] == 5050


def test_while_condicao_reavaliada_a_cada_volta():
    # A condição depende de uma variável alterada dentro do corpo.
    saida, _ = rodar("x = 0; while (x < 3) { x = x + 1; print(x); }")
    assert saida == ["1", "2", "3"]


# ---------- for ----------
def test_for_nao_executa_com_condicao_falsa_na_entrada():
    saida, vars_ = rodar("for (i = 10; i < 5; i = i + 1) { print(i); }")
    assert saida == []
    assert vars_["i"] == 10  # a inicialização roda; a atualização não


def test_for_executa_uma_vez():
    saida, vars_ = rodar("for (i = 0; i < 1; i = i + 1) { print(i); }")
    assert saida == ["0"]
    assert vars_["i"] == 1


def test_for_executa_n_vezes():
    saida, vars_ = rodar("for (i = 0; i < 5; i = i + 1) { print(i); }")
    assert saida == ["0", "1", "2", "3", "4"]
    assert vars_["i"] == 5


def test_for_atualizacao_de_dois_em_dois():
    saida, vars_ = rodar("for (i = 0; i < 10; i = i + 2) { print(i); }")
    assert saida == ["0", "2", "4", "6", "8"]
    assert vars_["i"] == 10


def test_for_contagem_regressiva():
    saida, vars_ = rodar("for (i = 3; i > 0; i = i - 1) { print(i); }")
    assert saida == ["3", "2", "1"]
    assert vars_["i"] == 0


def test_for_atualizacao_multiplicativa():
    saida, _ = rodar("for (i = 1; i < 100; i = i * 3) { print(i); }")
    assert saida == ["1", "3", "9", "27", "81"]


def test_for_corpo_altera_a_variavel_de_controle():
    # O corpo também mexe em i: o laço roda para i = 0 e i = 3 apenas.
    saida, _ = rodar("for (i = 0; i < 5; i = i + 1) { print(i); i = i + 2; }")
    assert saida == ["0", "3"]


def test_for_equivale_a_while_com_atualizacao_no_fim_do_corpo():
    com_for, vars_for = rodar(
        "s = 0; for (i = 0; i < 6; i = i + 1) { s = s + i; print(s); }")
    com_while, vars_while = rodar(
        "s = 0; i = 0; while (i < 6) { s = s + i; print(s); i = i + 1; }")
    assert com_for == com_while
    assert vars_for == vars_while


def test_variavel_de_controle_continua_existindo_depois_do_for():
    _, vars_ = rodar("for (k = 0; k < 3; k = k + 1) { } print(k);")
    assert vars_["k"] == 3


# ---------- aninhamento e combinação ----------
def test_for_dentro_de_while():
    saida, _ = rodar(
        "n = 2; while (n > 0) { for (i = 0; i < 2; i = i + 1) "
        "{ print(n * 10 + i); } n = n - 1; }")
    assert saida == ["20", "21", "10", "11"]


def test_while_dentro_de_for():
    _, vars_ = rodar(
        "t = 0; for (i = 0; i < 3; i = i + 1) "
        "{ j = 0; while (j < 2) { t = t + 1; j = j + 1; } }")
    assert vars_["t"] == 6


def test_laco_com_if_dentro():
    saida, _ = rodar(
        "for (i = 0; i < 6; i = i + 1) { if (i / 2 * 2 == i) { print(i); } }")
    assert saida == ["0", "2", "4"]


def test_laco_com_condicao_booleana_em_variavel():
    saida, _ = rodar(
        "ok = true; n = 0; while (ok) { n = n + 1; ok = n < 3; } print(n);")
    assert saida == ["3"]
