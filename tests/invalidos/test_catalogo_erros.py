"""Catálogo de erros executado de ponta a ponta (item f).

Resultado esperado: cada arquivo de exemplos/erros/ é executado pela linha de
comando (python -m src.interpreter <arquivo>), termina com código de saída 1,
não imprime nada em stdout e escreve em stderr a mensagem da tabela abaixo.
O prefixo da mensagem identifica a categoria (léxico, sintático, semântico).

| Arquivo                             | Mensagem esperada                                 |
|-------------------------------------|---------------------------------------------------|
| lexico_1_caractere_invalido         | Erro léxico (linha 2, coluna 7): caractere ...    |
| lexico_2_numero_seguido_de_letra    | Erro léxico (linha 2, coluna 5): número ...       |
| lexico_3_comentario_nao_fechado     | Erro léxico (linha 3, coluna 1): comentário ...   |
| sintatico_1_for_sem_atualizacao     | Erro sintático (linha 2, coluna 19): esperado ';' |
| sintatico_2_operando_faltando       | Erro sintático (linha 2, coluna 10): esperado um  |
| sintatico_3_while_sem_bloco         | Erro sintático (linha 4, coluna 3): esperado '{'  |
| semantico_1_while_condicao_inteira  | Erro semântico (linha 3): condição do while ...   |
| semantico_2_variavel_nao_definida   | Erro semântico (linha 2): variável 'j' ...        |
| semantico_3_divisao_por_zero        | Erro semântico (linha 4): divisão por zero        |
| semantico_4_tipo_incompativel       | Erro semântico (linha 2): tipo incompatível ...   |
"""
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]

CASOS = [
    ("lexico_1_caractere_invalido",
     "Erro léxico (linha 2, coluna 7): caractere inválido: '@'"),
    ("lexico_2_numero_seguido_de_letra",
     "Erro léxico (linha 2, coluna 5): número seguido de letra: '1x'"),
    ("lexico_3_comentario_nao_fechado",
     "Erro léxico (linha 3, coluna 1): comentário de bloco não fechado"),
    ("sintatico_1_for_sem_atualizacao",
     "Erro sintático (linha 2, coluna 19): esperado ';', encontrado ')'"),
    ("sintatico_2_operando_faltando",
     "Erro sintático (linha 2, coluna 10): esperado um operando"),
    ("sintatico_3_while_sem_bloco",
     "Erro sintático (linha 4, coluna 3): esperado '{', encontrado identificador"),
    ("semantico_1_while_condicao_inteira",
     "Erro semântico (linha 3): a condição do while deve ser booleana, mas é int"),
    ("semantico_2_variavel_nao_definida",
     "Erro semântico (linha 2): variável 'j' não definida"),
    ("semantico_3_divisao_por_zero",
     "Erro semântico (linha 4): divisão por zero"),
    ("semantico_4_tipo_incompativel",
     "Erro semântico (linha 2): tipo incompatível: '+' exige int e int, "
     "recebeu int e bool"),
]


@pytest.mark.parametrize("nome, mensagem", CASOS)
def test_exemplo_de_erro_pela_linha_de_comando(nome, mensagem):
    r = subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "src.interpreter",
         f"exemplos/erros/{nome}.ml"],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 1
    assert mensagem in r.stderr
    assert r.stdout == ""


def test_todo_arquivo_da_pasta_esta_no_catalogo():
    arquivos = {p.stem for p in (RAIZ / "exemplos" / "erros").glob("*.ml")}
    assert arquivos == {nome for nome, _ in CASOS}
