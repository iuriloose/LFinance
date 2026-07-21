# AGENTS.md — LFinance

## Produto

O LFinance é um aplicativo desktop de finanças pessoais para Windows. Ele organiza receitas, gastos pagos no dia, contas a pagar, contas fixas, parcelamentos, pagamentos e relatórios mensais.

Trate os dados financeiros como sensíveis. Preserve o comportamento existente e prefira mudanças pequenas, reversíveis e verificáveis.

## Estrutura e tecnologias

- `main.py`: entrada do aplicativo e preparação inicial.
- `telas/`: telas e diálogos PySide6.
- `componentes/`: menu, tabelas e cartões reutilizáveis.
- `banco/banco.py`: esquema SQLite e operações financeiras.
- `servicos/`: configurações, backup, atualização e conversão monetária.
- `modelos/`: modelos de domínio ainda pouco usados.
- `assets/`: marca, ícones e imagens.
- `LFinance.spec`: empacotamento do EXE com PyInstaller.
- `LFinance.iss`: instalador Windows com Inno Setup.
- `requirements.txt`: dependências fixadas.

Stack atual: Python, PySide6, SQLite, python-dateutil, PyInstaller e Inno Setup.

## Dados e segurança

- Banco real do usuário: `%LOCALAPPDATA%\LFinance\lfinance.db`.
- Configuração real: `%LOCALAPPDATA%\LFinance\config.json`.
- Nunca copiar, exibir, consultar linhas, alterar, excluir ou restaurar o banco real em testes.
- Nunca iniciar `main.py` ou o EXE em um teste sem isolar `LOCALAPPDATA`; a inicialização cria tabelas e pode ajustar o esquema.
- Testes devem apontar `LOCALAPPDATA` para uma pasta temporária dedicada e descartável.
- Não usar dados pessoais nos testes. Criar apenas dados fictícios identificados como teste.
- Não executar `limpar_todos_os_dados`, restauração, exclusão ou pagamento contra o perfil real.
- Antes de mudanças em esquema, restauração ou rotinas destrutivas: criar plano de reversão, backup verificado e teste em cópia descartável. Exigir autorização explícita.
- Não guardar segredos, tokens ou credenciais no projeto ou neste arquivo.

## Regras financeiras

- Valores monetários entram por `servicos/valores.py`; não duplicar parsing de moeda nas telas.
- Manter consistência entre despesa, pagamento e histórico.
- Contas fixas avançam um mês após pagamento.
- Parcelamentos avançam parcela e vencimento; a última parcela é encerrada.
- Ao desfazer pagamento recorrente, preservar a ordem histórica e desfazer primeiro o registro mais recente.
- Não inventar categorias, valores, datas, regras comerciais ou dados financeiros.

## Interface

- Manter português do Brasil e linguagem simples.
- Preservar a identidade escura atual, consistência entre telas e contraste legível.
- Reutilizar `componentes/` antes de criar estilos ou widgets duplicados.
- Toda ação destrutiva deve explicar o impacto e exigir confirmação clara.
- Manter navegação por teclado, foco visível, nomes acessíveis e tooltips úteis.
- Validar em pelo menos 1000×620 e na janela maximizada.

## Como executar com segurança

Ambiente de desenvolvimento esperado:

1. Criar e ativar um ambiente virtual.
2. Instalar `requirements.txt` sem atualizar versões implicitamente.
3. Definir `LOCALAPPDATA` para uma pasta temporária exclusiva do teste.
4. Executar `python main.py`.

Nunca use `gerar_exe.bat` como comando de teste rotineiro: ele atualiza o `pip`, instala dependências e apaga `build/` e `dist/` antes de gerar o EXE.

## Testes mínimos antes de concluir uma mudança

- Compilação/importação dos módulos Python.
- Testes unitários do domínio e do banco em SQLite temporário.
- `PRAGMA quick_check` no banco temporário.
- Fluxos fictícios: receita, gasto, conta simples, conta fixa, parcelamento, pagamento e desfazer pagamento.
- Backup e restauração somente entre arquivos temporários.
- Abertura e navegação das nove telas: inicial, pesquisar, receitas, gastos, contas a pagar, contas fixas, parcelamentos, relatórios e configurações.
- Confirmar que o banco real não mudou comparando caminho e data de modificação antes/depois.

## Build e publicação

- EXE: `python -m PyInstaller --clean --noconfirm LFinance.spec`.
- Instalador: compilar `LFinance.iss` no Inno Setup após validar o EXE.
- O build Windows deve ser feito no Windows; PyInstaller não é cross-compiler.
- Antes de publicar, sincronizar versão em `VERSION.txt`, `APP_VERSAO`, `LFinance.iss`, `version_info.txt`, README e CHANGELOG.
- Validar assinatura digital, hash SHA-256, instalação limpa, atualização sobre versão anterior, preservação do banco e desinstalação.
- Publicação é uma etapa separada e exige autorização explícita. Não criar release, tag, instalador público ou upload sem essa autorização.

## Dependências e mudanças estruturais

- Não atualizar dependências, Python, banco ou instalador sem pedido explícito.
- Antes de qualquer upgrade, consultar documentação oficial, notas de versão, compatibilidade, mudanças incompatíveis e plano de reversão.
- Evitar reescritas e substituições de tecnologia sem necessidade demonstrada.

## Estado do repositório

A cópia analisada em `D:\LFinance` não contém metadados Git. Antes de trabalho contínuo, confirmar qual é o repositório oficial e estabelecer versionamento/backup. Nunca presumir que os artefatos em `build/`, `dist/` e `instalador/` correspondem exatamente ao código-fonte atual sem um build reproduzível.
