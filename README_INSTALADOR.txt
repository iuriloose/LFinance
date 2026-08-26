LFinance - Geração do instalador Windows

Antes de gerar o instalador:

1. Teste o código:
   python main.py

2. Gere um EXE novo:
   python -m PyInstaller --clean --noconfirm LFinance.spec

3. Teste:
   dist\LFinance\LFinance.exe

4. Gere o instalador:
   & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" ".\LFinance.iss"

O instalador será criado na pasta:
   instalador\

Importante:
- Sempre faça um novo build antes de publicar uma versão.
- Nunca presuma que dist\ contém o código atual.
- Teste o instalador localmente antes de enviar para o GitHub.
- Os dados do usuário em %LOCALAPPDATA%\LFinance não devem ser removidos durante atualizações.

Desenvolvido por Iuri Loose.
© 2026 Iuri Loose.