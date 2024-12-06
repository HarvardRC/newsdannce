// export const BASE_API_URL = import.meta.env.VITE_API_URL || `http://localhost:5173/v1`;
export const BASE_API_URL = (window as any).config.apiUrl

console.log("BASE_APP_URL", BASE_API_URL)

