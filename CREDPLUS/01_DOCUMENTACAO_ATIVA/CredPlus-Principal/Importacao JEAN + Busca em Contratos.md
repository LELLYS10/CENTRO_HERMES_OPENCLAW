# IMPORTACAO JEAN + BUSCA EM CONTRATOS

Data: 01/05/2026

## Objetivo

Registrar no Obsidian:

- importacao da planilha `JEAN - MAIO 2026`
- validacao dos numeros no painel
- implementacao da busca por nome ou telefone em `Contratos`
- observacao importante sobre a area `Familia`

## Origem da planilha

Arquivo usado:

- `/Users/lellisflaviooliveirasantos/Desktop/PLANILHAS 2026/JEAN - MAIO 2026.csv`

Colunas consideradas para entrada no painel:

- `DT. EMP.`
- `NOME`
- `FONEs`
- `DT. VENC`
- `Valor Emp.`

Coluna descartada para importacao:

- `LELLIS`

Motivo:

- no painel esse valor deve ser derivado automaticamente pela regra do sistema
- evita duplicidade e erro manual

## Regra entendida

- juros do contrato: `12%`
- comissao do `JEAN`: `25%` sobre os `juros recebidos`
- nao sobre capital
- nao sobre valor total do contrato

Perfil confirmado no painel:

- nome: `JEAN`
- grupo: `b`
- taxa_comissao: `0.25`

## Validacao antes da importacao

Estado inicial do `JEAN` no painel:

- `0 clientes`
- `0 contratos`

Resumo da planilha:

- `99 registros`
- `95 clientes unicos`
- `R$ 153.600,00` de capital total

Duplicidades tratadas como mesmo cliente:

- `CAMILLA SILVA`
- `CARLITO PAI`
- `NATALIA / NATHALIA` nos casos repetidos por mesmo telefone

Regra usada:

- mesmo `nome + telefone` = mesmo cliente
- contratos repetidos do mesmo cliente continuam como contratos separados

## Importacao executada

Destino:

- `credpluspainel.com`

Responsavel vinculado:

- `JEAN`

Modelo de contrato criado:

- `recorrente`

Parametros principais gravados:

- `taxa_juros_mensal = 0.12`
- `gera_comissao = true`
- `responsavel_id = JEAN`
- `capital_atual = capital_inicial`
- `proximo_vencimento = primeiro_vencimento`

## Resultado final da importacao

Criados:

- `95 clientes`
- `99 contratos`

Reaproveitados:

- `4 clientes` ja consolidados por repeticao na planilha

Total de capital inserido:

- `R$ 153.600,00`

Estado final confirmado no painel:

- `95 clientes`
- `99 contratos`
- `R$ 153.600,00`

Conclusao:

- o painel bateu com a planilha
- a importacao fechou redonda

## Validacao visual

Tela confirmada:

- `Contratos`

Filtro visual confirmado:

- `JEAN`

Contagem visivel no painel:

- `99 contratos`

## Busca implementada em Contratos

Necessidade identificada:

- `Clientes` ja tinha busca
- `Contratos` nao tinha

Implementacao feita:

- campo de busca por `nome ou telefone`
- busca funcionando em `Contratos`
- compatibilidade com:
  - filtro por status
  - filtro por responsavel
  - paginacao

Arquivo alterado:

- `/docker/credplus-app/app/app/(dashboard)/contratos/page.tsx`

Validacao tecnica:

- lint passou
- build passou
- container `credplus-app` foi recriado com sucesso

## Familia

Observacao muito importante:

- a area `Familia` existe no painel
- ela foi identificada visualmente no menu lateral
- ela e tratada como area reservada e particular

Decisao:

- nao implementar nada na area `Familia`
- nao alterar filtros ou regras especificas dela
- nao misturar dados do painel principal com `Familia`

Na implementacao da busca em `Contratos`:

- `Familia` nao foi mexida
- a busca foi feita somente no fluxo da tela `Contratos`

