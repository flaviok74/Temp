import crypto from 'node:crypto';
import { config } from './config.js';

/**
 * Validate the X-Hub-Signature-256 header Meta sends with every webhook.
 * Requires the raw (unparsed) request body, captured via express.json's
 * `verify` callback. Returns true when no app secret is configured (dev mode).
 */
export function verifySignature(req) {
  if (!config.whatsapp.appSecret) return true; // signature check disabled

  const signature = req.get('x-hub-signature-256');
  if (!signature || !req.rawBody) return false;

  const expected =
    'sha256=' +
    crypto
      .createHmac('sha256', config.whatsapp.appSecret)
      .update(req.rawBody)
      .digest('hex');

  const a = Buffer.from(signature);
  const b = Buffer.from(expected);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

/**
 * Flatten a WhatsApp webhook body into a simple list of message + contact
 * objects so handlers don't have to walk the nested entry/changes structure.
 *
 * @returns {Array<{ message: object, contact: object|undefined, phoneNumberId: string }>}
 */
export function extractMessages(body) {
  const out = [];
  for (const entry of body?.entry ?? []) {
    for (const change of entry?.changes ?? []) {
      const value = change?.value;
      const messages = value?.messages ?? [];
      const contact = value?.contacts?.[0];
      const phoneNumberId = value?.metadata?.phone_number_id;
      for (const message of messages) {
        out.push({ message, contact, phoneNumberId });
      }
    }
  }
  return out;
}

/**
 * Extract delivery/read status updates (sent, delivered, read, failed).
 */
export function extractStatuses(body) {
  const out = [];
  for (const entry of body?.entry ?? []) {
    for (const change of entry?.changes ?? []) {
      for (const status of change?.value?.statuses ?? []) {
        out.push(status);
      }
    }
  }
  return out;
}
