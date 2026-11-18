"""Testes inválidos do lexer.

Resultado esperado: todas as entradas abaixo levantam LexerError, e a
mensagem informa a linha e a coluna do problema.
"""
import pytest

from src.lexer import LexerError, tokenizar


def test_caractere_invalido_arroba():
    with pytest.raises(LexerError) as erro:
        tokenizar("x = 5 @ 3;")
    assert "'@'" in str(erro.value)
    assert (erro.value.linha, erro.value.coluna) == (1, 7)


def test_numero_seguido_de_letra():
    with pytest.raises(LexerError) as erro:
        tokenizar("1x")
    assert "1x" in str(erro.value)


def test_comentario_de_bloco_nao_fechado():
    with pytest.raises(LexerError) as erro:
        tokenizar("x = 1; /* comentário sem fim")
    assert "não fechado" in str(erro.value)


def test_exclamacao_sozinha():
    with pytest.raises(LexerError):
        tokenizar("!x")


def test_exclamacao_separada_do_igual():
    with pytest.raises(LexerError):
        tokenizar("a ! = b")


def test_outros_caracteres_fora_do_alfabeto():
    for simbolo in ["#", "$", "%", "&", "?", "_", "."]:
        with pytest.raises(LexerError):
            tokenizar(f"x {simbolo} 1")


def test_posicao_do_erro_em_outra_linha():
    with pytest.raises(LexerError) as erro:
        tokenizar("x = 1;\ny = @;")
    assert (erro.value.linha, erro.value.coluna) == (2, 5)
