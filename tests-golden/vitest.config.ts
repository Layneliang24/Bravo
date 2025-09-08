import { defineConfig } from "vitest/config";
import { resolve } from "path";

export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./vitest.setup.ts"],
    exclude: ["**/e2e/**", "**/node_modules/**"],
  },
  resolve: {
    alias: {
      "@": resolve(__dirname, "../frontend/src"),
    },
  },
});
