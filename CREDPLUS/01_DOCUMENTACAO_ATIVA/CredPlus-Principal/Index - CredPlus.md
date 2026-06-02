# CREDPLUS — INDICE MESTRE

## 1. Visão Geral

O `CredPlus` é o sistema central de gestão de empréstimos, carteira, vencimentos, recebimentos, comissões, pré-cadastros e leitura operacional.

### Cérebro dedicado (novo)

[[10 - Projetos/CredPlus/Cerebro CredPlus/00 - INDEX - Cerebro CredPlus|Cerebro CredPlus]]

Hoje o projeto já tem:

- painel web em produção
- Supabase como banco oficial
- área de IA no painel
- estrutura pensada para Telegram
- documentação de arquitetura e operação no Obsidian

---

## 2. Decisão Atual

### Stack principal recomendada

[[10 - Projetos/CredPlus/Stack Final Recomendada - CredPlus|Stack Final Recomendada - CredPlus]]

Resumo da decisão atual:

- `CredPlus Painel` como centro da operação
- `Supabase` como fonte oficial dos dados
- `Claude` como IA principal
- `Telegram` como canal principal
- `OpenClaw` fora do núcleo por enquanto

---

## 3. Arquitetura Principal

### Automação e notificações

[[10 - Projetos/CredPlus/Arquitetura - Automação e Notificações|Arquitetura - Automação e Notificações]]

Essa nota define:

- separação por carteiras
- regra de classificação operacional
- visão `LELLIS`, `SOCIOS` e `COLABORADORES`
- `n8n` como motor futuro de automação
- `Telegram` como canal principal

### Hercules + Telegram + IA do painel

[[10 - Projetos/CredPlus/Arquitetura - Hercules + Telegram + IA do Painel|Arquitetura - Hercules + Telegram + IA do Painel]]

Essa nota define:

- papel do `Hercules`
- papel do `Telegram`
- papel da IA do painel
- endpoints que a camada conversacional deve consumir
- regra de isolamento entre projetos

---

## 4. IA do Sistema

### Estado atual

A IA do painel já consegue:

- gerar leitura visual com dados reais
- separar relatório por escopo
- mostrar cards, listas e resumo
- gerar HTML simples para Telegram

### Escopos atuais

- `sistema`
- `lellis`
- `socios`
- `colaboradores`

### Observação importante

A IA do painel lê dados reais do sistema, mas ainda não é um chat livre completo.

Ela está hoje em modo:

- relatório visual
- resumo operacional
- leitura por escopo

---

## 5. Operação e Ambiente

### Status de ambientes

[[10 - Projetos/CredPlus/Status de Ambientes - CredPlus Painel e EMP|Status de Ambientes - CredPlus Painel e EMP]]

### Fontes reais na mesa

[[10 - Projetos/CredPlus/Mapa de Fontes - Desktop|Mapa de Fontes - Desktop]]

### Mapas e fluxos n8n

[[10 - Projetos/CredPlus/Mapa JSON n8n - Desktop|Mapa JSON n8n - Desktop]]

### OpenClaw

[[10 - Projetos/CredPlus/Arquitetura OpenClaw 24-7 - Painel|Arquitetura OpenClaw 24-7 - Painel]]

Observação:

- manter apenas como estudo e laboratório por enquanto
- não usar como centro da operação atual

---

## 6. Documentos Técnicos

- [[10 - Projetos/CredPlus/Migração de Estorno SQL|Migração de Estorno SQL]]
- [[10 - Projetos/CredPlus/Cobranca Semanal - Implementacao|Cobranca Semanal - Implementacao]]
- [[10 - Projetos/CredPlus/Importacao JEAN + Busca em Contratos|Importacao JEAN + Busca em Contratos]]

---

## 7. Documentos de Estratégia

- [[10 - Projetos/CredPlus/Arquitetura Painel + Agentes + WhatsApp|Arquitetura Painel + Agentes + WhatsApp]]
- [[10 - Projetos/CredPlus/Cowork Package|Cowork Package]]

---

## 8. Próximos Passos Recomendados

### Ordem ideal

1. consolidar `Painel + IA visual`
2. amadurecer `HTML para Telegram`
3. criar `chat inteligente` dentro do painel
4. integrar uma camada conversacional estável
5. automatizar com `n8n` só depois da regra estar fechada

### Evitar agora

- misturar com `credplusemp.com.br`
- usar `OpenClaw` como peça principal
- confiar automação crítica a agente instável

---

## 9. Referências úteis

- [[30 - Prompts/Manual de Regras CredPlus V2|Manual de Regras CredPlus V2]]
- [[20 - Skills/Skill - Análise de Crédito|Skill de Análise de Crédito]]

---

Retornar ao [[10 - Projetos/Index - Projetos|Índice de Projetos]]
