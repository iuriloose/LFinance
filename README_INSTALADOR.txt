LFinance 1.0.3 - Instalador Windows

Como gerar o instalador final:

1. Confirme que o EXE já existe em:
   dist\LFinance.exe

2. Abra o arquivo:
   LFinance.iss

3. No Inno Setup, clique em:
   Build > Compile

4. O instalador será gerado em:
   instalador\LFinance_Setup_v1.0.3.exe

O instalador final:
- Instala o LFinance em C:\Program Files\LFinance.
- Cria atalho no Menu Iniciar.
- Cria atalho na Área de Trabalho automaticamente.
- Registra o desinstalador no Windows.
- Mantém os dados do usuário em %LOCALAPPDATA%\LFinance.
- A desinstalação remove o programa, mas não apaga os dados financeiros do usuário.

Observação importante:
Se já existir um instalador antigo na pasta instalador, ele será substituído quando você compilar novamente.


Desenvolvido por Iuri Loose.
© 2026 Iuri Loose. Todos os direitos reservados.
