import { NextRequest, NextResponse } from 'next/server'
import { createServiceClient } from '@/lib/supabase/server'
import { getAuthUser } from '@/lib/auth'
import {
  calcularComissao,
  calcularJurosRecorrente,
  empurrarCronograma,
  adicionarMeses,
  formatarData,
} from '@/lib/financeiro'
import { isCobrancaSemanal } from '@/lib/contrato-meta'
import type { Parcela } from '@/types'
import { z } from 'zod'

// GET /api/recebimentos
// Filtros: contrato_id, tipo, data_inicio, data_fim, page, limit
export async function GET(req: NextRequest) {
  try {
    const { profile } = await getAuthUser()
    const sc = await createServiceClient()
    const { searchParams } = new URL(req.url)

    const contratoId = searchParams.get('contrato_id')
    const tipo       = searchParams.get('tipo')
    const dataInicio = searchParams.get('data_inicio')
    const dataFim    = searchParams.get('data_fim')
    const page       = Math.max(1, Number(searchParams.get('page')  ?? '1'))
    const limit      = Math.min(100, Math.max(1, Number(searchParams.get('limit') ?? '20')))
    const offset     = (page - 1) * limit

    let contratoIds: string[] | null = null
    if (profile.grupo === 'b' || profile.grupo === 'familia') {
      const { data: contratos } = await sc
        .from('contratos')
        .select('id')
        .eq('responsavel_id', profile.id)
      contratoIds = (contratos ?? []).map((c: any) => c.id)
      if (contratoIds.length === 0) {
        return NextResponse.json({ data: [], meta: { total: 0, page, limit, pages: 0 } })
      }
    }

    let query = sc
      .from('recebimentos')
      .select(`
        id, contrato_id, parcela_id, tipo,
        capital_recebido, juros_recebido, valor_acrescimo,
        data_recebimento, forma_pagamento, observacoes, criado_em,
        comissao:comissoes!recebimento_id(valor_comissao, status),
        contrato:contratos!contrato_id(id, modalidade, cliente:clientes!cliente_id(id, nome)),
        registrado_por_profile:profiles!registrado_por(nome)
      `, { count: 'exact' })
      .order('data_recebimento', { ascending: false })
      .range(offset, offset + limit - 1)

    if (contratoIds) query = query.in('contrato_id', contratoIds)
    if (contratoId)  query = query.eq('contrato_id', contratoId)
    if (tipo)        query = query.eq('tipo', tipo)
    if (dataInicio)  query = query.gte('data_recebimento', dataInicio)
    if (dataFim)     query = query.lte('data_recebimento', dataFim)

    const { data, error, count } = await query
    if (error) throw error

    return NextResponse.json({
      data,
      meta: { total: count ?? 0, page, limit, pages: Math.ceil((count ?? 0) / limit) },
    })
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 })
  }
}

const schema = z.object({
  contrato_id:      z.string().uuid(),
  tipo:             z.enum(['parcela_completa', 'somente_juros']),
  parcela_id:       z.string().uuid().optional(),
  data_recebimento: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Data inválida (YYYY-MM-DD)'),
  forma_pagamento:  z.enum(['pix', 'dinheiro', 'transferencia', 'outro']).optional().nullable(),
  observacoes:      z.string().max(500).optional().nullable(),
  // NOVOS — só processados quando profile.grupo === 'especial'
  juros_recebido_override: z.number().min(0).optional(),
  valor_acrescimo:         z.number().min(0).optional(),
})

