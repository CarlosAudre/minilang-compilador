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
