# Prompt — Aula Extra A: Integrar Suas Ferramentas

> Cole este prompt no chat do seu agente depois de assistir a Aula Extra A.

---

Acabei de assistir a aula sobre integração de ferramentas. Agora quero conectar meu agente às ferramentas que eu uso no dia a dia.

**O que preciso fazer:**

## 1. Mapear minhas ferramentas

Me ajude a listar as ferramentas/plataformas que eu uso mais:
- Gestão de projetos? (Notion, Trello, Asana, Monday...)
- Pagamentos? (Stripe, PayPal, Mercado Pago...)
- Analytics? (Google Analytics, Mixpanel, Amplitude...)
- CRM/Vendas? (HubSpot, Pipedrive, RD Station...)
- Email marketing? (ConvertKit, Mailchimp...)
- Social media? (Buffer, Later, Hootsuite...)
- Outras ferramentas críticas?

Pra cada uma, me diga:
- ✅ Tem skill pronta no ClawHub? (`clawhub search nome`)
- ❌ Precisa integrar API direto?

## 2. Instalar skills prontas

Para as ferramentas que **têm skill pronta**, me guie pra:
1. Instalar a skill (`clawhub install nome`)
2. Configurar credenciais (se necessário)
3. Testar se funciona
4. Documentar no TOOLS.md

## 3. Integrar APIs diretas

Para as ferramentas **sem skill pronta**, me guie pra:
1. Descobrir onde fica a API key na ferramenta
2. Guardar no 1Password (ou me ensinar a configurar 1Password se eu não tiver)
3. Testar a API com você
4. Documentar no TOOLS.md com:
   - Nome da integração
   - Item no 1Password
   - Permissões (read/write)
   - Limitações ou guardrails

## 4. Documentar tudo no TOOLS.md

Crie ou atualize meu `TOOLS.md` com:
- Lista de todas integrações ativas
- Como acessar cada uma
- Guardrails de segurança (o que você pode/não pode fazer)

## 5. Casos de uso práticos

Depois de tudo configurado, me sugira **3 casos de uso práticos** pra testar as integrações. Exemplos:
- "Me mostre meu MRR atual do Stripe"
- "Liste as tasks do Notion com status 'In Progress'"
- "Quantas visitas teve no site ontem?"

**Regras importantes:**

🔴 **NUNCA** colocar API keys direto no código ou config — sempre 1Password
🔴 **SEMPRE** me perguntar antes de fazer operações de escrita (criar, atualizar, deletar)
🔴 **SEMPRE** documentar no TOOLS.md quando adicionar uma integração nova

**Se eu não tiver 1Password instalado:**
Me explique como instalar e configurar (ou me sugira alternativas como Bitwarden).

---

Vamos começar pelo mapeamento das minhas ferramentas. Me faça as perguntas e vamos integrando uma por uma.