## Estado atual

Painel:

- no ar
- respondendo normal
- com importacao do `JEAN` concluida
- com busca em `Contratos` ativa

## Proximos passos possiveis

- validar a busca no uso real com nomes e telefones
- mapear gatilhos operacionais para Telegram
- documentar fluxo completo de contratos e recebimentos


## 2026-05-01 - Barra de Progressao em Familia
- Autorizado explicitamente pelo usuario aplicar a mesma barra visual de recuperacao em `Familia`.
- Implementacao reaproveita o componente compartilhado de lista de contratos.
- Barra fina abaixo do nome do cliente.
- Vermelha abaixo de 100% e verde a partir de 100%.
- Formula visual preservada: `(capital_recebido acumulado + juros_recebido acumulado) / capital_inicial`.
- Mudanca apenas visual; nenhuma regra financeira foi alterada.
- Build e deploy da VPS concluidos com sucesso apos ajuste de tipagem na pagina `familia/[id]`.


## 2026-05-01 - Ajuste JAILTON pela planilha da mesa
- Fonte de verdade usada: `PLANILHAS 2026/JAILTON - ABRIL - 2026.csv`.
- Painel do socio JAILTON foi ajustado para bater com a planilha em: `nome`, `fone`, `capital` e `vencimento`.
- Casos com cliente compartilhado foram desmembrados em novos cadastros para nao sobrescrever outro contrato: `JACQUELINE`, `JAILTON 02`, `LAYANE`, `RAFAEL OLIVEIRA`.
- Enderecos e demais campos existentes foram preservados quando possivel; CPFs/emails dos clones foram zerados para nao herdar identidade errada.
- Backup gerado na VPS: `/root/jailton_backup_20260502T001551Z.json`.

- Ajuste fino posterior no JAILTON: telefone da LAYANE confirmado e corrigido para `(63) 9 9930-9340`; JACQUELINE e RAFAEL revalidados com os dados enviados pelo usuario.

## 2026-05-01 - Correcao dashboard individual
- Corrigido bug no `dashboard` de `especial/admin` onde cards financeiros continuavam globais mesmo com filtro individual ativo.
- Agora `Juros / mes`, `Pro-labore` e metricas financeiras extras respeitam o `responsavel` selecionado em `LELLIS`, `Socios` e `Colaboradores`.
- Sem filtro: continua visao consolidada.
- Com filtro: passa a mostrar apenas os dados do dashboard individual selecionado.
- Nenhuma alteracao em `Familia`.

## Correcao Pro-labore no Dashboard
- Data: 2026-05-01
- Regra ajustada no dashboard principal:
  - `Pró-labore` aparece apenas em `Visão Geral`
  - Base de cálculo: soma dos `juros recebidos` de `Especial + Sócios + Colaboradores`
  - `Família` fica fora da base
  - Aplicação: `30%` sobre essa base global
- Em dashboards filtrados/individuais (`LELLIS`, `JAILTON`, colaboradores), o card de `Pró-labore` não deve aparecer.
- Arquivo ajustado em produção: `/docker/credplus-app/app/app/(dashboard)/dashboard/page.tsx`
- Ajuste adicional no dashboard: card `Comissões pagas` ficou exclusivo para dashboards de colaboradores.
- Regra aplicada:
  - não aparece em `Visão Geral`
  - não aparece em `Especial`
  - não aparece em `Sócios`
  - aparece quando o painel exibido é de `colaborador`
- Correção do card `Comissões pagas` no dashboard:
  - `Visão Geral`: mostra o total de comissões pagas no mês
  - filtro individual de `colaborador`: mostra quanto foi pago para ele no mês
  - `Sócios` e `Especial` individual: não exibem comissão como se fosse deles
  - ciclo mensal: a consulta usa apenas o mês corrente e reinicia automaticamente no mês seguinte
