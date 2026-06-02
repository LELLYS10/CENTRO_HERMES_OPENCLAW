# CredPlus Painel — Patch de Headers de Segurança

**Data:** 2026-05-08
**Arquivo alvo:** `next.config.js` (ou `.ts` / `.mjs`) na raiz do projeto
**Impacto:** Zero em lógica. Apenas adiciona 4 headers HTTP nas respostas.
**Risco:** Baixo. Reversível removendo o bloco `async headers()`.

---

## O que este patch faz

Adiciona 4 headers de segurança recomendados pela OWASP, sem alterar nenhuma lógica de aplicação:

| Header | Função |
|---|---|
| `Strict-Transport-Security` | Força HTTPS em todas as conexões (já é o caso, só formaliza) |
| `X-Content-Type-Options: nosniff` | Impede browser de adivinhar tipo de arquivo |
| `X-Frame-Options: SAMEORIGIN` | Impede embed em iframe de outros domínios (anti-clickjacking) |
| `Referrer-Policy` | Controla envio do header Referer pra terceiros |

---

## Código pra colar

### Versão JavaScript (`next.config.js`)

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // ... suas configs atuais aqui (não mexa)

  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
```

### Versão TypeScript (`next.config.ts`)

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // ... suas configs atuais aqui (não mexa)

  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ]
  },
}

export default nextConfig
```

---

## Casos especiais

### Se já existe `async headers()` no arquivo
Não duplique a função. Adicione apenas os 4 headers dentro do array já existente.

### Se for `next.config.mjs`
Use a sintaxe ESM com `export default nextConfig` (igual ao TS).

---

## Passo a passo do deploy

1. Abrir `next.config.js` (ou `.ts` / `.mjs`) na raiz do projeto credpluspainel
2. Colar o bloco `async headers()` conforme acima
3. Salvar
4. `git add next.config.js && git commit -m "feat: add basic security headers"`
5. `git push`
6. Aguardar o deploy automático no Vercel terminar
7. Validar com:
   ```bash
   curl -sI https://credpluspainel.com/login | grep -iE "strict-transport|x-frame|x-content-type|referrer-policy"
   ```
   Deve retornar 4 linhas (uma pra cada header).

---

## Como reverter (caso algo quebre — não deve)

Apenas remover o bloco `async headers()` inteiro e fazer push. Site volta exatamente como estava.

---

## Headers que NÃO foram incluídos (de propósito)

- **Content-Security-Policy (CSP):** Exige tuning específico (Google Fonts, Supabase, Vercel Analytics etc). Mal configurado, buga o site. Aplicar depois com auditoria.
- **Permissions-Policy:** Restringe APIs do browser (câmera, mic, geo). Aplicar quando definirmos quais APIs o app realmente usa.
