LFinance 1.0.1 - Geração do EXE de teste

1. Extraia o ZIP do projeto.
2. Abra a pasta LFinance.
3. Dê dois cliques em:
   gerar_exe.bat

O executável será criado em:
   dist\LFinance.exe

Banco de dados:
- O banco do usuário fica fora da pasta do programa.
- Caminho usado no Windows:
  %LOCALAPPDATA%\LFinance\lfinance.db
- Isso evita perder dados ao trocar/atualizar o EXE.

Observações:
- A pasta assets já está configurada no PyInstaller.
- O ícone do EXE já está configurado.
- Este pacote ainda é para gerar e testar o EXE.
- O instalador profissional entra na próxima etapa, depois do EXE testado.


Desenvolvido por Iuri Loose.
© 2026 Iuri Loose. Todos os direitos reservados.
