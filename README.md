# LFinance 2.0.4

Sistema financeiro pessoal para Windows.

## Situação do projeto

Versão 2.0 em desenvolvimento, baseada na versão estável 1.0.7:

- nova tela Valores a receber, sem alterar a Tela inicial;
- controle por pessoa ou empresa, previsão, categoria e situação;
- recebimentos totais, parciais ou acima do previsto, vinculados automaticamente a Receitas;
- recorrência quinzenal ou mensal, com histórico preservado;
- compatibilidade com backups da versão 1.0.7;
- testes executados somente em perfil temporário.

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
