# Prompt do Aluno — Aula N-8: Telegram Bot Não Responde no Grupo

> **Como usar:** Copie o prompt abaixo e cole no chat do seu agente OpenClaw após assistir a aula.

---

## 📋 Prompt Principal

```
Olá! Assisti a aula N-8 sobre configuração de bot em grupos do Telegram.

Estou tentando fazer meu bot funcionar em um grupo, mas [ele não responde / só responde comandos / responde às vezes].

Me ajude a:
1. Diagnosticar o problema específico no meu caso
2. Aplicar os fixes necessários
3. Verificar que funcionou

Vamos começar com o diagnóstico?
```

---

## 🔍 Exercício 1 — Diagnóstico Completo

```
Por favor, faça um diagnóstico completo do meu setup de bot para grupos:

1. Verifique a configuração atual:
   - `openclaw config get channels.telegram.groupPolicy`
   - `openclaw config get channels.telegram.groupAllowlist`
   
2. Me diga qual das 3 causas é mais provável:
   - Privacy mode ativado no BotFather
   - groupPolicy não configurado
   - Chat ID não está no allowlist

3. Cheque os logs por mensagens de grupo:
   `openclaw gateway logs | tail -50`

Após o diagnóstico, me diga exatamente o que preciso fazer.
```

---

## 🤖 Exercício 2 — Fix do Privacy Mode

```
Preciso verificar e corrigir o privacy mode do meu bot.

Por favor, me guie pelo processo completo:
1. Como verificar se o privacy mode está ativado (sinal no comportamento do bot)
2. Passo a passo para desativar via BotFather:
   - Qual comando enviar ao BotFather
   - O que selecionar quando ele perguntar
   - Como confirmar que foi desativado
3. Por que preciso remover e re-adicionar o bot ao grupo
4. Como confirmar que a mudança funcionou

(Se já verificou e o privacy mode está desativado, me confirme isso e vamos para o próximo passo)
```

---

## ⚙️ Exercício 3 — Configurar groupPolicy

```
Quero configurar o groupPolicy do OpenClaw corretamente.

Por favor:
1. Explique a diferença entre groupPolicy = "allowlist" e "open"
2. Configure o allowlist (recomendado para segurança):
   `openclaw config set channels.telegram.groupPolicy allowlist`
3. Me ajude a descobrir o chat ID do meu grupo:
   - Execute `openclaw gateway logs | grep -i "chat_id"` 
   - Ou me diga outro método se não aparecer
4. Após encontrar o ID, configure o allowlist:
   `openclaw config set channels.telegram.groupAllowlist "[-100XXXXXXXXXX]"`
5. Reinicie o gateway: `openclaw gateway restart`
6. Teste: envie uma mensagem no grupo e verifique nos logs

(Meu grupo é: [DESCREVA SEU GRUPO — ex: "grupo familiar de 5 pessoas"])
```

---

## 📍 Exercício 4 — Descobrir Chat ID na Prática

```
Preciso descobrir o chat ID do meu grupo do Telegram.

Por favor, me guie por TODOS os métodos disponíveis:

Método 1 — Via logs do OpenClaw:
- Como enviar uma mensagem de teste no grupo
- Onde exatamente o chat ID aparece nos logs
- Formato do comando correto para filtrar

Método 2 — Via @userinfobot:
- Como usar esse bot para descobrir o ID
- O que fazer com a informação que ele retorna

Método 3 — Via Telegram API (se necessário):
- Como usar a URL da API para ver updates recentes

Qual método é mais fácil para iniciantes?
```

---

## 🔄 Exercício 5 — dmPolicy vs groupPolicy na Prática

```
Quero entender de vez a diferença entre dmPolicy e groupPolicy.

Por favor:
1. Mostre minha configuração atual dos dois:
   - `openclaw config get channels.telegram.dmPolicy`
   - `openclaw config get channels.telegram.groupPolicy`
   
2. Me explique o que cada configuração atual significa na prática:
   - Quem consegue mandar mensagem privada pro bot?
   - Em quais grupos o bot responde?
   
3. Me recomende a configuração ideal para segurança:
   - dmPolicy para uso pessoal (só eu)
   - groupPolicy para um grupo específico que eu quero

4. Se precisar ajustar, me dê os comandos exatos.
```

---

## 🗺️ Exercício 6 — Fluxograma de Diagnóstico (use se ainda tiver problemas)

```
Ainda não consegui fazer o bot funcionar no grupo. Vamos ser sistemáticos.

Por favor, me leve pelo fluxograma de diagnóstico passo a passo:

Passo 1: O bot responde no grupo quando manda /start?
[Sim → Passo 2] [Não → Privacy mode ou bot não está no grupo]

Passo 2: O groupPolicy está configurado?
[Sim → Passo 3] [Não → configurar groupPolicy]

Passo 3: O chat ID do grupo está no allowlist?
[Sim → Passo 4] [Não → adicionar chat ID]

Passo 4: O gateway foi reiniciado após as mudanças?
[Sim → ver logs] [Não → openclaw gateway restart]

Para cada passo, execute o diagnóstico e me diga o resultado. Vamos resolver isso juntos.
```

---

## ✅ Verificação Final de Aprendizado

```
Para encerrar os exercícios da aula N-8, me faça um quiz rápido com 5 perguntas sobre:
- O que é privacy mode e quando causa problemas
- Diferença entre dmPolicy e groupPolicy
- Como descobrir o chat ID de um grupo
- Por que precisa remover e re-adicionar o bot ao mudar o privacy mode
- Quando usar groupPolicy "open" vs "allowlist"

Após eu responder, me dê feedback sobre o que acertei e o que preciso revisar.
```

---

## 💡 Prompt de Emergência (se nada funcionar)

> Se você tentou tudo e o bot ainda não responde no grupo:

```
Meu bot NÃO está respondendo no grupo e já tentei de tudo. Me ajude com um debug completo:

1. Execute `openclaw gateway logs | tail -100` e analise tudo
2. Verifique se há erros relacionados ao Telegram
3. Verifique se o webhook está funcionando: `openclaw provider status telegram`
4. Me mostre TODA a configuração atual do canal Telegram:
   `openclaw config get channels.telegram`
5. Baseado no que encontrar, me dê a solução específica

Estou disposto a seguir qualquer passo — só preciso que o bot funcione no grupo.
```
