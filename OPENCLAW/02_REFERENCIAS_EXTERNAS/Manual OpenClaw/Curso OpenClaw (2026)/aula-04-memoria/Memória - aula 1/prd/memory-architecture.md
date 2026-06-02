# PRD: Arquitetura de Memória (Atualizado Março 2026)

> Jogue este arquivo no agente: "Implementa esta arquitetura de memória"

## Contexto

Agentes AI esquecem tudo a cada sessão. Sem memória estruturada, você repete contexto todo dia. Esta arquitetura resolve isso com uma estrutura em subpastas que permite busca semântica precisa.

**Novidade Março 2026:** `memory_search` agora funciona nativamente — sem precisar de chave de API externa (OpenAI/Gemini). A busca por embedding é built-in.

**⚠️ Breaking v2026.3.13 — MEMORY.md obrigatório em maiúsculas:** O agente carrega apenas um arquivo de memória raiz. `MEMORY.md` (maiúsculas) tem prioridade; `memory.md` (minúsculas) só é usado quando `MEMORY.md` não existe. Se você criou `memory.md` antes da v3.13, renomeie:

```bash
mv memory.md MEMORY.md
```

**Comportamento pós-compaction (v2026.3.13):** Após compaction automática, o índice de memória é reindexado de forma assíncrona. Se o agente parecer "esquecer" algo logo após uma compaction — aguarde alguns segundos e tente `memory_search` novamente. Isso é normal e temporário.

## O que o agente carrega vs. busca

| Sempre carregado na sessão | Buscado sob demanda |
|---------------------------|---------------------|
| SOUL.md, USER.md, AGENTS.md | memory/context/decisions.md |
| MEMORY.md (índice) | memory/context/lessons.md |
| memory/sessions/ (hoje + ontem) | memory/projects/*.md |
| | skills/ (qualquer skill) |

## Tarefas

### 1. Criar estrutura de subpastas

```bash
mkdir -p memory/context memory/projects memory/sessions memory/integrations
```

### 2. Criar os arquivos de contexto

| Arquivo | Propósito |
|---------|-----------|
| `memory/context/decisions.md` | Decisões permanentes e irreversíveis |
| `memory/context/lessons.md` | Lições aprendidas, erros, padrões |
| `memory/context/people.md` | Equipe, parceiros, contatos — como interagir com cada um |
| `memory/context/business-context.md` | Contexto do negócio, produtos, clientes |

**Retenção de lições:**
- 🔒 Estratégicas = permanentes (filosofia, padrões de arquitetura)
- ⏳ Táticas = expiram em 30 dias (bugs, workarounds temporários)

### 3. Criar projetos individuais

Em vez de um `projects.md` gigante, um arquivo por projeto:

```
memory/projects/
├── meu-saas.md          ← MRR atual, próximas features, pendências
├── lançamento-maio.md   ← status, checklist, responsáveis
└── produto-b.md
```

**Por que separado?** A busca semântica acha o projeto certo sem trazer contexto de outros projetos junto.

### 4. Criar MEMORY.md (índice)

Na raiz do workspace. É o mapa — não duplica conteúdo, apenas referencia:

```markdown
# MEMORY.md

## Contexto
- Decisões: memory/context/decisions.md
- Lições: memory/context/lessons.md
- Pessoas: memory/context/people.md

## Projetos ativos
- [Nome do Projeto]: memory/projects/nome.md

## Integrações
- Mapa de ferramentas: memory/integrations/
```

### 5. Configurar ciclo de memória no AGENTS.md

```
Regras de memória:
1. Notas diárias: criar memory/sessions/YYYY-MM-DD.md a cada sessão relevante
2. Projetos: um arquivo separado por projeto em memory/projects/
3. INVIOLÁVEL: antes de compactar → extrair lições, decisões e pendências
4. Feedback: ao rejeitar sugestão → salvar motivo em memory/feedback/
```

### 6. Configurar busca semântica

O agente usa dois tools:
- `memory_search("termo")` — busca semântica em todos os arquivos (~400 tokens/chunk)
- `memory_get("arquivo.md", linha_início)` — lê só o trecho relevante

**Funciona nativamente** desde Março 2026. Não precisa de chave externa.

### 7. Configurar feedback loops (avançado)

```
memory/feedback/
├── content.json    ← sugestões de conteúdo aprovadas/rejeitadas
├── tasks.json      ← preferências de execução de tarefas
└── tone.json       ← ajustes de tom e estilo
```

Formato:
```json
{
  "entries": [
    {
      "date": "2026-03-14",
      "context": "Sugeri post LinkedIn com linguagem formal",
      "decision": "reject",
      "reason": "Tom muito corporativo — prefere direto e conversacional",
      "tags": ["linkedin", "tom"]
    }
  ]
}
```

### 8. Configure dreaming (experimental, opt-in)

O OpenClaw tem um sistema de consolidação automática de memória que funciona em segundo plano — o **Dreaming**.

**As 3 fases do ciclo:**

| Fase | O que faz | Escreve em MEMORY.md? |
|------|-----------|----------------------|
| 🌅 **Light** | Coleta sinais recentes das sessões e notas diárias, separa ruído do relevante | Não |
| 🌙 **Deep** | Pontua candidatos e promove os melhores para `MEMORY.md` | ✅ Sim |
| 💤 **REM** | Extrai temas recorrentes e gera resumo narrativo | Não |

**Output:** Depois de cada ciclo, escreve um **Dream Diary** em `DREAMS.md` (ou `dreams.md`). É leitura humana — não é fonte de promoção.

**Como ativar:**
- Na sessão: `/dreaming` — roda o ciclo completo
- `/dreaming --dry-run` — mostra o que faria sem executar

**Nota:** Dreaming vem desabilitado por padrão. Ative se quiser que o agente promova memórias automaticamente entre sessões.

## Como pedir para salvar

| ❌ Não funciona | ✅ Funciona |
|----------------|------------|
| "Lembra disso" | "Salva em memory/context/decisions.md" |
| "Guarda essa info" | "Adiciona em memory/projects/nome.md" |
| "Não esquece que..." | "Registra em memory/sessions/hoje como lição" |

## Resultado Esperado

1. Estrutura criada com subpastas organizadas
2. MEMORY.md como índice apontando para tudo
3. Teste: fechar sessão → abrir nova → perguntar algo salvo → agente encontra via memory_search
