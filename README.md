# WhatsApp Business Cloud API Integration

A minimal, production-shaped Node.js + Express integration with the official
[WhatsApp Business Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api).
It can **receive** messages via webhooks and **send** text, templates, images,
and interactive buttons.

## Features

- ✅ Webhook verification (GET) and event handling (POST)
- ✅ `X-Hub-Signature-256` signature validation
- ✅ Send text, template, image, and interactive-button messages
- ✅ Mark incoming messages as read
- ✅ Auto-reply / echo example handler
- ✅ Delivery & read status logging
- ✅ Zero third-party HTTP deps (uses native `fetch`, Node 18+)

## Project structure

```
src/
  config.js     Loads & validates environment variables
  whatsapp.js   Cloud API client (send messages, mark as read)
  webhook.js    Signature verification + payload parsing
  server.js     Express app: webhook routes + message handler
```

## Setup

1. **Install dependencies**

   ```bash
   npm install
   ```

2. **Create a Meta app** with the WhatsApp product at
   <https://developers.facebook.com/>. From **WhatsApp → API Setup** grab:
   - a **temporary access token** (or create a permanent one via a System User)
   - the **Phone number ID**
   - your **App Secret** (App → Settings → Basic)

3. **Configure environment**

   ```bash
   cp .env.example .env
   # then edit .env with your values
   ```

4. **Run**

   ```bash
   npm run dev    # auto-restart on changes
   # or
   npm start
   ```

## Exposing the webhook

Meta needs a public HTTPS URL. For local development, tunnel it:

```bash
npx localtunnel --port 3000
# or: ngrok http 3000
```

Then in the Meta dashboard under **WhatsApp → Configuration → Webhook**:

- **Callback URL:** `https://<your-tunnel>/webhook`
- **Verify token:** the same value as `WEBHOOK_VERIFY_TOKEN` in your `.env`
- Subscribe to the **`messages`** field.

## Sending a message from code

```js
import { sendText, sendTemplate, sendButtons } from './src/whatsapp.js';

// Plain text (only allowed within the 24h customer-service window)
await sendText('15551234567', 'Hello from the Cloud API!');

// Template (required to initiate a conversation)
await sendTemplate('15551234567', 'hello_world', 'en_US');

// Interactive buttons
await sendButtons('15551234567', 'Pick one:', [
  { id: 'yes', title: 'Yes' },
  { id: 'no', title: 'No' },
]);
```

> **Note:** Recipient numbers use international format **without** a `+`
> (e.g. `15551234567`). To message a user first (outside the 24-hour window)
> you must use a pre-approved **template**.

## Security notes

- Keep `WHATSAPP_TOKEN` and `WHATSAPP_APP_SECRET` secret — never commit `.env`.
- Signature verification is enabled automatically when `WHATSAPP_APP_SECRET`
  is set; leave it blank only for local testing.

## License

MIT
