import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8888',
        changeOrigin: true,
        logLevel: 'debug' // 打印代理日志，确认是否转发
      }
    }
  }, plugins: [vue(),], resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  }, // 配置日志级别，减少提示信息
  logLevel: 'warn', // 只显示警告和错误信息，不显示信息性日志
})
