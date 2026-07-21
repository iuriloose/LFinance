# LFinance 1.0.5

Sistema financeiro pessoal para Windows.

## Situação do projeto

Versão de manutenção focada em estabilidade e segurança dos dados:

- correções encontradas nos testes reais;
- preservação do histórico de pagamentos;
- backup e restauração validados;
- geração do EXE e do instalador profissional.

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
