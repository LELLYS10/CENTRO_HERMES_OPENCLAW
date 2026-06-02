# Visao Operacional CredPlus

## Objetivo diario

1. Receber pagamentos sem inconsistencias.
2. Manter contratos, juros e comissoes corretos por grupo.
3. Entregar cobranca e relatorios no formato padrao.

## Escopos de operacao

- `especial`: controle total
- `grupo A (socios)`: visao conforme regra do operador
- `grupo B (colaboradores)`: carteira propria + regra de comissao
- `familia`: area restrita e independente

## Rotina operacional minima

1. Conferir status do app e login.
2. Conferir pagamentos do dia e movimentacoes.
3. Conferir contratos criticos/vencidos.
4. Validar comissoes de colaboradores (somente quando `gera_comissao = true`).
5. Fechar resumo diario.

## Alertas de falha conhecidos

- juros reportado em escala errada (ex.: 100x menor)
- contrato editado sem refletir parcelas esperadas
- cliente duplicado por importacao de planilha
- automacao de bot enviando formato divergente
