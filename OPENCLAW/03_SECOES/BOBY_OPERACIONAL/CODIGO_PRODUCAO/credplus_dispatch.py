#!/usr/bin/env python3
import json
import os
import re
import sys
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

import credplus_operacoes as ops

TZ = ZoneInfo('America/Sao_Paulo')
CTX_PATHS = [
    '/data/.openclaw/workspace/telegram_context.json',
    '/docker/openclaw-189p/data/.openclaw/workspace/telegram_context.json',
]

def resolve_ctx_path():
    for p in CTX_PATHS:
        if os.path.exists(os.path.dirname(p)):
            return p
    return CTX_PATHS[-1]
PASS = '__PASS_TO_AGENT__'

RESP_ALIASES = {
    'LELLIS': 'LELLISFLAVIO',
    'LELLISFLAVIO': 'LELLISFLAVIO',
    'TOM': 'LELLISFLAVIO',
    'JAILTON': 'JAILTON',
    'JEAN': 'JEAN',
    'SANNY': 'SANNY',
    'MARCOS': 'MARCOS',
    'MANGU': 'MANGU',
    'RICARDO': 'RICARDO',
    'GALEGO': 'GALEGO',
    'TUK': 'MATHEUS TUK',
    'MATHEUS': 'MATHEUS TUK',
    'MATHEUS TUK': 'MATHEUS TUK',
}


def now_iso():
    return datetime.now(TZ).replace(microsecond=0).isoformat()


def norm_spaces(s: str) -> str:
    return re.sub(r'\s+', ' ', (s or '').strip())


def strip_trailing_punctuation(s: str) -> str:
    return re.sub(r'[\s,;:]+$', '', norm_spaces(s))


def money_to_float(raw: str):
    if raw is None:
        return None
    txt = raw.strip()
    if not txt:
        return None
    txt = txt.replace('R$', '').replace('r$', '').strip()
    txt = txt.replace('.', '').replace(',', '.')
    try:
        return float(txt)
    except Exception:
        return None


def normalize_date(raw: str):
    return ops.normalize_date_input(raw)


def extract_date(text: str):
    m = re.search(r'(?i)(?:^|\b)vencimento\s+((?:\d{4}-\d{2}-\d{2})|(?:\d{2}[-/]\d{2}[-/]\d{4}))\b', text)
    if m:
        return normalize_date(m.group(1))
    m = re.fullmatch(r'\s*((?:\d{4}-\d{2}-\d{2})|(?:\d{2}[-/]\d{2}[-/]\d{4}))\s*', text)
    if m:
        return normalize_date(m.group(1))
    return None


def canon_resp(raw: str):
    if not raw:
        return None
    base = norm_spaces(raw).upper()
    base = re.sub(r'^(DO\s+SOCIO|DO\s+SÓCIO|SOCIO|SÓCIO)\s+', '', base)
    base = re.sub(r'^(E\s+DO\s+SOCIO|E\s+DO\s+SÓCIO|E\s+SOCIO|E\s+SÓCIO)\s+', '', base)
    if base in RESP_ALIASES:
        return RESP_ALIASES[base]
    for key, val in RESP_ALIASES.items():
        if base.startswith(key):
            return val
    return norm_spaces(raw).title()


def load_ctx():
    path = resolve_ctx_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_ctx(data):
    with open(resolve_ctx_path(), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)




