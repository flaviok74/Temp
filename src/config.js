import 'dotenv/config';

function required(name) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

export const config = {
  port: Number(process.env.PORT) || 3000,
  graphApiVersion: process.env.GRAPH_API_VERSION || 'v21.0',
  whatsapp: {
    token: required('WHATSAPP_TOKEN'),
    phoneNumberId: required('WHATSAPP_PHONE_NUMBER_ID'),
    appSecret: process.env.WHATSAPP_APP_SECRET || '',
  },
  webhook: {
    verifyToken: required('WEBHOOK_VERIFY_TOKEN'),
  },
};

export const graphBaseUrl = `https://graph.facebook.com/${config.graphApiVersion}`;
