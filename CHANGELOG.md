# LFinance 2.1.1

## 2.1.1

- Substitui as barras horizontais por gráfico vertical de gastos por categoria nos últimos seis meses.
- Cada barra abre os lançamentos completos do mês e da categoria selecionados.
- Elimina a rolagem horizontal da tela de Relatórios.
# LFinance 2.1.0

## 2.1.0

- Simplifica Relatórios com quatro indicadores, comparação de gastos entre meses e categorias clicáveis para abrir os lançamentos.
- Mantém alertas apenas quando há algo que exige atenção e resume o planejamento do mês.

# LFinance 2.0.10

## 2.0.10

- Ajusta a largura responsiva da lista de Valores a receber para evitar rolagem horizontal e manter as acoes visiveis.

# LFinance 2.0.9

## 2.0.9

- Compacta os indicadores e os controles de Valores a receber para deixar mais espaco visivel para a lista.

# LFinance 2.0.8

## 2.0.8

- Reorganiza Valores a receber para priorizar a lista, com cartões compactos e navegação mensal integrada ao cabeçalho da lista.
- Aumenta as linhas da tabela para facilitar a leitura dos lançamentos.

# LFinance 2.0.7

## 2.0.7

- Deixa os cartões de Valores a receber no formato compacto da Tela inicial.
- Permite navegar entre meses para consultar os indicadores de previsto e recebido do período escolhido.

# LFinance 2.0.6

## 2.0.6

- Transforma Valores a receber em painel de acompanhamento, com total pendente, previsto no mês, atrasados e recebido no mês.
- Mantém a Tela inicial como painel financeiro principal e separa os indicadores de recebimentos.

# LFinance 2.0.5

## 2.0.5

- Restaura a visualização completa dos detalhes de Valores a receber, com seis campos legíveis e sem marcações técnicas.

# LFinance 2.0.4

## 2.0.4

- Destaca o seletor de lançamentos em Valores a receber.
- Padroniza o formulário e as confirmações da área Valores a receber.
- Corrige a formatação dos detalhes abertos por duplo clique.

# LFinance 2.0.3

## 2.0.3

- Adicionado botão visível para desfazer o último recebimento em Valores a receber.
- Bloqueada a confirmação duplicada no diálogo de recebimento.
- Corrigidos os textos, ícones, acentuação e contagens da tela Relatórios.

## 2.0.2

- Restaurada a tela Relatórios com resumo mensal de receitas, pagamentos, pendências e atrasos.
- Adicionados valores previstos a receber, recebimentos atrasados e resultado planejado sem alterar o saldo real.
- Integrada a décima tela ao menu e ampliada a cobertura de testes.

## 2.0.1

- Adicionada a frequência quinzenal para valores recorrentes, criando a próxima previsão 15 dias depois.
- No recebimento, agora é possível informar um valor maior que o previsto; o lançamento atual é ajustado ao valor real sem alterar a previsão da próxima recorrência.
- Ao desfazer esse recebimento, o valor previsto original é restaurado com segurança.

## 2.0.0

- Adicionada a tela Valores a receber, acessível pelo menu abaixo de Receitas.
- Criado cadastro de salários, comissões, vendas, empréstimos e outros valores previstos.
- Adicionados recebimentos totais e parciais com histórico por pessoa ou empresa.
- Cada recebimento confirmado gera automaticamente uma Receita vinculada.
- Valores pendentes não alteram o saldo nem os cálculos da Tela inicial.
- Adicionada recorrência mensal com criação automática da próxima competência.
- Adicionados estados Em aberto, Parcial, Atrasado, Recebido e Cancelado.
- Incluídos Valores a receber na pesquisa global e na limpeza total protegida.
- Mantida compatibilidade com backups criados pela versão 1.0.7.

## 1.0.7

- Aplicada a nova identidade visual oficial no programa, no executável e no instalador.
- Padronizados os arquivos de logo usados pela janela, menu lateral, PyInstaller e Inno Setup.
- Removida a tela Relatórios, que repetia informações já disponíveis nas telas principais e dificultava a leitura.
- Simplificado o menu lateral para manter somente as funções essenciais do controle financeiro.
- Preservados todos os dados, históricos, pagamentos e parcelamentos; apenas a tela redundante foi retirada.

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
