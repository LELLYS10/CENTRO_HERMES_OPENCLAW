import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import { google } from 'googleapis';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  const oauth2Client = new google.auth.OAuth2(
    process.env.GOOGLE_CLIENT_ID,
    process.env.GOOGLE_CLIENT_SECRET,
    `${process.env.APP_URL}/auth/callback`
  );

  // Auth Routes
  app.get('/api/auth/url', (req, res) => {
    const url = oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/userinfo.profile',
      ],
      prompt: 'consent',
    });
    res.json({ url });
  });

  app.get('/auth/callback', async (req, res) => {
    const { code } = req.query;
    try {
      const { tokens } = await oauth2Client.getToken(code as string);
      res.send(`
        <html>
          <body style="background: #020806; color: #00FF9C; font-family: monospace; display: flex; align-items: center; justify-content: center; height: 100vh;">
            <script>
              if (window.opener) {
                window.opener.postMessage({ 
                  type: 'OAUTH_AUTH_SUCCESS', 
                  tokens: ${JSON.stringify(tokens)} 
                }, '*');
                window.close();
              } else {
                window.location.href = '/';
              }
            </script>
            <div style="text-align: center;">
              <h1>PROTOCOLO OAUTH CONCLUÍDO</h1>
              <p>Sincronizando neural link com JARVIS...</p>
            </div>
          </body>
        </html>
      `);
    } catch (error) {
      console.error('Auth Error:', error);
      res.status(500).send('Authentication failed');
    }
  });

  // Unified Google API Proxy
  app.post('/api/google/proxy', async (req, res) => {
    const { tokens, service, action, data } = req.body;
    
    if (!tokens || !tokens.access_token) {
      return res.status(401).json({ error: 'Sincronização necessária.' });
    }

    try {
      oauth2Client.setCredentials(tokens);
      
      if (service === 'system') {
        if (action === 'integrity') {
          const status: any = { calendar: false, gmail: false, drive: false };
          try {
            const calendar = google.calendar({ version: 'v3', auth: oauth2Client });
            await calendar.calendarList.list({ maxResults: 1 });
            status.calendar = true;
          } catch (e) {}
          try {
            const gmail = google.gmail({ version: 'v1', auth: oauth2Client });
            await gmail.users.getProfile({ userId: 'me' });
            status.gmail = true;
          } catch (e) {}
          try {
            const drive = google.drive({ version: 'v3', auth: oauth2Client });
            await drive.about.get({ fields: 'user' });
            status.drive = true;
          } catch (e) {}
          return res.json(status);
        }
      }

      if (service === 'calendar') {
        const calendar = google.calendar({ version: 'v3', auth: oauth2Client });
        switch (action) {
          case 'list':
            const resp = await calendar.events.list({ calendarId: 'primary', timeMin: new Date().toISOString(), maxResults: 10, singleEvents: true, orderBy: 'startTime' });
            return res.json(resp.data.items || []);
          case 'create':
            const createResp = await calendar.events.insert({ calendarId: 'primary', requestBody: data });
            return res.json(createResp.data);
          case 'delete':
            await calendar.events.delete({ calendarId: 'primary', eventId: data.eventId });
            return res.json({ success: true });
        }
      }

      if (service === 'gmail') {
        const gmail = google.gmail({ version: 'v1', auth: oauth2Client });
        switch (action) {
          case 'list':
            const list = await gmail.users.messages.list({ userId: 'me', maxResults: 10, q: data?.q });
            const messages = await Promise.all((list.data.messages || []).map(async (m) => {
              const details = await gmail.users.messages.get({ userId: 'me', id: m.id! });
              const subject = details.data.payload?.headers?.find(h => h.name === 'Subject')?.value;
              const from = details.data.payload?.headers?.find(h => h.name === 'From')?.value;
              return { id: m.id, subject, from, snippet: details.data.snippet, date: details.data.internalDate };
            }));
            return res.json(messages);
          case 'draft':
            const draft = await gmail.users.drafts.create({ userId: 'me', requestBody: { message: { raw: Buffer.from(`To: ${data.to}\r\nSubject: ${data.subject}\r\n\r\n${data.body}`).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '') } } });
            return res.json(draft.data);
          case 'search':
            const searchRes = await gmail.users.messages.list({ userId: 'me', q: data.query, maxResults: 5 });
            return res.json(searchRes.data.messages || []);
        }
      }

      if (service === 'drive') {
        const drive = google.drive({ version: 'v3', auth: oauth2Client });
        const list = await drive.files.list({ 
          pageSize: 10, 
          fields: 'files(id, name, mimeType, modifiedTime)',
          q: data?.q || "trashed = false" 
        });
        return res.json(list.data.files);
      }

      if (service === 'sheets') {
        const sheets = google.sheets({ version: 'v4', auth: oauth2Client });
        const response = await sheets.spreadsheets.values.get({
          spreadsheetId: data.spreadsheetId,
          range: data.range || 'A1:Z100',
        });
        return res.json(response.data.values);
      }

      res.status(400).send('Action or Service not supported in proxy');
    } catch (error) {
      console.error('Google Proxy Error:', error);
      res.status(500).json({ error: 'Operation failed' });
    }
  });

  // Vite Middleware
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Jarvis core active on http://localhost:${PORT}`);
  });
}

startServer();
