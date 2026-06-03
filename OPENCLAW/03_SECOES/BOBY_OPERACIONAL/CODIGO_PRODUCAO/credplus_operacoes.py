#!/usr/bin/env python3
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo('America/Sao_Paulo')
ENV_PATHS = [
    '/data/.openclaw/workspace/credplus.env',
    '/docker/openclaw-189p/data/.openclaw/workspace/credplus.env',
]
PENDING_PATHS = [
    '/data/.openclaw/workspace/pending_operacoes.json',
    '/docker/openclaw-189p/data/.openclaw/workspace/pending_operacoes.json',
]


def resolve_env_path():
    for p in ENV_PATHS:
        if os.path.exists(p):
            return p
    return ENV_PATHS[-1]


def resolve_pending_path():
    for p in PENDING_PATHS:
        if os.path.exists(os.path.dirname(p)):
            return p
    return PENDING_PATHS[-1]


def load_env():
    path = resolve_env_path()
    if not os.path.exists(path):
        raise RuntimeError('credplus.env ausente')
    env = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    url = env.get('NEXT_PUBLIC_SUPABASE_URL') or env.get('SUPABASE_URL')
    key = env.get('SUPABASE_SERVICE_ROLE_KEY')
    if not url or not key:
        raise RuntimeError('credplus.env incompleto')
    return url.rstrip('/'), key


def request(method, table, params=None, body=None, prefer=None):
    base, key = load_env()
    qs = urllib.parse.urlencode(params or {}, doseq=True)
    url = f"{base}/rest/v1/{table}" + (f"?{qs}" if qs else '')
    req = urllib.request.Request(url, method=method.upper())
    req.add_header('apikey', key)
    req.add_header('Authorization', f'Bearer {key}')
    req.add_header('Accept', 'application/json')
    if prefer:
        req.add_header('Prefer', prefer)
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, data=data, timeout=30) as res:
        raw = res.read().decode('utf-8').strip()
        if not raw:
            return None
        return json.loads(raw)


def sb_get(table, params=None):
    return request('GET', table, params=params)


def sb_insert(table, body):
    return request('POST', table, body=body, prefer='return=representation')


def sb_patch(table, filters, body):
    return request('PATCH', table, params=filters, body=body, prefer='return=representation')


