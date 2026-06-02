# PRD: Security Hardening do OpenClaw

> Jogue este arquivo no chat do seu agente e diga: "Executa este PRD de segurança"
> Ele vai blindar seu servidor seguindo cada passo.
> **Atualizado para OpenClaw v2026.3.13**

---

## ⚠️ Por Que Isso É Urgente

Em fevereiro de 2026, uma vulnerabilidade crítica (**CVE com CVSS 8.8**) foi descoberta em instâncias OpenClaw expostas na internet. Mais de **30.000 instâncias** foram identificadas como vulneráveis antes do patch da versão 2026.2.12. Servidores sem proteção básica foram comprometidos — dados exfiltrados, API keys roubadas, agentes usados para spam.

Além disso: servidores OpenClaw expostos na internet recebem 1.000+ tentativas de brute force por dia. Sem proteção, qualquer pessoa pode acessar seu agente e seus dados.

Este guia te protege contra todos os vetores de ataque conhecidos.

## Contexto da v2026.3.2+

**WebSocket agora é loopback-only por padrão.** O painel web do OpenClaw (`http://IP:18789`) só aceita conexões de `127.0.0.1` — ou seja, só de dentro do próprio servidor. Para acessar remotamente, você precisa do Cloudflare Tunnel (coberto abaixo).

### Novidades de segurança na v2026.3.13

A versão 2026.3.13 trouxe um pacote expressivo de correções de segurança:

- **Device pairing single-use:** Códigos de setup agora são de uso único — não podem ser reaproveitados para ganhar acesso. Cada `openclaw qr` ou `/pair` gera um código que expira no primeiro scan (ou em poucos minutos sem uso). Se tentar usar o mesmo QR duas vezes → erro "código expirado". Gere um novo para cada pareamento. ⚠️ Nunca compartilhe QR por screenshot — quem escanear primeiro ganha acesso.
- **Exec approvals hardened:** Várias formas de contornar a análise de comandos foram corrigidas (Unicode zero-width, backslash-newline, pnpm wrappers, Perl/Ruby -r/-I flags)
- **WebSocket preauth:** Janela de handshake não-autenticado reduzida; frames oversized rejeitados antes do parsing
- **Proxy attachments:** Limite de 5MB restaurado para arquivos persistidos pelo browser proxy
- **GIT_EXEC_PATH blocked:** Variável de ambiente herdada não pode mais redirecionar Git helpers
- **Webhook secrets:** Feishu, LINE e Zalo com validação de assinatura mais rigorosa

> ✅ Não há ações específicas necessárias para o aluno além de manter o OpenClaw atualizado. As correções são automáticas após o `npm update -g openclaw`.

---

## Tarefas (executar na ordem)

### 1. Telegram Allowlist (CRÍTICO — fazer PRIMEIRO)

> 🔴 **Ordem importa:** Configure o dmPolicy ANTES de qualquer outra coisa. O UFW e outras proteções vêm depois.

Verificar se o OpenClaw está configurado com `dmPolicy: "allowlist"` e que APENAS os IDs autorizados estão na lista.

```bash
# Verificar config atual
cat /root/.openclaw/openclaw.json | grep -A5 dmPolicy
```

Se estiver "open", mudar IMEDIATAMENTE para "allowlist" com os IDs corretos.

> **Por que primeiro?** O UFW protege a porta do servidor, mas o Telegram é uma conexão de SAÍDA — não tem porta pra bloquear. Se o dmPolicy estiver "open", qualquer pessoa que descobrir o username do seu bot consegue commandar seu agente, mesmo com UFW ativo. São duas camadas diferentes de proteção.

### 2. Firewall (UFW)

```bash
# Instalar e configurar
sudo apt install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw --force enable
sudo ufw status
```

### 3. Fail2ban (proteção SSH)

```bash
# Instalar
sudo apt install -y fail2ban

# Configurar
sudo cat > /etc/fail2ban/jail.local << 'EOF'
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime = 3600
findtime = 600
EOF

# Ativar
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban

# Verificar
sudo fail2ban-client status sshd
```

### 4. Cloudflare Tunnel (acesso remoto seguro)

> 🔒 **Novo na v2026.3.2:** O WebSocket do painel OpenClaw agora só aceita conexões de `127.0.0.1` (loopback). Para acessar o painel remotamente (Mission Control, dashboards), você **precisa** do Cloudflare Tunnel. Não tem atalho.

Usar Cloudflare Tunnel pra expor serviços web (Mission Control, dashboards) sem abrir portas:

```bash
# Instalar cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb

# Autenticar
cloudflared tunnel login

# Criar tunnel
cloudflared tunnel create meu-tunnel

# Configurar (exemplo pra app na porta 18789 — painel OpenClaw)
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: meu-tunnel
credentials-file: /root/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: painel.meudominio.com
    service: http://127.0.0.1:18789
  - service: http_status:404
EOF

# Rodar como serviço
cloudflared service install
systemctl enable cloudflared
systemctl start cloudflared
```

**Por que:**
- Zero portas expostas na internet — tunnel faz conexão de SAÍDA
- Servidor fica "invisível" (sem IP público exposto)
- SSL/TLS automático pelo Cloudflare
- Proteção DDoS gratuita inclusa
- NUNCA usar `0.0.0.0` — sempre `127.0.0.1` + tunnel

### 5. Portas de aplicação

Se tiver aplicações web rodando (Mission Control, dashboards, etc.):
- Mudar binding de `0.0.0.0` para `127.0.0.1`
- Usar Cloudflare Tunnel (acima) para acesso externo
- NUNCA expor portas direto na internet

### 6. SSH Hardening

```bash
# Verificar se root login com senha está ativo
grep "PermitRootLogin" /etc/ssh/sshd_config
```

Ideal: `PermitRootLogin prohibit-password` (só SSH key, sem senha)

### 7. Credenciais: Auditar com `openclaw secrets`

**O problema:** A CVE de 2026.2.12 explorou justamente API keys hardcodadas em arquivos de configuração. Se alguém acessa seu servidor, pega TODAS as suas chaves de uma vez.

**A partir da v2026.3.2**, o OpenClaw tem o comando `openclaw secrets` para gerenciar credenciais de forma segura. **Use esse comando em vez de editar .env manualmente.**

**Passo 1 — Auditar (descobrir se tem chaves expostas):**

```bash
# Ver tudo que está exposto nos seus arquivos
openclaw secrets audit
```

Este comando escaneia todos os arquivos do workspace e configuração, procurando padrões de API keys hardcodadas. Se encontrar algo, vai listar com o caminho e linha exata.

**Passo 2 — Migrar pro sistema seguro:**

```bash
# Migrar automaticamente para o gerenciador de secrets seguro
openclaw secrets apply
```

Este comando move as credenciais encontradas para o cofre seguro do OpenClaw, onde ficam criptografadas. Os arquivos originais têm as chaves removidas automaticamente.

**Passo 3 — Verificar que tudo foi migrado:**

```bash
# Rodar audit de novo — deve retornar limpo
openclaw secrets audit
# Output esperado: "✅ No exposed credentials found"
```

> ℹ️ **Compatibilidade retroativa:** Se você já tem um `.env` manual com chaves, o `openclaw secrets apply` lê de lá também e migra pro sistema seguro. Após migração, o `.env` manual pode ser removido.

**Rotação trimestral:** A cada 3 meses, gerar novas chaves nos painéis (OpenAI, OpenRouter, Telegram). O `openclaw secrets` faz a atualização:

```bash
openclaw secrets set ANTHROPIC_API_KEY=sk-ant-nova-chave-aqui
```

### 8. Sync systemd + secrets (armadilha comum!)

Quando trocar qualquer credencial, o systemd precisa saber:

```bash
# 1. Atualizar o secret
openclaw secrets set NOME_DA_CHAVE=novo-valor

# 2. Atualizar o override do systemd se tiver variável hard-coded lá
sudo systemctl edit openclaw

# 3. Recarregar e reiniciar
sudo systemctl daemon-reload
sudo systemctl restart openclaw
```

**Por que:** O systemd override tem prioridade sobre o sistema de secrets. Se trocar só o secret e o override tiver o valor antigo, vai continuar usando o antigo. Muita gente perde horas debugando isso.

---

## Checklist Final

- [ ] **dmPolicy = allowlist** (PRIMEIRO — antes do UFW)
- [ ] UFW ativo
- [ ] Fail2ban ativo
- [ ] Cloudflare Tunnel configurado (painel loopback-only na v2026.3.2)
- [ ] Portas em 127.0.0.1 (não 0.0.0.0)
- [ ] SSH hardened (key-only)
- [ ] `openclaw secrets audit` — zero resultados
- [ ] `openclaw secrets apply` — credenciais migradas pro cofre seguro
- [ ] Rotação trimestral agendada
- [ ] systemd + secrets sincronizados

## Resultado Esperado

Servidor blindado contra os ataques mais comuns, incluindo o vetor da CVE 2026.2.12. **9 camadas de proteção** ativas. Reportar status de cada item.

## Manter Atualizado

Execute periodicamente para garantir que está na versão mais recente (com todos os patches de segurança):

```bash
npm update -g openclaw
openclaw gateway restart
openclaw gateway status
```

> ✅ A versão 2026.3.13 é o pacote de segurança mais robusto até hoje — inclui correções em exec approvals, device pairing, WebSocket e webhooks.
