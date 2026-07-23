# LFinance 1.0.7

## 1.0.7

- Aplicada a nova identidade visual oficial no programa, no executável e no instalador.
- Padronizados os arquivos de logo usados pela janela, menu lateral, PyInstaller e Inno Setup.
- Reorganizada a apresentação da tela Relatórios para exibir informações mais úteis e consistentes.
- Corrigida a seção Parcelamentos em aberto para considerar todos os parcelamentos ativos, mesmo quando a próxima parcela vence fora do mês selecionado.
- Adicionados parcela atual, quantidade restante, próximo vencimento e valor total restante aos parcelamentos exibidos nos relatórios.
- Melhorados os textos de estados vazios e os totais das listas do relatório.

## 1.0.6

- Adicionados testes automatizados que usam somente banco temporário.
- Restauração de backup agora usa troca atômica e recuperação automática em caso de falha.
- Limpeza total agora cria e valida um backup automático antes de apagar dados.
- Validação de backup agora verifica integridade, tabelas e colunas essenciais.
- Salvamento das configurações agora protege contra arquivos parcialmente gravados.
- A inicialização repetida não regrava um banco já atualizado, preservando o arquivo quando nenhum dado mudou.
- Melhorados o tratamento de bloqueios do SQLite e a acessibilidade do menu.
- Tabelas de contas e parcelamentos agora adaptam colunas em janelas estreitas sem cortar os botões de ação.
- O roteiro do instalador agora aceita caminhos separados para builds beta sem sobrescrever os artefatos atuais.
- O instalador não cria dados no perfil administrativo e abre o aplicativo no perfil normal do usuário.
- Centralizado o conteúdo das tabelas de receitas, gastos, contas, contas fixas, parcelamentos e pesquisa.
- Padronizada a largura da coluna Situação para manter Em aberto em uma linha.
- Reforçada a atualização automática para aceitar somente o instalador HTTPS oficial da Release correspondente.
- Adicionados testes para versões, seleção segura do instalador e acionamento automático da verificação.

## 1.0.5

- Padronizadas as telas A pagar, Receitas, Gastos do dia, Contas a pagar, Contas fixas e Parcelamentos.
- Substituídos os cartões grandes por tabelas compactas e consistentes.
- Criada uma tela exclusiva de pesquisa para contas, gastos do dia e receitas.
- Reorganizada a tela Pago no mês em uma lista única, compacta e mais legível.
- Adicionadas a coluna Categoria e a seleção múltipla com somador dinâmico em Pago no mês.
- Ajustado o aproveitamento de espaço nas telas Contas a pagar e Contas fixas.
- Ajustadas as cores laterais dos cartões de saídas para vermelho.
- Corrigido o tamanho da seta do filtro na tela Pesquisar.
- Preservadas as ações de pagar, reabrir, desfazer, editar e excluir.

## 1.0.4

- Adicionada soma dinâmica das contas selecionadas em Próximos vencimentos.
- Adicionada seleção múltipla com Ctrl, Shift ou arraste.
- Adicionado botão para selecionar automaticamente as contas do próximo mês.
- Adicionado botão para limpar a seleção e zerar o total.
- Compactada a lista inicial para exibir mais contas sem reduzir a legibilidade.

## 1.0.3

- Adicionada janela para informar o valor e a data real do pagamento.
- Adicionado cálculo automático de juros, multas e descontos.
- Incluído resumo mensal de acréscimos e descontos nos relatórios.
- Adicionados totais nas telas de gastos, despesas, contas e parcelamentos.
- Mantido o valor original das contas fixas e parcelas futuras.
- Adicionado botão para desfazer o último pagamento de uma conta fixa.
- Adicionada escolha para manter ou estornar o pagamento ao excluir uma conta fixa.
- Contas fixas agora são identificadas como FIXA na coluna Parcela da tela inicial.
- Reorganizada a janela de pagamento para destacar juros, desconto e total sem sobreposição.
- Cards de juros e descontos nos relatórios agora abrem os pagamentos detalhados.
- Removidas as setas do campo de valor final pago.
- Padronizadas as confirmações de estorno e exclusão de contas fixas.
- Confirmações de contas fixas substituídas por janelas compactas e proporcionais.

## 1.0.2

- Publicação oficial das correções de estabilidade, segurança, backup e consistência financeira.
- Versão incrementada para preservar a tag 1.0.1 já publicada anteriormente.

## 1.0.1

- Corrigido o desfazer pagamento de contas fixas e parcelamentos.
- Protegido o histórico ao excluir lançamentos recorrentes.
- Removidas duplicações internas da tela inicial.
- Corrigido o período das contas atrasadas e parcelamentos nos relatórios.
- Adicionada validação dos arquivos de backup antes da restauração.
- Padronizada a leitura de valores monetários e bloqueados valores inválidos.
- Atualizada a identificação da versão e fixadas as dependências de geração.

### Verificação automática de atualizações

- Adicionada a opção "Não avisar novamente para esta versão" no aviso automático.
- A verificação manual continua disponível em Configurações mesmo quando uma versão foi ignorada.
- O LFinance consulta a última Release publicada no GitHub ao iniciar.
- Quando existe uma versão mais nova, exibe um aviso com botão para baixar o instalador.
- Adicionado botão "Verificar atualizações" em Configurações > Sobre o LFinance.
- Falhas de conexão durante a verificação automática não interrompem a abertura do programa.
