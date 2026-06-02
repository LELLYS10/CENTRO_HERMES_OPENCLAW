# Prompt do Aluno: Tópicos no Telegram + Arquitetura de Agentes

**Cole este prompt no chat com sua Amora:**

---

Amora, preciso da sua ajuda para configurar tópicos no Telegram e entender a diferença entre ter um agente MAIN compartilhado vs agentes isolados.

**Tarefas:**

1. **Me guiar na criação de tópicos no Telegram:**
   - Como transformar meu grupo em supergrupo
   - Como ativar e criar tópicos
   - Como descobrir o chat ID de cada tópico

2. **Configurar você para responder sem menção em tópicos específicos:**
   - Mostrar como editar o `config.yaml` pra você responder automaticamente
   - Explicar o `mode: mention` vs `mode: all`
   - Testar se funcionou

3. **Me explicar as duas arquiteturas:**
   - **MAIN compartilhado** — um agente respondendo em múltiplos tópicos
   - **Agentes isolados** — um agente por tópico
   - Pros e contras de cada
   - Quando usar cada uma

4. **Impacto em:**
   - Workspace (onde ficam os arquivos?)
   - Memória (MEMORY.md compartilhado ou isolado?)
   - Crons (heartbeats compartilhados ou isolados?)
   - SOUL.md, USER.md, TOOLS.md (globais ou por agente?)

5. **Me ajudar a decidir qual arquitetura usar:**
   - Fazer perguntas sobre meu caso de uso
   - Recomendar a melhor opção
   - Mostrar exemplo de config completo

**Contexto sobre mim:**
- [Descreva aqui: você trabalha sozinho? tem múltiplos clientes? precisa de privacidade entre tópicos? projetos relacionados ou isolados?]

**Exemplo:**
> "Sou freelancer e tenho 3 clientes. Cada cliente tem um tópico no meu grupo do Telegram. Preciso que dados de um cliente NUNCA apareçam pra outro."

---

**Leia o guia completo em:**
`/root/.openclaw/workspace-curso-openclaw/prds/topicos-telegram-arquitetura.md`

**Depois de configurar:**
- Teste mandando mensagem nos tópicos
- Verifique se você responde automaticamente (quando `mode: all`)
- Confirme que cada agente isolado **não vê** o workspace dos outros
- Ajuste o SOUL.md de cada agente (se isolados)

**Se algo der errado:**
- `openclaw logs --tail 100` pra ver erros
- `openclaw gateway restart` pra aplicar mudanças no config
- Me chame no privado que te ajudo

Tá pronta pra começar?
