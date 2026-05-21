import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],

  // 👇 关键：代理配置，接收任意后端地址
  server: {
    port: 5173, // 你自己的前端端口
    proxy: {
      // 匹配所有 /api 开头的请求
      // '/api': {
      //   target: 'http://127.0.0.1:8000', // 你的后端地址
      //   changeOrigin: true, // ✅ 核心：开启跨域允许
      //   rewrite: (path) => path.replace(/^\/api/, '') // 去掉 /api 前缀
      // },
      '/llm': {
        target: 'http://localhost/v1', // 你的后端地址
        changeOrigin: true, // ✅ 核心：开启跨域允许
        rewrite: (path) => path.replace(/^\/llm/, '') // 去掉 /api 前缀
      }
    }
  }
})