// POST /api/recebimentos
export async function POST(req: NextRequest) {
  try {
    const { profile } = await getAuthUser()
    if (profile.grupo !== 'especial' && profile.grupo !== 'familia') {
      return NextResponse.json({ error: 'Sem permissão.' }, { status: 403 })
    }

    const body = await req.json()
    const parsed = schema.safeParse(body)
    if (!parsed.success) {
      return NextResponse.json({ error: parsed.error.issues[0].message }, { status: 422 })
    }
    const d = parsed.data

    // PROTEÇÃO: campos juros_recebido_override e valor_acrescimo são exclusivos do Especial.
    // Se Familia tentar enviar, ignora silenciosamente.
    if (profile.grupo !== 'especial') {
      d.juros_recebido_override = undefined
      d.valor_acrescimo = undefined
    }

    const sc = await createServiceClient()

    const { data: contrato, error: contratoErr } = await sc
      .from('contratos')
      .select(`
        id, modalidade, capital_atual, taxa_juros_mensal,
        parcelas_pagas, parcelas_empurradas, num_parcelas, status,
        proximo_vencimento, responsavel_id, gera_comissao, observacoes,
        responsavel:profiles!responsavel_id(id, grupo, taxa_comissao)
      `)
      .eq('id', d.contrato_id)
      .maybeSingle()

    if (contratoErr || !contrato) {
      return NextResponse.json({ error: 'Contrato não encontrado.' }, { status: 404 })
    }

    if (profile.grupo === 'familia' && contrato.responsavel_id !== profile.id) {
      return NextResponse.json({ error: 'Sem permissão.' }, { status: 403 })
    }

    if (contrato.status === 'quitado') {
      return NextResponse.json({ error: 'Contrato já está quitado.' }, { status: 422 })
    }

    const responsavel  = contrato.responsavel as any
    const geraComissao =
      contrato.gera_comissao !== false && (
        responsavel?.grupo === 'familia' ||
        (responsavel?.grupo === 'b' &&
         typeof responsavel?.taxa_comissao === 'number' &&
         responsavel.taxa_comissao > 0)
      )

    if (d.tipo === 'parcela_completa') {
      return await handleParcelaCompleta({ d, contrato, responsavel, geraComissao, profile, sc })
    }
    return await handleSomenteJuros({ d, contrato, responsavel, geraComissao, profile, sc })
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 })
  }
}

