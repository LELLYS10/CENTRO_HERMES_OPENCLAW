# Mapa de Automacoes e Bots

## Estado atual (controle)

- n8n CredPlus pode operar vazio por decisao de limpeza.
- bots devem ficar desligados ate ordem explicita.
- PM2 e cron de disparo precisam de revisao antes de religar.

## Canais

- Telegram: extratos e alertas operacionais
- WhatsApp: envio orientado por fluxo do painel

## Formato padrao de extrato

Seguir o template de cobranca por responsavel:

- VENCIDOS
- VENCE HOJE
- VENCE AMANHA
- CRITICOS
- TOTAL PENDENTE

Com cliente + juros (sem capital no formato de cobranca quando essa for a regra ativa).

## Regra de acionamento

1. nunca religar automacao sem checklist de teste.
2. validar em 1 responsavel antes de liberar geral.
3. confirmar data de referencia no disparo.
