import express from 'express';
import { config } from './config.js';
import {
  verifySignature,
  extractMessages,
  extractStatuses,
} from './webhook.js';
import { sendText, markAsRead } from './whatsapp.js';

const app = express();

// Capture the raw body so we can verify Meta's X-Hub-Signature-256 header.
app.use(
  express.json({
    verify: (req, _res, buf) => {
      req.rawBody = buf;
    },
  })
);

// Health check
app.get('/', (_req, res) => res.send('WhatsApp Cloud API integration is running'));

// ── Webhook verification (GET) ───────────────────────────────────────────
// Meta calls this once when you register the callback URL.
app.get('/webhook', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode === 'subscribe' && token === config.webhook.verifyToken) {
    console.log('Webhook verified');
    return res.status(200).send(challenge);
  }
  return res.sendStatus(403);
});

// ── Incoming events (POST) ───────────────────────────────────────────────
app.post('/webhook', async (req, res) => {
  if (!verifySignature(req)) {
    console.warn('Invalid webhook signature — rejecting');
    return res.sendStatus(401);
  }

  // Acknowledge immediately; Meta retries if we don't 200 within ~10s.
  res.sendStatus(200);

  try {
    for (const status of extractStatuses(req.body)) {
      console.log(`Status: ${status.status} for ${status.recipient_id}`);
    }

    for (const { message, contact } of extractMessages(req.body)) {
      const from = message.from;
      const name = contact?.profile?.name ?? 'there';

      // Mark the message as read (blue ticks).
      await markAsRead(message.id).catch(() => {});

      if (message.type === 'text') {
        const text = message.text.body;
        console.log(`Message from ${name} (${from}): ${text}`);
        await handleMessage(from, name, text);
      } else if (message.type === 'interactive') {
        const reply =
          message.interactive?.button_reply ??
          message.interactive?.list_reply;
        console.log(`Interactive reply from ${from}: ${reply?.id}`);
        await sendText(from, `You selected: ${reply?.title}`);
      } else {
        await sendText(from, `Received a ${message.type} message — thanks!`);
      }
    }
  } catch (err) {
    console.error('Error handling webhook:', err);
  }
});

/**
 * Simple echo/auto-reply handler. Replace this with your own logic
 * (route to a bot, an LLM, a ticketing system, etc.).
 */
async function handleMessage(from, name, text) {
  const trimmed = text.trim().toLowerCase();

  if (trimmed === 'hi' || trimmed === 'hello') {
    await sendText(from, `Hello ${name}! 👋 How can I help you today?`);
    return;
  }

  await sendText(from, `You said: "${text}"`);
}

app.listen(config.port, () => {
  console.log(`Server listening on port ${config.port}`);
  console.log(`Webhook URL path: /webhook`);
});
