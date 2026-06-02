# 🛠️ Script Técnico: Migração de Estorno

## 📋 Descrição
Este script adiciona colunas de auditoria e status à tabela de `recebimentos`, permitindo que pagamentos sejam marcados como estornados sem serem excluídos, mantendo a integridade histórica.

## 💻 Código SQL
```sql
ALTER TABLE recebimentos
  ADD COLUMN IF NOT EXISTS status         text        NOT NULL DEFAULT 'ativo',
  ADD COLUMN IF NOT EXISTS estornado_em   timestamptz,
  ADD COLUMN IF NOT EXISTS estornado_por  uuid,
  ADD COLUMN IF NOT EXISTS motivo_estorno text;

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'recebimentos_status_check'
  ) THEN
    ALTER TABLE recebimentos
      ADD CONSTRAINT recebimentos_status_check
      CHECK (status IN ('ativo', 'estornado'));
  END IF;
END$$;

CREATE INDEX IF NOT EXISTS idx_recebimentos_status ON recebimentos(status);
```

---
_Relacionado a: [[30 - Prompts/Manual de Regras CredPlus V2|Manual de Regras CredPlus V2]]_
