"""Parser descendente recursivo da MiniLang (item c).

Há uma função para cada regra da EBNF de docs/gramatica.md, com o mesmo nome.
O parser lê os tokens da esquerda para a direita, olhando só o token atual
(LL(1)), e devolve a AST.
"""
from src.ast_nodes import (
    Atribuicao, Bloco, Booleano, For, If, Numero, OpBinaria, Print, Programa,
    Variavel, While,
)
from src.lexer import tokenizar


class ParserError(Exception):
    """Erro sintático."""

    def __init__(self, mensagem, linha, coluna):
        super().__init__(f"Erro sintático (linha {linha}, coluna {coluna}): {mensagem}")
        self.linha = linha
        self.coluna = coluna


# Como cada classe de token aparece nas mensagens de erro.
NOMES = {
    "T_num": "número", "T_id": "identificador",
    "T_true": "'true'", "T_false": "'false'", "T_while": "'while'",
    "T_for": "'for'", "T_if": "'if'", "T_else": "'else'", "T_print": "'print'",
    "T_mais": "'+'", "T_menos": "'-'", "T_mult": "'*'", "T_div": "'/'",
    "T_menor": "'<'", "T_maior": "'>'", "T_menorig": "'<='", "T_maiorig": "'>='",
    "T_igual": "'=='", "T_dif": "'!='", "T_atrib": "'='",
    "T_apar": "'('", "T_fpar": "')'", "T_ach": "'{'", "T_fch": "'}'",
    "T_ptvg": "';'",
}

COMPARACAO = {"T_menor": "<", "T_maior": ">", "T_menorig": "<=",
              "T_maiorig": ">=", "T_igual": "==", "T_dif": "!="}
