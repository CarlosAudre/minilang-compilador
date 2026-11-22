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

- ### 19/11: Item (c), parser
- **O que foi feito:** `src/parser.py` (descendente recursivo, uma função por regra da EBNF), 49 testes do parser (válidos e inválidos, incluindo o `for` mal formado) e a seção do relatório com as árvores de derivação, as ASTs, a justificativa formal e a comparação com SLR(1).
- **Uso de IA (Claude):** geração do parser e dos testes; rascunho da seção do relatório.
- **Aceito / reescrito / descartado e por quê:**
  - **Falha da IA:** as árvores do relatório eram só ASTs, e o enunciado do item (c) fala em "árvore sintática"; acrescentamos as árvores de derivação (concretas) para cobrir as duas leituras.
  - Mantivemos `comparacao` com `[ ]` (não encadeia) e rejeitamos `-5`, por não haver menos unário.
- **Dificuldades:** entender por que cada operador fica em um nível da gramática e como a hierarquia de funções vira precedência.

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

### 22/11: Item (f), catálogo de erros
- **O que foi feito:** pasta `exemplos/erros/` com 10 programas (3 léxicos, 3 sintáticos, 4 semânticos), incluindo `for` sem atualização, `while` sem bloco, `while` com condição `int` e variável de controle não definida; catálogo (mensagem, causa, exemplo) e justificativa da estratégia fail-fast em `docs/relatorio_letras_f_g.md`; `tests/invalidos/test_catalogo_erros.py` executa cada arquivo pela linha de comando e confere código de saída 1 e a mensagem.
- **Uso de IA (Claude):** geração dos programas de erro, do teste do catálogo e do rascunho do catálogo e da justificativa.
- **Aceito / reescrito / descartado e por quê:**
  - Aceito: um arquivo de teste por categoria já existia (`test_lexer_invalido`, `test_parser_invalido`, `test_interpreter_invalido`), cada um com o resultado esperado no topo; o novo teste só cobre a execução de ponta a ponta.
  - Decisão: estratégia fail-fast (parar no primeiro erro), sem recuperação em modo pânico, porque erros em cascata confundem o iniciante.
  - Limitação aceita: verificação semântica dinâmica; erro de tipo dentro de `if (false)` não é detectado.
- **Dificuldades:** separar o que é erro léxico (`1x`) do que seria erro sintático.

### 22/11: Item (g), suíte de testes e relatório
- **O que foi feito:** `tests/validos/test_lacos.py` (laço que não executa, executa 1 vez, executa N vezes, `for` com passo diferente de 1, equivalência `for` e `while`, aninhamento) e `tests/invalidos/test_laco_infinito.py` (limite de iterações em `while` e `for`, borda do limite, contador por laço). A suíte passou de 126 para 169 testes, todos passando.
- **Uso de IA (Claude):** geração dos testes de laços e de laço infinito; rascunho da seção do relatório e da tabela de fundamentação teórica.
- **Aceito / reescrito / descartado e por quê:**
  - Aceito: limite pequeno (5 a 100) nos testes, para a suíte não travar nem demorar.
  - Pendente do grupo: conferir os exemplos de acertos e falhas do relatório (o quinto está em branco) e passar `docs/relatorio_letras_f_g.md` para o `docs/relatorio.pdf`, que deve ter de 2 a 3 páginas na Parte A.
- **Próximos passos:** vídeo de 5 minutos (`docs/apresentacao.mp4`), preencher o link no README, atualizar `declaracao_IA.md`.
