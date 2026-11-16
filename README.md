# MiniLang — Compilador-Interpretador

Projeto da disciplina Linguagens Formais e Compiladores (UNIT, Ciência da Computação).

## Integrantes
- Nome 1
- Nome 2
- Nome 3

## Ferramenta de IA utilizada
Claude (Anthropic). Detalhes em [declaracao_IA.md](declaracao_IA.md).

## Requisitos
- Python 3.10 ou superior

## Instalação
```bash
pip install -r requirements.txt
```

## Executando um programa MiniLang
```bash
python -m src.interpreter exemplos/programa_valido.ml
python -m src.interpreter exemplos/programa_invalido.ml
```

## Executando os testes
```bash
pytest
```

## Estrutura
- `src/`: lexer, parser, AST e interpretador
- `tests/`: suíte de testes (`validos/` e `invalidos/`)
- `exemplos/`: programas MiniLang de demonstração
- `docs/`: gramática, diário de bordo, relatório e vídeo

## Vídeo de apresentação
`docs/apresentacao.mp4` (ou link público: _preencher_)