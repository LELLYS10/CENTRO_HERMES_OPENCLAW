# 🔧 Troubleshooting — FAQ de Problemas Comuns

> 35+ lições aprendidas em 13 dias de produção. Se deu erro, a resposta provavelmente tá aqui.

---

## 🔴 Críticos (quebra tudo se não resolver)

### Meu cron dispara mas não executa nada
**Sintoma:** Cron mostra `status: "ok"` mas `durationMs` é ~0ms. Nada acontece.
**Causa:** Usar `systemEvent` + `sessionTarget: main`
**Solução:**
```json
{
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "sua instrução aqui"
  }
}
```
**Regra:** SEMPRE usar `isolated` + `agentTurn` + `announce` pra crons.

---

### Token overflow — sessão estourou
**Sintoma:** Agente para de responder, erros de contexto, respostas cortadas.
**Causa:** Contexto excedeu o limite sem compactação configurada.
**Solução:**
```json
{
  "compaction": { "mode": "default" },
  "contextTokens": 160000,
  "reserveTokensFloor": 30000
}
```
**Dica:** O `reserveTokensFloor` garante que o agente termina o raciocínio antes de compactar.

---

### Qualquer pessoa comanda meu bot
**Sintoma:** Estranhos mandando mensagem pro seu bot e ele respondendo.
**Causa:** `dmPolicy` configurado como `"open"`.
**Solução:** Mudar pra `"allowlist"` e adicionar só o seu Telegram ID:
```json
{
  "dmPolicy": "allowlist",
  "allowedUsers": ["SEU_TELEGRAM_ID"]
}
```
**Como descobrir seu ID:** Mande `/start` pro @userinfobot no Telegram.

---

### Me tranquei fora do SSH
**Sintoma:** Não consigo acessar o servidor depois de configurar firewall.
**Causa:** UFW bloqueou a porta SSH antes de liberar.
**Solução:** Acesse pelo console web do painel da Hostinger (ou sua VPS) e rode:
```bash
sudo ufw allow ssh
sudo ufw allow 22/tcp
```
**Prevenção:** SEMPRE rode `sudo ufw allow ssh` ANTES de `sudo ufw enable`.

---

## 🟠 Importantes (funciona mas com problemas)

### Lembrete/cron não notifica no Telegram
**Sintoma:** Cron roda mas não aparece mensagem no Telegram.
**Causa:** `systemEvent` não envia pra canais — é evento interno.
**Solução:** Usar `agentTurn` + `delivery: { mode: "announce" }`. O agente precisa usar a tool `message` pra enviar.

---

### Múltiplos crons falhando no mesmo horário
**Sintoma:** Alguns crons executam, outros dão timeout ou falham.
**Causa:** Colisão de horários — muitos crons no mesmo minuto causam rate limit.
**Solução:** Espaçar crons em pelo menos 15-30 minutos entre si.

> ⚠️ **Atualização Mar/2026:** Rate limits agora são **por modelo**, não global. Se você usa Haiku pra heartbeats e Opus pra interação, eles têm limites separados. Mas crons no mesmo modelo ainda colidem.

---

### config.patch matou meus crons
**Sintoma:** Crons pararam depois de alterar a config.
**Causa:** `config.patch` reinicia o gateway e mata crons em execução.
**Solução:** Fazer patches em horários sem crons rodando. Verificar schedule antes de alterar.

---

### Cloud IP bloqueado pelo YouTube/Instagram/X
**Sintoma:** Erros ao tentar acessar YouTube transcripts, scraping de redes sociais.
**Causa:** IPs de cloud (AWS, Hetzner, DigitalOcean) são bloqueados por plataformas.
**Solução:** Usar **RapidAPI** como proxy:
- YouTube Transcripts: Apify actor (~$0.007/vídeo)
- Instagram: RapidAPI Instagram Statistics
- X/Twitter: RapidAPI API45
- Free tiers generosos na maioria

---

