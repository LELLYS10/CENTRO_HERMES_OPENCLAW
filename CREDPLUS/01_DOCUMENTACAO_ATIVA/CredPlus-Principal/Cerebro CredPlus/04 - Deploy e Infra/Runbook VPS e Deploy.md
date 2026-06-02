# Runbook VPS e Deploy

## Alvos

- dominio: `credpluspainel.com`
- app principal em container docker
- n8n em container separado

## Checklist antes de deploy

1. revisar alteracoes pendentes no repo.
2. validar regra afetada (juros, parcela, comissao, filtro).
3. testar rota critica em ambiente real com 1 caso.
4. garantir que automacoes nao serao religadas sem intencao.

## Checklist depois de deploy

1. confirmar app responde e redireciona login.
2. testar pagamento de juros.
3. testar contrato editado.
4. testar visao por grupo (especial/A/B/familia).

## Regra de rollback

- manter backup de banco/fluxos antes de mudanca estrutural.
- em bug financeiro, interromper automacoes e corrigir antes de novo disparo.
