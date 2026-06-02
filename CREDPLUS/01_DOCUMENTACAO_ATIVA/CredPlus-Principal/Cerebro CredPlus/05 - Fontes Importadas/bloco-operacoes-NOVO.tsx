'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import {
  Select, SelectContent, SelectItem,
  SelectTrigger, SelectValue,
} from '@/components/ui/select'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from '@/components/ui/dialog'

import {
  calcularJurosRecorrente, calcularComissao, formatarMoeda, formatarDataBR, arredondar,
} from '@/lib/financeiro'
import MenuSaidas from '@/components/saidas/menu-saidas'
import {
  Banknote, TrendingDown, AlertCircle, Loader2, CheckCircle2,
} from 'lucide-react'

function getHojeBrasil() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(new Date())
}

// ── Tipos ────────────────────────────────────────────────────────
interface ParcelaAtual {
  id: string
  numero_parcela: number
  total_parcelas: number
  capital_parcela: number
  juros_parcela: number
  data_vencimento: string
  status: 'pendente' | 'empurrado'
}

interface Props {
  contratoId: string
  modalidade: 'parcelado' | 'recorrente'
  capitalAtual: number
  taxaMensal: number
  parcelaAtual: ParcelaAtual | null
  responsavelId: string | null
  grupoResponsavel: 'especial' | 'a' | 'b' | 'familia' | null
  taxaComissaoResponsavel: number | null
  geraComissaoContrato: boolean
  podeGerarSaidasGestao?: boolean
  somenteVisual?: boolean
  // NOVO: grupo do USUÁRIO logado (não do responsável do contrato)
  usuarioGrupo?: 'especial' | 'a' | 'b' | 'familia' | 'admin' | null
}

