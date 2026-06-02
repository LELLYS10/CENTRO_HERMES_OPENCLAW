# Especificação — Sistema de Acréscimos no CredPlusPainel

**Data:** 2026-05-08
**Aprovado por:** Tom (Lellis Flavio)
**Status:** Aprovado para implementação
**Snapshot VPS:** Criado em 2026-05-08 13:38 (rede de segurança até 2026-05-28)

---

## Contexto

Sistema CredPlusPainel (Next.js + Supabase, hospedado em Docker `/docker/credplus-app/` na VPS Hostinger).

Sistema gerencia empréstimos com 3 grupos de usuários:
- **Especial** (Lellis Flavio = Tom): admin, edita tudo
- **Grupo A** (Sócios): pré-cadastro, visualiza cliente/juros
- **Grupo B** (Colaboradores): pré-cadastro, visualiza cliente/juros, vê SUA comissão

Comissão de Grupo B = % × juros_contrato (NUNCA inclui acréscimo).

---

## Mudanças aprovadas

### 1. Modal "Registrar Recebimento" (só Grupo Especial)

Adicionar 2 alterações:

- Campo **"Juros recebidos"** vira EDITÁVEL (atualmente fixo). Sistema sugere o valor calculado, Tom pode digitar por cima.
- Campo NOVO **"Acréscimo (atraso/manual)"** abaixo do juros, opcional. Soma no Total recebido. Não entra na base de comissão.

### 2. Cálculo automático de multa por atraso

A partir do **4º dia de atraso**, sistema sugere automaticamente um valor de acréscimo:
- **R$ 5,00 por dia** retroativo (contando do dia do vencimento)
- **R$ 10,00 multa fixa** (uma vez só, não cumula)

Exemplo: cliente vence dia 10, paga dia 13 → 4 dias × R$ 5 + R$ 10 = R$ 30 sugerido.

Valor sugerido é **opcional** — Tom decide cobrar, alterar ou zerar.

### 3. Reset mensal

- Acréscimos do **Grupo A e B**: param de calcular no último dia do mês, zeram no início do mês seguinte.
- Acréscimos dos **clientes próprios do Tom (Especial)**: calculam INFINITO, não resetam (clientes que dão dor de cabeça).

### 4. Permissões

| Grupo | Vê acréscimo? | Edita acréscimo? | Pré-cadastro? |
|---|---|---|---|
| Especial (Tom) | ✅ Sim | ✅ Sim | ✅ Sim |
| Grupo A (Sócios) | ❌ Não | ❌ Não | ✅ Sim |
| Grupo B (Colaboradores) | ❌ Não | ❌ Não | ✅ Sim |

### 5. Recibos

- **NÃO mostram acréscimo** por enquanto (consistente com porcentagem, que já não aparece)
- Pode ser revisto no futuro

### 6. Comissão (regra protegida)

- Comissão calculada **SEMPRE** sobre `juros_contrato` (valor da tabela do cliente)
- **NUNCA** sobre `valor_acrescimo`
- Reset mensal preservado para Grupo B
- Se cliente do colaborador não pagou, Tom desconta da comissão dele

---

## Mudanças técnicas necessárias

### Banco de dados

Adicionar coluna `valor_acrescimo` (NUMERIC, default 0) na tabela de recebimentos (Supabase). Registros antigos ficam com 0 — não bagunça histórico.

### Código (Next.js)

Arquivos prováveis a editar (a confirmar lendo o repo):
- Componente do modal "RegistrarRecebimento" (transformar campo de display em input editável + adicionar campo acréscimo)
- Função/hook de cálculo de comissão (blindar para usar SÓ juros_contrato)
- Lógica de cálculo automático de multa (calcular dias de atraso + sugerir valor)
- Permissão por grupo (esconder campo acréscimo para A e B)

### Build e deploy

Após edição:
```
cd /docker/credplus-app && docker compose up -d --build
```

---

## Validação

- Login como Especial → ver os 2 campos novos no modal
- Login como Grupo A → modal NÃO mostra campo acréscimo
- Login como Grupo B → modal NÃO mostra, comissão calcula igual antes
- Registrar recebimento com R$ 100 juros + R$ 25 acréscimo → total R$ 125
- Conferir no banco: registro tem valor_juros=100 e valor_acrescimo=25
- Conferir comissão do colaborador: aumentou só sobre os R$ 100

---

## Reversão (caso algo dê errado)

1. Reverter código Git e fazer rebuild Docker
2. Caso pior: restaurar snapshot Hostinger (30 minutos)
3. Snapshot expira em 2026-05-28
