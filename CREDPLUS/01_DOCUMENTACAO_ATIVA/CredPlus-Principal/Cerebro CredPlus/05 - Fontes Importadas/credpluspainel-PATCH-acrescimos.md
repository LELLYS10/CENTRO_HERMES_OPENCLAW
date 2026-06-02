# Patch CredPlusPainel — Campo Acréscimo no Recebimento

**Data:** 2026-05-08
**Caminho:** A (simples — sem cálculo automático de multa)
**Snapshot VPS:** 2026-05-08 13:38 (válido até 2026-05-28)
**Risco:** Baixo. Reversível por git revert + rebuild Docker.

---

## O que este patch faz

Adiciona ao modal "Registrar Recebimento" do CredPlusPainel:

1. **Campo Juros recebidos EDITÁVEL** — sistema sugere o valor calculado, mas Tom (Especial) pode digitar por cima.
2. **Campo Acréscimo** — input opcional manual, somente visível para Grupo Especial. Soma no Total recebido. NÃO entra na base de comissão.

Para Grupo A, B e Família o modal continua exatamente como hoje — zero mudança visual ou de comportamento.

---

## Arquivos modificados

1. **Banco de dados (Supabase)**: nova coluna `valor_acrescimo` na tabela `recebimentos`
2. **`/docker/credplus-app/app/components/contratos/bloco-operacoes.tsx`**: adicionar campos no FormRecebimento
3. **`/docker/credplus-app/app/app/api/recebimentos/route.ts`**: aceitar e salvar `valor_acrescimo`
4. **Página pai que usa BlocoOperacoes**: passar prop `usuarioGrupo`

---

## Passo 1 — SQL migration (rodar no Supabase SQL Editor)

```sql
-- Adiciona coluna valor_acrescimo na tabela recebimentos
ALTER TABLE recebimentos
  ADD COLUMN IF NOT EXISTS valor_acrescimo NUMERIC(10,2) NOT NULL DEFAULT 0
  CHECK (valor_acrescimo >= 0);

COMMENT ON COLUMN recebimentos.valor_acrescimo IS
  'Valor de acréscimo manual (multa/juros de atraso) somado ao recebimento. Não entra na base de cálculo de comissão.';
```

Registros existentes ficam com `valor_acrescimo = 0` automaticamente. Não bagunça nada.

---

## Passo 2 — Atualizar tipos TypeScript

Em `/docker/credplus-app/app/types/index.ts`, encontre a interface `Recebimento` e adicione a linha:

```typescript
export interface Recebimento {
  id: string
  contrato_id: string
  parcela_id: string | null
  registrado_por: string
  tipo: TipoRecebimento
  capital_recebido: number
  juros_recebido: number
  valor_acrescimo: number   // ← ADICIONAR ESTA LINHA
  data_recebimento: string
  forma_pagamento: FormaPagamento | null
  observacoes: string | null
  criado_em: string
  contrato?: Contrato
  parcela?: Parcela
}
```

---

## Passo 3 — Atualizar API `/api/recebimentos/route.ts`

No handler **POST** do arquivo `/docker/credplus-app/app/app/api/recebimentos/route.ts`:

1. Aceitar `valor_acrescimo` do body
2. Validar: só Especial pode enviar valor > 0
3. Inserir no banco

Localizar onde o body é desestruturado (algo como `const { contrato_id, tipo, ... } = body`) e adicionar:

```typescript
const valor_acrescimo = Number(body.valor_acrescimo) || 0

// Proteção: só Especial pode lançar acréscimo
if (valor_acrescimo > 0 && profile.grupo !== 'especial') {
  return NextResponse.json(
    { error: 'Apenas Grupo Especial pode lançar acréscimo.' },
    { status: 403 }
  )
}
```

E onde o INSERT é feito, adicionar `valor_acrescimo` aos campos. Exemplo:

```typescript
const { data, error } = await supabase
  .from('recebimentos')
  .insert({
    contrato_id,
    parcela_id: parcela_id ?? null,
    registrado_por: profile.id,
    tipo,
    capital_recebido,
    juros_recebido,
    valor_acrescimo,                  // ← ADICIONAR
    data_recebimento,
    forma_pagamento: forma_pagamento ?? null,
    observacoes: observacoes ?? null,
  })
  .select()
  .single()
```

⚠️ **VALIDAÇÃO IMPORTANTE NA COMISSÃO:**
Onde a comissão é calculada/inserida no servidor (procurar `comissoes` ou `Comissao` ou `juros_base`), o valor `juros_base` deve ser o juros do contrato (`parcela.juros_parcela` ou cálculo recorrente), **NUNCA** `valor_acrescimo`. Provavelmente já está correto — mas o dev deve confirmar.

