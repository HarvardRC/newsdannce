export const BASE_API_URL =
  import.meta.env.MODE == 'development'
    ? 'http://localhost:7901/v1'
    : (window as any).config.apiUrl;

console.log('BASE_APP_URL', BASE_API_URL);
