// vite.config.js
import { defineConfig } from 'vite'

export default defineConfig({
  publicDir: 'images',   // Vite servira ton dossier images comme dossier public
  server: {
    allowedHosts: [
      '.gitpod.io'       // Autorise tous les sous-domaines Gitpod (pratique)
    ]
  }
})
