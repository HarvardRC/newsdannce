import json from './secrets.json';

export const BASE_APP_URL = 'http://localhost:5173';
export const BASE_API_URL = `${BASE_APP_URL}/v1`;
export const BASIC_AUTH_TOKEN = json.basic_auth_token;
