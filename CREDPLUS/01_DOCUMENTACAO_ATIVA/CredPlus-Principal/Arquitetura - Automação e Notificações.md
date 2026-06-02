# ARQUITETURA CREDPLUS — SISTEMA DE AUTOMAÇÃO E NOTIFICAÇÕES

**Versão:** 2.0  
**Data:** 03/05/2026  
**Status:** arquitetura operacional revisada para o sistema real

---

## 1. Objetivo

Estruturar o CredPlus para gerar leitura operacional automática, relatórios padronizados e notificações sem misturar carteiras.

O foco é:

- separar leitura por carteira operacional
- classificar vencimentos com regra fixa
- enviar relatórios no Telegram
- manter WhatsApp como extensão futura
- usar o painel como fonte principal da operação

---

## 2. Fluxo Principal

```text
CredPlus Painel
    ->
Supabase
    ->
n8n
    ->
Telegram
```

Camada de apoio:

```text
Claude
    ->
consulta, resumo, comando manual e leitura operacional
```

Princípio:

- o painel e o banco guardam a verdade
- o n8n automatiza
- o Telegram recebe os alertas
- o agente consulta e organiza, mas não substitui a regra central

---

## 3. Infraestrutura Atual

**VPS:** `72.61.60.213`

**Containers ativos principais:**

- `credplus-app`
- `n8n-credplus-n8n-1`
- `traefik-wvkg-traefik-1`
- `evolution-api-evolution-1`

**Domínios principais:**

- painel: `https://credpluspainel.com`
- n8n: `https://n8n-credplus.srv1416255.hstgr.cloud`

**Banco principal:**

- Supabase `xpmbbzjatlmrrpxogibc.supabase.co`

---

## 4. Fonte Oficial dos Dados

O sistema deve usar como base principal:

- `profiles`
- `clientes`
- `contratos`
- `parcelas`
- `recebimentos`
- `pre_cadastros`

### Estrutura real importante

**profiles**
- define o responsável e o grupo
- grupos reais do sistema:
  - `especial`
  - `a`
  - `b`
  - `familia`
  - `admin`

**clientes**
- cada cliente aponta para `responsavel_id`

**contratos**
- cada contrato aponta para `responsavel_id`
- campos importantes:
  - `capital_atual`
  - `capital_inicial`
  - `status`
  - `proximo_vencimento`
  - `taxa_juros_mensal`
  - `observacoes`

**parcelas**
- estrutura real do sistema:
  - `capital_parcela`
  - `juros_parcela`
  - `data_vencimento`
  - `status`
- nao usar modelo simplificado de `valor` e `pago=true/false`

**recebimentos**
- base real para juros recebidos
- campos importantes:
  - `capital_recebido`
  - `juros_recebido`
  - `data_recebimento`
  - `tipo`

---

## 5. Carteiras Operacionais

Os relatórios nao devem sair por grupo bruto apenas.  
Devem sair por carteira operacional, sem mistura.

### Carteiras principais

**1. LELLIS**
- dono
- visao executiva
- recebe consolidado da operação
- area de IA exclusiva no painel

**2. SOCIOS**
- carteira do grupo `a`
- pode ser:
  - consolidada em um bloco unico
  - ou separada por responsavel, se necessario depois

**3. COLABORADORES**
- carteira do grupo `b`
- mesma logica:
  - consolidada em um bloco unico
  - ou separada por responsavel depois

### Regra principal

O relatorio deve manter sempre o mesmo formato:

- `LELLIS`
- `SOCIOS`
- `COLABORADORES`

Sem misturar contratos de uma carteira na outra.

---

## 6. Classificação Operacional

Padrao fixo para leitura:

- `CRITICOS` = vencidos ha 5 dias ou mais
- `VENCIDOS` = vencidos entre 1 e 4 dias
- `VENCE HOJE`
- `VENCE AMANHA`
- `CADASTROS` = novos pre-cadastros ou novos registros do periodo

### Ordem de prioridade

```text
critico
-> vencido
-> vence hoje
-> vence amanha
-> cadastro
```

---

## 7. Relatório Diário

Horario sugerido inicial:

- `08:00`

Motor:

- `n8n`

Destino:

- `Telegram`

### Formato ideal

