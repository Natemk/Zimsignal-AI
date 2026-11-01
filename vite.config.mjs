import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "node:path";

export default defineConfig({
  root: resolve(process.cwd(), "web"),
  envDir: process.cwd(),
  plugins: [react()],
  server: {
    host: "localhost",
    port: 5173,
    strictPort: true,
    proxy: {
      "/chat": "http://127.0.0.1:8000",
    },
  },
  build: {
    outDir: resolve(process.cwd(), "dist"),
    emptyOutDir: true,
  },
});