// ────────────────────────────────────────────────────────────────
// HANDLER: parcela_completa
// ────────────────────────────────────────────────────────────────
async function handleParcelaCompleta({ d, contrato, responsavel, geraComissao, profile, sc }: any) {
  if (contrato.modalidade !== 'parcelado') {
    return NextResponse.json(
      { error: 'parcela_completa é válido apenas para contratos parcelados.' },
      { status: 422 },
    )
  }
  if (!d.parcela_id) {
    return NextResponse.json({ error: 'parcela_id é obrigatório para parcela_completa.' }, { status: 422 })
  }

  const { data: parcela, error: parcelaErr } = await sc
    .from('parcelas')
    .select('id, contrato_id, numero_parcela, capital_parcela, juros_parcela, status')
    .eq('id', d.parcela_id)
    .maybeSingle()

  if (parcelaErr || !parcela) {
    return NextResponse.json({ error: 'Parcela não encontrada.' }, { status: 404 })
  }
  if (parcela.contrato_id !== d.contrato_id) {
    return NextResponse.json({ error: 'Parcela não pertence a este contrato.' }, { status: 422 })
  }
  if (parcela.status !== 'pendente' && parcela.status !== 'empurrado') {
    return NextResponse.json({ error: 'Parcela já foi paga ou cancelada.' }, { status: 409 })
  }

  // Valor BASE — sempre o do contrato (usado pra comissão, NÃO MUDA)
  const juros_calculado  = parcela.juros_parcela
  const capital_recebido = parcela.capital_parcela

  // Valor REGISTRADO — pode ser editado pelo Especial
  const juros_recebido = (typeof d.juros_recebido_override === 'number')
    ? d.juros_recebido_override
    : juros_calculado
  const valor_acrescimo = d.valor_acrescimo ?? 0

  const { data: atomicRows, error: atomicErr } = await sc
    .from('parcelas')
    .update({ status: 'pago', atualizado_em: new Date().toISOString() })
    .eq('id', d.parcela_id)
    .in('status', ['pendente', 'empurrado'])
    .select('id')

  if (atomicErr) throw atomicErr
  if (!atomicRows || atomicRows.length === 0) {
    return NextResponse.json(
      { error: 'Parcela já foi processada por outro usuário.' },
      { status: 409 },
    )
  }

  const { data: recebimento, error: recErr } = await sc
    .from('recebimentos')
    .insert({
      contrato_id:      d.contrato_id,
      parcela_id:       d.parcela_id,
      registrado_por:   profile.id,
      tipo:             'parcela_completa',
      capital_recebido,
      juros_recebido,
      valor_acrescimo,
      data_recebimento: d.data_recebimento,
      forma_pagamento:  d.forma_pagamento ?? null,
      observacoes:      d.observacoes ?? null,
    })
    .select()
    .single()

  if (recErr || !recebimento) throw recErr ?? new Error('Falha ao inserir recebimento.')

  const { data: restantes } = await sc
    .from('parcelas')
    .select('id, data_vencimento')
    .eq('contrato_id', d.contrato_id)
    .in('status', ['pendente', 'empurrado'])
    .order('numero_parcela')

  const novoCapital       = Math.max(0, contrato.capital_atual - capital_recebido)
  const proximoVencimento = restantes?.[0]?.data_vencimento ?? null
  const quitado           = !restantes || restantes.length === 0

  const contrUpdates: Record<string, unknown> = {
    capital_atual:      novoCapital,
    parcelas_pagas:     contrato.parcelas_pagas + 1,
    proximo_vencimento: proximoVencimento,
    status:             'ativo',
    atualizado_em:      new Date().toISOString(),
  }
  if (quitado) {
    contrUpdates.status        = 'quitado'
    contrUpdates.data_quitacao = d.data_recebimento
  }

  const { error: contrErr } = await sc
    .from('contratos')
    .update(contrUpdates)
    .eq('id', d.contrato_id)
  if (contrErr) throw contrErr

  if (quitado) {
    const { count: outrosAtivos } = await sc
      .from('contratos')
      .select('id', { count: 'exact', head: true })
      .eq('cliente_id', contrato.cliente_id ?? (contrato as any).cliente_id)
      .in('status', ['ativo', 'inadimplente'])
      .neq('id', d.contrato_id)
    if ((outrosAtivos ?? 0) === 0) {
      const { data: ctr } = await sc
        .from('contratos')
        .select('cliente_id')
        .eq('id', d.contrato_id)
        .single()
      if (ctr?.cliente_id) {
        await sc.from('clientes')
          .update({ ativo: false, atualizado_em: new Date().toISOString() })
          .eq('id', ctr.cliente_id)
      }
    }
  }

  // ⚠️ COMISSÃO — SEMPRE sobre juros_calculado (juros do contrato).
  // NUNCA sobre o juros editado nem sobre o acréscimo.
  if (geraComissao && juros_calculado > 0) {
    const valorComissao = responsavel.grupo === 'familia'
      ? juros_calculado
      : calcularComissao(juros_calculado, responsavel.taxa_comissao)
    if (valorComissao > 0) {
      await sc.from('comissoes').insert({
        colaborador_id: responsavel.id,
        recebimento_id: recebimento.id,
        contrato_id:    d.contrato_id,
        juros_base:     juros_calculado,
        percentual:     responsavel.grupo === 'familia' ? 1 : responsavel.taxa_comissao,
        valor_comissao: valorComissao,
        status:         'pendente',
      })
    }
  }

  await sc.from('historico_eventos').insert([
    {
      entidade:     'recebimento',
      entidade_id:  recebimento.id,
      evento:       'criacao',
      usuario_id:   profile.id,
      dados_depois: recebimento,
    },
    {
      entidade:     'parcela',
      entidade_id:  d.parcela_id,
      evento:       'pagamento',
      usuario_id:   profile.id,
      dados_depois: { status: 'pago', recebimento_id: recebimento.id },
    },
  ])

  return NextResponse.json({ data: recebimento }, { status: 201 })
}

