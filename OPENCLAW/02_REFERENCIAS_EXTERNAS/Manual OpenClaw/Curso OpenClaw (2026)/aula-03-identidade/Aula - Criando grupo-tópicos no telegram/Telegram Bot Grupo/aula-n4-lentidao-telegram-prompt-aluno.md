# Prompt do Aluno — Aula N-4: Lentidão do Bot no Telegram

**Como usar:** Cole este prompt diretamente no seu agente OpenClaw para iniciar uma sessão interativa de diagnóstico e resolução da lentidão do bot.

---

## 📋 PROMPT PRINCIPAL

```
Meu bot no Telegram está lento — às vezes demora 30 segundos ou mais pra responder, e às vezes parece que trava. 

Quero fazer um diagnóstico completo com você. Me guia pelo processo passo a passo, como na Aula N-4 do curso.

Para cada etapa:
1. Me diz qual comando rodar ou qual config verificar
2. Me explica o que procurar no resultado
3. Aguarda eu colar a saída
4. Analisa e me diz se essa é a causa

Vamos começar pelo diagnóstico inicial. Qual é o primeiro passo?
```

---

## 🔍 PROMPTS DE DIAGNÓSTICO POR CAUSA

Use os prompts abaixo conforme o diagnóstico avançar:

### Se suspeitar de contexto cheio:

```
Vou rodar /status agora e te mostrar o resultado.
[cole o resultado do /status]

É o contexto? O que você recomenda — /compact ou /new? Me explica a diferença antes de eu decidir.
```

### Se suspeitar de modelo pesado:

```
Me mostra como ver qual modelo está configurado agora e como trocar 
para usar Sonnet nas conversas e Haiku nos crons. 
Quero entender o impacto real no tempo de resposta.
```

### Se suspeitar de VPS fraca:

```
Me ajuda a interpretar a saída do `openclaw status` e do `htop`.
O que os números me dizem sobre se minha VPS aguenta a carga atual?
```

### Se suspeitar de crons simultâneos:

```
Roda mentalmente: se eu tiver 4 crons todos às 09:00, o que acontece 
no servidor? Me mostra como escalonar eles e como listar os crons ativos.
```

### Se suspeitar de heartbeat agressivo:

```
Meu heartbeat está configurado a cada X minutos. 
Qual é o intervalo ideal? E devo usar Haiku pra ele? Por quê?
```

### Para ativar streaming parcial:

```
Quero ativar o streaming parcial no Telegram pra melhorar a percepção 
de velocidade. Me mostra exatamente onde e como configurar isso no openclaw.json.
```

---

## ✅ PROMPT DE VERIFICAÇÃO FINAL

Após implementar as mudanças:

```
Implementei as mudanças que você sugeriu. Agora vamos verificar se funcionou:

1. Como eu testo se o bot ficou mais rápido de forma objetiva?
2. O que devo monitorar nas próximas 24 horas para confirmar que está estável?
3. Tem alguma configuração de "prevenção" que você recomenda pra não ter esse problema de novo?

Me faz um resumo das mudanças que fizemos e do que cada uma resolve.
```

---

## 📊 PROMPT DE EXERCÍCIO PRÁTICO

Para praticar o diagnóstico de forma estruturada:

```
Vou te dar uma situação hipotética e você me guia no diagnóstico:

Situação: Bot funcionando bem por semanas. De repente, hoje à tarde começa a 
demorar 20-30s em toda mensagem. É o mesmo horário em que eu adicionei 3 novos 
crons de monitoramento e aumentei o heartbeat de 30 para 5 minutos.

Sem olhar os logs ainda — quais são as hipóteses mais prováveis? 
Em que ordem eu deveria investigar e por quê?
```

---

## 💡 DICAS DE USO

- **Cole resultados reais:** Quando o agente pedir saída de um comando, cole o resultado real do seu terminal. O diagnóstico fica muito mais preciso.
- **Um problema por vez:** Se tiver múltiplas causas, resolva uma por vez e teste antes de passar pra próxima.
- **Salve as mudanças:** Após cada alteração no `openclaw.json`, recarregue o gateway com `openclaw gateway restart`.
- **Meça antes e depois:** Anote o tempo médio de resposta antes das mudanças para comparar depois.

---

*Prompt criado para a Aula N-4 do Curso OpenClaw | Nível: Intermediário*
