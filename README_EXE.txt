LFinance - Geração do executável

Para gerar uma nova versão do executável:

1. Confirme que o código-fonte foi testado com:
   python main.py

2. Gere o executável com:
   python -m PyInstaller --clean --noconfirm LFinance.spec

3. O executável será criado em:
   dist\LFinance\LFinance.exe

Importante:
- Não atualize dependências durante o processo de build.
- Teste o EXE antes de gerar o instalador.
- Os dados do usuário ficam em:
  %LOCALAPPDATA%\LFinance

Desenvolvido por Iuri Loose.
© 2026 Iuri Loose.