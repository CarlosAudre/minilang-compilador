# Relatório: itens (f) e (g)

> Texto para incorporar ao `docs/relatorio.pdf` (seções B.6 e B.7 e Parte A).
> As mensagens abaixo foram copiadas da execução real de `exemplos/erros/*.ml`.

## B.6 Catálogo de erros (item f)

A MiniLang detecta erros em três fases, e cada uma tem a sua exceção e o seu prefixo de mensagem:

| Categoria | Fase | Exceção | Prefixo da mensagem |
|-----------|------|---------|---------------------|
| Léxico | lexer | `LexerError` | `Erro léxico (linha L, coluna C): ...` |
| Sintático | parser | `ParserError` | `Erro sintático (linha L, coluna C): ...` |
| Semântico | interpretador | `SemanticError` | `Erro semântico (linha L): ...` |

### Erros léxicos (a cadeia não pertence a nenhuma classe de token)

| Mensagem | Causa | Exemplo |
|----------|-------|---------|
| `caractere inválido: '@'` | Símbolo fora do alfabeto: nenhuma transição de q0 o reconhece. | `x = 5 @ 3;` |
| `número seguido de letra: '1x'` | Em q1 (lendo dígitos), uma letra leva ao estado de erro. | `x = 1x;` |
| `comentário de bloco não fechado` | A entrada acaba em q13 ou q14, que não são finais. | `/* isto nunca fecha` |
| `'!' deve ser seguido de '='` | A entrada acaba (ou muda de caractere) em q6, que não é final. | `x = !y;` |

### Erros sintáticos (os tokens são válidos, a ordem viola a EBNF)

| Mensagem | Causa | Exemplo |
|----------|-------|---------|
| `esperado ';', encontrado ')'` | `laco_for` exige `atribuicao ";" expressao ";" atribuicao`. Faltam o segundo `;` e a atualização. | `for (i = 0; i < 10) { ... }` |
| `esperado um operando (número, true, false, identificador ou '('), encontrado ';'` | `termo` exige um `fator` depois de `+`. | `x = (1 + ;` |
| `esperado '{', encontrado identificador` | `laco_while` exige `bloco`, e a MiniLang não aceita corpo sem chaves. | `while (x > 0) x = x - 1;` |
| `esperado um comando, encontrado ...` | Um token que não inicia nenhum `comando` (First de `comando`). | `= 5;` |
| `esperado X, mas a entrada terminou` | O arquivo acabou no meio de uma regra. | `x = 1 +` |

### Erros semânticos (a sintaxe é válida, o significado não)

| Mensagem | Causa | Exemplo |
|----------|-------|---------|
| `a condição do while deve ser booleana, mas é int` | Condição de `while`, `for` ou `if` com valor `int`. | `x = 10; while (x) { ... }` |
| `variável 'j' não definida` | Uso de variável sem atribuição prévia, inclusive a variável de controle do laço. | `for (i = 0; j < 3; i = i + 1) { ... }` |
| `divisão por zero` | O divisor vale 0 na hora da execução. | `b = a - a; print(a / b);` |
| `tipo incompatível: '+' exige int e int, recebeu int e bool` | Operador aritmético ou relacional com `bool`. | `x = 1 + true;` |
| `tipo incompatível: '==' compara int com bool` | Igualdade entre tipos diferentes. | `x = 1 == true;` |
| `tipo incompatível: variável 'x' é int ... e recebeu bool` | A variável muda de tipo depois da primeira atribuição. | `x = 1; x = true;` |
| `laço passou do limite de L iterações (possível laço infinito)` | Um laço passou de 100.000 voltas. | `while (true) { }` |

### Execução demonstrada (10 casos, 3 ou mais por categoria)

`python -m src.interpreter exemplos/erros/<arquivo>.ml` (cada um termina com código de saída 1):