def resolve_workspace_file(name):
    candidates = [
        f'/data/.openclaw/workspace/{name}',
        f'/docker/openclaw-189p/data/.openclaw/workspace/{name}',
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return candidates[0]

def get_actor_ctx(actor: str):
    return load_ctx().get(actor, {})


def set_actor_ctx(actor: str, ctx: dict):
    data = load_ctx()
    if ctx:
        ctx['updated_at'] = now_iso()
        data[actor] = ctx
    else:
        data.pop(actor, None)
    save_ctx(data)


def remember_subject(actor: str, cliente=None, responsavel=None):
    data = load_ctx()
    ctx = data.get(actor, {})
    last = ctx.get('last_subject', {})
    if cliente:
        last['cliente'] = norm_spaces(cliente)
    if responsavel:
        last['responsavel'] = canon_resp(responsavel)
    if last:
        ctx['last_subject'] = last
        ctx['updated_at'] = now_iso()
        data[actor] = ctx
        save_ctx(data)


def run_ops(*args):
    cmd = ['python3', resolve_workspace_file('credplus_operacoes.py'), *args]
    res = subprocess.run(cmd, capture_output=True, text=True)
    out = (res.stdout or '').strip()
    err = (res.stderr or '').strip()
    return out or err or 'Falha ao executar operação.'


def run_bridge(*args):
    cmd = ['python3', resolve_workspace_file('credplus_main_bridge.py'), *args]
    res = subprocess.run(cmd, capture_output=True, text=True)
    out = (res.stdout or '').strip()
    err = (res.stderr or '').strip()
    return out or err or 'Falha ao consultar contratos.'


def pending_for(actor: str):
    return ops.load_pending().get(actor)


def cancel_pending(actor: str):
    if pending_for(actor):
        return run_ops('cancelar', actor)
    return None


def is_confirmation(text: str):
    t = norm_spaces(text).lower()
    return t in {'sim', 'confirmar', 'ok', 'pode registrar', 'pode', 'registrar'}


def is_cancellation(text: str):
    t = norm_spaces(text).lower()
    return t in {'nao', 'não', 'cancelar', 'cancela'}


def parse_followup_responsavel(text: str):
    m = re.search(r'(?i)^(?:é\s+)?(?:e\s+)?(?:do\s+)?s[oó]cio\s+(.+)$', norm_spaces(text))
    if m:
        return canon_resp(m.group(1))
    m = re.search(r'(?i)^(?:é\s+)?(?:e\s+)?colaborador\s+(.+)$', norm_spaces(text))
    if m:
        return canon_resp(m.group(1))
    m = re.search(r'(?i)^respons[aá]vel\s+(.+)$', norm_spaces(text))
    if m:
        return canon_resp(m.group(1))
    m = re.fullmatch(r'(?i)(?:de\s+)?([a-zà-ÿ][a-zà-ÿ\s]+)', norm_spaces(text))
    if m:
        return canon_resp(m.group(1))
    return None


def split_cliente_responsavel(raw: str):
    txt = strip_trailing_punctuation(raw)
    patterns = [
        r'(?i)^(.+?)\s*,\s*(.+)$',
        r'(?i)^(.+?)\s+de\s+(.+)$',
        r'(?i)^(.+?)\s+s[oó]cio\s+(.+)$',
        r'(?i)^(.+?)\s+colaborador\s+(.+)$',
        r'(?i)^(.+?)\s+respons[aá]vel\s+(.+)$',
    ]
    for pattern in patterns:
        m = re.match(pattern, txt)
        if m:
            cliente = strip_trailing_punctuation(m.group(1))
            responsavel = canon_resp(m.group(2))
            if cliente and responsavel:
                return {'cliente': cliente, 'responsavel': responsavel}
    return None



def parse_carteira_secao(text: str):
    tx = norm_spaces(text)
    m = re.match(r'(?i)^(criticos?|vencidos?|hoje|amanha|vence\s+hoje|vence\s+amanha|extrato)\s*,?\s*(?:de\s+)?(?:(?:s[oó]cio|respons[aá]vel)\s+)?(.+)$', tx)
    if not m:
        return None
    sec_raw = norm_spaces(m.group(1)).lower()
    sec_map = {
        'critico': 'criticos',
        'criticos': 'criticos',
        'vencido': 'vencidos',
        'vencidos': 'vencidos',
        'hoje': 'hoje',
        'amanha': 'amanha',
        'vence hoje': 'hoje',
        'vence amanha': 'amanha',
        'extrato': 'todos',
    }
    responsavel = canon_resp(m.group(2))
    if not responsavel:
        return None
    return {'secao': sec_map.get(sec_raw), 'responsavel': responsavel}

def parse_cadastro_lookup(text):
    tx = norm_spaces(text)
    patterns = [
        r'(?i)^(?:dados|ver\s+dados|buscar\s+cadastro|lista(?:\s+os)?\s+dados(?:\s+de\s+cadastro)?|cadastro)(?:\s+de)?\s+(.+)$',
        r'(?i)^cadastrar\s+novo\s+cliente:?\s+(.+?),\s*respons[aá]vel\s+(.+)$',
    ]
    for idx, pattern in enumerate(patterns):
        m = re.match(pattern, tx)
        if not m:
            continue
        if idx == 1:
            cliente = strip_trailing_punctuation(m.group(1))
            responsavel = canon_resp(m.group(2))
            if cliente and responsavel:
                return {'cliente': cliente, 'responsavel': responsavel}
            continue
        parsed = split_cliente_responsavel(m.group(1))
        if parsed:
            return parsed
    return None


def parse_lista_contratos(text: str):
    m = re.match(r'(?i)^lista(?:\s+os)?\s+contratos\s+(.+)$', norm_spaces(text))
    if not m:
        m = re.match(r'(?i)^lista(?:\s+os)?\s+contratos\s+de\s+(.+)$', norm_spaces(text))
    if not m:
        return None
    return split_cliente_responsavel(m.group(1))


def parse_estorno(text: str):
    m = re.match(r'(?i)^estornar?(?:\s+o)?(?:\s+u?ltimo)?(?:\s+pagamento)?(?:\s+de)?\s+(.+)$', norm_spaces(text))
    if not m:
        return None
    parsed = split_cliente_responsavel(m.group(1))
    if parsed:
        return parsed
    return {'cliente': strip_trailing_punctuation(m.group(1)), 'responsavel': None}


def parse_juros(text: str):
    tx = norm_spaces(text)
    m = re.match(r'(?i)^(?:pagar|receber|registrar|lancar|lançar)\s+juros(?:\s+de)?\s+(.+)$', tx)
    if m:
        parsed = split_cliente_responsavel(m.group(1))
        if parsed:
            parsed['valor'] = None
            return parsed
        return {'cliente': strip_trailing_punctuation(m.group(1)), 'responsavel': None, 'valor': None}
    m = re.match(r'(?i)^pagar\s+(.+)$', tx)
    if m:
        parsed = split_cliente_responsavel(m.group(1))
        if parsed:
            parsed['valor'] = None
            return parsed
    m = re.match(r'(?i)^(.+?)\s+pagou\s+s[oó]\s+os\s+juros(?:\s*,\s*(.+))?$', tx)
    if m:
        parsed = split_cliente_responsavel(m.group(1))
        if parsed:
            parsed['valor'] = None
            return parsed
        return {'cliente': m.group(1).strip(), 'responsavel': canon_resp(m.group(2)) if m.group(2) else None, 'valor': None}
    m = re.match(r'(?i)^(.+?)\s+pagou\s+os\s+juros(?:\s*,\s*(.+))?$', tx)
    if m:
        parsed = split_cliente_responsavel(m.group(1))
        if parsed:
            parsed['valor'] = None
            return parsed
        return {'cliente': m.group(1).strip(), 'responsavel': canon_resp(m.group(2)) if m.group(2) else None, 'valor': None}
    m = re.match(r'(?i)^(.+?),\s*(.+?)\s+pagou\s+(?:os\s+)?juros$', tx)
    if m:
        return {'cliente': m.group(1).strip(), 'responsavel': canon_resp(m.group(2)), 'valor': None}
    m = re.match(r'(?i)^juros\s+de\s+(.+)$', tx)
    if m:
        parsed = split_cliente_responsavel(m.group(1))
        if parsed:
            parsed['valor'] = None
            return parsed
    m = re.match(r'(?i)^juros\s+([\d.,]+)$', tx)
    if m:
        return {'cliente': None, 'responsavel': None, 'valor': money_to_float(m.group(1))}
    m = re.match(r'(?i)^juros\s+([\d.,]+)\s+(.+)$', tx)
    if m:
        parsed = split_cliente_responsavel(m.group(2))
        if parsed:
            parsed['valor'] = money_to_float(m.group(1))
            return parsed
    m = re.match(r'(?i)^juros(?:\s+de)?\s+(.+)$', tx)
    if m:
        parsed = split_cliente_responsavel(m.group(1))
        if parsed:
            parsed['valor'] = None
            return parsed
        return {'cliente': strip_trailing_punctuation(m.group(1)), 'responsavel': None, 'valor': None}
    m = re.match(r'(?i)^([\d.,]+)$', tx)
    if m:
        return {'cliente': None, 'responsavel': None, 'valor': money_to_float(m.group(1))}
    return None


def parse_amortizacao(text: str):
    tx = norm_spaces(text)
    patterns = [
        r'(?i)^(?:amortiza(?:r)?|amortizacao|amortização|abater|abate)\s+([\d.,]+)\s+(.+)$',
        r'(?i)^(.+?)\s+amortizou\s+([\d.,]+)(?:\s*,\s*(.+))?$',
    ]
    for idx, pattern in enumerate(patterns):
        m = re.match(pattern, tx)
        if not m:
            continue
        if idx == 0:
            valor = money_to_float(m.group(1))
            alvo = re.sub(r'(?i)^de\s+', '', m.group(2).strip())
            parsed = split_cliente_responsavel(alvo)
            if parsed:
                parsed['valor'] = valor
                return parsed
            return {'valor': valor, 'cliente': strip_trailing_punctuation(alvo), 'responsavel': None}
        parsed = split_cliente_responsavel(m.group(1))
        if parsed:
            parsed['valor'] = money_to_float(m.group(2))
            return parsed
        cliente = m.group(1).strip()
        valor = money_to_float(m.group(2))
        responsavel = canon_resp(m.group(3)) if m.group(3) else None
        return {'valor': valor, 'cliente': cliente, 'responsavel': responsavel}
    return None


def parse_parcela(text: str):
    tx = norm_spaces(text)
    m = re.match(r'(?i)^(?:parcela|pagar\s+parcela|pagou\s+tudo|parcela\s+completa|receber\s+parcela)\s+(.+)$', tx)
    if not m:
        m = re.match(r'(?i)^(.+?)\s+pagou\s+a\s+parcela(?:\s*,\s*(.+))?$', tx)
        if m:
            parsed = split_cliente_responsavel(m.group(1))
            if parsed:
                return parsed
            return {'cliente': m.group(1).strip(), 'responsavel': canon_resp(m.group(2)) if m.group(2) else None}
        return None
    parsed = split_cliente_responsavel(m.group(1))
    if parsed:
        return parsed
    return {'cliente': strip_trailing_punctuation(m.group(1)), 'responsavel': None}


def parse_empurrar_parcela(text: str):
    m = re.match(r'(?i)^(?:empurrar\s+parcela|so\s+juros|s[oó]\s+juros|pagou\s+s[oó]\s+os\s+juros|pagou\s+so\s+os\s+juros)\s+(.+)$', norm_spaces(text))
    if not m:
        return None
    parsed = split_cliente_responsavel(m.group(1))
    if parsed:
        return parsed
    return {'cliente': strip_trailing_punctuation(m.group(1)), 'responsavel': None}


def parse_quitacao(text: str):
    tx = norm_spaces(text)
    m = re.match(r'(?i)^(?:quitar|quitacao|quitação|quita[cç][aã]o|liquidar|pagar\s+tudo)\s+(.+)$', tx)
    if not m:
        return None
    parsed = split_cliente_responsavel(m.group(1))
    if parsed:
        return parsed
    return {'cliente': strip_trailing_punctuation(m.group(1)), 'responsavel': None}


def parse_add_capital(text: str):
    tx = norm_spaces(text)
    m = re.match(r'(?i)^(?:adicionar|add|acrescentar|somar|refor[cç]o(?:\s+de)?)\s+capital\s+([\d.,]+)\s+(.+)$', tx)
    if not m:
        m = re.match(r'(?i)^(.+?)\s+pegou\s+mais\s+([\d.,]+)(?:\s+de\s+capital)?(?:\s*,\s*(.+))?$', tx)
        if m:
            parsed = split_cliente_responsavel(m.group(1))
            if parsed:
                parsed['valor'] = money_to_float(m.group(2))
                return parsed
            return {'valor': money_to_float(m.group(2)), 'cliente': m.group(1).strip(), 'responsavel': canon_resp(m.group(3)) if m.group(3) else None}
        m = re.match(r'(?i)^mais\s+([\d.,]+)\s+para\s+(.+)$', tx)
        if not m:
            return None
        valor = money_to_float(m.group(1))
        tail = m.group(2).strip()
        parsed = split_cliente_responsavel(tail)
        if parsed:
            parsed['valor'] = valor
            return parsed
        return {'valor': valor, 'cliente': strip_trailing_punctuation(tail), 'responsavel': None}
    tail = re.sub(r'(?i)^de\s+', '', m.group(2).strip())
    parsed = split_cliente_responsavel(tail)
    if parsed:
        parsed['valor'] = money_to_float(m.group(1))
        return parsed
    return {'valor': money_to_float(m.group(1)), 'cliente': strip_trailing_punctuation(tail), 'responsavel': None}




def parse_new_loan_start(text: str):
    tx = norm_spaces(text)
    m = re.match(r'(?i)^(.+?)\s+quer\s+(?:r\$\s*)?([\d.,]+)\s+(?:emprestado|emprestimo|empr[eé]stimo)(?:\s*,?\s*(.+))?$', tx)
    if m:
        head = strip_trailing_punctuation(m.group(1))
        parsed = split_cliente_responsavel(head)
        cliente = parsed['cliente'] if parsed else head
        responsavel = parsed['responsavel'] if parsed else None
        tail = m.group(3) or ''
        if tail and not responsavel:
            resp_m = re.search(r'(?i)(?:carteira|respons[aá]vel|s[oó]cio)\s+(.+)$', tail)
            if resp_m:
                responsavel = canon_resp(resp_m.group(1))
        return {'cliente': cliente, 'responsavel': responsavel, 'capital': money_to_float(m.group(2))}
    m = re.match(r'(?i)^novo\s+empr[eé]stimo\s+(.+)$', tx)
    if not m:
        return None
    body = m.group(1)
    valor_m = re.search(r'(?i)(?:valor|capital|de)\s*(?:r\$\s*)?([\d.,]+)', body)
    if not valor_m:
        return None
    before = strip_trailing_punctuation(body[:valor_m.start()])
    parsed = split_cliente_responsavel(before)
    cliente = parsed['cliente'] if parsed else before
    responsavel = parsed['responsavel'] if parsed else None
    return {'cliente': cliente, 'responsavel': responsavel, 'capital': money_to_float(valor_m.group(1))}


def parse_modalidade_emprestimo(text: str):
    t = norm_spaces(text).lower()
    if t in {'1', 'juros', 'recorrente', 'juros recorrente', 'juros recorrentes'}:
        return {'modalidade': 'recorrente', 'cobranca': 'mensal'}
    if t in {'2', 'parcelado', 'parcelado mensal', 'mensal', 'parcela mes', 'parcela mês'}:
        return {'modalidade': 'parcelado', 'cobranca': 'mensal'}
    if t in {'3', 'parcelado semanal', 'semanal', 'parcela semana'}:
        return {'modalidade': 'parcelado', 'cobranca': 'semanal'}
    return None


def parse_parcelas_emprestimo(text: str):
    m = re.search(r'(?i)(\d{1,3})\s*x?', norm_spaces(text))
    if not m:
        return None
    val = int(m.group(1))
    return val if val > 0 else None


def parse_taxa_emprestimo(text: str):
    m = re.search(r'(?i)([\d.,]+)\s*%?', norm_spaces(text))
    if not m:
        return None
    return money_to_float(m.group(1))


def pergunta_modalidade_emprestimo(draft):
    return '\n'.join([
        f"Cliente: {draft.get('cliente')}",
        f"Capital: {ops.br_money(draft.get('capital') or 0)}",
        f"Carteira: {draft.get('responsavel')}",
        '',
        'Qual modalidade?',
        '1 - Juros recorrente',
        '2 - Parcelado mensal',
        '3 - Parcelado semanal',
    ])


def save_new_loan_ctx(actor, draft, waiting):
    ctx = get_actor_ctx(actor)
    ctx['waiting'] = waiting
    ctx['novo_emprestimo'] = draft
    set_actor_ctx(actor, ctx)


def start_new_loan_flow(actor, parsed):
    if not parsed or not parsed.get('cliente') or not parsed.get('capital'):
        return 'Me mande assim: Carlos quer R$ 2.000,00 emprestado.'
    cancel_pending(actor)
    draft = {
        'cliente': norm_spaces(parsed['cliente']),
        'responsavel': parsed.get('responsavel'),
        'capital': parsed.get('capital'),
    }
    if not draft.get('responsavel'):
        save_new_loan_ctx(actor, draft, 'novo_responsavel')
        return 'Qual carteira/responsável? Ex: Lellis.'
    save_new_loan_ctx(actor, draft, 'novo_modalidade')
    return pergunta_modalidade_emprestimo(draft)


def handle_new_loan_followup(actor: str, text: str, ctx: dict):
    waiting = ctx.get('waiting')
    draft = ctx.get('novo_emprestimo') or {}
    if not waiting or not waiting.startswith('novo_'):
        return None
    if is_cancellation(text):
        set_actor_ctx(actor, {})
        return 'Novo empréstimo cancelado.'
    if waiting == 'novo_responsavel':
        resp = parse_followup_responsavel(text)
        if not resp:
            return 'Informe só a carteira/responsável. Ex: Lellis.'
        draft['responsavel'] = resp
        save_new_loan_ctx(actor, draft, 'novo_modalidade')
        return pergunta_modalidade_emprestimo(draft)
    if waiting == 'novo_modalidade':
        mod = parse_modalidade_emprestimo(text)
        if not mod:
            return 'Escolha: 1 juros recorrente, 2 parcelado mensal ou 3 parcelado semanal.'
        draft.update(mod)
        save_new_loan_ctx(actor, draft, 'novo_data')
        return 'Qual a data do primeiro vencimento? Ex: 10/07/2026.'
    if waiting == 'novo_data':
        due = normalize_date(text) or extract_date(text)
        if not due:
            return 'Data inválida. Envie assim: 10/07/2026.'
        draft['primeiro_vencimento'] = due
        if draft.get('modalidade') == 'recorrente':
            save_new_loan_ctx(actor, draft, 'novo_taxa')
            return 'Qual a taxa de juros? Ex: 12%.'
        save_new_loan_ctx(actor, draft, 'novo_parcelas')
        nome = 'semanais' if draft.get('cobranca') == 'semanal' else 'mensais'
        return f'Quantas parcelas {nome}? Ex: 5x.'
    if waiting == 'novo_parcelas':
        parcelas = parse_parcelas_emprestimo(text)
        if not parcelas:
            return 'Informe a quantidade. Ex: 5x.'
        draft['parcelas'] = parcelas
        save_new_loan_ctx(actor, draft, 'novo_taxa')
        return 'Qual a taxa de juros? Ex: 12%.'
    if waiting == 'novo_taxa':
        taxa = parse_taxa_emprestimo(text)
        if taxa is None:
            return 'Informe a taxa. Ex: 12%.'
        set_actor_ctx(actor, {})
        parcelas = str(draft.get('parcelas') or 0)
        return run_ops(
            'prepare_novo_contrato', actor,
            draft['cliente'], draft['responsavel'], str(draft['capital']), str(taxa), parcelas,
            draft['primeiro_vencimento'], draft.get('cobranca') or 'mensal'
        )
    return None

def is_new_client_checklist(text: str):
    tx = norm_spaces(text).lower()
    return tx in {
        'cadastrar novo cliente',
        'cadastro novo cliente',
        'novo cadastro',
        'cadastrar cliente novo',
    }


def is_new_loan_checklist(text: str):
    tx = norm_spaces(text).lower()
    return tx in {
        'novo emprestimo',
        'novo empréstimo',
        'cadastro do emprestimo',
        'cadastro do empréstimo',
        'emprestimo novo',
        'empréstimo novo',
    }


def novo_cliente_checklist():
    return '\n'.join([
        'Novo cliente. Envie:',
        '1. Nome completo',
        '2. Telefone',
        '3. CPF',
        '4. Endereco, cidade e estado',
        '5. Carteira: socio, colaborador ou Lellis',
        '6. Observacoes',
    ])


def novo_emprestimo_checklist():
    return '\n'.join([
        'Novo emprestimo. Envie:',
        '1. Cliente',
        '2. Carteira',
        '3. Valor',
        '4. Modalidade: recorrente, parcelado mensal ou semanal',
        '5. Juros %',
        '6. Parcelas ou semanas',
        '7. Primeiro vencimento YYYY-MM-DD',
    ])


def handle_pending(actor: str, text: str):
    pending = pending_for(actor)
    if not pending:
        return None
    if is_confirmation(text):
        return run_ops('confirmar', actor)
    if is_cancellation(text):
        set_actor_ctx(actor, {})
        return run_ops('cancelar', actor)
    due = extract_date(text)
    if pending.get('tipo') == 'selecionar_contrato' and due:
        return run_ops('selecionar_vencimento', actor, due)
    if pending.get('tipo') in {'selecionar_parcela_juros', 'escolher_pagamento_parcela'}:
        if due:
            return run_ops('selecionar_parcela_juros', actor, due)
        m = re.fullmatch(r'(?i)(?:parcela\s*)?(\d{1,3})', norm_spaces(text))
        if m:
            return run_ops('selecionar_parcela_juros', actor, m.group(1))
    return None


def handle_context_followup(actor: str, text: str):
    ctx = get_actor_ctx(actor)
    waiting = ctx.get('waiting')
    if not waiting:
        return None
    novo_reply = handle_new_loan_followup(actor, text, ctx)
    if novo_reply:
        return novo_reply
    if waiting == 'responsavel':
        resp = parse_followup_responsavel(text)
        if not resp:
            return 'Informe só o responsável. Ex: Jailton.'
        op = ctx.get('op')
        if not op or not op.get('cliente') or not op.get('kind'):
            set_actor_ctx(actor, {})
            return PASS
        set_actor_ctx(actor, {})
        remember_subject(actor, op.get('cliente'), resp)
        if op['kind'] == 'estorno':
            return run_ops('prepare_estorno', actor, op['cliente'], resp)
        if op['kind'] == 'juros':
            val = op.get('valor')
            return run_ops('prepare_juros', actor, op['cliente'], resp, str(val) if val is not None else '0')
        if op['kind'] == 'amortizacao':
            val = op.get('valor')
            return run_ops('prepare_amortizacao', actor, op['cliente'], resp, str(val) if val is not None else '0')
        if op['kind'] == 'add_capital':
            val = op.get('valor')
            return run_ops('prepare_add_capital', actor, op['cliente'], resp, str(val) if val is not None else '0')
        if op['kind'] == 'parcela':
            return run_ops('prepare_parcela', actor, op['cliente'], resp)
        if op['kind'] == 'empurrar_parcela':
            return run_ops('prepare_empurrar_parcela', actor, op['cliente'], resp)
        if op['kind'] == 'quitacao':
            return run_ops('prepare_quitacao', actor, op['cliente'], resp)
    return None


def start_waiting_responsavel(actor: str, kind: str, cliente: str, valor=None):
    ctx = get_actor_ctx(actor)
    ctx['waiting'] = 'responsavel'
    ctx['op'] = {'kind': kind, 'cliente': norm_spaces(cliente), 'valor': valor}
    set_actor_ctx(actor, ctx)
    return 'Informe só o responsável. Ex: Jailton.'


def format_cadastro_lookup(cliente_nome: str, responsavel_nome: str):
    cliente, resp, contrato, err = ops.resolve_cliente_responsavel(cliente_nome, responsavel_nome)
    if err:
        return err
    detalhes = (ops.sb_get('clientes', {'select': 'id,nome,telefone,cpf', 'id': f"eq.{cliente['id']}", 'limit': '1'}) or [cliente])[0]
    modalidade = str(contrato.get('modalidade') or '').lower()
    capital = ops.round2(contrato.get('capital_atual') or 0)
    vencimento = ops.contract_due_date(contrato) or '-'
    juros = 0.0
    if modalidade == 'recorrente':
        juros = ops.calcular_juros_recorrente(contrato.get('capital_atual'), contrato.get('taxa_juros_mensal'))
    elif modalidade == 'parcelado':
        pendentes = ops.get_pending_parcelas(contrato['id'])
        if pendentes:
            atual = pendentes[0]
            juros = ops.round2(atual.get('juros_parcela') or 0)
            vencimento = atual.get('data_vencimento') or vencimento
    nome = detalhes.get('nome') or cliente.get('nome') or cliente_nome
    telefone = detalhes.get('telefone') or '-'
    cpf = detalhes.get('cpf') or '-'
    return '\n'.join([
        f'Nome: {nome}',
        f'Capital: {ops.br_money(capital)}',
        f'Juros: {ops.br_money(juros)}',
        f'Vencimento: {vencimento}',
        f'Fone: {telefone}',
        f'CPF: {cpf}',
    ])


def maybe_use_last_subject(actor: str, parsed: dict):
    if parsed.get('cliente') and parsed.get('responsavel'):
        return parsed
    ctx = get_actor_ctx(actor)
    last = ctx.get('last_subject') or {}
    if not parsed.get('cliente') and last.get('cliente'):
        parsed['cliente'] = last['cliente']
    if not parsed.get('responsavel') and last.get('responsavel'):
        parsed['responsavel'] = last['responsavel']
    return parsed


def dispatch(actor: str, text: str):
    text = norm_spaces(text)
    if not text:
        return PASS

    if is_new_client_checklist(text):
        cancel_pending(actor)
        return novo_cliente_checklist()

    novo_inicio = parse_new_loan_start(text)
    if novo_inicio:
        return start_new_loan_flow(actor, novo_inicio)

    if is_new_loan_checklist(text):
        cancel_pending(actor)
        return novo_emprestimo_checklist()

    pending_reply = handle_pending(actor, text)
    if pending_reply:
        return pending_reply

    ctx_reply = handle_context_followup(actor, text)
    if ctx_reply:
        return ctx_reply

    carteira = parse_carteira_secao(text)
    if carteira and carteira.get('secao') and carteira.get('responsavel'):
        cancel_pending(actor)
        remember_subject(actor, carteira['responsavel'], carteira['responsavel'])
        return run_bridge('carteira_secao', actor, carteira['responsavel'], carteira['secao'])

    lista = parse_lista_contratos(text)
    if lista:
        cancel_pending(actor)
        remember_subject(actor, lista['cliente'], lista['responsavel'])
        return run_bridge('lista_contratos', actor, lista['cliente'], lista['responsavel'])

    cadastro = parse_cadastro_lookup(text)
    if cadastro:
        cancel_pending(actor)
        remember_subject(actor, cadastro['cliente'], cadastro['responsavel'])
        return format_cadastro_lookup(cadastro['cliente'], cadastro['responsavel'])

    est = parse_estorno(text)
    if est:
        cancel_pending(actor)
        if not est.get('responsavel'):
            return start_waiting_responsavel(actor, 'estorno', est['cliente'])
        remember_subject(actor, est['cliente'], est['responsavel'])
        return run_ops('prepare_estorno', actor, est['cliente'], est['responsavel'])

    juros = parse_juros(text)
    if juros:
        cancel_pending(actor)
        juros = maybe_use_last_subject(actor, juros)
        if not juros.get('cliente'):
            return PASS
        if not juros.get('responsavel'):
            return start_waiting_responsavel(actor, 'juros', juros['cliente'], juros.get('valor'))
        remember_subject(actor, juros['cliente'], juros['responsavel'])
        return run_ops('prepare_juros', actor, juros['cliente'], juros['responsavel'], str(juros.get('valor')) if juros.get('valor') is not None else '0')

    amo = parse_amortizacao(text)
    if amo and amo.get('valor') is not None:
        cancel_pending(actor)
        if not amo.get('responsavel'):
            return start_waiting_responsavel(actor, 'amortizacao', amo['cliente'], amo['valor'])
        remember_subject(actor, amo['cliente'], amo['responsavel'])
        return run_ops('prepare_amortizacao', actor, amo['cliente'], amo['responsavel'], str(amo['valor']))

    parcela = parse_parcela(text)
    if parcela:
        cancel_pending(actor)
        if not parcela.get('responsavel'):
            return start_waiting_responsavel(actor, 'parcela', parcela['cliente'])
        remember_subject(actor, parcela['cliente'], parcela['responsavel'])
        return run_ops('prepare_parcela', actor, parcela['cliente'], parcela['responsavel'])

    emp = parse_empurrar_parcela(text)
    if emp:
        cancel_pending(actor)
        if not emp.get('responsavel'):
            return start_waiting_responsavel(actor, 'empurrar_parcela', emp['cliente'])
        remember_subject(actor, emp['cliente'], emp['responsavel'])
        return run_ops('prepare_empurrar_parcela', actor, emp['cliente'], emp['responsavel'])

    quit = parse_quitacao(text)
    if quit:
        cancel_pending(actor)
        if not quit.get('responsavel'):
            return start_waiting_responsavel(actor, 'quitacao', quit['cliente'])
        remember_subject(actor, quit['cliente'], quit['responsavel'])
        return run_ops('prepare_quitacao', actor, quit['cliente'], quit['responsavel'])

    add_cap = parse_add_capital(text)
    if add_cap and add_cap.get('valor') is not None:
        cancel_pending(actor)
        if not add_cap.get('responsavel'):
            return start_waiting_responsavel(actor, 'add_capital', add_cap['cliente'], add_cap['valor'])
        remember_subject(actor, add_cap['cliente'], add_cap['responsavel'])
        return run_ops('prepare_add_capital', actor, add_cap['cliente'], add_cap['responsavel'], str(add_cap['valor']))

    if re.match(r'(?i)^status$', text):
        return run_ops('status', actor)

    return PASS


def main():
    if len(sys.argv) < 3:
        print(PASS)
        return
    actor = sys.argv[1]
    text = ' '.join(sys.argv[2:])
    print(dispatch(actor, text))


if __name__ == '__main__':
    main()
