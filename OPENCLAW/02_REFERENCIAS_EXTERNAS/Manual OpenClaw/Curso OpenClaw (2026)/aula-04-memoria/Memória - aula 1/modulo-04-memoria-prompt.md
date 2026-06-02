# Prompt — Módulo 4: Sistema de Memória (Atualizado Março 2026)

> Cole este prompt no chat do seu OpenClaw depois de assistir o Módulo 4.
> Anexe junto os arquivos: `prds/memory-architecture.md`, `templates/MEMORY-template.md`, `templates/HEARTBEAT-template.md` e a pasta `templates/memory/`

---

Acabei de assistir o Módulo 4 do curso sobre memória. Leia o PRD de arquitetura de memória e me guie na implementação.

**O que preciso que você faça:**

1. **Me explique como funciona sua memória** — quero entender o problema (Alzheimer entre sessões) e a solução (memória em camadas)

2. **Crie a estrutura de memória** organizada em subpastas:
   ```
   memory/
   ├── MEMORY.md              ← índice geral (único arquivo sempre carregado)
   ├── context/
   │   ├── decisions.md       ← regras permanentes e irreversíveis
   │   ├── lessons.md         ← erros e aprendizados
   │   ├── people.md          ← equipe, parceiros, contatos
   │   └── business-context.md
   ├── projects/              ← um arquivo por projeto ativo
   ├── sessions/              ← diário: um arquivo por dia (YYYY-MM-DD.md)
   └── integrations/          ← mapa de ferramentas, IDs, acessos
   ```

3. **Configure a regra de extração antes de compactação** — NUNCA compactar sem extrair lições, decisões e pendências primeiro. Isso é INVIOLÁVEL.

4. **Explique o que é carregado vs. buscado sob demanda:**
   - Carregado sempre: `SOUL.md`, `USER.md`, `AGENTS.md`, `MEMORY.md`, sessões de hoje + ontem
   - Buscado sob demanda: todos os outros arquivos via `memory_search`

5. **Configure o memory search** — busca semântica nativa:
   - `memory_search()` para busca por significado em todos os arquivos
   - `memory_get()` para puxar só o trecho específico (econômico em tokens)
   - ✅ Funciona nativamente — sem chave de API externa (bug do OpenAI embedding foi corrigido definitivamente)
   - **Novo:** A compactação agora é gerenciada pelo plugin `memory-core` — mais estável e sem perda de dados durante compressão

6. **Ensine como salvar corretamente** — mostre exemplos práticos:
   - ❌ "Lembra disso" (mental note — morre na próxima sessão)
   - ✅ "Salva em memory/context/decisions.md como decisão permanente"
   - ✅ "Registra em memory/projects/meu-projeto.md"

7. **Configure feedback loops** — JSONs em `memory/feedback/` que capturam approve/reject:
   - O agente consulta ANTES de sugerir novamente
   - Não repete erros — evolução real

**Regras:**
- Me explique cada arquivo e PRA QUE SERVE antes de criar
- Me mostre um exemplo prático de como uma decisão vira memória permanente
- Regra INVIOLÁVEL: antes de CADA compactação, rodar checklist de extração (lessons, decisions, people, projects, pending)
- Teste a busca semântica: feche a sessão, abra uma nova e pergunte algo que foi salvo

**Critério rápido — o que vai onde:**

| O que é | Arquivo |
|---------|---------|
| Decisão que não pode mudar | `memory/context/decisions.md` |
| Erro que não pode repetir | `memory/context/lessons.md` |
| Status de projeto | `memory/projects/nome-do-projeto.md` |
| Aguardando seu input | `memory/pending.md` |
| O que aconteceu hoje | `memory/sessions/YYYY-MM-DD.md` |

Vamos criar sua memória?
