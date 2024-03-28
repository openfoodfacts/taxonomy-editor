import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import viteTsconfigPaths from "vite-tsconfig-paths";
import svgr from "vite-plugin-svgr";

export default defineConfig({
  build: {
    outDir: "build",
  },
  plugins: [react(), viteTsconfigPaths(), svgr()],
  server: {
    port: parseInt(process.env.VITE_SERVER_PORT || "3000"),
    host: process.env.VITE_SERVER_HOST || "localhost",
  },
});
