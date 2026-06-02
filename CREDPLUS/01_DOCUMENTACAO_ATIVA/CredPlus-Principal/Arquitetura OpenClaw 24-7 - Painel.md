# Arquitetura OpenClaw 24-7 - Painel

## Objetivo
Transformar o OpenClaw na camada operacional 24/7 do `credpluspainel.com`, com monitoramento contínuo, relatórios automáticos e execução de comandos operacionais com segurança.

## Visão Geral
- `Painel (API)` = fonte única de verdade
- `OpenClaw Worker` = leitura, classificação, decisão e execução
- `Telegram` = canal de comando e alertas
- `Auditoria` = registro completo das ações

## Arquitetura Proposta
1. Painel (`credpluspainel.com`)
- APIs já existentes para clientes, contratos, recebimentos, amortizações e comissões.

2. OpenClaw Worker
- Rotinas agendadas (scheduler)
- Executor de comandos
- Camada de validação

3. Canal Telegram
- Entrada de comandos
- Saída de alertas e relatórios

4. Log/Auditoria
- Registro de `quem`, `quando`, `o que`, `antes/depois`

## Módulos do OpenClaw
1. `Collector`
- Busca dados no painel: vencidos, vence hoje, vence amanhã, críticos, novos cadastros.

2. `Classifier`
- Aplica prioridade operacional: `crítico > vencido > hoje > amanhã`.

3. `Reporter`
- Monta relatório em formato fixo e envia no Telegram.

4. `Command Router`
- Interpreta comando e mapeia para ação do painel.

5. `Executor`
- Executa ações de escrita nas APIs com validação.

6. `Guardrails`
- Idempotência, confirmação de ações sensíveis, controle de falhas.

## Relatórios 24/7 (proposta)
1. `07:00` - Abertura
- Vencidos, vence hoje, críticos, contratos ativos, alertas.

2. `12:00` - Pulso
- Mudanças desde a manhã e pendências em aberto.

3. `18:00` - Fechamento
- Pagamentos do dia, novas entradas, críticos remanescentes, próxima ação sugerida.

4. Tempo real
- Alertas de novos críticos e falhas de integração.

## Comandos Telegram (proposta)
1. `/resumo`
- Resumo operacional atual.

2. `/vencidos`, `/hoje`, `/amanha`, `/criticos`
- Listas filtradas.

3. `/cliente novo ...`
- Pré-cadastro/cadastro de cliente.

4. `/emprestimo novo ...`
- Criação de contrato.

5. `/parcela quitar ...`
- Quitação de parcela (com confirmação).

6. `/recebimento registrar ...`
- Registro de pagamento, mantendo capital e juros separados.

7. `/amortizacao ...`
- Amortização com recálculo conforme regra do painel.

## Regras de Segurança
1. Escrita exige confirmação explícita (`CONFIRMAR <id>`).
2. Reenvio não duplica operação (idempotency key).
3. Se API falhar ou houver inconsistência, OpenClaw não grava.
4. Toda ação gera log auditável.

## Operação no Dia a Dia
- Relatório pronto no início do dia.
- Alertas apenas quando relevante.
- Comandos operacionais via Telegram, sem depender de navegação manual para tudo.
- Painel segue como base oficial de dados.

## Fases de Execução (sem implementar nesta etapa)
1. Fase 1
- Monitoramento e relatórios (somente leitura).

2. Fase 2
- Comandos de escrita básicos (cadastro, empréstimo, recebimento).

3. Fase 3
- Ações sensíveis com dupla confirmação (quitação, amortização, estorno).

4. Fase 4
- Indicadores executivos e rotina de saúde do sistema.

## Critério de Aceite por Fase
- Cada fase só avança após validação em ambiente real com checklist aprovado.

## Referências (Obsidian)
- Mapa dos JSONs na mesa: `Mapa JSON n8n - Desktop.md`
- Status dos ambientes e portas: `Status de Ambientes - CredPlus Painel e EMP.md`
