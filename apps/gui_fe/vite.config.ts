import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
// DO NOT COMMIT THIS FILE
const AUTH_TOKEN = process.env.AUTH_TOKEN;
// https://vitejs.dev/config/
export default defineConfig({
  build: {
    emptyOutDir: true,
    sourcemap: true,
    rollupOptions: {
      output: {
        dir: './react-dist',
      },
    },
  },
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  // Run proxy server only if auth token is provided for development
  server: AUTH_TOKEN
    ? {
        proxy: {
          '/v1': {
            target:
              'https://rcood.rc.fas.harvard.edu/rnode/holy8a24108.rc.fas.harvard.edu/10790',
            // rewrite: (path) => path.replace(/^\/v1/, 'v1'), // replace everything preceeding /v1
            changeOrigin: true,
            secure: false,
            configure: (proxy, _options) => {
              proxy.on('start', () => {
                console.log('PROXY STARTED');
              });
              proxy.on('error', (err, _req, _res) => {
                console.log('proxy error', err);
              });
              proxy.on('proxyReq', (proxyReq, req, _res) => {
                console.log(
                  'Sending Request to the Target:',
                  req.method,
                  req.url
                );
                proxyReq.appendHeader('Authorization', `Basic ${AUTH_TOKEN}`);
              });
              proxy.on('proxyRes', (proxyRes, req, _res) => {
                console.log(
                  'Received Response from the Target:',
                  proxyRes.statusCode,
                  req.url
                );
              });
            },
          },
          '/static': {
            target:
              'https://rcood.rc.fas.harvard.edu/rnode/holy8a24108.rc.fas.harvard.edu/10790',

            rewrite: (path) => path.replace(/^\/v1/, 'static'),
            changeOrigin: true,
            secure: false,
            configure: (proxy, _options) => {
              proxy.on('error', (err, _req, _res) => {
                console.log('[static] proxy error', err);
              });
              proxy.on('proxyReq', (proxyReq, req, _res) => {
                console.log(
                  '[static] Sending Request to the Target:',
                  req.method,
                  req.url
                );
                proxyReq.appendHeader('Authorization', `Basic ${AUTH_TOKEN}`);
              });
              proxy.on('proxyRes', (proxyRes, req, _res) => {
                console.log(
                  '[static] Received Response from the Target:',
                  proxyRes.statusCode,
                  req.url
                );
              });
            },
          },
        },
      }
    : {},
});
