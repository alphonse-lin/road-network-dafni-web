import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173, // 前端服务器端口
    proxy: {
      '/api': {
        target: 'http://localhost:3000', // 修改后端端口为3000
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path
      }
    }
  }
})