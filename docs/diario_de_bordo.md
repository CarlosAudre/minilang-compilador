# Diário de bordo

> Registrar datas reais, o que a IA fez, o que foi aceito, reescrito ou descartado, e por quê.

## 17/11/2026
- **O que foi feito:** tabela de 25 classes de token (feita por nós), EBNF com as 13 regras, tabela de precedência/associatividade e os 5 exemplos justificados, em `docs/gramatica.md`; exemplos em `exemplos/`.
- **Uso de IA (Claude):**
  - Explicação da diferença entre lexema, classe e padrão, e da convenção S/CA.
  - Rascunho das regras de expressão; nós escrevemos as regras dos comandos e de `aritmetica`/`termo`/`fator`.
  - Revisão da nossa EBNF e redação da seção de precedência e dos 5 exemplos.
- **Aceito / reescrito / descartado e por quê:**
  - Nós escolhemos `T_true` e `T_false` como classes separadas, em vez de `T_boolean`, porque cada classe tem um só lexema.
  - Corrigido na nossa EBNF, com ajuda da IA: faltavam os `";"` de `atribuicao` e de `print`, e a regra `comparacao` com `{ }` aceitaria `a < b < c`; trocamos por `[ ]`.
  - **Falha da IA:** afirmou que `1x` é erro léxico automaticamente. Está errado: um lexer comum lê `1` e `x` como dois tokens válidos. Vamos decidir no item (b) que o lexer rejeita número seguido de letra.
- **Dificuldades:** entender por que cada token fica em um nível da gramática e como a precedência vem da hierarquia das regras.
- **Próximos passos:** item (b): expressões regulares de cada token, autômato, tabela de transições e `lexer.py`.

  ### 18/11: Item (b), análise léxica
- **O que foi feito:** padrão (expressão regular) de cada token, tabela de transições do autômato (q0 a q14), `src/lexer.py` e 21 testes (válidos e inválidos).
- **Uso de IA (Claude):** explicação de expressão regular e autômato; geração do `lexer.py` e da tabela de transições; geração dos testes.
- **Aceito / reescrito / descartado e por quê:**
  - Decidimos aceitar comentário de bloco `/* */`, porque o `//` nunca fica aberto e o enunciado pede o teste "comentário não fechado".
  - Decidimos rejeitar `1x` no lexer, para o erro ser léxico.
  - Conferimos a tabela fazendo o trace de `1x` e de `/* oi */` no código e na tabela.
  - **Falha da IA:** misturou o escopo dos itens (a) e (b) e antecipou a coluna "padrão" e o autômato; corrigimos conferindo o enunciado.
- **Dificuldades:** entender a ligação entre expressão regular, autômato e código.
- **Próximos passos:** item (c), parser e AST.

### 19/11: Item (d), AST
- **O que foi feito:** revisão das classes de `src/ast_nodes.py` (campos de `While`: condição e corpo; de `For`: inicialização, condição, atualização e corpo), campo `linha` em todos os nós, preenchido pelo parser, e testes da AST em `tests/validos/test_ast.py`.
- **Uso de IA (Claude):** sugestão do campo `linha` (para as mensagens de erro semântico do item e) e geração dos testes da AST.
- **Aceito / reescrito / descartado e por quê:**
  - Aceito: `linha` com `compare=False`, para duas árvores com a mesma estrutura continuarem iguais mesmo vindo de linhas diferentes; assim os testes do parser não mudaram.
  - Aceito: teste que mostra que um `for` tem as mesmas partes de um `i = 0; while (...) { corpo; atualização; }`, usado na justificativa de que a AST não perde informação.
- **Dificuldades:** diferença entre árvore sintática concreta e abstrata; entender por que os parênteses não precisam virar nó.
- **Próximos passos:** item (e), interpretador e tabela de símbolos.

### 19/11: Item (e), interpretador
- **O que foi feito:** `src/interpreter.py` com a tabela de símbolos (dicionário nome -> símbolo com tipo, valor e linha de definição; operações `inserir` e `buscar`), interpretador que percorre a AST, verificações semânticas e limite de iterações dos laços; testes em `tests/validos/test_interpreter_valido.py` e `tests/invalidos/test_interpreter_invalido.py`.
- **Uso de IA (Claude):** geração do interpretador e dos testes; explicação de semântica operacional.
- **Aceito / reescrito / descartado e por quê:**
  - Decisão do grupo: o tipo da variável é fixado na primeira atribuição (`x = 1; x = true;` é erro de tipo incompatível), para a tabela de símbolos ter papel na verificação de tipos.
  - Decisão do grupo: `/` trunca em direção a zero, como C e Java; o `//` do Python daria `-7 / 2 = -4`.
  - Ponto de atenção: em Python `bool` é subclasse de `int`, então `isinstance(True, int)` é verdadeiro; a verificação usa `type(v) is bool` para `1 + true` ser rejeitado.
  - Limitação aceita: as verificações são dinâmicas; um erro de tipo dentro de um `if (false)` não é detectado.
- **Dificuldades:** escrever a semântica operacional do `for` e mostrar que equivale a `inicialização; while (condição) { corpo atualização }`.
- **Próximos passos:** item (f), catálogo de erros; item (g), testes de laços e laço infinito.

