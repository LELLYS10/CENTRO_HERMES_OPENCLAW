# Cobrança Semanal - Implementação

Data: 2026-05-03

## Objetivo
Adicionar uma forma de cobrança semanal ao painel CredPlus sem quebrar a lógica mensal existente.

## Regra Mantida
- A lógica financeira principal do contrato continua mensal.
- Exemplo base:
  - capital: R$ 1.500,00
  - taxa: 12% ao mês
  - juros mensal base: R$ 180,00
- Comissão do colaborador grupo B continua incidindo somente sobre `juros_recebido`.
- Exemplo Jean:
  - 25% de R$ 180,00 = R$ 45,00 por ciclo mensal conveniente.

## Estratégia Técnica
- A cobrança semanal foi implementada por baixo como `parcelado`.
- O painel grava metadados em `observacoes` com prefixo interno `[[CREDPLUS_META:...]]`.
- Isso preserva compatibilidade com o restante do sistema.

## Metadados
- `cobranca: semanal`
- `total_semanas`
- `juros_mensal_base`

## Regras da Geração Semanal
- O usuário informa o total de semanas.
- O sistema considera 4 semanas = 1 mês.
- Fórmula do período:
  - meses inteiros = `floor(semanas / 4)`
  - semanas extras = `semanas % 4`
  - fator do período = `meses + semanas_extras / 4`
- O sistema distribui capital + juros do período nas parcelas semanais.
- A última parcela recebe o ajuste de centavos.

## Comissão
- Não foi criada comissão paralela nova.
- A comissão continua sendo gerada no recebimento, exclusivamente sobre `juros_recebido`.
- No semanal, como o juros da parcela é proporcional, a soma natural do mês respeita o teto mensal combinado.

## UI
- Nova opção visual no contrato:
  - `Cobrança Semanal`
- Cor própria do semanal: âmbar.
- Locais com destaque visual:
  - criação de contrato
  - edição de contrato
  - dashboard
  - lista de contratos
  - detalhe do contrato
  - perfil do cliente

## Recebimentos
- `somente_juros` em contrato semanal empurra o cronograma em 7 dias.
- `somente_juros` em contrato mensal continua empurrando 1 mês.

## Observações
- `Família` não foi alterada como regra de negócio.
- A modalidade semanal aproveita o fluxo seguro já existente de parcelas, recibos, dashboard e status.

## Rollback
- Existe backup do estado anterior na VPS em `/root/credplus-backups/`.
