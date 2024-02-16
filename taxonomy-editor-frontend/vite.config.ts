import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import viteTsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  build: {
    outDir: "build",
  },
  plugins: [react(), viteTsconfigPaths()],
  server: {
    port: parseInt(process.env.VITE_SERVER_PORT || "3000"),
    host: process.env.VITE_SERVER_HOST || "localhost",
    open: true,
  },
});
