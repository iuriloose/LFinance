# Contrato de sincronização LFinance v1

Esta camada não sincroniza dados reais ainda. Ela define o mesmo significado para Desktop e Mobile.

## Regras obrigatórias

- Desktop e Mobile continuam funcionando offline e de forma independente.
- Valores monetários trafegam como centavos inteiros; nunca como `float`.
- Datas usam `YYYY-MM-DD`; horários usam ISO-8601 UTC.
- IDs de sincronização são globais e não dependem do ID numérico do Desktop.
- Conta (`payable`) e pagamento (`payment`) são registros diferentes.
- Valor a receber (`receivable`) e recebimento (`receipt`) são registros diferentes.
- Gasto rápido é `expense`; receita avulsa é `income`.
- Exclusões trafegam como marcadores (`deleted_at`) para não ressuscitar registros.
- Importação bidirecional permanece desativada até existir controle de revisão e conflitos.

## Política de conflitos prevista

- Alteração simultânea nos dois aparelhos não será sobrescrita silenciosamente.
- Exclusão concorrente com edição exigirá escolha do usuário.
- Pagamentos e recebimentos serão tratados como eventos vinculados, permitindo desfazer com segurança.
- Duplicações serão impedidas por `id`, não por descrição ou valor.

## Pareamento futuro

O transporte poderá usar código temporário e chave de recuperação, sem exigir telefone ou e-mail. O transporte será independente do contrato, permitindo trocar o serviço de nuvem sem reescrever as regras financeiras.