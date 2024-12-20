import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import secrets from './src/secrets.json';

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

    // rollupOptions:
    // {
    //   output:{
    //     assetFileNames:'assets/config.js'
    //   }
    // }
  },
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/v1': {
        target: secrets.base_api_url,
        rewrite: (path) => path.replace(/^\/v1/, 'v1'),
        changeOrigin: false,
        secure: false,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request to the Target:', req.method, req.url);
            proxyReq.appendHeader(
              'Authorization',
              `Basic ${secrets.basic_auth_token}`
            );
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
        target: secrets.base_api_url,
        rewrite: (path) => path.replace(/^\/v1/, 'static'),
        changeOrigin: false,
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
            proxyReq.appendHeader(
              'Authorization',
              `Basic ${secrets.basic_auth_token}`
            );
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
  },
});