def load_pending():
    path = resolve_pending_path()
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_pending(data):
    with open(resolve_pending_path(), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def br_today():
    return datetime.now(TZ).date().isoformat()


def br_now_iso():
    return datetime.now(TZ).replace(microsecond=0).isoformat()


def br_money(v):
    return f'R$ {float(v):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def normalize(txt):
    return ''.join(ch for ch in (txt or '').strip().upper() if ch.isalnum() or ch.isspace())


def parse_iso_local(iso_date):
    y, m, d = [int(x) for x in iso_date.split('-')]
    return datetime(y, m, d, 12, 0, 0)


def normalize_date_input(value):
    txt = (value or '').strip()
    if not txt:
        return None
    txt = txt.replace('/', '-')
    parts = txt.split('-')
    if len(parts) != 3:
        return None
    if len(parts[0]) == 4:
        y, m, d = parts
    else:
        d, m, y = parts
    try:
        return f'{int(y):04d}-{int(m):02d}-{int(d):02d}'
    except Exception:
        return None


def add_months(iso_date, months=1):
    dt = parse_iso_local(iso_date)
    year = dt.year + ((dt.month - 1 + months) // 12)
    month = ((dt.month - 1 + months) % 12) + 1
    day = min(dt.day, [31,29 if year%4==0 and (year%100!=0 or year%400==0) else 28,31,30,31,30,31,31,30,31,30,31][month-1])
    return datetime(year, month, day, 12, 0, 0).date().isoformat()


def add_weeks(iso_date, weeks=1):
    dt = parse_iso_local(iso_date)
    return (dt.date() + timedelta(days=weeks * 7)).isoformat()


def round2(v):
    return round(float(v or 0), 2)


def calcular_juros_recorrente(capital, taxa):
    return round2(float(capital or 0) * float(taxa or 0))



def pct_label(taxa_decimal):
    return (f"{float(taxa_decimal or 0) * 100:.2f}".rstrip('0').rstrip('.') + '%')


def br_date(iso_date):
    if not iso_date:
        return '-'
    try:
        y, m, d = iso_date[:10].split('-')
        return f'{d}/{m}/{y}'
    except Exception:
        return str(iso_date)


def gera_comissao_para(resp):
    grupo = normalize(resp.get('grupo') or '')
    return 'GRUPO B' in grupo or 'GRUPOB' in grupo or 'COLABORADOR' in grupo


def montar_grade_parcelas(capital, taxa_decimal, parcelas, primeiro_vencimento, cobranca='mensal'):
    total = int(parcelas or 0)
    capital = round2(capital)
    taxa_decimal = float(taxa_decimal or 0)
    if total <= 0:
        return []
    capital_por = round2(capital / total)
    juros_total = round2(capital * taxa_decimal * total)
    juros_por = round2(juros_total / total)
    soma_cap = round2(capital_por * (total - 1))
    soma_j = round2(juros_por * (total - 1))
    cap_last = round2(capital - soma_cap)
    jur_last = round2(juros_total - soma_j)
    rows = []
    for i in range(total):
        venc = primeiro_vencimento if i == 0 else (add_weeks(primeiro_vencimento, i) if cobranca == 'semanal' else add_months(primeiro_vencimento, i))
        cp = cap_last if i == total - 1 else capital_por
        jp = jur_last if i == total - 1 else juros_por
        rows.append({
            'numero_parcela': i + 1,
            'capital_parcela': cp,
            'juros_parcela': jp,
            'total': round2(cp + jp),
            'data_vencimento': venc,
        })
    return rows


def format_novo_contrato_preview(cliente_nome, responsavel_nome, payload, parcelas_preview=None):
    capital = round2(payload.get('capital_inicial') or 0)
    taxa = float(payload.get('taxa_juros_mensal') or 0)
    modalidade = payload.get('modalidade')
    data_contrato = payload.get('data_contrato') or br_today()
    primeiro = payload.get('primeiro_vencimento')
    linhas = [
        'RECIBO DE PRE-CADASTRO',
        'CREDPLUS SOLUCOES FINANCEIRAS',
        '--------------------------------',
        f'Cliente: {cliente_nome}',
        f'Carteira: {responsavel_nome}',
        f'Capital: {br_money(capital)}',
        f'Data do contrato: {br_date(data_contrato)}',
        f'Primeiro vencimento: {br_date(primeiro)}',
        f'Taxa: {pct_label(taxa)} ao mes',
    ]
    if modalidade == 'parcelado':
        cobranca = 'semanal' if is_cobranca_semanal(payload.get('observacoes')) else 'mensal'
        linhas += [
            f'Modalidade: Parcelado {cobranca}',
            f'Parcelas: {int(payload.get("num_parcelas") or 0)}x',
            '--------------------------------',
            'GRADE DE PARCELAS',
        ]
        rows = parcelas_preview or montar_grade_parcelas(capital, taxa, payload.get('num_parcelas'), primeiro, cobranca)
        for row in rows:
            linhas.append(
                f"{row['numero_parcela']}/{len(rows)} - {br_date(row['data_vencimento'])} - "
                f"Capital {br_money(row['capital_parcela'])} + Juros {br_money(row['juros_parcela'])} = {br_money(row['total'])}"
            )
        juros_total = round2(sum(r['juros_parcela'] for r in rows))
        total_receber = round2(sum(r['total'] for r in rows))
        linhas += [
            '--------------------------------',
            f'Capital total: {br_money(capital)}',
            f'Juros total: {br_money(juros_total)}',
            f'Total a receber: {br_money(total_receber)}',
            '--------------------------------',
            'Confirma criar esse emprestimo?',
            'Responda SIM ou NAO.',
        ]
        return '\n'.join(linhas)
    juros_ciclo = calcular_juros_recorrente(capital, taxa)
    linhas += [
        'Modalidade: Juros recorrente',
        '--------------------------------',
        'COBRANCA DO CICLO',
        f'{br_date(primeiro)} - Juros {br_money(juros_ciclo)}',
        f'Capital permanece: {br_money(capital)}',
        '--------------------------------',
        'Confirma criar esse emprestimo?',
        'Responda SIM ou NAO.',
    ]
    return '\n'.join(linhas)


def recalcular_parcelas_apos_amortizacao(parcelas, novo_capital, taxa_mensal):
    qtd = len(parcelas)
    if qtd == 0:
        return []
    novo_capital_por_parcela = round2(novo_capital / qtd)
    novo_juros_por_parcela = round2(novo_capital * taxa_mensal)
    soma_capital = novo_capital_por_parcela * (qtd - 1)
    soma_juros = novo_juros_por_parcela * (qtd - 1)
    total_juros_contrato = round2(novo_capital * taxa_mensal * qtd)
    out = []
    for i, p in enumerate(parcelas):
        out.append({
            'id': p['id'],
            'capital_parcela': round2(novo_capital - soma_capital) if i == qtd - 1 else novo_capital_por_parcela,
            'juros_parcela': round2(total_juros_contrato - soma_juros) if i == qtd - 1 else novo_juros_por_parcela,
        })
    return out


def find_profile_by_name(nome):
    rows = sb_get('profiles', {'select': 'id,nome,grupo,ativo,taxa_comissao', 'ativo': 'eq.true', 'order': 'nome.asc'}) or []
    alvo = normalize(nome)
    exact = [r for r in rows if normalize(r.get('nome')) == alvo]
    if exact:
        return exact[0]
    contains = [r for r in rows if alvo in normalize(r.get('nome'))]
    return contains[0] if len(contains) == 1 else None


def find_llellis_profile():
    p = find_profile_by_name('LELLISFLAVIO')
    if not p:
        raise RuntimeError('perfil LELLISFLAVIO não encontrado')
    return p


def find_cliente(nome):
    rows = sb_get('clientes', {'select': 'id,nome,telefone,ativo', 'order': 'nome.asc'}) or []
    alvo = normalize(nome)
    exact = [r for r in rows if normalize(r.get('nome')) == alvo]
    if exact:
        return exact
    return [r for r in rows if alvo in normalize(r.get('nome'))]


def get_active_contracts(cliente_id, responsavel_id):
    return sb_get('contratos', {
        'select': 'id,modalidade,capital_inicial,capital_atual,taxa_juros_mensal,proximo_vencimento,primeiro_vencimento,status,responsavel_id,parcelas_pagas,parcelas_empurradas,num_parcelas,gera_comissao,cliente_id,data_quitacao,criado_em,observacoes',
        'cliente_id': f'eq.{cliente_id}',
        'responsavel_id': f'eq.{responsavel_id}',
        'status': 'in.(ativo,inadimplente)',
        'order': 'criado_em.desc',
        'limit': '10',
    }) or []


def contract_due_date(contrato):
    return contrato.get('proximo_vencimento') or contrato.get('primeiro_vencimento')


def is_cobranca_semanal(observacoes):
    txt = str(observacoes or '')
    return '"cobranca":"semanal"' in txt or '"cobranca": "semanal"' in txt

def classify_priority(contrato):
    due = contract_due_date(contrato)
    if not due:
        return (4, 'CONTRATO')
    try:
        d = datetime.fromisoformat(due).date()
    except Exception:
        return (4, 'CONTRATO')
    delta = (datetime.now(TZ).date() - d).days
    if delta > 5:
        return (0, 'CRITICO')
    if delta >= 1:
        return (1, 'VENCIDO')
    if delta == 0:
        return (2, 'HOJE')
    if delta == -1:
        return (3, 'AMANHA')
    return (4, 'CONTRATO')


def pick_priority_contract(contratos):
    if not contratos:
        return None, 'CONTRATO'
    ranked = []
    for c in contratos:
        rank, label = classify_priority(c)
        due = contract_due_date(c) or '9999-12-31'
        ranked.append((rank, due, c, label))
    ranked.sort(key=lambda x: (x[0], x[1]))
    _, _, chosen, label = ranked[0]
    return chosen, label


def format_contract_options(cliente_nome, responsavel_nome, contratos):
    lines = [f'Contratos de {cliente_nome}, {responsavel_nome}:']
    for idx, c in enumerate(contratos, start=1):
        venc = c.get('vencimento') or contract_due_date(c) or 'sem vencimento'
        juros = calcular_juros_recorrente(c.get('capital_atual'), c.get('taxa_juros_mensal')) if c.get('modalidade') == 'recorrente' else 0
        lines.append(f'{idx}. Juros {br_money(juros)} · vencimento {venc}')
    lines.append('Responda só com a data. Ex: vencimento 2026-05-16.')
    return '\n'.join(lines)


def format_parcela_juros_options(cliente_nome, responsavel_nome, parcelas):
    total_parcelas = max([int(p.get('numero_parcela') or 0) for p in parcelas] or [0])
    faltam = len(parcelas)
    lines = [f'{cliente_nome} · {responsavel_nome}', f'Parcelas pendentes: {faltam}']
    for idx, p in enumerate(parcelas, start=1):
        venc = p.get('data_vencimento') or 'sem vencimento'
        try:
            y, m, d = venc.split('-')
            venc_fmt = f'{d}/{m}/{y[2:]}'
        except Exception:
            venc_fmt = venc
        juros = round2(p.get('juros_parcela') or 0)
        capital = round2(p.get('capital_parcela') or 0)
        total = round2(juros + capital)
        num_raw = int(p.get('numero_parcela') or idx)
        num = str(num_raw).zfill(2)
        total_txt = f'/{total_parcelas}' if total_parcelas else ''
        lines.append(f'{idx}. Parcela do mês {num}{total_txt} · venc. {venc_fmt} · juros {br_money(juros)} · parcela {br_money(total)}')
    lines.append('Responda com o número da parcela ou o vencimento.')
    return '\n'.join(lines)

def format_escolha_pagamento_parcela(op):
    numero = op.get('numero_parcela')
    total_parcelas = int(op.get('total_parcelas') or numero or 0)
    pendentes = int(op.get('parcelas_pendentes') or 1)
    venc = op.get('vencimento') or 'sem vencimento'
    try:
        y, m, d = venc.split('-')
        venc_fmt = f'{d}/{m}/{y}'
    except Exception:
        venc_fmt = venc
    juros = round2(op.get('juros_parcela') or 0)
    total = round2(op.get('total') or 0)
    return (f"Encontrei {op['cliente_nome']} na carteira de {op['responsavel_nome']}:\n\n"
            f"Parcela do mês: {numero}/{total_parcelas}\n"
            f"Vencimento: {venc_fmt}\n"
            f"Faltam: {pendentes} parcela(s) pendente(s), contando esta.\n\n"
            f"1 - Pagar só os juros: {br_money(juros)}\n"
            f"2 - Pagar parcela completa: {br_money(total)}\n\n"
            f"Responda 1 ou 2.")

def save_parcela_juros_pending(actor, cliente, resp, contrato, parcelas):
    p = parcelas[0]
    cp = round2(p.get('capital_parcela') or 0)
    jp = round2(p.get('juros_parcela') or 0)
    total = round2(cp + jp)
    op = {
        'tipo': 'escolher_pagamento_parcela',
        'cliente_id': cliente['id'],
        'cliente_nome': cliente['nome'],
        'responsavel_id': resp['id'],
        'responsavel_nome': resp['nome'],
        'contrato_id': contrato['id'],
        'parcela_id': p['id'],
        'numero_parcela': p.get('numero_parcela'),
        'total_parcelas': int(contrato.get('num_parcelas') or p.get('numero_parcela') or 0),
        'parcelas_pendentes': len(parcelas),
        'capital_parcela': cp,
        'juros_parcela': jp,
        'total': total,
        'vencimento': p.get('data_vencimento'),
        'prepared_at': br_now_iso(),
    }
    pending = load_pending()
    pending[actor] = op
    save_pending(pending)
    return format_escolha_pagamento_parcela(op)

def save_selection_pending(actor, acao, cliente, resp, contratos, extra=None):
    pending = load_pending()
    pending[actor] = {
        'tipo': 'selecionar_contrato',
        'acao': acao,
        'cliente_id': cliente['id'],
        'cliente_nome': cliente['nome'],
        'responsavel_id': resp['id'],
        'responsavel_nome': resp['nome'],
        'contratos': [
            {
                'id': c['id'],
                'vencimento': contract_due_date(c),
                'modalidade': c.get('modalidade'),
                'capital_atual': round2(c.get('capital_atual') or 0),
                'taxa_juros_mensal': float(c.get('taxa_juros_mensal') or 0),
            }
            for c in contratos
        ],
        'extra': extra or {},
        'prepared_at': br_now_iso(),
    }
    save_pending(pending)
    return format_contract_options(cliente['nome'], resp['nome'], contratos)


def get_active_contract(cliente_id, responsavel_id):
    rows = get_active_contracts(cliente_id, responsavel_id)
    return rows[0] if rows else None


def get_pending_parcelas(contrato_id):
    return sb_get('parcelas', {
        'select': 'id,contrato_id,numero_parcela,capital_parcela,juros_parcela,data_vencimento,data_original,status,empurrado_de',
        'contrato_id': f'eq.{contrato_id}',
        'status': 'in.(pendente,empurrado)',
        'order': 'numero_parcela.asc',
    }) or []


def find_clientes_na_carteira(responsavel_id, cliente_nome):
    alvo = normalize(cliente_nome)
    contratos = sb_get('contratos', {
        'select': 'cliente_id,status,responsavel_id',
        'responsavel_id': f'eq.{responsavel_id}',
        'status': 'in.(ativo,inadimplente)',
        'limit': '200',
    }) or []
    ids = sorted({c.get('cliente_id') for c in contratos if c.get('cliente_id')})
    if not ids:
        return []
    id_filter = 'in.(' + ','.join(ids) + ')'
    rows = sb_get('clientes', {
        'select': 'id,nome,telefone,ativo',
        'id': id_filter,
        'order': 'nome.asc',
        'limit': '200',
    }) or []
    exact = [r for r in rows if normalize(r.get('nome')) == alvo]
    if exact:
        return exact
    return [r for r in rows if alvo in normalize(r.get('nome'))]


def resolve_cliente_responsavel(cliente_nome, responsavel_nome, vencimento=None):
    resp = find_profile_by_name(responsavel_nome)
    if not resp:
        return None, None, None, f'Responsável não encontrado: {responsavel_nome}.'
    clientes = find_clientes_na_carteira(resp['id'], cliente_nome)
    if not clientes:
        return None, None, None, f'Cliente não encontrado na carteira de {resp.get("nome")}: {cliente_nome}.'
    if len(clientes) > 1:
        nomes = ', '.join(c.get('nome', '?') for c in clientes[:5])
        return None, None, None, f'Cliente ambíguo na carteira de {resp.get("nome")}: {nomes}.'
    cliente = clientes[0]
    contratos = get_active_contracts(cliente['id'], resp['id'])
    if not contratos:
        return None, None, None, f"{cliente.get('nome')} não tem contrato ativo ou inadimplente na carteira de {resp.get('nome')}."
    due_filter = normalize_date_input(vencimento) if vencimento else None
    if due_filter:
        filtrados = [c for c in contratos if contract_due_date(c) == due_filter]
        if len(filtrados) == 1:
            contrato = filtrados[0]
            return cliente, resp, contrato, None
        if len(filtrados) > 1:
            return None, None, None, f"Mais de um contrato com vencimento {due_filter} para {cliente.get('nome')} na carteira de {resp.get('nome')}."
        return None, None, None, f"Não encontrei contrato de {cliente.get('nome')} na carteira de {resp.get('nome')} com vencimento {due_filter}."
    if len(contratos) > 1:
        datas = []
        for c in contratos[:5]:
            venc = contract_due_date(c) or 'sem vencimento'
            datas.append(venc)
        datas_txt = ', '.join(datas)
        return None, None, None, f"{cliente.get('nome')} tem mais de um contrato ativo na carteira de {resp.get('nome')}. Use: lista os contratos de {cliente.get('nome')}, {resp.get('nome')}. Vencimentos: {datas_txt}."
    contrato = contratos[0]
    return cliente, resp, contrato, None


def prepare_juros(actor, cliente_nome, responsavel_nome, valor=None, vencimento=None):
    cliente, resp, contrato, err = resolve_cliente_responsavel(cliente_nome, responsavel_nome, vencimento)
    if err:
        resp_obj = find_profile_by_name(responsavel_nome)
        clientes = find_clientes_na_carteira(resp_obj['id'], cliente_nome) if resp_obj else []
        if resp_obj and len(clientes) == 1 and 'mais de um contrato ativo' in err:
            contratos = get_active_contracts(clientes[0]['id'], resp_obj['id'])
            escolhido, label = pick_priority_contract(contratos)
            if not escolhido:
                return 'Sem contrato ativo para juros.'
            if escolhido.get('modalidade') != 'recorrente':
                return save_selection_pending(actor, 'juros', clientes[0], resp_obj, contratos, {'valor': round2(valor) if valor is not None else None})
            juros = calcular_juros_recorrente(escolhido.get('capital_atual'), escolhido.get('taxa_juros_mensal'))
            if valor is not None and round2(valor) != juros:
                return f"Valor divergente. Juros atual: {br_money(juros)}."
            pending = load_pending()
            existente = pending.get(actor)
            if existente and existente.get('tipo') in {'confirmar_prioridade_juros', 'somente_juros_recorrente'}:
                mesmo_cliente = existente.get('cliente_nome') == clientes[0]['nome']
                mesmo_resp = existente.get('responsavel_nome') == resp_obj['nome']
                mesmo_contrato = existente.get('contrato_id') == escolhido['id']
                mesmo_juros = round2(existente.get('juros') or 0) == juros
                if mesmo_cliente and mesmo_resp and mesmo_contrato and mesmo_juros:
                    return confirm(actor)
            pending[actor] = {
                'tipo': 'confirmar_prioridade_juros',
                'cliente_nome': clientes[0]['nome'],
                'responsavel_nome': resp_obj['nome'],
                'contrato_id': escolhido['id'],
                'juros': juros,
                'prioridade': label,
                'proximo_vencimento': escolhido.get('proximo_vencimento') or escolhido.get('primeiro_vencimento'),
                'prepared_at': br_now_iso(),
            }
            save_pending(pending)
            nome_curto = clientes[0]['nome'].split(',')[0].strip().title()
            return f"Juros {nome_curto} {br_money(juros)} · SIM ou NAO"
        return err
    if not contrato:
        return f"Não encontrei contrato ativo na carteira de {resp['nome']} para {cliente['nome']}."
    if contrato['modalidade'] == 'parcelado':
        parcelas = get_pending_parcelas(contrato['id'])
        if not parcelas:
            return f"{cliente['nome']} não tem parcelas pendentes."
        return save_parcela_juros_pending(actor, cliente, resp, contrato, parcelas)
    if contrato['modalidade'] != 'recorrente':
        return f"{cliente['nome']} está em contrato {contrato['modalidade']}. Só juros em recorrente."
    juros = calcular_juros_recorrente(contrato['capital_atual'], contrato['taxa_juros_mensal'])
    if valor is not None and round2(valor) != juros:
        return f"Valor divergente. Juros atual: {br_money(juros)}."
    pending = load_pending()
    existente = pending.get(actor)
    if existente and existente.get('tipo') in {'confirmar_prioridade_juros', 'somente_juros_recorrente'}:
        mesmo_cliente = existente.get('cliente_nome') == cliente['nome']
        mesmo_resp = existente.get('responsavel_nome') == resp['nome']
        mesmo_contrato = existente.get('contrato_id') == contrato['id']
        mesmo_juros = round2(existente.get('juros') or 0) == juros
        if mesmo_cliente and mesmo_resp and mesmo_contrato and mesmo_juros:
            return confirm(actor)
    pending[actor] = {
        'tipo': 'somente_juros_recorrente',
        'cliente_nome': cliente['nome'], 'responsavel_nome': resp['nome'], 'contrato_id': contrato['id'],
        'juros': juros, 'proximo_vencimento': contrato.get('proximo_vencimento'), 'prepared_at': br_now_iso()
    }
    save_pending(pending)
    nome_curto = cliente['nome'].split(',')[0].strip().title()
    return f"Juros {nome_curto} {br_money(juros)} · SIM ou NAO"

def prepare_add_capital(actor, cliente_nome, responsavel_nome, valor, vencimento=None):
    cliente, resp, contrato, err = resolve_cliente_responsavel(cliente_nome, responsavel_nome, vencimento)
    if err:
        resp_obj = find_profile_by_name(responsavel_nome)
        clientes = find_clientes_na_carteira(resp_obj['id'], cliente_nome) if resp_obj else []
        if resp_obj and len(clientes) == 1 and 'mais de um contrato ativo' in err:
            return save_selection_pending(actor, 'adicionar_capital', clientes[0], resp_obj, get_active_contracts(clientes[0]['id'], resp_obj['id']), {'valor': round2(valor)})
        return err
    atual = round2(contrato['capital_atual'])
    inicial = round2(contrato.get('capital_inicial') or atual)
    valor = round2(valor)
    novo_atual = round2(atual + valor)
    novo_inicial = round2(inicial + valor)
    juros_novo = calcular_juros_recorrente(novo_atual, contrato['taxa_juros_mensal'])
    pending = load_pending()
    if contrato['modalidade'] == 'recorrente':
        pending[actor] = {
            'tipo': 'adicionar_capital_recorrente',
            'cliente_nome': cliente['nome'], 'responsavel_nome': resp['nome'], 'contrato_id': contrato['id'],
            'valor_adicionado': valor, 'capital_atual_antes': atual, 'capital_inicial_antes': inicial,
            'capital_atual_depois': novo_atual, 'capital_inicial_depois': novo_inicial, 'juros_novo_ciclo': juros_novo,
            'prepared_at': br_now_iso()
        }
        save_pending(pending)
        return f"Encontrei {cliente['nome']} na carteira de {resp['nome']}. Capital atual: {br_money(atual)}. Novo capital: {br_money(novo_atual)}. Novo juros do ciclo: {br_money(juros_novo)}. Confirmar adição de {br_money(valor)}?"
    parcelas = get_pending_parcelas(contrato['id'])
    if not parcelas:
        return f"{cliente['nome']} não tem parcelas pendentes para redistribuir o capital adicional."
    cobranca = 'semanal' if is_cobranca_semanal(contrato.get('observacoes')) else 'mensal'
    recalculadas = recalcular_parcelas_apos_amortizacao(parcelas, novo_atual, contrato['taxa_juros_mensal'])
    parcela_ref = recalculadas[0] if recalculadas else None
    total_ref = round2((parcela_ref or {}).get('capital_parcela', 0) + (parcela_ref or {}).get('juros_parcela', 0))
    pending[actor] = {
        'tipo': 'adicionar_capital_parcelado',
        'cliente_nome': cliente['nome'], 'responsavel_nome': resp['nome'], 'contrato_id': contrato['id'],
        'valor_adicionado': valor, 'capital_atual_antes': atual, 'capital_inicial_antes': inicial,
        'capital_atual_depois': novo_atual, 'capital_inicial_depois': novo_inicial, 'juros_novo_ciclo': juros_novo,
        'cobranca': cobranca, 'parcelas_recalculadas': recalculadas, 'parcela_total_referencia': total_ref,
        'prepared_at': br_now_iso()
    }
    save_pending(pending)
    return f"Encontrei {cliente['nome']} na carteira de {resp['nome']}. Contrato parcelado {cobranca}. Capital atual: {br_money(atual)}. Novo capital: {br_money(novo_atual)}. Vou redistribuir nas parcelas pendentes mantendo o {cobranca}. Próxima parcela estimada: {br_money(total_ref)}. Confirmar adição de {br_money(valor)}?"



def prepare_novo_contrato(actor, cliente_nome, responsavel_nome, capital, taxa_percent, parcelas=None, primeiro_vencimento=None, cobranca='mensal'):
    resp = find_profile_by_name(responsavel_nome)
    if not resp:
        return f'Responsável não encontrado: {responsavel_nome}.'
    clientes = find_cliente(cliente_nome)
    if not clientes:
        return f'Cliente não encontrado no cadastro: {cliente_nome}.'
    if len(clientes) > 1:
        nomes = ', '.join(c.get('nome', '?') for c in clientes[:5])
        return f'Cliente ambíguo no cadastro: {nomes}. Seja mais específico.'
    cliente = clientes[0]
    if not primeiro_vencimento:
        return 'Falta o primeiro vencimento. Exemplo: primeiro vencimento 2026-06-12.'
    primeiro_vencimento = normalize_date_input(primeiro_vencimento)
    if not primeiro_vencimento:
        return 'Data da primeira parcela inválida. Use DD/MM/AAAA ou YYYY-MM-DD.'
    modalidade = 'parcelado' if parcelas else 'recorrente'
    capital = round2(capital)
    taxa_decimal = round2(float(taxa_percent) / 100)
    cobranca = 'semanal' if str(cobranca or '').lower().startswith('sem') else 'mensal'
    pending = load_pending()
    payload = {
        'cliente_id': cliente['id'],
        'responsavel_id': resp['id'],
        'modalidade': modalidade,
        'capital_inicial': capital,
        'capital_atual': capital,
        'taxa_juros_mensal': taxa_decimal,
        'data_contrato': br_today(),
        'primeiro_vencimento': primeiro_vencimento,
        'proximo_vencimento': primeiro_vencimento,
        'status': 'ativo',
        'parcelas_pagas': 0,
        'parcelas_empurradas': 0,
        'gera_comissao': gera_comissao_para(resp),
    }
    parcelas_preview = []
    if modalidade == 'parcelado':
        payload['num_parcelas'] = int(parcelas)
        if cobranca == 'semanal':
            payload['observacoes'] = json.dumps({'cobranca': 'semanal'}, ensure_ascii=False)
        parcelas_preview = montar_grade_parcelas(capital, taxa_decimal, int(parcelas), primeiro_vencimento, cobranca)
    pending[actor] = {
        'tipo': 'novo_contrato',
        'cliente_nome': cliente['nome'],
        'responsavel_nome': resp['nome'],
        'payload': payload,
        'parcelas_preview': parcelas_preview,
        'prepared_at': br_now_iso(),
    }
    save_pending(pending)
    return format_novo_contrato_preview(cliente['nome'], resp['nome'], payload, parcelas_preview)

def prepare_parcela(actor, cliente_nome, responsavel_nome, vencimento=None):
    cliente, resp, contrato, err = resolve_cliente_responsavel(cliente_nome, responsavel_nome, vencimento)
    if err:
        resp_obj = find_profile_by_name(responsavel_nome)
        clientes = find_clientes_na_carteira(resp_obj['id'], cliente_nome) if resp_obj else []
        if resp_obj and len(clientes) == 1 and 'mais de um contrato ativo' in err:
            return save_selection_pending(actor, 'parcela', clientes[0], resp_obj, get_active_contracts(clientes[0]['id'], resp_obj['id']))
        return err
    if contrato['modalidade'] != 'parcelado':
        return f"{cliente['nome']} está em contrato recorrente. Parcela completa só existe para parcelado."
    parcelas = get_pending_parcelas(contrato['id'])
    if not parcelas:
        return f"{cliente['nome']} não tem parcelas pendentes."
    p = parcelas[0]
    cp = round2(p['capital_parcela'])
    jp = round2(p['juros_parcela'])
    total = round2(cp + jp)
    total_parcelas = int(contrato.get('num_parcelas') or p.get('numero_parcela') or 0)
    pendentes = len(parcelas)
    venc = p.get('data_vencimento') or contrato.get('proximo_vencimento') or 'sem vencimento'
    try:
        y, m, d = venc.split('-')
        venc_fmt = f'{d}/{m}/{y}'
    except Exception:
        venc_fmt = venc
    pending = load_pending()
    pending[actor] = {
        'tipo': 'parcela_completa',
        'cliente_nome': cliente['nome'], 'responsavel_nome': resp['nome'], 'contrato_id': contrato['id'], 'parcela_id': p['id'],
        'numero_parcela': p['numero_parcela'], 'total_parcelas': total_parcelas, 'parcelas_pendentes': pendentes,
        'capital_parcela': cp, 'juros_parcela': jp, 'total': total, 'vencimento': venc,
        'capital_atual_antes': round2(contrato['capital_atual']), 'prepared_at': br_now_iso()
    }
    save_pending(pending)
    return (f"Encontrei {cliente['nome']} na carteira de {resp['nome']}:\n\n"
            f"Parcela do mês: {p['numero_parcela']}/{total_parcelas}\n"
            f"Vencimento: {venc_fmt}\n"
            f"Faltam: {pendentes} parcela(s) pendente(s), contando esta.\n\n"
            f"Capital: {br_money(cp)}\nJuros: {br_money(jp)}\nTotal: {br_money(total)}\n\n"
            f"Confirma o pagamento da parcela completa? Responda SIM ou NÃO.")

def prepare_empurrar_parcela(actor, cliente_nome, responsavel_nome, vencimento=None):
    cliente, resp, contrato, err = resolve_cliente_responsavel(cliente_nome, responsavel_nome, vencimento)
    if err:
        resp_obj = find_profile_by_name(responsavel_nome)
        clientes = find_clientes_na_carteira(resp_obj['id'], cliente_nome) if resp_obj else []
        if resp_obj and len(clientes) == 1 and 'mais de um contrato ativo' in err:
            return save_selection_pending(actor, 'empurrar_parcela', clientes[0], resp_obj, get_active_contracts(clientes[0]['id'], resp_obj['id']))
        return err
    if contrato['modalidade'] != 'parcelado':
        return f"{cliente['nome']} está em contrato recorrente. Empurrar parcela só existe para parcelado."
    parcelas = get_pending_parcelas(contrato['id'])
    if not parcelas:
        return f"{cliente['nome']} não tem parcelas pendentes."
    p = parcelas[0]
    jp = round2(p['juros_parcela'])
    pending = load_pending()
    pending[actor] = {
        'tipo': 'empurrar_parcela',
        'cliente_nome': cliente['nome'], 'responsavel_nome': resp['nome'], 'contrato_id': contrato['id'], 'parcela_id': p['id'],
        'numero_parcela': p['numero_parcela'], 'juros_parcela': jp, 'data_vencimento': p['data_vencimento'],
        'cobranca': 'semanal' if is_cobranca_semanal(contrato.get('observacoes')) else 'mensal',
        'prepared_at': br_now_iso()
    }
    save_pending(pending)
    return f"Encontrei {cliente['nome']} · parcela {p['numero_parcela']} · juros {br_money(jp)}. Vai empurrar o vencimento e receber só os juros. Confirmar?"


def prepare_amortizacao(actor, cliente_nome, responsavel_nome, valor, vencimento=None):
    cliente, resp, contrato, err = resolve_cliente_responsavel(cliente_nome, responsavel_nome, vencimento)
    if err:
        resp_obj = find_profile_by_name(responsavel_nome)
        clientes = find_clientes_na_carteira(resp_obj['id'], cliente_nome) if resp_obj else []
        if resp_obj and len(clientes) == 1 and 'mais de um contrato ativo' in err:
            return save_selection_pending(actor, 'amortizacao', clientes[0], resp_obj, get_active_contracts(clientes[0]['id'], resp_obj['id']), {'valor': round2(valor)})
        return err
    atual = round2(contrato['capital_atual'])
    if atual <= 0:
        return 'Capital do contrato já está zerado.'
    valor = round2(valor)
    efetivo = min(valor, atual)
    posterior = round2(atual - efetivo)
    total = efetivo >= atual
    juros_novo = calcular_juros_recorrente(posterior, contrato['taxa_juros_mensal']) if contrato['modalidade'] == 'recorrente' and posterior > 0 else 0
    pending = load_pending()
    pending[actor] = {
        'tipo': 'amortizacao',
        'cliente_nome': cliente['nome'], 'responsavel_nome': resp['nome'], 'contrato_id': contrato['id'],
        'modalidade': contrato['modalidade'], 'valor_amortizado': efetivo, 'capital_anterior': atual, 'capital_posterior': posterior,
        'quitacao': total, 'juros_novo_ciclo': juros_novo, 'prepared_at': br_now_iso()
    }
    save_pending(pending)
    if total:
        return f"Encontrei {cliente['nome']} na carteira de {resp['nome']}. Amortização total de {br_money(efetivo)}. Contrato ficará quitado. Confirmar?"
    msg = f"Encontrei {cliente['nome']} na carteira de {resp['nome']}. Capital atual: {br_money(atual)}. Após amortização: {br_money(posterior)}."
    if contrato['modalidade'] == 'recorrente':
        msg += f" Novo juros do ciclo: {br_money(juros_novo)}."
    msg += f" Confirmar amortização de {br_money(efetivo)}?"
    return msg


def prepare_quitacao(actor, cliente_nome, responsavel_nome, vencimento=None):
    cliente, resp, contrato, err = resolve_cliente_responsavel(cliente_nome, responsavel_nome, vencimento)
    if err:
        resp_obj = find_profile_by_name(responsavel_nome)
        clientes = find_clientes_na_carteira(resp_obj['id'], cliente_nome) if resp_obj else []
        if resp_obj and len(clientes) == 1 and 'mais de um contrato ativo' in err:
            return save_selection_pending(actor, 'quitacao', clientes[0], resp_obj, get_active_contracts(clientes[0]['id'], resp_obj['id']))
        return err
    return prepare_amortizacao(actor, cliente['nome'], resp['nome'], round2(contrato['capital_atual']))


def prepare_estorno(actor, cliente_nome, responsavel_nome, vencimento=None):
    cliente, resp, contrato, err = resolve_cliente_responsavel(cliente_nome, responsavel_nome, vencimento)
    if err:
        resp_obj = find_profile_by_name(responsavel_nome)
        clientes = find_clientes_na_carteira(resp_obj['id'], cliente_nome) if resp_obj else []
        if resp_obj and len(clientes) == 1 and 'mais de um contrato ativo' in err:
            return save_selection_pending(actor, 'estorno', clientes[0], resp_obj, get_active_contracts(clientes[0]['id'], resp_obj['id']))
        return err
    recebimentos = sb_get('recebimentos', {
        'select': 'id,tipo,capital_recebido,juros_recebido,data_recebimento,status,parcela_id',
        'contrato_id': f"eq.{contrato['id']}",
        'status': 'in.(ativo,inadimplente)',
        'order': 'data_recebimento.desc',
        'limit': '5',
    }) or []
    if not recebimentos:
        return f"{cliente['nome']} não tem recebimento ativo para estornar."
    rec = recebimentos[0]
    tipo = str(rec.get('tipo') or '').lower()
    pending = load_pending()
    pending[actor] = {
        'tipo': 'estorno',
        'cliente_nome': cliente['nome'], 'responsavel_nome': resp['nome'], 'contrato_id': contrato['id'],
        'recebimento_id': rec['id'], 'recebimento_tipo': tipo,
        'capital_recebido': round2(rec.get('capital_recebido') or 0),
        'juros_recebido': round2(rec.get('juros_recebido') or 0),
        'parcela_id': rec.get('parcela_id'), 'data_recebimento': rec.get('data_recebimento'),
        'prepared_at': br_now_iso()
    }
    save_pending(pending)
    partes = []
    if round2(rec.get('juros_recebido') or 0) > 0:
        partes.append(f"juros {br_money(rec.get('juros_recebido') or 0)}")
    if round2(rec.get('capital_recebido') or 0) > 0:
        partes.append(f"capital {br_money(rec.get('capital_recebido') or 0)}")
    detalhe = ' + '.join(partes) if partes else 'sem valores'
    return f"Último recebimento encontrado de {cliente['nome']}: tipo {tipo}, {detalhe}, data {rec.get('data_recebimento')}. Confirmar estorno?"


def confirm_juros(op):
    contrato = (sb_get('contratos', {'select': 'id,modalidade,capital_atual,taxa_juros_mensal,proximo_vencimento,status,parcelas_pagas', 'id': f"eq.{op['contrato_id']}", 'limit': '1'}) or [None])[0]
    if not contrato:
        return 'Contrato não encontrado no momento da confirmação.'
    if contrato['status'] not in ('ativo', 'inadimplente') or contrato['modalidade'] != 'recorrente':
        return 'Contrato não permite juros agora.'
    juros = calcular_juros_recorrente(contrato['capital_atual'], contrato['taxa_juros_mensal'])
    if round2(op['juros']) != juros:
        return f"Juros mudaram desde a preparação. Agora o ciclo está em {br_money(juros)}. Refazer comando."
    lellis = find_llellis_profile()
    receb = sb_insert('recebimentos', {
        'contrato_id': contrato['id'], 'parcela_id': None, 'registrado_por': lellis['id'], 'tipo': 'somente_juros',
        'capital_recebido': 0, 'juros_recebido': juros, 'data_recebimento': br_today(), 'forma_pagamento': None,
        'observacoes': 'Registro via agente main OpenClaw', 'status': 'ativo'
    })
    novo_proximo = add_months(contrato['proximo_vencimento'])
    sb_patch('contratos', {'id': f"eq.{contrato['id']}"}, {'parcelas_pagas': int(contrato.get('parcelas_pagas') or 0) + 1, 'proximo_vencimento': novo_proximo, 'status': 'ativo', 'atualizado_em': br_now_iso()})
    receb_row = receb[0] if isinstance(receb, list) else receb
    try:
        sb_insert('historico_eventos', {'entidade': 'recebimento', 'entidade_id': receb_row['id'], 'evento': 'criacao', 'usuario_id': lellis['id'], 'dados_depois': receb_row})
    except Exception:
        pass
    nome_curto = op['cliente_nome'].split(',')[0].strip().title()
    return f"Baixa feita. {nome_curto} · juros {br_money(juros)} · prox {novo_proximo}."

def confirm_add_capital(op):
    contrato = (sb_get('contratos', {'select': 'id,modalidade,capital_inicial,capital_atual,taxa_juros_mensal,status,observacoes', 'id': f"eq.{op['contrato_id']}", 'limit': '1'}) or [None])[0]
    if not contrato:
        return 'Contrato não encontrado no momento da confirmação.'
    if contrato['status'] not in ('ativo', 'inadimplente'):
        return 'Contrato não permite adição de capital agora.'
    valor = round2(op['valor_adicionado'])
    atual = round2(contrato['capital_atual'])
    inicial = round2(contrato.get('capital_inicial') or atual)
    novo_atual = round2(atual + valor)
    novo_inicial = round2(inicial + valor)
    juros_novo = calcular_juros_recorrente(novo_atual, contrato['taxa_juros_mensal'])
    lellis = find_llellis_profile()
    try:
        sb_patch('contratos', {'id': f"eq.{contrato['id']}"}, {'capital_inicial': novo_inicial, 'capital_atual': novo_atual, 'atualizado_em': br_now_iso()})
    except Exception:
        return 'Falha ao atualizar capital no app.'
    if contrato['modalidade'] == 'parcelado':
        parcelas = op.get('parcelas_recalculadas') or []
        if not parcelas:
            parcelas_vivas = get_pending_parcelas(contrato['id'])
            parcelas = recalcular_parcelas_apos_amortizacao(parcelas_vivas, novo_atual, contrato['taxa_juros_mensal'])
        for parcela in parcelas:
            sb_patch('parcelas', {'id': f"eq.{parcela['id']}"}, {
                'capital_parcela': parcela['capital_parcela'],
                'juros_parcela': parcela['juros_parcela'],
                'atualizado_em': br_now_iso(),
            })
        try:
            sb_insert('historico_eventos', {'entidade': 'contrato', 'entidade_id': contrato['id'], 'evento': 'edicao', 'usuario_id': lellis['id'], 'dados_antes': {'capital_inicial': inicial, 'capital_atual': atual}, 'dados_depois': {'capital_inicial': novo_inicial, 'capital_atual': novo_atual, 'reforco_capital': valor, 'modalidade': 'parcelado', 'cobranca': op.get('cobranca', 'mensal')}})
        except Exception:
            pass
        return f"Capital adicionado no app. {op['cliente_nome']} · +{br_money(valor)} · capital {br_money(novo_atual)} · parcelas recalculadas no {op.get('cobranca', 'mensal')}."
    try:
        sb_insert('historico_eventos', {'entidade': 'contrato', 'entidade_id': contrato['id'], 'evento': 'edicao', 'usuario_id': lellis['id'], 'dados_antes': {'capital_inicial': inicial, 'capital_atual': atual}, 'dados_depois': {'capital_inicial': novo_inicial, 'capital_atual': novo_atual, 'reforco_capital': valor, 'juros_novo_ciclo': juros_novo}})
    except Exception:
        pass
    return f"Capital adicionado no app. {op['cliente_nome']} · +{br_money(valor)} · capital {br_money(novo_atual)} · novo juros {br_money(juros_novo)}."


def confirm_parcela(op):
    contrato = (sb_get('contratos', {'select': 'id,modalidade,capital_atual,parcelas_pagas,status', 'id': f"eq.{op['contrato_id']}", 'limit': '1'}) or [None])[0]
    if not contrato:
        return 'Contrato não encontrado no momento da confirmação.'
    if contrato['status'] != 'ativo' or contrato['modalidade'] != 'parcelado':
        return 'Contrato não permite parcela completa agora.'
    parcela = (sb_get('parcelas', {'select': 'id,numero_parcela,capital_parcela,juros_parcela,status,data_vencimento', 'id': f"eq.{op['parcela_id']}", 'limit': '1'}) or [None])[0]
    if not parcela or parcela['status'] not in ('pendente', 'empurrado'):
        return 'Parcela não está mais disponível para pagamento.'
    cp = round2(parcela['capital_parcela'])
    jp = round2(parcela['juros_parcela'])
    lellis = find_llellis_profile()
    sb_patch('parcelas', {'id': f"eq.{parcela['id']}"}, {'status': 'pago', 'atualizado_em': br_now_iso()})
    receb = sb_insert('recebimentos', {
        'contrato_id': contrato['id'], 'parcela_id': parcela['id'], 'registrado_por': lellis['id'], 'tipo': 'parcela_completa',
        'capital_recebido': cp, 'juros_recebido': jp, 'data_recebimento': br_today(), 'forma_pagamento': None,
        'observacoes': 'Registro via agente main OpenClaw', 'status': 'ativo'
    })
    restantes = get_pending_parcelas(contrato['id'])
    novo_capital = round2(float(contrato['capital_atual']) - cp)
    quitado = len(restantes) == 0
    patch = {'capital_atual': novo_capital, 'parcelas_pagas': int(contrato.get('parcelas_pagas') or 0) + 1, 'proximo_vencimento': restantes[0]['data_vencimento'] if restantes else None, 'status': 'quitado' if quitado else 'ativo', 'atualizado_em': br_now_iso()}
    if quitado:
        patch['data_quitacao'] = br_today()
    sb_patch('contratos', {'id': f"eq.{contrato['id']}"}, patch)
    receb_row = receb[0] if isinstance(receb, list) else receb
    sb_insert('historico_eventos', {'entidade': 'recebimento', 'entidade_id': receb_row['id'], 'evento': 'criacao', 'usuario_id': lellis['id'], 'dados_depois': receb_row})
    return f"Parcela registrada no app. {op['cliente_nome']} · capital {br_money(cp)} · juros {br_money(jp)}."


def confirm_empurrar_parcela(op):
    contrato = (sb_get('contratos', {'select': 'id,modalidade,parcelas_empurradas,proximo_vencimento,status,observacoes', 'id': f"eq.{op['contrato_id']}", 'limit': '1'}) or [None])[0]
    if not contrato:
        return 'Contrato não encontrado no momento da confirmação.'
    if contrato['status'] != 'ativo' or contrato['modalidade'] != 'parcelado':
        return 'Contrato não permite empurrar parcela agora.'
    parcela = (sb_get('parcelas', {'select': 'id,numero_parcela,capital_parcela,juros_parcela,status,data_vencimento,data_original,empurrado_de', 'id': f"eq.{op['parcela_id']}", 'limit': '1'}) or [None])[0]
    if not parcela or parcela['status'] != 'pendente':
        return 'Parcela não está mais disponível para empurrar.'
    lellis = find_llellis_profile()
    original = parcela['data_vencimento']
    sb_patch('parcelas', {'id': f"eq.{parcela['id']}"}, {'status': 'empurrado', 'empurrado_de': original, 'atualizado_em': br_now_iso()})
    todas = get_pending_parcelas(contrato['id'])
    idx = next((i for i, row in enumerate(todas) if row['id'] == parcela['id']), 0)
    semanal = is_cobranca_semanal(contrato.get('observacoes'))
    novas = []
    for row in todas[idx:]:
        novo_venc = add_weeks(row['data_vencimento'], 1) if semanal else add_months(row['data_vencimento'], 1)
        novas.append((row['id'], novo_venc))
    for pid, due in novas:
        sb_patch('parcelas', {'id': f"eq.{pid}"}, {'data_vencimento': due, 'atualizado_em': br_now_iso()})
    juros = round2(parcela['juros_parcela'])
    receb = sb_insert('recebimentos', {
        'contrato_id': contrato['id'], 'parcela_id': parcela['id'], 'registrado_por': lellis['id'], 'tipo': 'somente_juros',
        'capital_recebido': 0, 'juros_recebido': juros, 'data_recebimento': br_today(), 'forma_pagamento': None,
        'observacoes': 'Empurrar parcela via agente main OpenClaw', 'status': 'ativo'
    })
    novo_proximo = None
    if todas:
        primeiro_id = todas[0]['id']
        novo_proximo = next((due for pid, due in novas if pid == primeiro_id), todas[0]['data_vencimento'])
    sb_patch('contratos', {'id': f"eq.{contrato['id']}"}, {
        'parcelas_empurradas': int(contrato.get('parcelas_empurradas') or 0) + 1,
        'proximo_vencimento': novo_proximo,
        'status': 'ativo',
        'atualizado_em': br_now_iso(),
    })
    receb_row = receb[0] if isinstance(receb, list) else receb
    try:
        sb_insert('historico_eventos', {'entidade': 'recebimento', 'entidade_id': receb_row['id'], 'evento': 'criacao', 'usuario_id': lellis['id'], 'dados_depois': receb_row})
        sb_insert('historico_eventos', {'entidade': 'parcela', 'entidade_id': parcela['id'], 'evento': 'empurramento', 'usuario_id': lellis['id'], 'dados_depois': {'status': 'empurrado', 'recebimento_id': receb_row['id']}})
    except Exception:
        pass
    return f"Parcela empurrada no app. {op['cliente_nome']} · juros {br_money(juros)} · novo vencimento {novo_proximo}."


def confirm_amortizacao(op):
    contrato = (sb_get('contratos', {'select': 'id,modalidade,capital_atual,taxa_juros_mensal,status', 'id': f"eq.{op['contrato_id']}", 'limit': '1'}) or [None])[0]
    if not contrato:
        return 'Contrato não encontrado no momento da confirmação.'
    if contrato['status'] not in ('ativo', 'inadimplente'):
        return 'Contrato não permite amortização agora.'
    atual = round2(contrato['capital_atual'])
    valor = min(round2(op['valor_amortizado']), atual)
    posterior = round2(atual - valor)
    total = valor >= atual
    lellis = find_llellis_profile()
    amort = sb_insert('amortizacoes', {
        'contrato_id': contrato['id'], 'registrado_por': lellis['id'], 'valor_amortizado': valor,
        'capital_anterior': atual, 'capital_posterior': posterior, 'taxa_anterior': contrato['taxa_juros_mensal'],
        'taxa_posterior': contrato['taxa_juros_mensal'], 'data_amortizacao': br_today(), 'observacoes': 'Registro via agente main OpenClaw'
    })
    sb_insert('recebimentos', {
        'contrato_id': contrato['id'], 'parcela_id': None, 'registrado_por': lellis['id'], 'tipo': 'amortizacao',
        'capital_recebido': valor, 'juros_recebido': 0, 'data_recebimento': br_today(), 'forma_pagamento': None,
        'observacoes': 'Registro via agente main OpenClaw', 'status': 'ativo'
    })
    patch = {'capital_atual': posterior, 'atualizado_em': br_now_iso()}
    if total:
        patch['status'] = 'quitado'
        patch['data_quitacao'] = br_today()
    if contrato['modalidade'] == 'parcelado':
        parcelas = get_pending_parcelas(contrato['id'])
        if total:
            for p in parcelas:
                sb_patch('parcelas', {'id': f"eq.{p['id']}"}, {'status': 'cancelado', 'atualizado_em': br_now_iso()})
        else:
            recalculadas = recalcular_parcelas_apos_amortizacao(parcelas, posterior, contrato['taxa_juros_mensal'])
            for p in recalculadas:
                sb_patch('parcelas', {'id': f"eq.{p['id']}"}, {'capital_parcela': p['capital_parcela'], 'juros_parcela': p['juros_parcela'], 'atualizado_em': br_now_iso()})
    sb_patch('contratos', {'id': f"eq.{contrato['id']}"}, patch)
    amort_row = amort[0] if isinstance(amort, list) else amort
    sb_insert('historico_eventos', {'entidade': 'amortizacao', 'entidade_id': amort_row['id'], 'evento': 'criacao', 'usuario_id': lellis['id'], 'dados_depois': {'valor_amortizado': valor, 'capital_anterior': atual, 'capital_posterior': posterior, 'tipo': 'total' if total else 'parcial'}})
    if total:
        return f"Quitação registrada no app. {op['cliente_nome']} · capital quitado {br_money(valor)}."
    if contrato['modalidade'] == 'recorrente':
        return f"Amortização registrada no app. {op['cliente_nome']} · novo capital {br_money(posterior)} · novo juros {br_money(calcular_juros_recorrente(posterior, contrato['taxa_juros_mensal']))}."
    return f"Amortização registrada no app. {op['cliente_nome']} · novo capital {br_money(posterior)} · parcelas recalculadas."



def confirm_novo_contrato(op):
    payload = dict(op['payload'])
    lellis = find_llellis_profile()
    payload['criado_por'] = lellis['id']
    contrato = sb_insert('contratos', payload)
    if not contrato:
        return 'Falha ao criar contrato.'
    contrato_row = contrato[0] if isinstance(contrato, list) else contrato
    if payload['modalidade'] == 'parcelado':
        total = int(payload['num_parcelas'])
        capital = round2(payload['capital_inicial'])
        taxa = float(payload['taxa_juros_mensal'])
        capital_por = round2(capital / total)
        juros_total = round2(capital * taxa * total)
        juros_por = round2(juros_total / total)
        soma_cap = capital_por * (total - 1)
        cap_last = round2(capital - soma_cap)
        soma_j = juros_por * (total - 1)
        jur_last = round2(juros_total - soma_j)
        parcelas = []
        base = payload['primeiro_vencimento']
        cobranca = 'semanal' if is_cobranca_semanal(payload.get('observacoes')) else 'mensal'
        for i in range(total):
            dt = base if i == 0 else (add_weeks(base, i) if cobranca == 'semanal' else add_months(base, i))
            parcelas.append({
                'contrato_id': contrato_row['id'],
                'numero_parcela': i + 1,
                'capital_parcela': cap_last if i == total - 1 else capital_por,
                'juros_parcela': jur_last if i == total - 1 else juros_por,
                'data_vencimento': dt,
                'data_original': dt,
                'status': 'pendente',
            })
        request('POST', 'parcelas', body=parcelas, prefer='return=representation')
    sb_insert('historico_eventos', {'entidade': 'contrato', 'entidade_id': contrato_row['id'], 'evento': 'criacao', 'usuario_id': lellis['id'], 'dados_depois': contrato_row})
    return f"Contrato criado no app. {op['cliente_nome']} · {op['responsavel_nome']} · capital {br_money(payload['capital_inicial'])}."


def confirm_estorno(op):
    contrato = (sb_get('contratos', {'select': 'id,modalidade,capital_atual,taxa_juros_mensal,parcelas_pagas,parcelas_empurradas,proximo_vencimento,status,data_quitacao', 'id': f"eq.{op['contrato_id']}", 'limit': '1'}) or [None])[0]
    if not contrato:
        return 'Contrato não encontrado no momento da confirmação.'
    recs = sb_get('recebimentos', {
        'select': 'id,contrato_id,parcela_id,tipo,capital_recebido,juros_recebido,data_recebimento,status',
        'id': f"eq.{op['recebimento_id']}", 'limit': '1'
    }) or []
    if not recs:
        return 'Recebimento não encontrado.'
    rec = recs[0]
    if rec.get('status') == 'estornado':
        return 'Recebimento já foi estornado.'
    lellis = find_llellis_profile()
    tipo = str(rec.get('tipo') or '').lower()
    if tipo == 'somente_juros':
        if rec.get('parcela_id'):
            parcelas = sb_get('parcelas', {'select': 'id,status,data_vencimento,empurrado_de,numero_parcela', 'id': f"eq.{rec['parcela_id']}", 'limit': '1'}) or []
            if parcelas:
                parcela = parcelas[0]
                data_revertida = parcela.get('empurrado_de') or parcela.get('data_vencimento')
                sb_patch('parcelas', {'id': f"eq.{parcela['id']}"}, {'status': 'pendente', 'data_vencimento': data_revertida, 'empurrado_de': None, 'atualizado_em': br_now_iso()})
            sb_patch('contratos', {'id': f"eq.{contrato['id']}"}, {'parcelas_empurradas': max(0, int(contrato.get('parcelas_empurradas') or 0) - 1), 'atualizado_em': br_now_iso()})
        else:
            novo_prox = add_months(contrato['proximo_vencimento'], -1) if contrato.get('proximo_vencimento') else None
            patch = {'parcelas_pagas': max(0, int(contrato.get('parcelas_pagas') or 0) - 1), 'atualizado_em': br_now_iso()}
            if novo_prox:
                patch['proximo_vencimento'] = novo_prox
            sb_patch('contratos', {'id': f"eq.{contrato['id']}"}, patch)
    elif tipo == 'parcela_completa':
        if not rec.get('parcela_id'):
            return 'Recebimento de parcela sem parcela vinculada.'
        parcelas = sb_get('parcelas', {'select': 'id,status,data_vencimento', 'id': f"eq.{rec['parcela_id']}", 'limit': '1'}) or []
        if not parcelas:
            return 'Parcela não encontrada para estorno.'
        parcela = parcelas[0]
        sb_patch('parcelas', {'id': f"eq.{parcela['id']}"}, {'status': 'pendente', 'atualizado_em': br_now_iso()})
        novo_capital = round2(float(contrato.get('capital_atual') or 0) + float(rec.get('capital_recebido') or 0))
        patch = {
            'capital_atual': novo_capital,
            'parcelas_pagas': max(0, int(contrato.get('parcelas_pagas') or 0) - 1),
            'status': 'ativo' if contrato.get('status') == 'quitado' else contrato.get('status'),
            'data_quitacao': None if contrato.get('status') == 'quitado' else contrato.get('data_quitacao'),
            'atualizado_em': br_now_iso(),
        }
        sb_patch('contratos', {'id': f"eq.{contrato['id']}"}, patch)
    elif tipo == 'amortizacao':
        capital_reverter = round2(rec.get('capital_recebido') or 0)
        novo_capital = round2(float(contrato.get('capital_atual') or 0) + capital_reverter)
        patch = {'capital_atual': novo_capital, 'atualizado_em': br_now_iso()}
        if contrato.get('status') == 'quitado':
            patch['status'] = 'ativo'
            patch['data_quitacao'] = None
        sb_patch('contratos', {'id': f"eq.{contrato['id']}"}, patch)
    else:
        return f"Tipo de recebimento '{tipo}' ainda não suportado neste fluxo."
    # remover comissao se houver
    try:
        request('DELETE', 'comissoes', params={'recebimento_id': f"eq.{rec['id']}"})
    except Exception:
        pass
    sb_patch('recebimentos', {'id': f"eq.{rec['id']}"}, {'status': 'estornado', 'estornado_em': br_now_iso(), 'estornado_por': lellis['id'], 'motivo_estorno': 'Estorno via agente main OpenClaw'})
    sb_insert('historico_eventos', {'entidade': 'recebimento', 'entidade_id': rec['id'], 'evento': 'estorno', 'usuario_id': lellis['id'], 'dados_antes': rec, 'dados_depois': {'status': 'estornado', 'origem': 'main_openclaw'}})
    return f"Estorno registrado no app. {op['cliente_nome']} · tipo {tipo}."

def confirm(actor):
    pending = load_pending()
    op = pending.get(actor)
    if not op:
        return 'Sem pendencia para confirmar.'
    tipo = op.get('tipo')
    if tipo == 'confirmar_prioridade_juros':
        result = confirm_juros(op)
    elif tipo == 'selecionar_contrato':
        return format_contract_options(op['cliente_nome'], op['responsavel_nome'], op.get('contratos') or [])
    elif tipo == 'somente_juros_recorrente':
        result = confirm_juros(op)
    elif tipo in {'adicionar_capital_recorrente', 'adicionar_capital_parcelado'}:
        result = confirm_add_capital(op)
    elif tipo == 'parcela_completa':
        result = confirm_parcela(op)
    elif tipo == 'empurrar_parcela':
        result = confirm_empurrar_parcela(op)
    elif tipo == 'amortizacao':
        result = confirm_amortizacao(op)
    elif tipo == 'novo_contrato':
        result = confirm_novo_contrato(op)
    elif tipo == 'estorno':
        result = confirm_estorno(op)
    else:
        return 'Pendencia invalida.'
    pending.pop(actor, None)
    save_pending(pending)
    return result


def selecionar_parcela_juros(actor, escolha):
    pending = load_pending()
    op = pending.get(actor)
    if not op:
        return 'Sem selecao pendente.'
    if op.get('tipo') == 'escolher_pagamento_parcela':
        alvo = (escolha or '').strip()
        if alvo == '1':
            pending[actor] = {
                'tipo': 'empurrar_parcela',
                'cliente_nome': op['cliente_nome'], 'responsavel_nome': op['responsavel_nome'], 'contrato_id': op['contrato_id'], 'parcela_id': op['parcela_id'],
                'numero_parcela': op['numero_parcela'], 'total_parcelas': op.get('total_parcelas'), 'parcelas_pendentes': op.get('parcelas_pendentes'),
                'capital_parcela': op.get('capital_parcela'), 'juros_parcela': op.get('juros_parcela'), 'total': op.get('total'),
                'vencimento': op.get('vencimento'), 'prepared_at': br_now_iso()
            }
            save_pending(pending)
            return (f"Só juros da parcela {op['numero_parcela']}/{op.get('total_parcelas')} de {op['cliente_nome']}.\n"
                    f"Juros: {br_money(op.get('juros_parcela') or 0)}\n"
                    f"Faltam: {op.get('parcelas_pendentes')} parcela(s) pendente(s), contando esta.\n\n"
                    f"Confirma receber só os juros e empurrar a parcela? Responda SIM ou NÃO.")
        if alvo == '2':
            pending[actor] = {
                'tipo': 'parcela_completa',
                'cliente_nome': op['cliente_nome'], 'responsavel_nome': op['responsavel_nome'], 'contrato_id': op['contrato_id'], 'parcela_id': op['parcela_id'],
                'numero_parcela': op['numero_parcela'], 'total_parcelas': op.get('total_parcelas'), 'parcelas_pendentes': op.get('parcelas_pendentes'),
                'capital_parcela': op.get('capital_parcela'), 'juros_parcela': op.get('juros_parcela'), 'total': op.get('total'),
                'vencimento': op.get('vencimento'), 'capital_atual_antes': None, 'prepared_at': br_now_iso()
            }
            save_pending(pending)
            return (f"Parcela completa {op['numero_parcela']}/{op.get('total_parcelas')} de {op['cliente_nome']}.\n"
                    f"Capital: {br_money(op.get('capital_parcela') or 0)}\n"
                    f"Juros: {br_money(op.get('juros_parcela') or 0)}\n"
                    f"Total: {br_money(op.get('total') or 0)}\n"
                    f"Faltam: {op.get('parcelas_pendentes')} parcela(s) pendente(s), contando esta.\n\n"
                    f"Confirma o pagamento da parcela completa? Responda SIM ou NÃO.")
        return format_escolha_pagamento_parcela(op)
    if op.get('tipo') != 'selecionar_parcela_juros':
        return 'Sem selecao de parcela pendente.'
    parcelas = op.get('parcelas') or []
    alvo = (escolha or '').strip()
    selecionada = None
    if alvo.isdigit():
        idx = int(alvo)
        if 1 <= idx <= len(parcelas):
            selecionada = parcelas[idx - 1]
    if not selecionada:
        due = normalize_date_input(alvo)
        if due:
            hits = [p for p in parcelas if p.get('data_vencimento') == due]
            if len(hits) == 1:
                selecionada = hits[0]
    if not selecionada:
        return format_parcela_juros_options(op['cliente_nome'], op['responsavel_nome'], parcelas)
    total_parcelas = int(op.get('total_parcelas') or selecionada.get('numero_parcela') or 0)
    pendentes = len(parcelas)
    pending[actor] = {
        'tipo': 'empurrar_parcela',
        'cliente_nome': op['cliente_nome'], 'responsavel_nome': op['responsavel_nome'], 'contrato_id': op['contrato_id'], 'parcela_id': selecionada['id'],
        'numero_parcela': selecionada['numero_parcela'], 'total_parcelas': total_parcelas, 'parcelas_pendentes': pendentes,
        'capital_parcela': round2(selecionada.get('capital_parcela') or 0), 'juros_parcela': round2(selecionada.get('juros_parcela') or 0),
        'total': round2((selecionada.get('capital_parcela') or 0) + (selecionada.get('juros_parcela') or 0)),
        'vencimento': selecionada.get('data_vencimento'), 'prepared_at': br_now_iso()
    }
    save_pending(pending)
    juros = round2(selecionada.get('juros_parcela') or 0)
    total = round2((selecionada.get('capital_parcela') or 0) + (selecionada.get('juros_parcela') or 0))
    venc = selecionada.get('data_vencimento') or 'sem vencimento'
    try:
        y, m, d = venc.split('-')
        venc_fmt = f'{d}/{m}/{y[2:]}'
    except Exception:
        venc_fmt = venc
    return (f"Só juros da parcela {selecionada['numero_parcela']}/{total_parcelas} de {op['cliente_nome']}.\n"
            f"Vencimento: {venc_fmt}\n"
            f"Faltam: {pendentes} parcela(s) pendente(s), contando esta.\n\n"
            f"Juros: {br_money(juros)}\nParcela completa seria: {br_money(total)}\n\n"
            f"Confirma receber só os juros e empurrar a parcela? Responda SIM ou NÃO.")

def selecionar_vencimento(actor, vencimento):
    pending = load_pending()
    op = pending.get(actor)
    if not op:
        return 'Sem selecao pendente.'
    if op.get('tipo') != 'selecionar_contrato':
        return 'Sem selecao de contrato pendente.'
    due = normalize_date_input(vencimento)
    if not due:
        return 'Data invalida. Use YYYY-MM-DD.'
    contratos = op.get('contratos') or []
    escolhidos = [c for c in contratos if c.get('vencimento') == due]
    if len(escolhidos) != 1:
        return format_contract_options(op['cliente_nome'], op['responsavel_nome'], contratos)
    acao = op.get('acao')
    extra = op.get('extra') or {}
    pending.pop(actor, None)
    save_pending(pending)
    if acao == 'juros':
        return prepare_juros(actor, op['cliente_nome'], op['responsavel_nome'], extra.get('valor'), due)
    if acao == 'adicionar_capital':
        return prepare_add_capital(actor, op['cliente_nome'], op['responsavel_nome'], extra.get('valor'), due)
    if acao == 'parcela':
        return prepare_parcela(actor, op['cliente_nome'], op['responsavel_nome'], due)
    if acao == 'empurrar_parcela':
        return prepare_empurrar_parcela(actor, op['cliente_nome'], op['responsavel_nome'], due)
    if acao == 'amortizacao':
        return prepare_amortizacao(actor, op['cliente_nome'], op['responsavel_nome'], extra.get('valor'), due)
    if acao == 'quitacao':
        return prepare_quitacao(actor, op['cliente_nome'], op['responsavel_nome'], due)
    if acao == 'estorno':
        return prepare_estorno(actor, op['cliente_nome'], op['responsavel_nome'], due)
    return 'Ação pendente não suportada.'


def cancel(actor):
    pending = load_pending()
    if actor in pending:
        pending.pop(actor, None)
        save_pending(pending)
        return 'Pendencia cancelada.'
    return 'Sem pendencia para cancelar.'


def status(actor):
    op = load_pending().get(actor)
    if not op:
        return 'Sem operação pendente.'
    t = op['tipo']
    if t == 'confirmar_prioridade_juros':
        return f"Pendente: {op['cliente_nome']} · {op.get('prioridade','CONTRATO')} · juros {br_money(op['juros'])}."
    if t == 'selecionar_contrato':
        return format_contract_options(op['cliente_nome'], op['responsavel_nome'], op.get('contratos') or [])
    if t == 'selecionar_parcela_juros':
        return format_parcela_juros_options(op['cliente_nome'], op['responsavel_nome'], op.get('parcelas') or [])
    if t == 'escolher_pagamento_parcela':
        return format_escolha_pagamento_parcela(op)
    if t == 'somente_juros_recorrente':
        return f"Pendente: {op['cliente_nome']} · {op['responsavel_nome']} · juros {br_money(op['juros'])}."
    if t == 'adicionar_capital_recorrente':
        return f"Pendente: {op['cliente_nome']} · {op['responsavel_nome']} · adicionar {br_money(op['valor_adicionado'])}."
    if t == 'parcela_completa':
        return f"Pendente: {op['cliente_nome']} · parcela {op['numero_parcela']} · total {br_money(op['total'])}."
    if t == 'empurrar_parcela':
        return f"Pendente: {op['cliente_nome']} · empurrar parcela {op['numero_parcela']} · juros {br_money(op['juros_parcela'])}."
    if t == 'amortizacao':
        return f"Pendente: {op['cliente_nome']} · amortização {br_money(op['valor_amortizado'])}."
    if t == 'novo_contrato':
        return f"Pendente: novo contrato · {op['cliente_nome']} · {op['responsavel_nome']} · capital {br_money(op['payload']['capital_inicial'])}."
    if t == 'estorno':
        return f"Pendente: estorno · {op['cliente_nome']} · tipo {op['recebimento_tipo']}."
    return 'Sem operação pendente.'


def main():
    if len(sys.argv) < 2:
        print('uso: credplus_operacoes.py <prepare_juros|prepare_add_capital|prepare_parcela|prepare_empurrar_parcela|prepare_amortizacao|prepare_quitacao|prepare_novo_contrato|prepare_estorno|selecionar_vencimento|selecionar_parcela_juros|confirmar|cancelar|status> ...')
        sys.exit(1)
    cmd = sys.argv[1]
    actor = sys.argv[2] if len(sys.argv) > 2 else 'mestre'
    if cmd == 'prepare_juros':
        valor = float(sys.argv[5].replace(',', '.')) if len(sys.argv) > 5 and sys.argv[5] != '0' else None
        venc = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] != '0' else None
        print(prepare_juros(actor, sys.argv[3], sys.argv[4], valor, venc))
    elif cmd == 'prepare_add_capital':
        venc = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] != '0' else None
        print(prepare_add_capital(actor, sys.argv[3], sys.argv[4], float(sys.argv[5].replace(',', '.')), venc))
    elif cmd == 'prepare_parcela':
        venc = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != '0' else None
        print(prepare_parcela(actor, sys.argv[3], sys.argv[4], venc))
    elif cmd == 'prepare_empurrar_parcela':
        venc = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != '0' else None
        print(prepare_empurrar_parcela(actor, sys.argv[3], sys.argv[4], venc))
    elif cmd == 'prepare_amortizacao':
        venc = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] != '0' else None
        print(prepare_amortizacao(actor, sys.argv[3], sys.argv[4], float(sys.argv[5].replace(',', '.')), venc))
    elif cmd == 'prepare_quitacao':
        venc = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != '0' else None
        print(prepare_quitacao(actor, sys.argv[3], sys.argv[4], venc))
    elif cmd == 'prepare_novo_contrato':
        cliente = sys.argv[3]
        responsavel = sys.argv[4]
        capital = float(sys.argv[5].replace(',', '.'))
        taxa = float(sys.argv[6].replace(',', '.'))
        parcelas = None if sys.argv[7] == '0' else int(sys.argv[7])
        primeiro = None if sys.argv[8] == '0' else sys.argv[8]
        cobranca = sys.argv[9] if len(sys.argv) > 9 and sys.argv[9] != '0' else 'mensal'
        print(prepare_novo_contrato(actor, cliente, responsavel, capital, taxa, parcelas, primeiro, cobranca))
    elif cmd == 'prepare_estorno':
        venc = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != '0' else None
        print(prepare_estorno(actor, sys.argv[3], sys.argv[4], venc))
    elif cmd == 'selecionar_vencimento':
        print(selecionar_vencimento(actor, sys.argv[3]))
    elif cmd == 'selecionar_parcela_juros':
        print(selecionar_parcela_juros(actor, sys.argv[3]))
    elif cmd == 'confirmar':
        print(confirm(actor))
    elif cmd == 'cancelar':
        print(cancel(actor))
    elif cmd == 'status':
        print(status(actor))
    else:
        print(f'comando desconhecido: {cmd}')
        sys.exit(2)


if __name__ == '__main__':
    main()
