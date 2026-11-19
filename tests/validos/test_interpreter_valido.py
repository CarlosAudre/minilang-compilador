"""Testes válidos do interpretador (item e).

Resultado esperado: o programa executa sem erro, o print gera a saída
indicada e a tabela de símbolos termina com os valores esperados.
"""
import subprocess
import sys
from pathlib import Path

from src.interpreter import TabelaSimbolos, dividir, executar

RAIZ = Path(__file__).resolve().parents[2]


def rodar(codigo):
    """Executa e devolve (saída do print, valores finais das variáveis)."""
    saida = []
    tabela = executar(codigo, escrever=saida.append)
    return saida, tabela.valores()


# ---------- Tabela de símbolos ----------
def test_tabela_inserir_e_buscar():
    t = TabelaSimbolos()
    t.inserir("x", 10, linha=1)
    assert t.buscar("x", linha=2) == 10
    assert "x" in t and "y" not in t


def test_tabela_atualizar_mantem_tipo_e_linha_de_definicao():
    t = TabelaSimbolos()
    t.inserir("x", 1, linha=1)
    t.inserir("x", 2, linha=5)
    s = t.simbolo("x")
    assert (s.tipo, s.valor, s.linha) == ("int", 2, 1)


def test_tabela_guarda_tipo_bool():
    t = TabelaSimbolos()
    t.inserir("ok", True, linha=1)
    assert t.simbolo("ok").tipo == "bool"


# ---------- Atribuição, print e expressões ----------
def test_atribuicao_e_print():
    assert rodar("x = 10; print(x + 1);") == (["11"], {"x": 10})


def test_print_de_booleanos_em_minusculas():
    saida, _ = rodar("print(true); print(false); print(1 < 2);")
    assert saida == ["true", "false", "true"]


def test_precedencia_na_execucao():
    saida, _ = rodar("print(1 + 2 * 3); print((1 + 2) * 3); print(10 - 4 - 3);")
    assert saida == ["7", "9", "3"]


def test_divisao_inteira():
    saida, _ = rodar("print(7 / 2); print(8 / 2 / 2);")
    assert saida == ["3", "2"]


def test_divisao_trunca_em_direcao_a_zero():
    assert dividir(7, 2) == 3
    assert dividir(-7, 2) == -3
    assert dividir(7, -2) == -3
    assert dividir(-7, -2) == 3
    saida, _ = rodar("x = 0 - 7; print(x / 2);")
    assert saida == ["-3"]


def test_comparacoes():
    saida, _ = rodar(
        "print(1 < 2); print(2 > 1); print(2 <= 2); print(3 >= 4);"
        "print(5 == 5); print(5 != 5);")
    assert saida == ["true", "true", "true", "false", "true", "false"]


def test_igualdade_entre_booleanos():
    saida, _ = rodar("print(true == true); print(true != false);")
    assert saida == ["true", "true"]


def test_variavel_booleana():
    _, vars_ = rodar("maior = 5 > 3; menor = 5 < 3;")
    assert vars_ == {"maior": True, "menor": False}


def test_reatribuicao_com_mesmo_tipo():
    assert rodar("x = 1; x = x + 1; x = x * 10;")[1] == {"x": 20}


# ---------- Condicional e blocos ----------
def test_if_verdadeiro_e_falso():
    saida, _ = rodar(
        "if (true) { print(1); } else { print(2); }"
        "if (false) { print(3); } else { print(4); }"
        "if (false) { print(5); }")
    assert saida == ["1", "4"]


def test_bloco_solto_executa_em_ordem():
    assert rodar("{ print(1); { print(2); } print(3); }")[0] == ["1", "2", "3"]


def test_variavel_criada_no_bloco_continua_existindo():
    # Escopo único: a MiniLang não tem escopo aninhado.
    assert rodar("if (true) { y = 7; } print(y);")[0] == ["7"]


# ---------- while ----------
def test_while_repete_enquanto_verdadeiro():
    saida, vars_ = rodar("x = 3; while (x > 0) { print(x); x = x - 1; }")
    assert saida == ["3", "2", "1"]
    assert vars_ == {"x": 0}


def test_while_com_condicao_falsa_nao_executa():
    assert rodar("x = 0; while (x > 0) { print(x); }") == ([], {"x": 0})


# ---------- for ----------
def test_for_ordem_init_condicao_corpo_atualizacao():
    saida, vars_ = rodar("for (i = 0; i < 3; i = i + 1) { print(i); }")
    assert saida == ["0", "1", "2"]
    # A atualização roda depois do último corpo; a condição falha com i == 3.
    assert vars_ == {"i": 3}


def test_for_inicializacao_roda_mesmo_sem_iterar():
    assert rodar("for (i = 10; i < 3; i = i + 1) { print(i); }") == ([], {"i": 10})


def test_for_acumulando_soma():
    _, vars_ = rodar("soma = 0; for (i = 1; i <= 4; i = i + 1) { soma = soma + i; }")
    assert vars_["soma"] == 10


def test_lacos_aninhados():
    saida, _ = rodar(
        "for (i = 0; i < 2; i = i + 1) {"
        "  j = 0; while (j < 2) { print(i * 10 + j); j = j + 1; }"
        "}")
    assert saida == ["0", "1", "10", "11"]


# ---------- Programa de exemplo ----------
def test_programa_valido_do_exemplo():
    codigo = (RAIZ / "exemplos" / "programa_valido.ml").read_text(encoding="utf-8")
    saida, vars_ = rodar(codigo)
    # while imprime 10..1; soma = 0+1+2+3+4 = 10, que não é > 20, então print(0).
    assert saida == [str(n) for n in range(10, 0, -1)] + ["0"]
    assert vars_ == {"x": 0, "y": 30, "soma": 10, "i": 5}


def test_linha_de_comando_programa_valido():
    r = subprocess.run(
        [sys.executable, "-m", "src.interpreter", "exemplos/programa_valido.ml"],
        cwd=RAIZ, capture_output=True, text=True)
    assert r.returncode == 0
    assert r.stdout.split() == [str(n) for n in range(10, 0, -1)] + ["0"]
