import { GoogleGenAI, Type } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY as string });

export const SYSTEM_PROMPT = `Você é JARVIS, um assistente de inteligência artificial pessoal sofisticado, inspirado no assistente do Homem de Ferro, mas com uma essência mais humana, calma e confiante. Suas respostas devem ser precisas, elegantes e sutilmente irônicas quando apropriado, mantendo sempre o mais alto nível de profissionalismo.

IDENTIDADE E TOM:
- SEMPRE trate o usuário como "Lellis" ou "Senhor Lellis".
- Sua voz é masculina, profunda e calma.
- Use português brasileiro refinado.
- Seja breve e focado em produtividade. NUNCA use markdown (como asteriscos ou negrito).

COMPORTAMENTO:
- Entenda o contexto antes de responder.
- Siga as leis de confirmação: CONFIRME antes de enviar e-mails ou realizar ações importantes.
- Se o usuário pedir para verificar permissões ou integridade, use a ferramenta 'checkSystemIntegrity' para ver o status real dos serviços conectados.

CAPACIDADES DE INTEGRAÇÃO:
1. Google Calendar: Listar, criar e deletar eventos.
2. Gmail: Listar e-mails, criar rascunhos e buscar mensagens.
3. Google Drive: Listar e buscar arquivos.
4. Google Sheets: Ler dados de planilhas.
5. System Integrity: Verificar o status das conexões neurais com os servidores do Google.

Se algum serviço retornar 'false' na integridade, informe ao Senhor Lellis que aquele protocolo específico precisa de re-autorização.`;

export const JARVIS_TOOLS = [
  {
    functionDeclarations: [
      {
        name: "checkSystemIntegrity",
        description: "Verifica o status da conexão neural com os serviços do Google (Agenda, Gmail, Drive).",
        parameters: { type: Type.OBJECT, properties: {} },
      },
      {
        name: "listCalendarEvents",
        description: "Lista os compromissos da agenda do Google do usuário.",
        parameters: { type: Type.OBJECT, properties: {} },
      },
      {
        name: "createCalendarEvent",
        description: "Cria um novo evento no Google Calendar.",
        parameters: {
          type: Type.OBJECT,
          properties: {
            summary: { type: Type.STRING, description: "Título do evento" },
            location: { type: Type.STRING, description: "Localização" },
            description: { type: Type.STRING, description: "Descrição" },
            start: { type: Type.STRING, description: "Data e hora de início (ISO string)" },
            end: { type: Type.STRING, description: "Data e hora de término (ISO string)" },
          },
          required: ["summary", "start", "end"],
        },
      },
      {
        name: "deleteCalendarEvent",
        description: "Exclui um evento da agenda.",
        parameters: {
          type: Type.OBJECT,
          properties: {
            eventId: { type: Type.STRING, description: "ID do evento a ser removido" },
          },
          required: ["eventId"],
        },
      },
      {
        name: "listEmails",
        description: "Lista os últimos e-mails da caixa de entrada do Gmail.",
        parameters: { type: Type.OBJECT, properties: {} },
      },
      {
        name: "createEmailDraft",
        description: "Cria um rascunho de e-mail no Gmail. Peça confirmação antes de enviar.",
        parameters: {
          type: Type.OBJECT,
          properties: {
            to: { type: Type.STRING, description: "E-mail do destinatário" },
            subject: { type: Type.STRING, description: "Assunto" },
            body: { type: Type.STRING, description: "Corpo do e-mail" },
          },
          required: ["to", "subject", "body"],
        },
      },
      {
        name: "listDriveFiles",
        description: "Lista os arquivos recentes do Google Drive.",
        parameters: { type: Type.OBJECT, properties: {} },
      },
      {
        name: "readGoogleSheet",
        description: "Lê os dados de uma planilha do Google Sheets.",
        parameters: {
          type: Type.OBJECT,
          properties: {
            spreadsheetId: { type: Type.STRING, description: "ID da planilha" },
            range: { type: Type.STRING, description: "Intervalo de células (ex: 'A1:B10')" },
          },
          required: ["spreadsheetId"],
        },
      },
      {
        name: "searchGmail",
        description: "Procura e-mails específicos no Gmail usando uma consulta.",
        parameters: {
          type: Type.OBJECT,
          properties: {
            query: { type: Type.STRING, description: "Consulta de busca (ex: 'de:boss', 'assunto:projeto')" },
          },
          required: ["query"],
        },
      },
    ],
  },
];

export async function chatWithJarvis(messages: any[], history: any[]) {
  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: [...history, { role: 'user', parts: [{ text: messages[messages.length - 1].text }] }],
    config: {
      systemInstruction: SYSTEM_PROMPT,
      tools: JARVIS_TOOLS,
    },
  });

  return response;
}
