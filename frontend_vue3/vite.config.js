import { fileURLToPath, URL } from 'node:url'
import { defineConfig, splitVendorChunkPlugin } from 'vite'
import vue from '@vitejs/plugin-vue'
import eslint from 'vite-plugin-eslint'
import vuetify from 'vite-plugin-vuetify'
import vueDevTools from 'vite-plugin-vue-devtools'
import pluginChecker from 'vite-plugin-checker'

export default defineConfig({
  server: {
    host: true,
    port: 80,
    watch: {
      usePolling: true,
      interval: 1000
    }
  },
  build: {
    sourcemap: true
  },
  plugins: [
    vue(),
    eslint({
      include: ['src/**/*.ts', 'src/**/*.vue'],
      exclude: ['node_modules', '**/*.test.ts'],
      lintOnStart: true,
      fix: true
    }),
    vuetify({
      styles: {
        configFile: 'src/styles/settings.scss'
      }
    }),
    vueDevTools(),
    splitVendorChunkPlugin(),
    pluginChecker({
      stylelint: {
        lintCommand: 'stylelint "./src/**/*.{css,scss,vue}"'
      }
    }),
    {
      name: 'full-reload',
      handleHotUpdate({ server }) {
        server.ws.send({ type: 'full-reload' });
        return [];
      }
    }
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