```text
RELATORIO LELLIS

CRITICOS: X
VENCIDOS: X
VENCE HOJE: X
VENCE AMANHA: X
CADASTROS: X

---

RELATORIO SOCIOS

CRITICOS: X
VENCIDOS: X
VENCE HOJE: X
VENCE AMANHA: X
CADASTROS: X

---

RELATORIO COLABORADORES

CRITICOS: X
VENCIDOS: X
VENCE HOJE: X
VENCE AMANHA: X
CADASTROS: X
```

### Conteudo esperado por bloco

Cada bloco pode trazer:

- quantidade
- valor total
- nomes principais
- datas
- observacoes curtas

---

## 8. Comandos Operacionais

Comandos desejados no Telegram ou via agente:

- `/lellis`
- `/socios`
- `/colaboradores`
- `/criticos`
- `/vencidos`
- `/hoje`
- `/amanha`
- `/cadastros`
- `/resumo`

### Perguntas naturais aceitas

- "quem vence hoje?"
- "me manda os criticos"
- "quais vencidos do grupo b?"
- "me passa o resumo dos socios"

---

## 9. Papel de Cada Tecnologia

**Painel CredPlus**
- operacao principal
- cadastro
- contratos
- recebimentos
- leitura visual humana

**Supabase**
- fonte oficial dos dados
- persistencia
- consulta operacional

**n8n**
- agendamento
- consulta
- classificacao
- formatacao dos relatórios
- envio Telegram
- webhook futuro para eventos

**Telegram**
- canal principal de notificacao do dono
- recebe relatorios e alertas

**OpenClaw**
- opcional
- nao e obrigatorio para a automacao principal
- pode existir como camada futura ou secundaria, se fizer sentido
- nao deve ser requisito para o CredPlus operar

**Claude**
- camada principal de IA
- consulta, analise, resumo e apoio operacional
- ajuda a interpretar dados reais do painel e do n8n
- nao substitui a regra central da automacao, mas e a IA principal da operacao

**Evolution API / WhatsApp**
- camada futura
- ideal para comprovantes e notificacoes externas
- nao deve ser a primeira camada operacional

---

## 10. O Que Ja Existe

Ja existe no ecossistema:

- painel online
- Supabase operando
- n8n na VPS
- Claude ja disponivel como IA principal
- Telegram como canal principal da automacao
- workflows mapeados para:
  - vencidos e criticos
  - vence hoje
  - vence amanha

Arquivos de referencia:

- `Mapa JSON n8n - Desktop.md`
- `Arquitetura Painel + Agentes + WhatsApp.md`

---

## 11. O Que Falta Implementar

### Alta prioridade

- validar e ativar workflows reais no n8n
- gerar relatorio diario separado por:
  - `LELLIS`
  - `SOCIOS`
  - `COLABORADORES`
- padronizar filtros de:
  - criticos
  - vencidos
  - hoje
  - amanha
- integrar envio automatico no Telegram

### Media prioridade

- comandos operacionais no Telegram
- relatorio semanal
- relatorio mensal
- detalhamento por responsavel individual dentro de socios/colaboradores

### Baixa prioridade

- WhatsApp oficial
- aprovacao de comprovante
- automacoes externas para clientes

---

## 12. Regra de Segurança

Automacao deve orbitar o painel e o banco, nao inventar regra paralela.

Principios:

- nao misturar carteiras
- nao enviar alerta com base em dado incerto
- nao automatizar escrita sensivel sem validacao
- leitura primeiro, acao depois
- Telegram primeiro, WhatsApp depois

---

## 13. Arquitetura Final Desejada

```text
PAINEL CREDPLUS
    ->
SUPABASE
    ->
N8N
    ->
FORMATADOR PADRAO
    ->
TELEGRAM

CLAUDE
    ->
CONSULTA / RESUMO / COMANDOS
```

### Resultado esperado

- Lellis recebe relatorio limpo
- socios nao se misturam com colaboradores
- vencidos, hoje, amanha e criticos saem no mesmo padrao
- o sistema opera com consistencia
- a camada de IA ajuda, mas a regra continua centralizada

---

## 14. Decisão Atual

Decisao recomendada para o CredPlus hoje:

- `Claude` como camada principal de agente e IA
- `n8n` como motor da automacao
- `Telegram` como canal principal
- `WhatsApp` como extensao futura
- `credpluspainel.com` e `Supabase` como fonte oficial

---

**Status desta nota:** revisada para refletir melhor o sistema real e a operacao desejada.  
**Proximo passo ideal:** transformar esta arquitetura em workflows reais do n8n + formato fixo de relatorio Telegram.
