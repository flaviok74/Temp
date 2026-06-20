import { config, graphBaseUrl } from './config.js';

const messagesUrl = `${graphBaseUrl}/${config.whatsapp.phoneNumberId}/messages`;

/**
 * Low-level helper that POSTs a payload to the WhatsApp Cloud API
 * messages endpoint and returns the parsed JSON response.
 */
async function postMessage(payload) {
  const res = await fetch(messagesUrl, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${config.whatsapp.token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ messaging_product: 'whatsapp', ...payload }),
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const detail = data?.error?.message || res.statusText;
    throw new Error(`WhatsApp API error (${res.status}): ${detail}`);
  }

  return data;
}

/**
 * Send a plain text message.
 * @param {string} to        Recipient phone number in international format, no '+'. e.g. "15551234567"
 * @param {string} body      Message text (max 4096 chars).
 * @param {boolean} [previewUrl=false]  Whether to render link previews.
 */
export function sendText(to, body, previewUrl = false) {
  return postMessage({
    to,
    type: 'text',
    text: { preview_url: previewUrl, body },
  });
}

/**
 * Send a pre-approved message template (required to start a conversation
 * outside the 24-hour customer-service window).
 * @param {string} to
 * @param {string} templateName
 * @param {string} [languageCode='en_US']
 * @param {Array}  [components=[]]  Template components (header/body params, buttons).
 */
export function sendTemplate(to, templateName, languageCode = 'en_US', components = []) {
  return postMessage({
    to,
    type: 'template',
    template: {
      name: templateName,
      language: { code: languageCode },
      ...(components.length ? { components } : {}),
    },
  });
}

/**
 * Send an image by public URL or by previously-uploaded media id.
 * @param {string} to
 * @param {{ link?: string, id?: string, caption?: string }} image
 */
export function sendImage(to, image) {
  return postMessage({ to, type: 'image', image });
}

/**
 * Send interactive reply buttons (max 3).
 * @param {string} to
 * @param {string} bodyText
 * @param {Array<{id: string, title: string}>} buttons
 */
export function sendButtons(to, bodyText, buttons) {
  return postMessage({
    to,
    type: 'interactive',
    interactive: {
      type: 'button',
      body: { text: bodyText },
      action: {
        buttons: buttons.map((b) => ({
          type: 'reply',
          reply: { id: b.id, title: b.title },
        })),
      },
    },
  });
}

/**
 * Mark an incoming message as read (blue ticks).
 * @param {string} messageId  The wamid from the incoming message.
 */
export function markAsRead(messageId) {
  return postMessage({ status: 'read', message_id: messageId });
}
