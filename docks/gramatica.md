# Definição formal da MiniLang

## 1. Alfabeto (tokens)
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
(* TODO (item a) *)
```

## 3. Precedência e associatividade
| Nível | Operadores | Associatividade |
|-------|------------|-----------------|
| _TODO_ | | |

## 4. Exemplos (5 programas)
_TODO: mínimo 1 válido e 1 inválido de cada categoria (léxico, sintático, semântico), incluindo um laço mal formado._

## 5. Lexer
### Tabela de tokens
| Tipo | Padrão | Exemplo |
|------|--------|---------|
| _TODO (item b)_ | | |

### Tabela de transições do autômato
_TODO (item b)_
