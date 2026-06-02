# Status de Ambientes - CredPlus Painel e EMP

**Data de verificação:** 29/04/2026  
**Servidor:** `72.61.60.213` (`srv1416255`)

## App 1 — Empresa (Painel Oficial)
- **Domínio principal:** `https://credpluspainel.com`
- **Domínio adicional:** `https://www.credpluspainel.com`
- **Runtime:** Docker
- **Container:** `credplus-app`
- **Rede/Entrada:** Traefik em `:443` e `:80`
- **Porta interna do app:** `3000/tcp` (exposta internamente via Traefik)
- **Comportamento HTTP atual:** `307` para `/login` e depois `200` (normal para app com autenticação)
- **Status atual:** Online e saudável

## App 2 — Filhos (EMP)
- **Domínio principal:** `https://credplusemp.com.br`
- **Runtime:** PM2
- **Processo PM2:** `credplus`
- **Diretório do app:** `/root/CredPlus1.0`
- **Porta do serviço:** `3000` no host
- **Roteamento:** Traefik (`/docker/traefik-wvkg/dynamic/credplusemp.yml`) apontando para `http://127.0.0.1:3000`
- **Comportamento HTTP atual:** `200` (servindo `index.html`)
- **Status atual:** Online e saudável

## Infra Compartilhada
- **Traefik:** `traefik-wvkg-traefik-1` (terminação TLS e roteamento de domínios)
- **n8n:** `n8n-credplus-n8n-1` na porta host `5679`

## Regra de Operação (alinhamento)
- `credpluspainel.com` = app da empresa (foco de evolução)
- `credplusemp.com.br` = app separado dos filhos (manter isolado)
- Evitar mistura de deploy, variáveis e automações entre os dois ambientes

