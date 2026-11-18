"""Testes válidos do lexer. Resultado esperado: tokens gerados corretamente."""
from src.lexer import tokenizar


def tipos(codigo):
    return [t.tipo for t in tokenizar(codigo)]


def test_atribuicao_simples():
    tokens = tokenizar("x = y * 2;")
    assert [t.tipo for t in tokens] == [
        "T_id", "T_atrib", "T_id", "T_mult", "T_num", "T_ptvg"]
    assert tokens[0].valor == "x"
    assert tokens[2].valor == "y"
    assert tokens[4].valor == 2


def test_while_com_menor_igual():
    assert tipos("while (x <= 10) {") == [
        "T_while", "T_apar", "T_id", "T_menorig", "T_num", "T_fpar", "T_ach"]


def test_for_completo():
    assert tipos("for (i = 0; i < 5; i = i + 1) { }") == [
        "T_for", "T_apar", "T_id", "T_atrib", "T_num", "T_ptvg",
        "T_id", "T_menor", "T_num", "T_ptvg",
        "T_id", "T_atrib", "T_id", "T_mais", "T_num", "T_fpar",
        "T_ach", "T_fch"]


def test_palavras_reservadas():
    assert tipos("true false while for if else print") == [
        "T_true", "T_false", "T_while", "T_for", "T_if", "T_else", "T_print"]


def test_reservada_dentro_de_identificador_e_id():
    # "forx" e "whiley" não são palavras reservadas
    tokens = tokenizar("forx whiley")
    assert [t.tipo for t in tokens] == ["T_id", "T_id"]
    assert tokens[0].valor == "forx"


def test_operadores_de_comparacao():
    assert tipos("< > <= >= == !=") == [
        "T_menor", "T_maior", "T_menorig", "T_maiorig", "T_igual", "T_dif"]


def test_atribuicao_diferente_de_igualdade():
    assert tipos("= ==") == ["T_atrib", "T_igual"]


def test_aritmeticos_e_delimitadores():
    assert tipos("+ - * / ( ) { } ;") == [
        "T_mais", "T_menos", "T_mult", "T_div",
        "T_apar", "T_fpar", "T_ach", "T_fch", "T_ptvg"]


def test_identificador_com_digitos():
    tokens = tokenizar("soma1 a1b2")
    assert [t.valor for t in tokens] == ["soma1", "a1b2"]


def test_comentario_de_linha_ignorado():
    assert tipos("x = 1; // comentário\ny = 2;") == [
        "T_id", "T_atrib", "T_num", "T_ptvg",
        "T_id", "T_atrib", "T_num", "T_ptvg"]


def test_comentario_de_bloco_ignorado():
    assert tipos("x /* qualquer\ncoisa */ = 1;") == [
        "T_id", "T_atrib", "T_num", "T_ptvg"]


def test_divisao_nao_e_comentario():
    assert tipos("a / b") == ["T_id", "T_div", "T_id"]


def test_entrada_vazia():
    assert tokenizar("") == []


def test_posicao_do_token():
    tokens = tokenizar("x = 1;\n  y = 2;")
    y = tokens[4]
    assert (y.linha, y.coluna) == (2, 3)
