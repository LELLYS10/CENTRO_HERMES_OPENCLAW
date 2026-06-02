# PRD — Aula Extra: Organize as Pastas do Seu Agente Para Escalar

> **Tipo:** Aula extra (material HTML + prompt de execução)
> **Nível:** Intermediário
> **Pré-requisito:** OpenClaw instalado, SOUL.md e USER.md configurados, pelo menos 1 semana de uso
> **Material:** `aula-extra-workspace-v2.html` (leitura) + prompt do aluno (execução)

---

## 🎯 O que essa aula entrega

O aluno lê o material HTML e depois cola o prompt no agente. O agente **executa** — não explica, faz:

1. **Diagnóstico** do workspace atual (o que está certo, o que está errado)
2. **Criação** da estrutura de pastas completa (memory/, skills/, reports/, archive/)
3. **Migração** de arquivos soltos para os destinos corretos
4. **Atualização dos arquivos raiz** — insere no TOOLS.md a tabela de "onde salvar cada output", atualiza MEMORY.md como índice
5. **Organização de skills** por categoria de trabalho (não por ferramenta)
6. **Configuração de projetos** — cada projeto aponta para sua fonte de verdade de tasks
7. **Teste de sanidade** — cria um output, salva no lugar certo, confirma que memory_search encontra

---

## 📋 Problema que resolve

Workspace desorganizado causa:
- Agente não sabe onde salvar outputs → pergunta toda vez ou joga na raiz
- memory_search retorna lixo → agente perde contexto entre sessões
- Skills sem categoria → impossível auditar ou encontrar
- Arquivos raiz desatualizados → agente age como se integrações/skills não existissem
- Sem regra de destino → cada sessão cria estrutura diferente

---

## 🏗️ Estrutura-alvo que o prompt implementa

```
workspace/
├── SOUL.md, IDENTITY.md, USER.md, MEMORY.md     ← 7 arquivos raiz (já existem)
├── AGENTS.md, TOOLS.md, HEARTBEAT.md
│
├── memory/
│   ├── context/         ← decisions.md, lessons.md, people.md
│   ├── projects/        ← um .md por projeto ativo + _index.md
│   ├── integrations/    ← credentials-map.md, acessos, IDs
│   └── sessions/        ← YYYY-MM-DD.md (diário de sessão)
│
├── skills/              ← subpastas por categoria de trabalho
│   ├── {categoria}/     ← cada skill em {categoria}/SKILL.md
│   └── _registry.md     ← índice por categoria
│
├── reports/             ← outputs consultáveis
│   ├── business/
│   └── misc/
│
├── scripts/             ← scripts operacionais
├── projects/            ← PRDs de projetos grandes
└── archive/             ← rascunhos, temporários, obsoletos
```

---

## ✅ Critérios de sucesso

O prompt funcionou quando:

1. ✅ Nenhum arquivo solto na raiz além dos 7 de identidade
2. ✅ Estrutura de pastas criada (memory/context, memory/projects, memory/sessions, skills/, reports/, archive/)
3. ✅ TOOLS.md contém tabela "Onde Salvar Cada Output"
4. ✅ MEMORY.md funciona como índice (aponta para memory/, não duplica conteúdo)
5. ✅ Skills organizadas por categoria com _registry.md
6. ✅ O agente salva um output no destino correto sem perguntar
7. ✅ memory_search encontra o output salvo

---

## 📐 Regras do prompt

- O prompt **executa**, não ensina. O material HTML já ensinou.
- Se o aluno já tem estrutura parcial → o agente **adapta**, não destrói
- Arquivos existentes são **movidos**, nunca deletados
- Cada arquivo movido → log de "de onde saiu → pra onde foi → por quê"
- A tabela de destinos no TOOLS.md é **adaptada** ao contexto do aluno (categorias de reports)
- Skills com menos de 2 por categoria → juntar em "general" até ter volume

---

## 🔗 Arquivos relacionados

- **Material HTML:** `reports/misc/aula-extra-workspace-v2.html`
- **Prompt do aluno:** `memory/curso-openclaw/prompts/aula-extra-workspace-prompt-aluno.md`
- **Referência real:** Workspace da Amora (workspace-amora-cos)
