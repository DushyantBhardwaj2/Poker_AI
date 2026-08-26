import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import vercel from '@astrojs/vercel';

// https://astro.build/config
export default defineConfig({
  output: 'server',
  adapter: vercel({
    webAnalytics: {
      enabled: false, // Set to true only after enabling in Vercel Dashboard
    },
  }),
  integrations: [
    react()
  ],
  devToolbar: {
    enabled: false
  },
  vite: {
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
        // wakeupBackend() in src/lib/api.ts derives this from the API base, so
        // with no PUBLIC_API_URL set it resolves to a same-origin /health.
        // Without this entry the warmup ping 404s against the Astro dev server
        // instead of reaching the API.
        '/health': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        }
      }
    }
  }
});