### yt-dlp não funciona na VPS
**Sintoma:** Erro de bot detection ao baixar vídeos.
**Causa:** YouTube bloqueia downloads de cloud IPs.
**Solução:** Usar Tella.tv pra gravar (sync automático) ou Apify pra transcrições.

---

### Agente carregando 50KB de histórico toda sessão
**Sintoma:** Tokens queimando rápido, respostas lentas, custo alto.
**Causa:** Session initialization sem regra de carregamento.
**Solução:** Configurar session initialization rule:
- Carregar APENAS: SOUL.md, USER.md, IDENTITY.md, memory/YYYY-MM-DD.md
- Usar `memory_search()` sob demanda pro resto
- Reduz de 50KB → 8KB por sessão

---

## 🟡 Moderados (inconvenientes)

### systemd override sobrescreve .env
**Sintoma:** Troquei a API key no .env mas o agente usa a antiga.
**Causa:** O override do systemd tem precedência sobre .env.
**Solução:** Atualizar AMBOS: `.env` E `systemctl edit openclaw` (override).

---

### Brave Search intermitente
**Sintoma:** Buscas falham às vezes.
**Causa:** API do Brave tem instabilidade ocasional.
**Solução:** Ter fallback com `web_fetch` direto na URL.

---

### Sub-agent retorna histórico vazio
**Sintoma:** Spawn de sub-agente não traz resultado.
**Causa:** Sub-agents rodam em sandbox isolado — não acessam localhost.
**Solução:** Ter fallback manual. QA de sub-agents deve rodar na main session.

---

### Notion API só retorna parte dos dados
**Sintoma:** Listagem de pages/databases incompleta.
**Causa:** Notion API usa paginação — sem paginar, retorna só a primeira página.
**Solução:** Sempre implementar paginação (`has_more` + `start_cursor`).

---

### Agente esquece de extrair lições antes de compactar
**Sintoma:** Após compactação, informações importantes sumiram.
**Causa:** Mesmo com regra "inviolável", o agente às vezes esquece.
**Solução:**
1. Reforçar no AGENTS.md como regra inviolável
2. Configurar consolidação periódica (a cada 15 dias) que revisa notas diárias
3. Essa consolidação é o safety net — pega o que escapou

---

### trash-cli não encontrado
**Sintoma:** Erro `trash: command not found`.
**Causa:** Não vem instalado por padrão no Ubuntu.
**Solução:** `sudo apt install trash-cli`

---

## 💡 Dicas de Produção

### Economia de tokens
- **Heartbeat:** Haiku (~$0.005) ou Ollama local (grátis)
- **Crons de execução:** Sonnet (~90% economia vs Opus)
- **Interação:** Opus (quando qualidade importa)
- **Session initialization:** 8KB startup vs 50KB (~80% economia)

### Segurança
- Credenciais SEMPRE no 1Password — zero hardcode
- Rotação trimestral de API keys
- Audit de segurança semanal (cron)
- `openclaw security-audit` + `openclaw doctor fix`
- Portas de app: `127.0.0.1` + Cloudflare Tunnel
- **Novo:** `exec` config agora é protegida — agente não pode alterar suas próprias permissões de execução via config.patch
- **Dica:** Use `openclaw config schema` pra inspecionar qualquer campo de configuração sem adivinhar nomes

### Memória
- MEMORY.md fica grande? Quebre em topic files
- Lições estratégicas = permanentes, táticas = expiram em 30 dias
- Feedback loops em JSON: agente consulta antes de repetir erros

### Multi-agentes
- Todo agente novo começa L1 (Observer) — sem confiança automática
- Hub model > Mesh model (coordenação central)
- Agentes que não precisam de Opus não devem usar Opus
- Sub-agent travou? → retry 2x → se falhar → avisar humano (NUNCA limbo silencioso)

---

### Requisitos mínimos
- **Node.js:** 22.14+ (versões anteriores podem causar crashes silenciosos)
- Se o agente parar de responder sem erro claro, verifique `node --version`

---

*Baseado em produção real. Atualizado Março 2026.*