---

## Passo 4 — Atualizar componente `bloco-operacoes.tsx`

Substituir o conteúdo atual de `/docker/credplus-app/app/components/contratos/bloco-operacoes.tsx` pelo arquivo **`bloco-operacoes-NOVO.tsx`** entregue junto neste patch.

Mudanças:

- Adicionada prop `usuarioGrupo` no componente
- No `FormRecebimento`:
  - `jurosPreview` virou `jurosBase` (sempre calculado, não muda — usado para comissão)
  - Novo state `jurosRecebido` (editável, default = `jurosBase`)
  - Novo state `valorAcrescimo` (editável, default = "0")
  - Inputs visíveis APENAS quando `usuarioGrupo === 'especial'`
  - Para outros grupos, o modal funciona como hoje (sem campos editáveis)
- Preview atualizado:
  - Mostra 3 linhas (Capital + Juros + Acréscimo) quando há acréscimo
  - Total = capital + juros editado + acréscimo
- Comissão preview usa `jurosBase` (não o editado, não o acréscimo)
- POST envia `juros_recebido` e `valor_acrescimo`

---

## Passo 5 — Atualizar página pai

A página que renderiza `<BlocoOperacoes ... />` precisa passar o `usuarioGrupo`. Provavelmente é uma Server Component em `/docker/credplus-app/app/app/(dashboard)/contratos/[id]/page.tsx` ou similar.

Adicionar:

```typescript
import { getAuthUser } from '@/lib/auth'

export default async function Page({ params }: { params: { id: string } }) {
  const { profile } = await getAuthUser()
  // ... código existente ...

  return (
    <BlocoOperacoes
      // ... props existentes ...
      usuarioGrupo={profile.grupo}   // ← ADICIONAR
    />
  )
}
```

---

## Passo 6 — Build e deploy

Na VPS Hostinger, terminal:

```bash
cd /docker/credplus-app
docker compose down
docker compose up -d --build
docker logs credplus-app -f
```

Aguarde o build (1-3 minutos). O log vai mostrar "Ready in Xs" quando subir.

---

## Plano de teste

### Teste 1 — Como Especial (Tom)
1. Login no painel como Tom
2. Ir em algum contrato
3. Clicar "Registrar Recebimento"
4. ✅ Deve ver os 2 campos editáveis: Juros recebidos e Acréscimo
5. Digitar Juros R$ 100, Acréscimo R$ 25
6. Total = R$ 125
7. Confirmar
8. Conferir no banco: registro com `juros_recebido=100` e `valor_acrescimo=25`

### Teste 2 — Como Sócio (Grupo A)
1. Login como sócio
2. Mesmo fluxo
3. ✅ Modal NÃO mostra campo Acréscimo
4. ✅ Juros recebidos pode aparecer como display fixo (igual hoje)
5. Confirma recebimento normal

### Teste 3 — Como Colaborador (Grupo B)
1. Login como colaborador
2. Ver tela de comissão antes de registrar
3. Registrar recebimento de juros R$ 100
4. ✅ Comissão dele aumenta na proporção dos R$ 100 (não inclui acréscimo, porque ele não viu nem inseriu)

### Teste 4 — Comissão protegida (Especial gerando comissão pra Colaborador)
1. Tom registra recebimento num contrato de cliente cujo responsável é Colaborador
2. Tom digita Juros R$ 100 (igual ao do contrato) + Acréscimo R$ 25
3. ✅ Comissão do colaborador deve ser % × R$ 100 (NUNCA × R$ 125)

---

## Reversão (se algo der errado)

```bash
cd /docker/credplus-app
git checkout HEAD~1 -- components/contratos/bloco-operacoes.tsx
git checkout HEAD~1 -- app/api/recebimentos/route.ts
git checkout HEAD~1 -- types/index.ts
docker compose down
docker compose up -d --build
```

E no Supabase, a coluna `valor_acrescimo` pode ficar lá sem prejuízo (default 0). Se quiser remover:

```sql
ALTER TABLE recebimentos DROP COLUMN valor_acrescimo;
```

Caso pior absoluto: restaurar snapshot Hostinger 2026-05-08 13:38 (30 min, válido até 2026-05-28).

---

## O que ESTE patch NÃO faz (deixei pra fase 2)

- Cálculo automático de multa (R$ 5/dia + R$ 10) a partir do 4º dia
- Reset mensal por grupo
- Cálculo infinito pros clientes do Especial
- Mostrar acréscimo em recibos PDF

Tudo isso é fácil de adicionar depois, se você quiser. Por enquanto, lança manual.
