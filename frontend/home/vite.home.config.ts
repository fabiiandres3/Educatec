import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    outDir: resolve(rootDir, "../../static/home_app"),
    emptyOutDir: true,
    rollupOptions: {
      input: resolve(rootDir, "home-app.html"),
      output: {
        entryFileNames: "home-app.js",
        chunkFileNames: "chunks/[name]-[hash].js",
        assetFileNames: (asset) => asset.name?.endsWith(".css") ? "home-app.css" : "assets/[name]-[hash][extname]",
      },
    },
  },
});