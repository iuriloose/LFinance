# LFinance 1.0.6

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

## Atualizações

Ao iniciar, o LFinance consulta automaticamente a Release mais recente no repositório oficial.
Se houver uma versão nova, mostra as novidades e oferece o instalador oficial somente após confirmação do usuário.
A verificação manual continua disponível em Configurações > Sobre o LFinance.

## Gerar EXE

Execute sem atualizar dependências implicitamente:

`python -m PyInstaller --clean --noconfirm LFinance.spec`

O arquivo final será criado em:

`dist\LFinance.exe`

## Testes seguros

Os testes usam um perfil temporário e nunca apontam para o banco real do usuário:

`python -m unittest discover -s tests -v`


Desenvolvido por Iuri Loose.
© 2026 Iuri Loose. Todos os direitos reservados.