ADITIVOS = {"T_mais": "+", "T_menos": "-"}
MULTIPLICATIVOS = {"T_mult": "*", "T_div": "/"}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ---------- utilitários ----------
    def atual(self):
        """Token atual, ou None no fim da entrada."""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def tipo_atual(self):
        t = self.atual()
        return t.tipo if t else None

    def erro(self, esperado):
        t = self.atual()
        if t is None:
            if self.tokens:
                ultimo = self.tokens[-1]
                linha, coluna = ultimo.linha, ultimo.coluna
            else:
                linha, coluna = 1, 1
            raise ParserError(f"esperado {esperado}, mas a entrada terminou", linha, coluna)
        raise ParserError(f"esperado {esperado}, encontrado {NOMES[t.tipo]}",
                          t.linha, t.coluna)

    def consumir(self, tipo):
        """Consome o token atual se for do tipo esperado; senão, erro."""
        if self.tipo_atual() != tipo:
            self.erro(NOMES[tipo])
        t = self.atual()
        self.pos += 1
        return t

    # ---------- programa e comandos ----------
    def programa(self):                      # programa = { comando } ;
        comandos = []
        while self.atual() is not None:
            comandos.append(self.comando())
        return Programa(comandos, linha=1)

    def comando(self):
        # comando = atribuicao ";" | impressao | condicional
        #         | laco_while | laco_for | bloco ;
        tipo = self.tipo_atual()
        if tipo == "T_id":
            no = self.atribuicao()
            self.consumir("T_ptvg")
            return no
        if tipo == "T_print":
            return self.impressao()
        if tipo == "T_if":
            return self.condicional()
        if tipo == "T_while":
            return self.laco_while()
        if tipo == "T_for":
            return self.laco_for()
        if tipo == "T_ach":
            return self.bloco()
        self.erro("um comando")

    def atribuicao(self):                    # atribuicao = ID "=" expressao ;
        t = self.consumir("T_id")
        self.consumir("T_atrib")
        return Atribuicao(t.valor, self.expressao(), linha=t.linha)

    def impressao(self):                     # "print" "(" expressao ")" ";" ;
        t = self.consumir("T_print")
        self.consumir("T_apar")
        expr = self.expressao()
        self.consumir("T_fpar")
        self.consumir("T_ptvg")
        return Print(expr, linha=t.linha)

    def condicional(self):                   # "if" "(" e ")" bloco [ "else" bloco ] ;
        t = self.consumir("T_if")
        self.consumir("T_apar")
        cond = self.expressao()
        self.consumir("T_fpar")
        entao = self.bloco()
        senao = None
        if self.tipo_atual() == "T_else":
            self.consumir("T_else")
            senao = self.bloco()
        return If(cond, entao, senao, linha=t.linha)

    def laco_while(self):                    # "while" "(" expressao ")" bloco ;
        t = self.consumir("T_while")
        self.consumir("T_apar")
        cond = self.expressao()
        self.consumir("T_fpar")
        return While(cond, self.bloco(), linha=t.linha)

    def laco_for(self):
        # "for" "(" atribuicao ";" expressao ";" atribuicao ")" bloco ;
        t = self.consumir("T_for")
        self.consumir("T_apar")
        inicio = self.atribuicao()
        self.consumir("T_ptvg")
        cond = self.expressao()
        self.consumir("T_ptvg")
        atualizacao = self.atribuicao()
        self.consumir("T_fpar")
        return For(inicio, cond, atualizacao, self.bloco(), linha=t.linha)

    def bloco(self):                         # bloco = "{" { comando } "}" ;
        t = self.consumir("T_ach")
        comandos = []
        while self.tipo_atual() not in ("T_fch", None):
            comandos.append(self.comando())
        self.consumir("T_fch")
        return Bloco(comandos, linha=t.linha)

    # ---------- expressões (um nível de precedência por função) ----------
    def expressao(self):                     # expressao = comparacao ;
        return self.comparacao()

    def comparacao(self):
        # comparacao = aritmetica [ ( "<" | ">" | ... ) aritmetica ] ;
        esquerda = self.aritmetica()
        if self.tipo_atual() in COMPARACAO:  # [ ] : no máximo uma vez
            t = self.atual()
            self.pos += 1
            direita = self.aritmetica()
            return OpBinaria(COMPARACAO[t.tipo], esquerda, direita, linha=t.linha)
        return esquerda

    def aritmetica(self):                    # termo { ( "+" | "-" ) termo } ;
        esquerda = self.termo()
        while self.tipo_atual() in ADITIVOS: # { } : repete, associa à esquerda
            t = self.atual()
            self.pos += 1
            esquerda = OpBinaria(ADITIVOS[t.tipo], esquerda, self.termo(),
                                 linha=t.linha)
        return esquerda

    def termo(self):                         # fator { ( "*" | "/" ) fator } ;
        esquerda = self.fator()
        while self.tipo_atual() in MULTIPLICATIVOS:
            t = self.atual()
            self.pos += 1
            esquerda = OpBinaria(MULTIPLICATIVOS[t.tipo], esquerda, self.fator(),
                                 linha=t.linha)
        return esquerda

    def fator(self):                         # NUM | "true" | "false" | ID | "(" e ")"
        t = self.atual()
        tipo = self.tipo_atual()
        if tipo == "T_num":
            self.pos += 1
            return Numero(t.valor, linha=t.linha)
        if tipo == "T_true":
            self.pos += 1
            return Booleano(True, linha=t.linha)
        if tipo == "T_false":
            self.pos += 1
            return Booleano(False, linha=t.linha)
        if tipo == "T_id":
            self.pos += 1
            return Variavel(t.valor, linha=t.linha)
        if tipo == "T_apar":
            self.pos += 1
            expr = self.expressao()
            self.consumir("T_fpar")
            return expr
        self.erro("um operando (número, true, false, identificador ou '(')")


def parse(tokens: list):
    """Recebe a lista de tokens e devolve a AST (Programa)."""
    return Parser(tokens).programa()


if __name__ == "__main__":
    import sys
    from src.ast_nodes import formatar

    if len(sys.argv) != 2:
        print("Uso: python -m src.parser <arquivo.ml>")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        print(formatar(parse(tokenizar(f.read()))))
