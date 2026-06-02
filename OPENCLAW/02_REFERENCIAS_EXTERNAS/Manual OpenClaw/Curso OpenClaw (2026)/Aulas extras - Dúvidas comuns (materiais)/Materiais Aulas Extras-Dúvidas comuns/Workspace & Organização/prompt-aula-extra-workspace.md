# Prompt do Aluno — Aula Extra: Organize as Pastas do Seu Agente Para Escalar

> **Como usar:** Cole o prompt abaixo no chat do seu agente OpenClaw depois de ler o material da aula.

---

## 📋 Prompt Principal

```
Acabei de ler o material sobre organização de workspace do curso OpenClaw. Quero que você organize meu workspace agora.

Siga estas 5 fases na ordem. Faça cada uma e me mostre o resultado antes de ir pra próxima.

---

**FASE 1 — DIAGNÓSTICO**

Faça um scan completo do meu workspace:
1. Liste tudo na raiz — identifique o que NÃO deveria estar aqui (só os 7 arquivos de identidade ficam na raiz: SOUL.md, IDENTITY.md, USER.md, MEMORY.md, AGENTS.md, TOOLS.md, HEARTBEAT.md)
2. Verifique quais dos 7 arquivos raiz existem e quais faltam
3. Verifique se existem as pastas: memory/, skills/, reports/, archive/
4. Dentro de memory/, verifique: context/, projects/, integrations/, sessions/

Me mostre um relatório de saúde:
- 🟢 OK
- 🟡 Pode melhorar
- 🔴 Precisa de atenção

---

**FASE 2 — CRIAR ESTRUTURA + MOVER ARQUIVOS**

Baseado no diagnóstico:

1. Crie as pastas que faltam:
   - memory/context/
   - memory/projects/
   - memory/integrations/
   - memory/sessions/
   - skills/ (com subpastas por categoria de trabalho — sugira 3-5 categorias baseadas no meu uso)
   - reports/ (com subpastas: business/, misc/ — sugira outras se fizer sentido)
   - archive/

2. Mova todo arquivo que está fora do lugar para o destino correto. Para cada arquivo movido, me diga: de onde saiu → pra onde foi → por quê.

3. Se algum dos 7 arquivos raiz não existe, crie um template mínimo pra eu preencher depois.

---

**FASE 3 — ATUALIZAR TOOLS.md**

Adicione ao meu TOOLS.md uma seção "Onde Salvar Cada Output" com esta tabela (adapte as categorias pro meu contexto):

| Tipo de arquivo | Destino |
|----------------|---------|
| Report / análise | reports/{categoria}/ |
| Dashboard HTML | reports/{categoria}/ |
| PDF / imagem entregável | reports/{categoria}/ |
| Screenshot / temporário | archive/imgs/ |
| PRD de projeto | projects/{nome}/PRD.md |
| Skill nova | skills/{categoria}/SKILL.md |
| Script operacional | scripts/{categoria}/ |
| Doc obsoleto | archive/ |
| Memória de projeto | memory/projects/{nome}.md |
| Decisão permanente | memory/context/decisions.md |
| Diário de sessão | memory/sessions/YYYY-MM-DD.md |

Se eu já tenho seções no TOOLS.md, integre — não sobrescreva.

---

**FASE 4 — ATUALIZAR MEMORY.md**

Faça o MEMORY.md funcionar como índice:

1. Se não existe, crie com:
   - Seção "Estrutura de Memória" (tabela: pasta → o que contém)
   - Seção "Mapa de Memória" (tabela: "estou buscando X" → "onde encontrar")
2. Se já existe, reorganize pra seguir esse formato
3. MEMORY.md deve ser LEVE (50-100 linhas) — só aponta para os arquivos, nunca duplica conteúdo

---

**FASE 5 — ORGANIZAR SKILLS + TESTE**

1. Liste minhas skills atuais (se existirem)
2. Mova cada skill pra skills/{categoria}/ baseado no tipo de trabalho
3. Crie um _registry.md em cada categoria listando as skills
4. Se não tenho skills ainda, crie a estrutura vazia

Depois teste tudo:
5. Crie um relatório simples de teste e salve seguindo a tabela do TOOLS.md
6. Use memory_search pra confirmar que encontra
7. Me mostre o resultado: "Perguntei onde salvar X → salvei em Y → busquei e encontrei ✅"

---

No final, me dê um resumo:
- Quantos arquivos movidos e pra onde
- Quais pastas criadas
- O que mudou nos arquivos raiz
- O que eu ainda preciso preencher manualmente
```

---

## 🔄 Prompt de Manutenção Mensal

> Use 1x/mês pra manter o workspace saudável.

```
Faça uma auditoria mensal do meu workspace:

1. Tem arquivo na raiz que não deveria estar?
2. Alguma pasta cresceu demais e precisa de subcategorias?
3. Tem algo em archive/ que pode ser deletado?
4. Algum projeto em memory/projects/ que já terminou?
5. TOOLS.md e MEMORY.md estão sincronizados com a estrutura real?
6. Alguma skill sem documentação ou sem _registry.md?

Me dê um relatório de saúde com ações recomendadas. Execute as que forem óbvias sem perguntar.
```