- Polimento visual no dashboard:
  - cards principais ganharam efeito de flutuação suave no hover
  - métricas extras do dashboard também flutuam no hover
  - sem alteração de cores
  - sem alteração de lógica
- Fluxo novo de cadastro público implementado:
  - botão `Fazer cadastro` na tela de login
  - rota pública `/cadastro`
  - envio cria `pré-cadastro` pendente na fila do admin `credplusemp@gmail.com`
  - notificador em tempo real passou a incluir `admin`
  - `Visão Geral` do painel mostra aviso quando houver pré-cadastros pendentes

## 2026-05-02 — Pré-cadastros por link
- Mantido o fluxo original de `Pré-cadastros -> Gerar Link -> /cadastro/[token]`.
- Ajustado o comportamento do link público após envio do formulário:
  - `pendente` ainda vazio: mostra o formulário normalmente.
  - `pendente` já preenchido e ainda não analisado: mostra `Em análise`.
  - `aprovado`: mostra `Cadastro aprovado`.
  - `rejeitado`: mostra `Cadastro recusado`.
- Reenvio do mesmo link após preenchimento agora retorna `409` com mensagem `Sua solicitação já foi enviada e está em análise.`.
- Na listagem do painel `Pré-cadastros`, os registros `aprovado` e `rejeitado` aparecem por até 7 dias após `processado_em`.
- Assunção conservadora aplicada: `pendentes` continuam visíveis sem corte automático, para evitar sumir com solicitações ainda não analisadas.

## 2026-05-02 — Extrato HTML para cobranca interna
- Adicionado botão `Extrato HTML` no dashboard, visível apenas para `especial/admin` quando o filtro estiver em um responsável dos grupos `a` (sócios) ou `b` (colaboradores).
- Nova rota interna: `/dashboard/extrato-html?responsavel=<id>`.
- O extrato HTML é somente de visualização e cobrança interna, sem alterar lógica financeira.
- Conteúdo atual do extrato:
  - cabeçalho `📋 EXTRATO NOME`
  - período `MES/ANO - Ref: dd/mm`
  - bloco `🔴 VENCIDOS` (une `critico` + `vencido`)
  - bloco `⚠️ VENCE HOJE`
  - `TOTAL PENDENTE`
- Regra de valores:
  - recorrente: mostra apenas juros do período
  - parcelado: mostra total da parcela pendente (`capital_parcela + juros_parcela`) com `Parc.XX.` no nome
- Não inclui `Família` e não mostra porcentagens no HTML.

## 2026-05-02 - Central de Saidas
- Implementado popup unico de saidas para o grupo especial/admin.
- No dashboard filtrado por socio ou colaborador, o botao abre 3 opcoes:
  - HTML Operacional
  - Recibo Termico
  - PDF Relatorio
- HTML operacional continua exclusivo para cobranca interna de socios e colaboradores.
- Recibo termico fica disponivel apos registrar um recebimento, em rota protegida `/recebimentos/[id]/recibo`.
- PDF relatorio ficou em `/api/dashboard/relatorio-pdf` com periodos: diario, semanal, mensal e anual.
- Percentuais ficam apenas no relatorio geral; nao aparecem no recibo do cliente.
- Familia nao foi tocado.

## 2026-05-02 - Correcao de links de pre-cadastro
- Revisado o fluxo de `Gerar Link` do pre-cadastro.
- `APP_BASE_URL` estava correto (`https://credpluspainel.com`).
- Endurecida a validacao publica do token para evitar falso `Link invalido` em links copiados por celular/WhatsApp.
- Agora o token publico eh normalizado com `trim + lowercase + decodeURIComponent` em:
  - `/cadastro/[token]`
  - `/api/pre-cadastros/publico/[token]`
- A geracao do link agora tambem normaliza o token e remove barra extra do `APP_BASE_URL`.
- Teste real confirmado com token publico em maiusculas: abriu corretamente no estado `Em analise`, em vez de `Link invalido`.
