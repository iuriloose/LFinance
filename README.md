# LFinance 1.0

Sistema financeiro pessoal para Windows.

## Situação do projeto

Funcionalidades encerradas. Esta fase é focada apenas em distribuição:

- organização do projeto;
- geração do EXE de teste;
- correções encontradas em testes;
- preparação do instalador profissional;
- validação em outro computador;
- lançamento da versão 1.0.

## Banco de dados

O banco do usuário não deve ficar dentro da pasta do programa instalado.

No Windows, o LFinance usa:

`%LOCALAPPDATA%\LFinance\lfinance.db`

Isso evita perda de dados ao atualizar ou substituir o executável.

## Gerar EXE

Execute:

`gerar_exe.bat`

O arquivo final será criado em:

`dist\LFinance.exe`


Desenvolvido por Iuri Loose.
© 2026 Iuri Loose. Todos os direitos reservados.
