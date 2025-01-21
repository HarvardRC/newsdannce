import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

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
});
