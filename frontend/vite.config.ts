import path from "node:path";
import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "src")
      }
    },
    server: {
      port: 5173,
      open: true,
      proxy: {
        "/api": {
          target: env.VITE_API_BASE_URL ?? "http://localhost:8000",
          changeOrigin: true
        },
        "/ws": {
          target: env.VITE_WS_BASE_URL ?? "ws://localhost:8000",
          ws: true
        }
      }
    }
  };
});

