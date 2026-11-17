# Definição formal da MiniLang

## 1. Alfabeto (tokens)

| # | Classe | Valor-lexema | Exemplo |
|---|--------|--------------|---------|
| 1 | T_num | CA | 0, 42 |
| 2 | T_id | CA | x, y |
| 3 | T_true | S | true |
| 4 | T_false | S | false |
| 5 | T_while | S | while |
| 6 | T_for | S | for |
| 7 | T_if | S | if |
| 8 | T_else | S | else |
| 9 | T_print | S | print |
| 10 | T_mais | S | + |
| 11 | T_menos | S | - |
| 12 | T_mult | S | * |
| 13 | T_div | S | / |
| 14 | T_menor | S | < |
| 15 | T_maior | S | > |
| 16 | T_menorig | S | <= |
| 17 | T_maiorig | S | >= |
| 18 | T_igual | S | == |
| 19 | T_dif | S | != |
| 20 | T_atrib | S | = |
| 21 | T_apar | S | ( |
| 22 | T_fpar | S | ) |
| 23 | T_ach | S | { |
| 24 | T_fch | S | } |
| 25 | T_ptvg | S | ; |

**Legenda:** CA = com argumento (o lexema precisa ser guardado); S = simples.

**Convenção na EBNF:** classes S aparecem como o próprio lexema entre aspas
(`"while"`, `"+"`); classes CA aparecem pelo nome (`NUM` para T_num, `ID` para T_id).

## 2. Gramática EBNF
```ebnf
programa    = { comando } ;
comando     = atribuicao ";" | impressao | condicional | laco_while | laco_for | bloco ;
atribuicao  = ID "=" expressao ;
impressao   = "print" "(" expressao ")" ";" ;
condicional = "if" "(" expressao ")" bloco [ "else" bloco ] ;
laco_while  = "while" "(" expressao ")" bloco ;
laco_for    = "for" "(" atribuicao ";" expressao ";" atribuicao ")" bloco ;
bloco       = "{" { comando } "}" ;
expressao   = comparacao ;
comparacao  = aritmetica [ ( "<" | ">" | "<=" | ">=" | "==" | "!=" ) aritmetica ] ;
aritmetica  = termo { ( "+" | "-" ) termo } ;
termo       = fator { ( "*" | "/" ) fator } ;
fator       = NUM | "true" | "false" | ID | "(" expressao ")" ;
```

## 3. Precedência e associatividade

Do nível mais fraco (resolvido por último) ao mais forte (resolvido primeiro):

| Nível | Operadores | Regra da gramática | Associatividade |
|-------|------------|--------------------|-----------------|
| 1 | `<` `>` `<=` `>=` `==` `!=` | `comparacao` | não associativa |
| 2 | `+` `-` | `aritmetica` | esquerda |
| 3 | `*` `/` | `termo` | esquerda |
| 4 | `( )` | `fator` | agrupamento (maior precedência) |

**Justificativas**

- **Precedência:** quanto mais fundo o nível na hierarquia
  (`comparacao` → `aritmetica` → `termo` → `fator`), mais cedo a operação é
  resolvida. Em `10 + 5 * 2`, o `*` fica dentro de um `termo`, abaixo do `+`,
  então `5 * 2` é calculado primeiro.
- **Associatividade à esquerda (`+ -` e `* /`):** a repetição `{ ... }` lê os
  operandos da esquerda para a direita, então `10 - 4 - 3` é `(10 - 4) - 3`.
- **Comparação não associativa:** usa `[ ... ]` (no máximo uma vez), então
  `a < b < c` é rejeitado pela gramática.
- **Parênteses:** `"(" expressao ")"` em `fator` reinicia a hierarquia dentro
  do par, por isso `(1 + 2) * 3` soma antes de multiplicar.
- **Menos unário:** não faz parte da MiniLang. `-5` é inválido sintaticamente.

## 4. Exemplos (5 programas)
## 4. Exemplos (5 programas)

### Exemplo 1: válido (`exemplos/programa_valido.ml`)
```
x = 10;
y = 2 * (x + 5);
while (x > 0) {
  print(x);
  x = x - 1;
}
soma = 0;
for (i = 0; i < 5; i = i + 1) {
  soma = soma + i;
}
if (soma > 20) {
  print(soma);
} else {
  print(0);
}
```
**Justificativa:** todos os símbolos pertencem aos 25 tokens (léxico). A sequência
segue `programa = { comando }`, usando `atribuicao ";"`, `laco_while`, `laco_for`
com as três cláusulas e `condicional` com `else` (sintaxe). As variáveis são
definidas antes do uso e as condições (`x > 0`, `i < 5`, `soma > 20`) são
booleanas (semântica).

### Exemplo 2: inválido léxico
```
x = 5 @ 3;
```
**Justificativa:** o caractere `@` não pertence a nenhuma das 25 classes de token,
então nenhuma expressão regular o reconhece. O erro ocorre no lexer, antes do parser.

### Exemplo 3: inválido sintático
```
x = (1 + ;
```
**Justificativa:** os tokens são válidos, mas a regra
`aritmetica = termo { ( "+" | "-" ) termo }` exige um `termo` depois do `+`, e
aparece `";"`. Além disso, o `"("` aberto em `fator` nunca é fechado por `")"`.

### Exemplo 4: inválido sintático, laço mal formado (`exemplos/programa_invalido.ml`)
```
for (i = 0; i < 10) {
  print(i);
}
```
**Justificativa:** viola `laco_for = "for" "(" atribuicao ";" expressao ";" atribuicao ")" bloco`.
Depois da condição `i < 10`, a regra exige um `";"` e a atribuição de atualização,
mas o parser encontra `")"`. Faltam a segunda cláusula `;` e a atualização.

### Exemplo 5: inválido semântico
```
x = 10;
while (x) {
  x = x - 1;
}
```
**Justificativa:** sintaticamente é válido: `laco_while = "while" "(" expressao ")" bloco`
aceita qualquer `expressao`, e `x` é um `fator`. A violação é semântica: a condição
do `while` deve ser booleana, mas `x` é inteiro. A gramática não distingue tipos;
essa verificação é feita pelo interpretador (item e).

## 5. Lexer
### Tabela de tokens
| Tipo | Padrão | Exemplo |
|------|--------|---------|
| _TODO (item b)_ | | |

### Tabela de transições do autômato
_TODO (item b)_