| Arquivo | Saída |
|---------|-------|
| `lexico_1_caractere_invalido.ml` | `Erro léxico (linha 2, coluna 7): caractere inválido: '@'` |
| `lexico_2_numero_seguido_de_letra.ml` | `Erro léxico (linha 2, coluna 5): número seguido de letra: '1x'` |
| `lexico_3_comentario_nao_fechado.ml` | `Erro léxico (linha 3, coluna 1): comentário de bloco não fechado` |
| `sintatico_1_for_sem_atualizacao.ml` (laço) | `Erro sintático (linha 2, coluna 19): esperado ';', encontrado ')'` |
| `sintatico_2_operando_faltando.ml` | `Erro sintático (linha 2, coluna 10): esperado um operando (...), encontrado ';'` |
| `sintatico_3_while_sem_bloco.ml` (laço) | `Erro sintático (linha 4, coluna 3): esperado '{', encontrado identificador` |
| `semantico_1_while_condicao_inteira.ml` (laço) | `Erro semântico (linha 3): a condição do while deve ser booleana, mas é int` |
| `semantico_2_variavel_nao_definida.ml` (laço) | `Erro semântico (linha 2): variável 'j' não definida` |
| `semantico_3_divisao_por_zero.ml` | `Erro semântico (linha 4): divisão por zero` |
| `semantico_4_tipo_incompativel.ml` | `Erro semântico (linha 2): tipo incompatível: '+' exige int e int, recebeu int e bool` |

Os testes que conferem essas saídas estão em `tests/invalidos/test_catalogo_erros.py`, e os de cada categoria em `test_lexer_invalido.py`, `test_parser_invalido.py` e `test_interpreter_invalido.py`, todos com o resultado esperado em comentário no topo.

### Estratégia de diagnóstico adotada: parar no primeiro erro (fail-fast)

Cada fase levanta uma exceção no primeiro erro, com linha e coluna (léxico e sintático) ou linha (semântico), e o programa termina com código 1. Não há recuperação (modo pânico, sincronização por `;` ou `}`). A escolha se justifica por quatro motivos:

1. **Os erros em cascata enganam.** Em `x = (1 + ;`, se o parser tentasse continuar depois do primeiro erro, a falta do `")"` geraria uma segunda mensagem que é só consequência da primeira. Um aluno iniciante, que é o público da plataforma, entende melhor uma mensagem certa do que cinco duvidosas.
2. **A posição do erro é precisa.** Como a gramática é LL(1), o parser detecta o erro no primeiro token que não pode continuar nenhum prefixo válido (propriedade do prefixo viável). A linha e a coluna apontam o ponto real, o que é a parte mais útil do diagnóstico.
3. **A ordem das fases evita erros sem sentido.** O erro léxico impede a análise sintática, e o sintático impede a execução. Por isso a AST que chega ao interpretador é sempre bem formada, e o interpretador só trata de significado.
4. **Custo e benefício.** Recuperação em modo pânico acrescenta conjuntos de sincronização por regra e mais testes, e o enunciado não pede mais de um erro por execução.

**Limitação aceita:** as verificações semânticas são dinâmicas, feitas quando o nó é visitado. Um erro de tipo dentro de um `if (false) { ... }` nunca é detectado, e a saída anterior ao erro continua impressa (`test_saida_anterior_ao_erro_e_mantida`). Uma análise semântica estática, em passada separada, resolveria isso, mas exigiria inferência de tipos fora do escopo do projeto.

## B.7 Suíte de testes (item g)

A suíte tem 169 testes (todos passando) em `tests/validos/` e `tests/invalidos/`. Para os laços:

| Caso exigido | `while` | `for` |
|--------------|---------|-------|
| Não executa (condição falsa na entrada) | `test_while_nao_executa_com_condicao_falsa_na_entrada` | `test_for_nao_executa_com_condicao_falsa_na_entrada` (a inicialização roda, a atualização não) |
| Executa uma vez | `test_while_executa_uma_vez` | `test_for_executa_uma_vez` |
| Executa N vezes | `test_while_executa_n_vezes`, `test_while_acumulador` (soma de 1 a 100) | `test_for_executa_n_vezes` |
| Atualização altera a variável de controle | `test_while_condicao_reavaliada_a_cada_volta` | passo 2, contagem regressiva, `i * 3`, corpo que altera `i` |
| Laço infinito com limite | `while (true)`, condição que nunca muda, `x` que se afasta da parada | atualização `i = i`, atualização `i = i - 1`, condição `true` |

Pontos de borda do limite de iterações (`tests/invalidos/test_laco_infinito.py`): um laço com exatamente o número de voltas do limite passa, e a volta seguinte estoura; o contador é por laço, não do programa inteiro; a saída anterior ao estouro é mantida; o erro informa a linha do laço. Nos testes o limite é pequeno (5 a 100), por isso a suíte roda em cerca de 1,5 s.

---

## Parte A: Pergunta de pesquisa (relatório de 2 a 3 páginas)

> *Em que etapas da construção de um compilador a IA generativa foi mais útil e onde ela introduziu erros que exigiram correção humana?*

