# PRD: Setup de Integrações

> Jogue este arquivo no agente: "Configura estas integrações seguindo o PRD"

## Contexto

Um agente sem integrações é só um chatbot. Estas são as integrações mais úteis por categoria.

## Nível 1 — Essenciais (fazer primeiro)

### Google Calendar
```bash
# gog CLI já vem instalado no OpenClaw (2026.4+)
# Se precisar instalar manualmente:
npm install -g gogcli
# ou
brew install steipete/tap/gogcli

# Autenticar (Google Workspace completo)
gog auth credentials /path/to/client_secret.json
gog auth add SEU_EMAIL@gmail.com --services gmail,calendar,drive,contacts,docs,sheets
gog auth list
```
- Permite: ver compromissos, criar/atualizar eventos, lembretes
- Cron sugerido: checar agenda a cada heartbeat
- **gog CLI (2026.4+)** é o caminho recomendado: autenticação via arquivo `client_secret.json` do Google Cloud Console — menos configuração manual, mesmo acesso completo ao Google Workspace (Calendar, Drive, Gmail, Docs, Sheets, Contacts).

> 💡 **gog CLI** é o caminho recomendado para Google Workspace: configura uma vez e o agente usa pra sempre. Suporta Google Workspace completo — Calendar, Drive, Gmail, Docs, Sheets e Contacts.

### Telegram (já configurado no setup)
- Criar grupo com tópicos para organizar conversas
- Tópicos sugeridos: Geral, Conteúdo, Métricas, Operacional
- dmPolicy: SEMPRE allowlist

## Nível 2 — Produtividade

### Google Drive
```bash
gog drive search "minha pasta" --account=SEU_EMAIL@gmail.com
```
- Upload/download de arquivos
- Útil para compartilhar reports, docs, planilhas

### Notion API
- Criar integração em https://www.notion.so/my-integrations
- Guardar API key no 1Password
- Útil para: kanban, base de conteúdo, CRM

### 1Password CLI
```bash
# Instalar
# Ver: https://developer.1password.com/docs/cli/get-started/

# Uso
op item get "Nome do Item" --field credential --reveal
```
- TODA credencial deve viver no 1Password
- Nunca hardcodar API keys em arquivos

## Nível 3 — Conteúdo & Métricas

### YouTube (Data API + OAuth)
- Criar projeto no Google Cloud Console
- Habilitar YouTube Data API v3
- Gerar OAuth credentials
- Permite: listar vídeos, ver analytics, agendar uploads

### Social Media via RapidAPI
- Cloud IPs são bloqueados por Instagram, X, LinkedIn
- RapidAPI funciona como proxy:
  - Instagram Statistics API (50 req/mês free)
  - X/Twitter API45 (1000 req/mês free)
  - Fresh LinkedIn Scraper
- Cadastro: https://rapidapi.com

### Brave Search
- API para pesquisa web
- Já vem configurado no OpenClaw (verificar)

## Nível 3.2 — Geração de Mídia (Built-in, sem skill)

### image_generate, video_generate, music_generate
Estas ferramentas são **primeira classe no OpenClaw** — nenhuma skill extra ou API key extra necessária.

```
# Gerar imagem
image_generate(prompt="Um carrossel de LinkedIn sobre automação de agentes")

# Gerar vídeo (built-in)
video_generate(prompt="...", durationSeconds=5, size="1280x720")

# Gerar música (built-in)
music_generate(prompt="ambient technology background music", durationSeconds=30)
```
- **image_generate:** OpenAI (DALL-E) como primário, Google Imagen como secundário
- **video_generate:** Built-in via provedores configurados (Hunyuan, Wan, etc.)
- **music_generate:** Built-in via provedores configurados
- **Importante:** não são skills — são ferramentas nativas do OpenClaw, disponíveis diretamente

## Nível 3.5 — PDF Nativo (Built-in desde 3.2)

### PDF Tool Nativo
Agentes OpenClaw analisam documentos PDF **nativamente** — sem precisar instalar nada.

```
# O agente simplesmente faz:
Analise este PDF: /caminho/para/documento.pdf
```

- **Suportado por:** OpenAI (GPT-4o) como primário, Google Gemini e Anthropic Claude como secundários
- **Multimodal nativo:** extrai texto e imagens automaticamente
- **Uso prático:** contratos, relatórios, notas fiscais, planilhas PDF
- **Limite:** até 10 PDFs por chamada
- Ferramenta: `pdf` tool — primeira classe no OpenClaw, nenhuma configuração extra

> 💡 Casos de uso reais: o agente analisa boletos, extrai dados de NFs para o Notion, resume relatórios longos automaticamente.

## Nível 4 — Avançado

### ChartMogul (se tiver SaaS)
- Métricas de MRR, churn, LTV
- Cron semanal para report

### Crisp / Intercom (se tiver suporte)
- Análise de conversas
- Insights de conteúdo a partir de dúvidas reais

## Crons Essenciais

Após configurar integrações, criar crons:

| Cron | Frequência | O que faz |
|------|-----------|-----------|
| Check agenda | A cada heartbeat | Compromissos próximos |
| Métricas sociais | Semanal | Puxar dados das redes |
| Revisão semanal | Sexta | Revisar projetos e pendências |

**REGRA CRÍTICA para crons:**
```
sessionTarget: "isolated"
payload.kind: "agentTurn"
delivery: { mode: "announce" }
```
NUNCA usar `systemEvent` + `main` — dispara mas não executa.

## Resultado Esperado

Agente conectado às suas ferramentas principais, com pelo menos 2 crons rodando.
