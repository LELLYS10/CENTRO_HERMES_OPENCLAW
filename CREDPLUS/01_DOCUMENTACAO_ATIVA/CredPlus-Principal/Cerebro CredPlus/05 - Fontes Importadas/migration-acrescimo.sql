-- ============================================================
-- Migration: adicionar coluna valor_acrescimo na tabela recebimentos
-- Data: 2026-05-08
-- App: credpluspainel.com (CredPlus V2)
-- ============================================================

-- Rodar no Supabase SQL Editor (Project: credpluspainel)

ALTER TABLE recebimentos
  ADD COLUMN IF NOT EXISTS valor_acrescimo NUMERIC(10,2) NOT NULL DEFAULT 0
  CHECK (valor_acrescimo >= 0);

COMMENT ON COLUMN recebimentos.valor_acrescimo IS
  'Valor de acréscimo manual (multa/juros de atraso) somado ao recebimento. Não entra na base de cálculo de comissão. Lançado apenas pelo Grupo Especial.';

-- Verificar que a coluna foi criada:
-- SELECT column_name, data_type, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'recebimentos' AND column_name = 'valor_acrescimo';
