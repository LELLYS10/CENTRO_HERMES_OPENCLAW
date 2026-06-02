# Regras Criticas de Negocio

## Juros

- base deve usar dados reais do contrato ativo.
- validar escala da taxa antes de calcular (formato percentual x decimal).

## Comissao

- grupo B: somente se `gera_comissao = true`.
- cabeca/autoemprestimo: comissao desligada.
- valor de comissao deve nascer do juros, nao do capital.

## Cliente e contrato

- cliente com contrato ativo nao pode ser excluido.
- exclusao so apos quitacao total (regra de seguranca operacional).
- em merge de cliente duplicado: mover contratos para cadastro principal e inativar duplicado.

## Parcelas e recebimentos

- pagamento precisa de consistencia completa (parcela, recebimento, contrato, historico).
- evitar estado parcial em caso de falha.
