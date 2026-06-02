# Prompt — Módulo 9: Sistema Imunológico

> Cole este prompt no chat do seu OpenClaw depois de assistir o Módulo 9.
> Anexe junto o arquivo: `prds/immune-system.md`

---

Acabei de assistir o Módulo 9 do curso sobre o sistema imunológico. "Agents are 30% of the work. The other 70% is the immune system." Leia o PRD e me guie.

**O que preciso que você faça:**

1. **Watchdog de crons** — Configure um cron que monitora se os outros crons estão executando. Se algum falhar, retry automático até 3x. Se falhar 3x, me avisa.

2. **Feedback Loops** — Me ajude a configurar um sistema de approve/reject:
   - Quando você me sugerir algo e eu rejeitar, anote o motivo
   - Consulte essas anotações antes de sugerir novamente
   - Me mostre como isso funciona na prática

3. **Monitoramento de custos:**
   - Configure o split de modelos (GPT-4o-mini pra heartbeats, GPT-4o pra crons e interação direta)
   - Configure rate limits e budgets pra prevenir runaway
   - Me mostre quanto estou gastando por dia/semana

4. **Audit de segurança periódico:**
   - Configure um cron semanal de security audit
   - Rode um agora pra eu ver o resultado

5. **Backup antes de mudanças:**
   - Crie uma regra: antes de qualquer mudança estrutural, salvar backup + ROLLBACK.md
   - Me mostre como reverter se algo der errado

6. **openclaw secrets audit (v2026.3.2+):** Rode `openclaw secrets audit` para checar se há credenciais expostas no workspace. Isso é crítico antes de compartilhar arquivos ou fazer backup.

7. **Sub-agents: sessions_yield (v2026.3.13+):** Quando spawnar sub-agents, use sessions_yield para encerrar o turno limpo e receber os resultados na próxima mensagem — nunca deixe um sub-agent no limbo silencioso.

**Regras:**
- Esse módulo é o que separa "tô brincando" de "tô em produção"
- Me explique cada proteção e qual problema ela previne
- No final, rode um health check completo e me dê o score

Vamos construir a imunidade?