// ────────────────────────────────────────────────────────────────
// HANDLER: somente_juros
// ────────────────────────────────────────────────────────────────
async function handleSomenteJuros({ d, contrato, responsavel, geraComissao, profile, sc }: any) {
  if (contrato.modalidade === 'parcelado') {
    if (!d.parcela_id) {
      return NextResponse.json(
        { error: 'parcela_id é obrigatório para somente_juros em contrato parcelado.' },
        { status: 422 },
      )
    }

    const { data: parcela, error: parcelaErr } = await sc
      .from('parcelas')
      .select('id, contrato_id, numero_parcela, capital_parcela, juros_parcela, status, data_vencimento')
      .eq('id', d.parcela_id)
      .maybeSingle()

    if (parcelaErr || !parcela) {
      return NextResponse.json({ error: 'Parcela não encontrada.' }, { status: 404 })
    }
    if (parcela.contrato_id !== d.contrato_id) {
      return NextResponse.json({ error: 'Parcela não pertence a este contrato.' }, { status: 422 })
    }
    if (parcela.status !== 'pendente') {
      return NextResponse.json(
        { error: 'somente_juros requer parcela com status pendente.' },
        { status: 409 },
      )
    }

    const capital_recebido  = 0
    const juros_calculado   = parcela.juros_parcela
    const juros_recebido    = (typeof d.juros_recebido_override === 'number')
      ? d.juros_recebido_override
      : juros_calculado
    const valor_acrescimo   = d.valor_acrescimo ?? 0

    const { data: atomicRows, error: atomicErr } = await sc
      .from('parcelas')
      .update({
        status:         'empurrado',
        empurrado_de:   parcela.data_vencimento,
        atualizado_em:  new Date().toISOString(),
      })
      .eq('id', d.parcela_id)
      .eq('status', 'pendente')
      .select('id')

    if (atomicErr) throw atomicErr
    if (!atomicRows || atomicRows.length === 0) {
      return NextResponse.json(
        { error: 'Parcela já foi processada por outro usuário.' },
        { status: 409 },
      )
    }

    const { data: todasPendentes, error: listErr } = await sc
      .from('parcelas')
      .select('id, numero_parcela, capital_parcela, juros_parcela, data_vencimento, data_original, status, empurrado_de, contrato_id, criado_em, atualizado_em')
      .eq('contrato_id', d.contrato_id)
      .in('status', ['pendente', 'empurrado'])
      .order('numero_parcela')
    if (listErr) throw listErr

    const idx = (todasPendentes ?? []).findIndex((p: any) => p.id === d.parcela_id)
    const indice = idx >= 0 ? idx : 0

    const novasDatas = empurrarCronograma(
      (todasPendentes ?? []) as Parcela[],
      indice,
      isCobrancaSemanal(contrato.observacoes) ? 'semanal' : 'mensal',
    )

    await Promise.all(
      novasDatas.map(({ id, data_vencimento }) =>
        sc.from('parcelas')
          .update({ data_vencimento, atualizado_em: new Date().toISOString() })
          .eq('id', id),
      ),
    )

    const { data: recebimento, error: recErr } = await sc
      .from('recebimentos')
      .insert({
        contrato_id:      d.contrato_id,
        parcela_id:       d.parcela_id,
        registrado_por:   profile.id,
        tipo:             'somente_juros',
        capital_recebido,
        juros_recebido,
        valor_acrescimo,
        data_recebimento: d.data_recebimento,
        forma_pagamento:  d.forma_pagamento ?? null,
        observacoes:      d.observacoes ?? null,
      })
      .select()
      .single()

    if (recErr || !recebimento) throw recErr ?? new Error('Falha ao inserir recebimento.')

    const novoProximo = todasPendentes?.[0]
      ? novasDatas.find(n => n.id === todasPendentes![0].id)?.data_vencimento
        ?? todasPendentes[0].data_vencimento
      : null

    const { error: contrErr } = await sc
      .from('contratos')
      .update({
        parcelas_empurradas: contrato.parcelas_empurradas + 1,
        proximo_vencimento:  novoProximo,
        status:              'ativo',
        atualizado_em:       new Date().toISOString(),
      })
      .eq('id', d.contrato_id)
    if (contrErr) throw contrErr

    // ⚠️ COMISSÃO — SEMPRE sobre juros_calculado (juros do contrato).
    if (geraComissao && juros_calculado > 0) {
      const valorComissao = responsavel.grupo === 'familia'
        ? juros_calculado
        : calcularComissao(juros_calculado, responsavel.taxa_comissao)
      if (valorComissao > 0) {
        await sc.from('comissoes').insert({
          colaborador_id: responsavel.id,
          recebimento_id: recebimento.id,
          contrato_id:    d.contrato_id,
          juros_base:     juros_calculado,
          percentual:     responsavel.grupo === 'familia' ? 1 : responsavel.taxa_comissao,
          valor_comissao: valorComissao,
          status:         'pendente',
        })
      }
    }

    await sc.from('historico_eventos').insert([
      {
        entidade:     'recebimento',
        entidade_id:  recebimento.id,
        evento:       'criacao',
        usuario_id:   profile.id,
        dados_depois: recebimento,
      },
      {
        entidade:     'parcela',
        entidade_id:  d.parcela_id,
        evento:       'empurramento',
        usuario_id:   profile.id,
        dados_depois: { status: 'empurrado', recebimento_id: recebimento.id },
      },
    ])

    return NextResponse.json({ data: recebimento }, { status: 201 })
  }

  if (contrato.modalidade === 'recorrente') {
    if (!contrato.proximo_vencimento) {
      return NextResponse.json({ error: 'Contrato sem proximo_vencimento definido.' }, { status: 422 })
    }

    const capital_recebido = 0
    const juros_calculado  = calcularJurosRecorrente(
      contrato.capital_atual,
      contrato.taxa_juros_mensal,
    )
    const juros_recebido = (typeof d.juros_recebido_override === 'number')
      ? d.juros_recebido_override
      : juros_calculado
    const valor_acrescimo = d.valor_acrescimo ?? 0

    const { data: recebimento, error: recErr } = await sc
      .from('recebimentos')
      .insert({
        contrato_id:      d.contrato_id,
        parcela_id:       null,
        registrado_por:   profile.id,
        tipo:             'somente_juros',
        capital_recebido,
        juros_recebido,
        valor_acrescimo,
        data_recebimento: d.data_recebimento,
        forma_pagamento:  d.forma_pagamento ?? null,
        observacoes:      d.observacoes ?? null,
      })
      .select()
      .single()

    if (recErr || !recebimento) throw recErr ?? new Error('Falha ao inserir recebimento.')

    const novoProximo = formatarData(
      adicionarMeses(new Date(contrato.proximo_vencimento + 'T12:00:00'), 1),
    )

    const { error: contrErr } = await sc
      .from('contratos')
      .update({
        parcelas_pagas:     contrato.parcelas_pagas + 1,
        proximo_vencimento: novoProximo,
        status:             'ativo',
        atualizado_em:      new Date().toISOString(),
      })
      .eq('id', d.contrato_id)
    if (contrErr) throw contrErr

    // ⚠️ COMISSÃO — SEMPRE sobre juros_calculado (juros do contrato).
    if (geraComissao && juros_calculado > 0) {
      const valorComissao = responsavel.grupo === 'familia'
        ? juros_calculado
        : calcularComissao(juros_calculado, responsavel.taxa_comissao)
      if (valorComissao > 0) {
        await sc.from('comissoes').insert({
          colaborador_id: responsavel.id,
          recebimento_id: recebimento.id,
          contrato_id:    d.contrato_id,
          juros_base:     juros_calculado,
          percentual:     responsavel.grupo === 'familia' ? 1 : responsavel.taxa_comissao,
          valor_comissao: valorComissao,
          status:         'pendente',
        })
      }
    }

    await sc.from('historico_eventos').insert({
      entidade:     'recebimento',
      entidade_id:  recebimento.id,
      evento:       'criacao',
      usuario_id:   profile.id,
      dados_depois: recebimento,
    })

    return NextResponse.json({ data: recebimento }, { status: 201 })
  }

  return NextResponse.json({ error: 'Modalidade de contrato não suportada.' }, { status: 422 })
}
