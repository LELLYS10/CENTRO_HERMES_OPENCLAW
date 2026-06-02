# ARQUITETURA CREDPLUS — HERCULES + TELEGRAM + IA DO PAINEL

**Versão:** 1.0  
**Data:** 03/05/2026  
**Status:** arquitetura alvo para integração operacional

---

## 1. Objetivo

Usar o `Hercules` como interface principal de conversa no `Telegram`, mantendo o `CredPlus Painel` como fonte oficial dos dados reais.

O objetivo não é mover a verdade para a IA.  
O objetivo é fazer a IA consultar o sistema real, responder no estilo do operador e aprender gradualmente o padrão de uso.

---

## 2. Regra Central

Qualquer IA que trabalhar neste projeto deve obedecer estas regras:

- o `CredPlus Painel` é a fonte oficial da verdade
- o `Supabase` é o banco oficial
- o `Hercules` não deve acessar o banco diretamente
- o `Hercules` deve consumir dados apenas pelos endpoints do painel
- o `Telegram` é o canal principal de uso
- o `WhatsApp` fica para uma etapa futura
- não misturar nada com `credplusemp.com.br`
- não misturar com bots, workflows ou automações antigas de outros projetos

---

## 3. Arquitetura Principal

```text
Telegram
    ->
Hercules
    ->
CredPlus Painel API
    ->
Supabase
    ->
CredPlus Painel API
    ->
Hercules
    ->
Telegram
```

### Leitura correta da arquitetura

- o usuário fala com o `Hercules` no `Telegram`
- o `Hercules` interpreta a intenção
- o `Hercules` consulta o `CredPlus Painel`
- o painel busca os dados reais no `Supabase`
- o painel devolve JSON estruturado
- o `Hercules` organiza a resposta no estilo operacional do usuário

---

## 4. Papel de Cada Camada

### Telegram

- canal de conversa com o operador
- recebe comandos, perguntas e relatórios

### Hercules

- interface conversacional principal
- memória gradual do estilo do operador
- interpretação do pedido
- organização da resposta
- nunca deve inventar dados

### CredPlus Painel API

- camada oficial de leitura do sistema
- aplica regras reais de carteira, status e escopo
- devolve dados confiáveis para o `Hercules`

### Supabase

- banco oficial do sistema
- fonte dos contratos, clientes, recebimentos, comissões e pré-cadastros

---

## 5. Fonte Oficial dos Dados

O `Hercules` deve considerar como verdade apenas o que vier do `CredPlus Painel`.

As tabelas principais do sistema são:

- `profiles`
- `clientes`
- `contratos`
- `parcelas`
- `recebimentos`
- `pre_cadastros`
- `comissoes`

### Regra obrigatória

Se o dado não vier do painel ou do banco oficial via endpoint autorizado, ele não deve ser tratado como verdadeiro.

---

## 6. Escopos de Leitura

O sistema deve conseguir responder nestes escopos:

### 1. SISTEMA

- visão geral completa da operação
- clientes
- contratos
- inadimplência
- pré-cadastros
- recebimentos
- comissões

### 2. LELLIS

- visão executiva consolidada
- leitura da operação em alto nível

### 3. SOCIOS

- carteira do grupo `a`

### 4. COLABORADORES

- carteira do grupo `b`

### Regra importante

Não misturar carteiras.

Cada escopo deve responder de forma isolada e padronizada.

---

## 7. Classificação Operacional

Regra fixa do sistema:

- `CRITICOS` = atraso de 5 dias ou mais
- `VENCIDOS` = atraso entre 1 e 4 dias
- `VENCE HOJE`
- `VENCE AMANHA`
- `CADASTROS`

### Ordem de prioridade

```text
critico
-> vencido
-> vence hoje
-> vence amanha
-> cadastro
```

---

## 8. Endpoints que o Hercules Deve Consumir

### Endpoint principal de relatório

`POST /api/ai/report`

Body aceito:

```json
{ "scope": "sistema" }
{ "scope": "lellis" }
{ "scope": "socios" }
{ "scope": "colaboradores" }
```

### O que esse endpoint devolve

- `scope`
- `label`
- `generatedAt`
- `totais`
- `overview`
- `sections`
- `cadastros`
- `aiSummary`
- `html`

### Próximos endpoints desejados

#### `POST /api/ai/chat`

Objetivo:

- receber pergunta livre
- consultar os dados necessários
- responder com base em dados reais

#### `POST /api/ai/telegram-preview`

Objetivo:

- devolver mensagem pronta para envio no Telegram
- usar HTML simples compatível com Telegram

---

## 9. Fluxo Operacional

### Exemplo 1

Usuário manda no Telegram:

`criticos dos socios`

Fluxo:

1. o `Hercules` entende que é um relatório
2. identifica o escopo `socios`
3. consulta o endpoint do painel
4. recebe JSON real
5. devolve resposta curta e prática no Telegram

### Exemplo 2

Usuário manda:

`resumo do sistema`

Fluxo:

1. o `Hercules` consulta `scope = sistema`
2. o painel junta os dados reais
3. a IA resume
4. o Telegram devolve a leitura executiva

---

## 10. Comandos Esperados no Telegram

Exemplos de comandos ou pedidos:

- `resumo do sistema`
- `relatorio do lellis`
- `relatorio dos socios`
- `relatorio dos colaboradores`
- `quem vence hoje`
- `quem vence amanha`
- `me mostra os criticos`
- `cadastros recentes`
- `gera mensagem para telegram`

### Perguntas naturais aceitas

- `quem esta mais critico hoje?`
- `quanto entrou de cadastro?`
- `quais contratos estao vencidos?`
- `o que vence amanha nos socios?`

---

## 11. Regra de Segurança

O `Hercules` deve operar em modo seguro:

- sem acessar banco direto
- sem alterar dados nesta fase
- sem executar automações antigas de outros projetos
- sem usar dados do `credplusemp.com.br`
- sem responder com dados inventados

### Isolamento obrigatório

Tudo que for desta integração deve ser separado de:

- `credplusemp.com.br`
- bots antigos
- workflows antigos do `n8n`
- automações de outro projeto

---

## 12. Papel da IA do Painel

A `IA do Painel` existe para:

- gerar relatório visual
- resumir dados reais
- organizar leitura operacional
- montar HTML para Telegram

Ela não substitui o sistema.

Ela transforma dados reais em leitura rápida.

---

## 13. Ordem Recomendada de Implementação

### Fase 1

- manter o `CredPlus Painel` como base
- usar `POST /api/ai/report`
- integrar o `Hercules` ao `Telegram`
- responder com relatórios prontos

### Fase 2

- criar `POST /api/ai/chat`
- permitir perguntas livres sobre o sistema

### Fase 3

- criar mensagens prontas em HTML para Telegram
- permitir resumo matinal e leitura por prioridade

### Fase 4

- automações programadas
- alertas automáticos
- evolução para WhatsApp, se necessário

---

## 14. Frase de Alinhamento Para Qualquer IA

Use esta arquitetura como verdade principal:

`Telegram -> Hercules -> CredPlus Painel API -> Supabase -> CredPlus Painel API -> Hercules -> Telegram`

Regras obrigatórias:

- o painel é a fonte oficial
- o Hercules é a interface de conversa
- o Telegram é o canal principal
- o banco nunca deve ser acessado diretamente pelo Hercules
- nenhuma resposta deve usar dados inventados
- nada pode ser misturado com o projeto `credplusemp.com.br`