**Resposta resumida.** A IA foi mais útil nas etapas **mecânicas e bem especificadas**: traduzir uma EBNF em funções do parser, gerar casos de teste e redigir a justificativa de exemplos. Introduziu erros nas etapas em que a decisão depende de **ler o enunciado com atenção ou de conhecer uma armadilha da linguagem de implementação**: o escopo de cada item, o que conta como erro léxico e o comportamento de `bool` em Python. Em nenhum caso o erro estava no formato do código; estava na premissa.

### Exemplos concretos (3 a 4 de acertos e falhas, além dos já registrados na seção A.2)

1. **Falha: `1x` como erro léxico "automático" (lexer).** A IA afirmou que as expressões regulares já rejeitariam `1x`. Com `T_num = dígito dígito*` e `T_id = letra (letra | dígito)*`, o lexer lê `1` e depois `x`, dois tokens válidos. O grupo criou a regra explícita em q1 (`raise LexerError("número seguido de letra")`) e o teste `test_numero_seguido_de_letra`. **Conceito:** o lexer implementa a leitura mais longa de cada padrão, e a concatenação de tokens válidos não é erro léxico.

2. **Acerto com ressalva: `comparacao` com `{ }` (EBNF).** A IA percebeu que a regra escrita pelo grupo aceitaria `a < b < c`, que compara um booleano com um número. A troca por `[ ]` torna a comparação não associativa. **Conceito:** diferença entre repetição `{ }` (associatividade) e opção `[ ]` (no máximo uma ocorrência).

3. **Ponto de atenção: `bool` é subclasse de `int` em Python (interpretador).** Com `isinstance(True, int)` verdadeiro, `1 + true` seria aceito e daria 2. O interpretador usa `type(valor) is bool` (função `nome_tipo`), e os testes `test_soma_de_int_com_bool` e `test_igualdade_entre_int_e_bool` garantem a rejeição. **Conceito:** a verificação de tipos da MiniLang tem de seguir a semântica da MiniLang, e não herdar a da linguagem hospedeira.

4. **Decisão do grupo sobre o código sugerido: divisão inteira.** O `//` de Python arredonda para baixo (`-7 // 2 == -4`). O grupo escolheu truncar em direção a zero, como C e Java (`-7 / 2 == -3`), com a função `dividir` e o teste `test_divisao_trunca_em_direcao_a_zero`. **Conceito:** semântica operacional do operador `/` definida pela linguagem-fonte.

5. **Falha de escopo: laço infinito.** (Preencher com a experiência do grupo ao rodar o item g. Se nenhum erro da IA ocorreu aqui, registrar isso também.)

### Fundamentação teórica: como cada conceito foi aplicado ou descartado

| Conceito da disciplina | Aplicação no projeto |
|------------------------|----------------------|
| Expressões regulares e AFD (Kleene) | Aplicado: os 25 tokens e os comentários viram o autômato q0 a q14, escrito à mão em `tokenizar`. |
| Leitura mais longa (maximal munch) | Aplicado: `<=` vence `<` e `==` vence `=`. |
| Gramática livre de contexto e EBNF | Aplicado: 13 regras; a precedência vem da hierarquia `comparacao`, `aritmetica`, `termo`, `fator`. |
| Eliminação de recursão à esquerda | Aplicado: as repetições `{ }` da EBNF viram `while` no parser, em vez de `exp = exp "+" termo`. |
| Análise descendente recursiva LL(1) | Aplicado: os First dos comandos são disjuntos, então um token de lookahead basta. |
| Análise ascendente SLR(1) | Descartado: aceitaria a mesma gramática, mas exigiria gerador de tabelas ou construção manual dos itens LR, sem ganho para uma gramática LL(1) tão pequena. |
| Ambiguidade (dangling else) | Evitado na origem: `if`, `while` e `for` exigem `bloco` com chaves. |
| Árvore concreta e árvore abstrata | Aplicado: a AST descarta parênteses, `;` e as regras intermediárias sem perder a ordem das operações. |
| Tabela de símbolos | Aplicado: dicionário nome para `Simbolo(tipo, valor, linha)`, inserção e busca O(1) em média, escopo único. |
| Semântica operacional | Aplicado: `for` equivale a `inicialização; while (condição) { corpo; atualização }`. |
| Análise semântica estática | Descartado: seria necessária uma passada com inferência de tipos; a verificação dinâmica atende ao enunciado, com a limitação do `if (false)`. |
| Recuperação de erros (modo pânico) | Descartado: ver B.6; fail-fast dá diagnóstico mais confiável. |
