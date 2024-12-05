export const BASE_APP_URL =
  import.meta.env.GUI_APP_URL || 'http://localhost:5173';
export const BASE_API_URL = import.meta.env.GUI_API_URL || `${BASE_APP_URL}/v1`;
