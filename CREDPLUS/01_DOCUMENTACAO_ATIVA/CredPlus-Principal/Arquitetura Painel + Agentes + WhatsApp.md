# ARQUITETURA PAINEL + AGENTES + WHATSAPP

Data: 01/05/2026

## Objetivo

Preparar o `credpluspainel.com` para operar com agentes e, futuramente, com integracao WhatsApp, sem mexer agora na logica principal do painel.

Premissa:

- o painel esta redondo
- a base operacional deve ser preservada
- automacao deve orbitar o painel, nao substituir regras internas

## Estado atual confirmado

Dominio principal:

- `https://credpluspainel.com`

Infra:

- VPS: `72.61.60.213`
- Proxy: `Traefik`
- Container: `credplus-app`
- Porta interna do app: `3000`

Codigo:

- projeto: `/docker/credplus-app`
- app: `/docker/credplus-app/app`

Stack:

- Next.js App Router
- Supabase
- Tailwind
- shadcn/ui
- n8n opcional por webhook

## O que o painel ja faz

- login e controle de acesso por grupo
- dashboard operacional
- cadastro de clientes
- criacao e gestao de contratos
- contratos recorrentes e parcelados
- recebimentos
- amortizacoes
- empurrar vencimento
- comissoes
- pre-cadastros
- PDF de contratos
- classificacao operacional
- webhook para n8n

## Regras centrais que nao devem ser quebradas

- separar capital e juros
- respeitar modalidades `recorrente` e `parcelado`
- usar a classificacao operacional centralizada
- nao duplicar logica financeira fora do painel
- nao enviar Telegram ou WhatsApp diretamente da regra de negocio principal sem camada de integracao

## Desenho recomendado

### Camada 1 — Painel principal

Responsavel por:

- cadastro
- calculo
- operacao financeira
- autenticacao
- status operacional

Essa camada continua sendo a fonte da verdade.

### Camada 2 — Leitura operacional

Responsavel por:

- consultar dashboard
- consultar contratos
- consultar clientes
- consultar pre-cadastros
- consultar recebimentos

Essa camada deve ser somente leitura no inicio.

### Camada 3 — Orquestracao de agentes

Responsavel por:

- transformar dados do painel em resumos
- montar extrato no formato padrao
- separar por responsavel
- detectar:
  - criticos
  - vencidos
  - vence hoje
  - vence amanha
  - novos cadastros

### Camada 4 — Entrega

Canais:

- Telegram
- WhatsApp futuro
- painel interno

## Formato das notificacoes

Padrao desejado pelo usuario:

- estilo extrato bancario
- mesma ordem visual
- mesmos icones
- valores e totais claros

Blocos principais:

- CRITICOS
- VENCIDOS
- VENCE HOJE
- VENCE AMANHA
- NOVO CADASTRO

## O que o agente pode fazer sem risco

- ler vencidos
- ler vence hoje
- ler vence amanha
- ler criticos
- ler novos cadastros
- montar extrato padrao
- filtrar por planilha, responsavel, periodo
- avisar no Telegram ou WhatsApp

## O que o agente nao deve fazer sozinho no inicio

- criar contrato
- quitar parcela
- amortizar
- excluir contrato
- alterar cliente
- alterar comissao

Essas acoes devem ficar como:

- confirmacao humana
- ou segunda fase do projeto

## WhatsApp — desenho pre-pronto

### Caminho recomendado

Usar a API oficial do WhatsApp Business Platform / Cloud API.

Motivo:

- menor risco operacional
- suporte oficial
- webhook confiavel
- escala melhor
- aceita integracao limpa com backend e n8n

### Caminho nao recomendado

Automacao por WhatsApp pessoal, QR paralelo, navegador, extensoes ou robo nao oficial.

Riscos:

- banimento
- instabilidade
- quebra silenciosa
- dependencia de sessao
- baixa previsibilidade

### Como deixar pre-pronto sem implementar agora

Criar mentalmente esta trilha:

`Painel -> Camada de leitura -> Normalizador de extrato -> Integrador de mensagens -> Canal`

No futuro:

`Painel -> webhook/n8n/backend -> formatador padrao -> WhatsApp Cloud API`

### Eventos ideais para WhatsApp futuro

- resumo diario
- vencidos
- vence hoje
- vence amanha
- criticos
- novo pre-cadastro
- aviso manual solicitado pelo dono

### Acoes futuras por WhatsApp, mas com confirmacao

- consultar cliente
- consultar contrato
- consultar parcela
- consultar saldo
- confirmar quitacao
- confirmar amortizacao

## Estrutura sugerida para integracao futura

### Entrada

- consulta manual do dono
- agendamento diario
- evento vindo do painel

### Processamento

- leitura de dados
- classificacao operacional
- formatacao no modelo fixo
- log de envio

### Saida

- Telegram agora
- WhatsApp depois

## O que eu digo sobre WhatsApp

Vale a pena deixar pre-pronto, sim.

Mas a ordem certa e:

1. preservar o painel atual
2. documentar o que cada fluxo faz
3. centralizar a formatacao de notificacao
4. manter canal de envio separado da regra de negocio
5. entrar com WhatsApp oficial so depois

## Decisao atual

Decisao tomada em 01/05/2026:

- `Telegram` sera o canal principal
- `WhatsApp` fica fora do fluxo principal por enquanto
- `WhatsApp` entra apenas como possibilidade futura e secundaria

Motivo:

- dificuldade recorrente para obter e estabilizar API oficial
- complexidade desnecessaria para o momento
- foco imediato deve ser operacao interna confiavel
- Telegram ja e mais adequado para alertas operacionais do dono

## Fluxo principal aprovado

`Painel -> Leitura operacional -> Formatador padrao -> Telegram`

## Fluxo futuro apenas opcional

`Painel -> Leitura operacional -> Formatador padrao -> WhatsApp secundario`

## Observacao importante

A documentacao oficial atual do WhatsApp Business informa que a plataforma trabalha com cobranca por mensagem entregue e por categoria de mensagem. Tambem informa janela de atendimento e pontos gratuitos especificos, como mensagens dentro da janela de servico e alguns pontos de entrada. Isso reforca que o desenho futuro deve usar canal oficial e controle claro de eventos.

Referencias:

- https://whatsappbusiness.com/products/platform-pricing/
- https://developers.facebook.com/docs/whatsapp/

## Proximo passo recomendado

Nao mexer no painel agora.

Fazer primeiro:

- mapa funcional do painel
- mapa dos dados necessarios para extrato
- mapa dos gatilhos de notificacao

Depois:

- montar integrador padrao Telegram
- deixar a mesma estrutura pronta para WhatsApp apenas como extensao futura
