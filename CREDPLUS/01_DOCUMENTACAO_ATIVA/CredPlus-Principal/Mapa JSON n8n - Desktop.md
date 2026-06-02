# Mapa JSON n8n - Desktop

## Origem (mesa)
Pasta identificada na mesa com os JSONs de workflow:

`/Users/lellisflaviooliveirasantos/Desktop/.agents/n8n-workflows`

## Arquivos encontrados
1. `w1-vencidos-criticos.json`
2. `w2-vence-hoje.json`
3. `w3-vence-amanha.json`
4. `w4-resumo-diario.json`
5. `workflow-resumo-diario.json`

## Leitura rápida de cada JSON
1. `w1-vencidos-criticos.json`
- Nome: `CredPlus V2 — Vencidos e Críticos`
- Agenda no JSON: 06:00, 10:00, 15:00, 19:00

2. `w2-vence-hoje.json`
- Nome: `CredPlus V2 — Vence Hoje`
- Agenda no JSON: 07:00, 12:00, 18:50

3. `w3-vence-amanha.json`
- Nome: `CredPlus V2 — Vence Amanhã`
- Agenda no JSON: 09:00, 20:00

4. `w4-resumo-diario.json`
- Nome: `CredPlus V2 — Resumo Diário`
- Agenda no JSON: 06:30, 21:00

5. `workflow-resumo-diario.json`
- Nome: `CredPlus - Resumo Diário`
- Agenda no JSON: 06:00, 09:00, 14:00, 17:00, 19:30
- Observação importante: este arquivo contém referência a Supabase antigo (`twmhusiebxxsizftjtdb.supabase.co`), diferente do painel oficial.

## Regra de alinhamento (painel)
- Supabase oficial do painel: `https://xpmbbzjatlmrrpxogibc.supabase.co`
- Fluxos com origem diferente do painel devem ficar fora da operação oficial do `credpluspainel.com`.
- Relatórios do painel devem seguir o formato fixo definido pelo MESTRE.

## Referência de status operacional atual
- Workflows V2 do painel no n8n foram desativados no runtime para zerar integração com n8n do painel.
- Painel segue online e operacional sem n8n.