// ── Bloco principal ──────────────────────────────────────────────
export default function BlocoOperacoes({
  contratoId, modalidade, capitalAtual, taxaMensal, parcelaAtual,
  responsavelId, grupoResponsavel, taxaComissaoResponsavel,
  geraComissaoContrato,
  podeGerarSaidasGestao = false, somenteVisual = false,
  usuarioGrupo = null,
}: Props) {
  const router = useRouter()
  const [dialog, setDialog] = useState<'recebimento' | 'amortizacao' | null>(null)

  const fechar  = () => setDialog(null)
  const refresh = () => { fechar(); router.refresh() }

  const jurosRecorrente = modalidade === 'recorrente'
    ? calcularJurosRecorrente(capitalAtual, taxaMensal)
    : 0

  return (
    <>
      {/* Card de operações */}
      <div
        className="rounded-xl border border-[oklch(0.55_0.18_160/0.30)]
          bg-[oklch(0.55_0.18_160/0.04)] p-5 space-y-4
          shadow-[0_2px_16px_oklch(0.55_0.18_160/0.08)]"
      >
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Operações Financeiras
        </h3>

        {modalidade === 'parcelado' && parcelaAtual ? (
          <div className="rounded-lg border border-border/50 bg-card p-4 space-y-3">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold">
                  Parcela {parcelaAtual.numero_parcela}/{parcelaAtual.total_parcelas}
                </span>
                {parcelaAtual.status === 'empurrado' && (
                  <Badge variant="outline" className="text-xs bg-info/10 border-info/40 text-info">
                    Empurrada
                  </Badge>
                )}
              </div>
              <span className="text-xs text-muted-foreground">
                vence {formatarDataBR(parcelaAtual.data_vencimento)}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 text-sm">
              <div>
                <p className="text-xs text-muted-foreground mb-0.5">Capital</p>
                <p className="font-medium">{formatarMoeda(parcelaAtual.capital_parcela)}</p>
              </div>
              <div className="border-l border-border/40 pl-3">
                <p className="text-xs text-muted-foreground mb-0.5">Juros</p>
                <p className="font-medium text-[oklch(0.65_0.18_160)]">
                  {formatarMoeda(parcelaAtual.juros_parcela)}
                </p>
              </div>
              <div className="border-l border-border/40 pl-3">
                <p className="text-xs text-muted-foreground mb-0.5">Total</p>
                <p className="font-semibold">
                  {formatarMoeda(parcelaAtual.capital_parcela + parcelaAtual.juros_parcela)}
                </p>
              </div>
            </div>
          </div>
        ) : modalidade === 'parcelado' ? (
          <div className="rounded-lg border border-border/40 bg-secondary/20 p-4">
            <p className="text-sm text-muted-foreground">Sem parcelas pendentes neste contrato.</p>
          </div>
        ) : (
          <div className="rounded-lg border border-border/50 bg-card p-4 space-y-3">
            <p className="text-xs font-medium text-fuchsia-400/80">Ciclo atual — juros recorrentes</p>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="text-xs text-muted-foreground mb-0.5">Capital em aberto</p>
                <p className="font-medium">{formatarMoeda(capitalAtual)}</p>
              </div>
              <div className="border-l border-border/40 pl-3">
                <p className="text-xs text-muted-foreground mb-0.5">Juros do ciclo</p>
                <p className="font-medium text-[oklch(0.65_0.18_160)]">
                  {formatarMoeda(jurosRecorrente)}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Ações */}
        {!somenteVisual && (
        <div className="flex gap-3 flex-wrap">
          <Button
            onClick={() => setDialog('recebimento')}
            disabled={modalidade === 'parcelado' && !parcelaAtual}
            className="gap-2 bg-[oklch(0.55_0.18_160)] hover:bg-[oklch(0.50_0.18_160)]
              text-white border-0 shadow-[0_2px_12px_oklch(0.55_0.18_160/0.35)]"
          >
            <Banknote className="w-4 h-4" />
            Registrar Recebimento
          </Button>
          <Button
            onClick={() => setDialog('amortizacao')}
            variant="outline"
            className="gap-2 border-border/60"
          >
            <TrendingDown className="w-4 h-4" />
            Amortização de Capital
          </Button>
        </div>
        )}
      </div>

      {/* Dialog — Recebimento */}
      <Dialog open={dialog === 'recebimento'} onOpenChange={open => !open && fechar()}>
        <DialogContent className="max-w-lg max-h-[92vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Registrar Recebimento</DialogTitle>
          </DialogHeader>
          <FormRecebimento
            contratoId={contratoId}
            modalidade={modalidade}
            capitalAtual={capitalAtual}
            taxaMensal={taxaMensal}
            parcelaAtual={parcelaAtual}
            responsavelId={responsavelId}
            grupoResponsavel={grupoResponsavel}
            taxaComissaoResponsavel={taxaComissaoResponsavel}
            geraComissaoContrato={geraComissaoContrato}
            podeGerarSaidasGestao={podeGerarSaidasGestao}
            usuarioGrupo={usuarioGrupo}
            onSucesso={refresh}
          />
        </DialogContent>
      </Dialog>

      {/* Dialog — Amortização */}
      <Dialog open={dialog === 'amortizacao'} onOpenChange={open => !open && fechar()}>
        <DialogContent className="max-w-lg max-h-[92vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Amortização de Capital</DialogTitle>
          </DialogHeader>
          <FormAmortizacao
            contratoId={contratoId}
            modalidade={modalidade}
            capitalAtual={capitalAtual}
            onSucesso={refresh}
          />
        </DialogContent>
      </Dialog>
    </>
  )
}

// ── Form Recebimento ─────────────────────────────────────────────
function FormRecebimento({
  contratoId, modalidade, capitalAtual, taxaMensal, parcelaAtual,
  responsavelId, grupoResponsavel, taxaComissaoResponsavel,
  geraComissaoContrato,
  podeGerarSaidasGestao, usuarioGrupo, onSucesso,
}: {
  contratoId: string
  modalidade: 'parcelado' | 'recorrente'
  capitalAtual: number
  taxaMensal: number
  parcelaAtual: ParcelaAtual | null
  responsavelId: string | null
  grupoResponsavel: 'especial' | 'a' | 'b' | 'familia' | null
  taxaComissaoResponsavel: number | null
  geraComissaoContrato: boolean
  podeGerarSaidasGestao: boolean
  usuarioGrupo: 'especial' | 'a' | 'b' | 'familia' | 'admin' | null
  onSucesso: () => void
}) {
  const hoje = getHojeBrasil()

  const [tipo, setTipo] = useState<'parcela_completa' | 'somente_juros'>(
    modalidade === 'parcelado' ? 'parcela_completa' : 'somente_juros',
  )
  const [data, setData]   = useState(hoje)
  const [forma, setForma] = useState<string | undefined>(undefined)
  const [obs, setObs]     = useState('')
  const [loading, setLoading] = useState(false)
  const [erro, setErro]       = useState('')
  const [sucesso, setSucesso] = useState(false)
  const [recebimentoId, setRecebimentoId] = useState<string | null>(null)

  // Capital extra (recorrente com amortização)
  const [comCapital, setComCapital]     = useState(false)
  const [capitalExtra, setCapitalExtra] = useState('')
  const capitalExtraNum = parseFloat(capitalExtra.replace(',', '.')) || 0

  // PERMISSÃO: só Especial pode editar juros e lançar acréscimo
  const ehEspecial = usuarioGrupo === 'especial'

  // Valores BASE — calculados pelo sistema, NUNCA mudam
  // (estes alimentam a base de comissão)
  const capitalBase = tipo === 'parcela_completa'
    ? (parcelaAtual?.capital_parcela ?? 0)
    : (comCapital ? capitalExtraNum : 0)

  const jurosBase = modalidade === 'recorrente'
    ? calcularJurosRecorrente(capitalAtual, taxaMensal)
    : (parcelaAtual?.juros_parcela ?? 0)

  // Valores EDITÁVEIS — Tom (Especial) pode digitar por cima
  const [jurosRecebidoStr, setJurosRecebidoStr] = useState(jurosBase.toFixed(2))
  const [acrescimoStr, setAcrescimoStr] = useState('0.00')

  const jurosRecebidoNum = parseFloat(jurosRecebidoStr.replace(',', '.')) || 0
  const acrescimoNum = parseFloat(acrescimoStr.replace(',', '.')) || 0

  // Valores PRA O PREVIEW
  // Para Especial: usa o que ele digitou
  // Para outros: usa o cálculo base (igual antes)
  const jurosPreview = ehEspecial ? jurosRecebidoNum : jurosBase
  const acrescimoPreview = ehEspecial ? acrescimoNum : 0
  const totalPreview = capitalBase + jurosPreview + acrescimoPreview

  // Comissão — SEMPRE sobre jurosBase (NUNCA inclui acréscimo, NUNCA usa o editado)
  const exibirComissao =
    geraComissaoContrato &&
    grupoResponsavel === 'b' &&
    (taxaComissaoResponsavel ?? 0) > 0

  const comissaoPreview = exibirComissao
    ? calcularComissao(jurosBase, taxaComissaoResponsavel!)
    : 0

  function toggleCapital() {
    setComCapital(v => !v)
    setCapitalExtra('')
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!data) { setErro('Informe a data do recebimento.'); return }
    if (comCapital && capitalExtraNum <= 0) { setErro('Informe o valor do capital.'); return }
    if (comCapital && capitalExtraNum > capitalAtual + 0.001) {
      setErro(`Capital máximo: ${formatarMoeda(capitalAtual)}`); return
    }
    if (ehEspecial && jurosRecebidoNum < 0) {
      setErro('Juros recebidos não pode ser negativo.'); return
    }
    if (ehEspecial && acrescimoNum < 0) {
      setErro('Acréscimo não pode ser negativo.'); return
    }

    setLoading(true); setErro('')

    try {
      // 1. Registrar juros (+ acréscimo se Especial)
      const payload: Record<string, unknown> = {
        contrato_id:      contratoId,
        tipo,
        data_recebimento: data,
        forma_pagamento:  forma ?? null,
        observacoes:      obs.trim() || null,
      }
      if (parcelaAtual) payload.parcela_id = parcelaAtual.id
      // Só Especial sobrescreve o juros e/ou envia acréscimo
      if (ehEspecial) {
        payload.juros_recebido_override = jurosRecebidoNum
        payload.valor_acrescimo = acrescimoNum
      }

      const res  = await fetch('/api/recebimentos', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
      })
      const json = await res.json()

      if (!res.ok) {
        setErro(json.error ?? 'Erro ao registrar.')
        toast.error('Erro ao registrar recebimento', { description: json.error })
        setLoading(false)
        return
      }
      setRecebimentoId(json.data?.id ?? null)

      // 2. Registrar capital (amortização) se solicitado
      if (comCapital && capitalExtraNum > 0) {
        const resAmort = await fetch('/api/amortizacoes', {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify({
            contrato_id:      contratoId,
            valor_amortizado: capitalExtraNum,
            data_amortizacao: data,
            observacoes:      obs.trim()
              ? `[Capital recebido junto aos juros] ${obs.trim()}`
              : 'Capital recebido junto aos juros do ciclo',
          }),
        })
        const jsonAmort = await resAmort.json()
        if (!resAmort.ok) {
          setErro(jsonAmort.error ?? 'Erro ao registrar capital.')
          toast.error('Erro ao registrar amortização', { description: jsonAmort.error })
          setLoading(false)
          return
        }
      }

      toast.success('Recebimento registrado!', {
        description: `${formatarMoeda(totalPreview)} lançado com sucesso.`,
      })
      setSucesso(true)
    } catch {
      setErro('Sem conexão. Tente novamente.')
      toast.error('Sem conexão')
      setLoading(false)
    }
  }

  if (sucesso) {
    return (
      <div className="flex flex-col items-center gap-4 py-10">
        <div
          className="w-16 h-16 rounded-full flex items-center justify-center
            bg-[oklch(0.55_0.18_160/0.12)] border-2 border-[oklch(0.55_0.18_160/0.35)]
            shadow-[0_0_24px_oklch(0.55_0.18_160/0.20)]"
        >
          <CheckCircle2 className="w-8 h-8 text-[oklch(0.65_0.18_160)]" />
        </div>
        <p className="text-lg font-semibold">Recebimento registrado!</p>
        <div className="w-full max-w-md">
          <MenuSaidas
            autoOpen
            hideTrigger
            title="Saídas do recebimento"
            description="Escolha como deseja visualizar ou imprimir este lançamento."
            reciboHref={recebimentoId ? `/recebimentos/${recebimentoId}/recibo` : null}
            htmlHref={podeGerarSaidasGestao && responsavelId && (grupoResponsavel === 'a' || grupoResponsavel === 'b')
              ? `/dashboard/extrato-html?responsavel=${encodeURIComponent(responsavelId)}`
              : null}
            pdfBaseHref={podeGerarSaidasGestao && responsavelId && (grupoResponsavel === 'a' || grupoResponsavel === 'b')
              ? `/api/dashboard/relatorio-pdf?responsavel=${encodeURIComponent(responsavelId)}`
              : null}
          />
        </div>
        <Button type="button" variant="outline" onClick={onSucesso}>
          Fechar e atualizar contrato
        </Button>
      </div>
    )
  }

  return (
    <form onSubmit={onSubmit} className="space-y-5 pt-1">
      {/* Seletor de tipo — apenas para parcelado */}
      {modalidade === 'parcelado' && parcelaAtual && (
        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => setTipo('parcela_completa')}
            className={`rounded-xl border p-3.5 text-left space-y-1.5 transition-all cursor-pointer ${
              tipo === 'parcela_completa'
                ? 'border-[oklch(0.55_0.18_160/0.60)] bg-[oklch(0.55_0.18_160/0.08)] ring-1 ring-[oklch(0.55_0.18_160/0.25)]'
                : 'border-border/60 hover:border-border bg-card'
            }`}
          >
            <p className="text-xs font-semibold leading-none">Parcela Completa</p>
            <p className="text-[11px] text-muted-foreground leading-snug">
              Capital + juros — parcela {parcelaAtual.numero_parcela}/{parcelaAtual.total_parcelas}
            </p>
            <p className="text-sm font-bold mt-0.5">
              {formatarMoeda(parcelaAtual.capital_parcela + parcelaAtual.juros_parcela)}
            </p>
          </button>
          <button
            type="button"
            onClick={() => setTipo('somente_juros')}
            className={`rounded-xl border p-3.5 text-left space-y-1.5 transition-all cursor-pointer ${
              tipo === 'somente_juros'
                ? 'border-[oklch(0.55_0.18_160/0.60)] bg-[oklch(0.55_0.18_160/0.08)] ring-1 ring-[oklch(0.55_0.18_160/0.25)]'
                : 'border-border/60 hover:border-border bg-card'
            }`}
          >
            <p className="text-xs font-semibold leading-none">Somente Juros</p>
            <p className="text-[11px] text-muted-foreground leading-snug">
              Parcela empurrada ao próx. mês
            </p>
            <p className="text-sm font-bold text-[oklch(0.65_0.18_160)] mt-0.5">
              {formatarMoeda(parcelaAtual.juros_parcela)}
            </p>
          </button>
        </div>
      )}

      {/* Recorrente — contexto + toggle de capital */}
      {modalidade === 'recorrente' && (
        <div className="space-y-3">
          <div className="rounded-xl border border-border/50 bg-secondary/30 p-3.5">
            <p className="text-xs font-medium text-fuchsia-400/80 mb-1">Ciclo atual — juros recorrentes</p>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Registra os juros do período e avança o vencimento em 1 mês.
            </p>
          </div>

          {/* Toggle: incluir capital */}
          <div
            className="flex items-center gap-3 cursor-pointer select-none"
            onClick={toggleCapital}
          >
            <div className={`relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors ${
              comCapital ? 'bg-[oklch(0.55_0.18_160)]' : 'bg-secondary border border-border'
            }`}>
              <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform ${
                comCapital ? 'translate-x-4' : 'translate-x-0.5'
              }`} />
            </div>
            <span className="text-sm font-medium">Cliente pagou capital também</span>
          </div>

          {comCapital && (
            <div className="space-y-1.5 pl-1">
              <Label className="text-xs font-medium">
                Valor de capital recebido
                <span className="ml-1.5 text-muted-foreground font-normal">
                  (máx. {formatarMoeda(capitalAtual)})
                </span>
              </Label>
              <Input
                type="number"
                step="0.01"
                min="0.01"
                max={capitalAtual + 0.01}
                placeholder="0,00"
                value={capitalExtra}
                onChange={e => setCapitalExtra(e.target.value)}
                className="h-10 text-base"
                autoFocus
              />
              {capitalExtraNum >= capitalAtual && capitalExtraNum > 0 && (
                <p className="text-xs text-sucesso font-medium">
                  Valor igual ou maior ao capital → contrato será quitado.
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {/* CAMPOS EDITÁVEIS — só Especial */}
      {ehEspecial && (
        <div className="space-y-3 rounded-xl border border-amber-500/30 bg-amber-500/5 p-3.5">
          <p className="text-[11px] font-semibold text-amber-400/80 uppercase tracking-wider">
            Ajustes (modo Especial)
          </p>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-xs font-medium">
                Juros recebidos
                <span className="ml-1.5 text-muted-foreground font-normal">
                  (sugestão: {formatarMoeda(jurosBase)})
                </span>
              </Label>
              <Input
                type="number"
                step="0.01"
                min="0"
                value={jurosRecebidoStr}
                onChange={e => setJurosRecebidoStr(e.target.value)}
                className="h-9 text-sm tabular-nums"
              />
            </div>

            <div className="space-y-1.5">
              <Label className="text-xs font-medium">
                Acréscimo
                <span className="ml-1.5 text-muted-foreground font-normal">
                  (atraso/multa)
                </span>
              </Label>
              <Input
                type="number"
                step="0.01"
                min="0"
                value={acrescimoStr}
                onChange={e => setAcrescimoStr(e.target.value)}
                className="h-9 text-sm tabular-nums"
              />
            </div>
          </div>

          <p className="text-[10px] text-muted-foreground/70 leading-snug">
            ⓘ O acréscimo é um valor manual seu. Ele soma no Total recebido,
            mas <strong>não entra na base de comissão</strong>. A comissão
            permanece sempre sobre os juros do contrato ({formatarMoeda(jurosBase)}).
          </p>
        </div>
      )}

      {/* Preview */}
      <div
        className="rounded-xl border border-[oklch(0.55_0.18_160/0.25)]
          bg-[oklch(0.55_0.18_160/0.06)] p-4 space-y-2.5"
      >
        <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
          O que será registrado
        </p>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Capital recebido</span>
            <span className={`font-medium tabular-nums ${capitalBase === 0 ? 'text-muted-foreground' : ''}`}>
              {formatarMoeda(capitalBase)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Juros recebidos</span>
            <span className="font-medium tabular-nums text-[oklch(0.65_0.18_160)]">
              {formatarMoeda(jurosPreview)}
            </span>
          </div>
          {ehEspecial && acrescimoPreview > 0 && (
            <div className="flex justify-between">
              <span className="text-muted-foreground">Acréscimo</span>
              <span className="font-medium tabular-nums text-amber-400">
                {formatarMoeda(acrescimoPreview)}
              </span>
            </div>
          )}
          <div className="border-t border-border/40 pt-2 flex justify-between font-semibold">
            <span>Total recebido</span>
            <span className="tabular-nums">{formatarMoeda(totalPreview)}</span>
          </div>
        </div>

        {exibirComissao && jurosBase > 0 && (
          <div className="border-t border-border/30 pt-2.5 space-y-1">
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">
                Comissão gerada
                <span className="ml-1 opacity-60">
                  ({((taxaComissaoResponsavel ?? 0) * 100).toFixed(0)}% sobre juros)
                </span>
              </span>
              <span className="text-xs font-semibold tabular-nums text-info">
                {formatarMoeda(comissaoPreview)}
              </span>
            </div>
            <p className="text-[10px] text-muted-foreground/60">
              Base: {formatarMoeda(jurosBase)} · capital e acréscimo não entram no cálculo
            </p>
          </div>
        )}

        {tipo === 'somente_juros' && modalidade === 'parcelado' && parcelaAtual && (
          <p className="text-[11px] text-info border-t border-border/40 pt-2">
            Parcela {parcelaAtual.numero_parcela} será movida para o próximo mês.
          </p>
        )}
      </div>

      {/* Data + Forma */}
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1.5">
          <Label className="text-xs font-medium">Data do recebimento</Label>
          <Input
            type="date"
            value={data}
            onChange={e => setData(e.target.value)}
            className="h-9 text-sm"
            required
          />
        </div>
        <div className="space-y-1.5">
          <Label className="text-xs font-medium">
            Forma de pagamento <span className="text-muted-foreground font-normal">(opcional)</span>
          </Label>
          <Select value={forma} onValueChange={(v) => setForma(v ?? undefined)}>
            <SelectTrigger className="h-9 w-full text-sm">
              <SelectValue placeholder="Selecionar..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="pix">PIX</SelectItem>
              <SelectItem value="dinheiro">Dinheiro</SelectItem>
              <SelectItem value="transferencia">Transferência</SelectItem>
              <SelectItem value="outro">Outro</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Observações */}
      <div className="space-y-1.5">
        <Label className="text-xs font-medium">
          Observações <span className="text-muted-foreground font-normal">(opcional)</span>
        </Label>
        <Textarea
          value={obs}
          onChange={e => setObs(e.target.value)}
          placeholder="Alguma nota sobre este recebimento..."
          rows={2}
          maxLength={500}
          className="text-sm resize-none"
        />
      </div>

      {erro && (
        <Alert variant="destructive" className="py-2">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="text-sm">{erro}</AlertDescription>
        </Alert>
      )}

      <Button
        type="submit"
        disabled={loading}
        className="w-full gap-2 bg-[oklch(0.55_0.18_160)] hover:bg-[oklch(0.50_0.18_160)]
          text-white border-0 shadow-[0_2px_12px_oklch(0.55_0.18_160/0.35)]"
      >
        {loading
          ? <><Loader2 className="w-4 h-4 animate-spin" /> Registrando...</>
          : <><Banknote className="w-4 h-4" /> Confirmar Recebimento</>
        }
      </Button>
    </form>
  )
}

// ── Form Amortização ─────────────────────────────────────────────
function FormAmortizacao({
  contratoId, modalidade, capitalAtual, onSucesso,
}: {
  contratoId: string
  modalidade: 'parcelado' | 'recorrente'
  capitalAtual: number
  onSucesso: () => void
}) {
  const hoje = getHojeBrasil()
  const [valor, setValor]   = useState('')
  const [data, setData]     = useState(hoje)
  const [obs, setObs]       = useState('')
  const [loading, setLoading] = useState(false)
  const [erro, setErro]       = useState('')
  const [sucesso, setSucesso] = useState(false)

  const valorNum         = parseFloat(valor.replace(',', '.')) || 0
  const isTotal          = valorNum > 0 && valorNum >= capitalAtual
  const capitalPosterior = isTotal ? 0 : arredondar(Math.max(0, capitalAtual - valorNum))
  const valorEfetivo     = isTotal ? capitalAtual : valorNum
  const isValido         = valorNum > 0 && valorNum <= capitalAtual + 0.001

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!isValido) { setErro(`Valor deve ser entre R$ 0,01 e ${formatarMoeda(capitalAtual)}.`); return }
    setLoading(true); setErro('')
    try {
      const res  = await fetch('/api/amortizacoes', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          contrato_id:      contratoId,
          valor_amortizado: valorNum,
          data_amortizacao: data,
          observacoes:      obs.trim() || null,
        }),
      })
      const json = await res.json()
      if (!res.ok) { setErro(json.error ?? 'Erro ao registrar.'); toast.error('Erro ao registrar amortização', { description: json.error }); setLoading(false); return }

      toast.success(isTotal ? 'Contrato quitado!' : 'Amortização registrada!', {
        description: `${formatarMoeda(valorEfetivo)} amortizado com sucesso.`,
      })
      setSucesso(true)
      setTimeout(onSucesso, 900)
    } catch {
      setErro('Sem conexão. Tente novamente.')
      toast.error('Sem conexão')
      setLoading(false)
    }
  }

  if (sucesso) {
    return (
      <div className="flex flex-col items-center gap-4 py-10">
        <div
          className="w-16 h-16 rounded-full flex items-center justify-center
            bg-sucesso/10 border-2 border-sucesso/30"
        >
          <CheckCircle2 className="w-8 h-8 text-sucesso" />
        </div>
        <p className="text-lg font-semibold">
          {isTotal ? 'Contrato quitado!' : 'Amortização registrada!'}
        </p>
      </div>
    )
  }

  return (
    <form onSubmit={onSubmit} className="space-y-5 pt-1">
      <div className="rounded-xl border border-border/50 bg-secondary/30 p-3.5">
        <p className="text-xs text-muted-foreground leading-relaxed">
          Amortização reduz o capital em aberto. Juros futuros incidem sobre o novo capital.
          {modalidade === 'parcelado' && (
            <> As parcelas pendentes serão recalculadas automaticamente.</>
          )}
        </p>
      </div>

      <div className="space-y-1.5">
        <Label className="text-xs font-medium">
          Valor a amortizar
          <span className="ml-1.5 text-muted-foreground font-normal">
            (máx. {formatarMoeda(capitalAtual)})
          </span>
        </Label>
        <Input
          type="number"
          step="0.01"
          min="0.01"
          max={capitalAtual + 0.01}
          placeholder="0,00"
          value={valor}
          onChange={e => setValor(e.target.value)}
          className="h-10 text-base"
          required
        />
      </div>

      {valorNum > 0 && (
        <div
          className={`rounded-xl border p-4 space-y-2.5 transition-colors ${
            isTotal
              ? 'border-sucesso/30 bg-sucesso/5'
              : 'border-[oklch(0.55_0.18_160/0.25)] bg-[oklch(0.55_0.18_160/0.06)]'
          }`}
        >
          <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            Impacto da operação
          </p>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Capital atual</span>
              <span className="font-medium tabular-nums">{formatarMoeda(capitalAtual)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Valor amortizado</span>
              <span className="font-medium tabular-nums text-perigo">
                − {formatarMoeda(valorEfetivo)}
              </span>
            </div>
            <div className="border-t border-border/40 pt-2 flex justify-between font-semibold">
              <span>Capital após</span>
              <span className={`tabular-nums ${isTotal ? 'text-sucesso' : ''}`}>
                {isTotal ? 'R$ 0,00 — Quitado' : formatarMoeda(capitalPosterior)}
              </span>
            </div>
          </div>
          <div className="border-t border-border/30 pt-2.5 flex justify-between text-xs text-muted-foreground">
            <span>Tipo do lançamento</span>
            <span className="font-medium">
              Capital: {formatarMoeda(valorEfetivo)} · Juros: R$ 0,00
            </span>
          </div>
          {isTotal && (
            <p className="text-xs text-sucesso font-medium">
              Contrato será marcado como quitado.
              {modalidade === 'parcelado' && ' Parcelas pendentes serão canceladas.'}
            </p>
          )}
          {!isTotal && modalidade === 'parcelado' && (
            <p className="text-xs text-muted-foreground">
              Parcelas pendentes serão recalculadas com o novo capital.
            </p>
          )}
        </div>
      )}

      <div className="space-y-1.5">
        <Label className="text-xs font-medium">Data da amortização</Label>
        <Input
          type="date"
          value={data}
          onChange={e => setData(e.target.value)}
          className="h-9 text-sm"
          required
        />
      </div>
      <div className="space-y-1.5">
        <Label className="text-xs font-medium">
          Observações <span className="text-muted-foreground font-normal">(opcional)</span>
        </Label>
        <Textarea
          value={obs}
          onChange={e => setObs(e.target.value)}
          placeholder="Alguma nota sobre esta amortização..."
          rows={2}
          maxLength={500}
          className="text-sm resize-none"
        />
      </div>

      {erro && (
        <Alert variant="destructive" className="py-2">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="text-sm">{erro}</AlertDescription>
        </Alert>
      )}

      <Button
        type="submit"
        disabled={loading || !isValido}
        className={`w-full gap-2 text-white border-0 ${
          isTotal
            ? 'bg-sucesso hover:bg-sucesso/90 shadow-[0_2px_12px_oklch(0.55_0.18_160/0.20)]'
            : 'bg-[oklch(0.55_0.18_160)] hover:bg-[oklch(0.50_0.18_160)] shadow-[0_2px_12px_oklch(0.55_0.18_160/0.35)]'
        }`}
      >
        {loading
          ? <><Loader2 className="w-4 h-4 animate-spin" /> Registrando...</>
          : isTotal
            ? <><TrendingDown className="w-4 h-4" /> Quitar Contrato</>
            : <><TrendingDown className="w-4 h-4" /> Confirmar Amortização</>
        }
      </Button>
    </form>
  )
}
