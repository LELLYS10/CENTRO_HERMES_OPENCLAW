# Prompt do Aluno — Aula N-2: Bot sem acesso ao shell

**Como usar:** Cole o prompt abaixo diretamente no chat do seu agente OpenClaw.  
O agente vai diagnosticar a própria configuração e guiar você até a solução.

---

## PROMPT PARA COLAR NO CHAT

```
Vou fazer um diagnóstico do seu acesso ao shell. Por favor, execute cada etapa na ordem.

## ETAPA 0 — Verificar tools.profile (primeiro check SEMPRE)

Antes de qualquer coisa, verifique se o perfil de ferramentas está correto:

1. Execute: `openclaw config get tools.profile`
2. Se o resultado NÃO for "full", execute: `openclaw config set tools.profile full`
3. Reinicie o gateway: `openclaw gateway restart`
4. Teste: `echo "TOOLS_PROFILE_CHECK_OK"`

> Este é o problema mais comum: o agente não executa nada porque o tools.profile está em "minimal" (padrão após instalação). Sem `tools.profile full`, o agente só responde mensagens.

Se o teste acima funcionou → problema resolvido! 🎉
Se ainda falha → continue para a Etapa 1.

---

## ETAPA 1 — Teste básico de acesso

Tente executar este comando e me diga exatamente o que aconteceu:
execute: echo "SHELL_TEST_OK"

Se funcionou → me confirme "OK" e vá para a Etapa 3.
Se falhou ou você recebeu erro → descreva o erro e continue na Etapa 2.

---

## ETAPA 2 — Diagnóstico de configuração

Agora verifique sua configuração atual:

1. Leia o arquivo de configuração principal:
   - Tente: `cat ~/.openclaw/config.json`
   - Ou: `cat openclaw.json` (se estiver num workspace)

2. Me mostre o conteúdo completo do arquivo. Procuro especificamente por:
   - Chave "tools" ou "allowlist" (para verificar se "exec" está na lista)
   - Chave "sandbox" (valores possíveis: "off", "non-main", "all")
   - Chave "security" (valores possíveis: "deny", "allowlist", "full")
   - Chave "shell" (path do shell, ex: "/bin/bash")

3. Também verifique os logs do gateway:
   `openclaw gateway logs --tail 30`

---

## ETAPA 3 — Identificar a causa

Com base no que você encontrou, me diga qual dessas situações se aplica:

**A) Causa 1 — exec não está no allowlist**
Sintoma: config tem "allowlist" mas "exec" não está na lista
→ Solução: adicionar "exec" ao allowlist de tools

**B) Causa 2 — Sandbox bloqueando**
Sintoma: config tem "sandbox": "all" ou sandbox configurado de forma restritiva
→ Solução: mudar para "sandbox": "off" (agente principal) ou "non-main"

**C) Causa 3 — Security mode "deny"**
Sintoma: config tem "security": "deny"
→ Solução: mudar para "security": "allowlist"

**D) Causa 4 — Shell não encontrado**
Sintoma: erro de path ou shell não localizado nos logs
→ Solução: configurar "shell": "/bin/bash" (ou o path correto)

**E) Não encontrei nada suspeito na config**
→ Me descreva o erro exato que você vê e os logs do gateway

---

## ETAPA 4 — Aplicar a correção

Baseado na causa identificada, edite o arquivo de configuração com a correção correta.

**Para Causa 1 (exec não no allowlist):**
```json
{
  "agents": {
    "main": {
      "tools": {
        "allowlist": ["exec", "read", "write", "edit", "web_search", "web_fetch"]
      }
    }
  }
}
```

**Para Causa 2 (sandbox bloqueando):**
```json
{
  "agents": {
    "main": {
      "sandbox": "off"
    }
  }
}
```

**Para Causa 3 (security deny):**
```json
{
  "agents": {
    "main": {
      "security": "allowlist"
    }
  }
}
```

**Para Causa 4 (shell não encontrado):**
```json
{
  "agents": {
    "main": {
      "shell": "/bin/bash"
    }
  }
}
```

Após editar, execute:
`openclaw gateway restart`

---

## ETAPA 5 — Verificação final

Após reiniciar, verifique se está funcionando:

1. `echo "VERIFICACAO_FINAL_OK"` → deve retornar o texto
2. `touch /tmp/teste-openclaw && echo "arquivo criado"` → deve funcionar
3. `openclaw gateway status` → deve mostrar status "running"

Se tudo passou: **problema resolvido!** 🎉
Se ainda falha: copie o erro exato e os logs do gateway para analisar.
```

---

## NOTAS PARA O ALUNO

### Quando usar este prompt
- Seu agente responde perguntas mas não executa comandos
- Você vê erros como "exec not available", "permission denied" ou "sandbox restriction"
- O agente diz "não consigo executar tarefas no sistema"

### O que o prompt faz
0. **Verifica o tools.profile** — causa #1 mais frequente, resolve 70% dos casos
1. Testa o acesso ao shell com um comando simples
2. Lê sua configuração atual
3. Identifica qual das 4 causas se aplica ao seu caso
4. Guia você na correção específica
5. Verifica que a correção funcionou

### Causa mais comum (verifique primeiro!)
Na maioria dos casos, o problema é simplesmente o `tools.profile` não estar em `full`. Execute no terminal do servidor:
```bash
openclaw config set tools.profile full
openclaw gateway restart
```

### Dica importante
Se o agente não conseguir nem ler o arquivo de configuração, você precisará fazer isso **manualmente no terminal** (não pelo agente). Nesse caso, abra um terminal no servidor onde o OpenClaw está rodando e edite o `config.json` diretamente.

---

*Prompt para Aula N-2 · Curso OpenClaw · Pixel Educação*
