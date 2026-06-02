# STATUS OAUTH GOOGLE - HERMES

Data: 30/04/2026

## Erro identificado

O Hermes/Jarvis estava com risco de falha no OAuth do Google por incompatibilidade entre a URL do app e a URL de callback autorizada no Google Cloud.

No código, o callback é montado assim:

`APP_URL/auth/callback`

Logo, o Google Cloud precisa autorizar exatamente:

- Origem JavaScript: somente o dominio base do app
- URI de redirecionamento: dominio base + `/auth/callback`

## Estrutura confirmada no projeto

Arquivo principal:

- `jarvis-ai-assistant/server.ts`

Trecho relevante:

- o servidor usa `process.env.APP_URL`
- o callback esperado é `process.env.APP_URL + /auth/callback`
- o servidor local do projeto usa porta `3000`

## URL usada no IA Studio

APP_URL configurada:

`https://ais-dev-uewwbzunklalc5tnluznk3-33113062815.us-west1.run.app`

## Configuração correta no Google Cloud

### Origens JavaScript autorizadas

`https://ais-dev-uewwbzunklalc5tnluznk3-33113062815.us-west1.run.app`

### URIs de redirecionamento autorizados

`https://ais-dev-uewwbzunklalc5tnluznk3-33113062815.us-west1.run.app/auth/callback`

## Secrets confirmados no IA Studio

Manter:

- `GEMINI_API_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `APP_URL`

Observacao:

- `APP_URL` deve conter somente a URL base do app
- nao colocar URL do Google Console
- nao colocar `/auth/callback` dentro do secret `APP_URL`

## APIs que precisam estar ativas no Google Cloud

- Google Drive API
- Google Sheets API
- Gmail API
- Google Calendar API

## Estado atual

Configuracao de `APP_URL` ja adicionada no IA Studio Secrets.

Usuario parou na etapa de retornar ao app e clicar em:

`SINCRONIZAR JARVIS`

## Proximo passo operacional

1. Abrir o app Hermes no IA Studio.
2. Clicar em `SINCRONIZAR JARVIS`.
3. Aceitar as permissoes da conta Google.
4. Se falhar, capturar a mensagem exata de erro.

## Risco observado

Existe um arquivo local com credenciais OAuth na pasta raiz:

- `client_secret_...json`

Boa pratica posterior:

- rotacionar o `GOOGLE_CLIENT_SECRET` depois que tudo estiver funcionando
- evitar deixar esse arquivo solto fora de um local protegido
