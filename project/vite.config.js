// vite.config.js
import { defineConfig } from "vite";
import { resolve } from "path";

export default defineConfig({
  // (facultatif) base: "/",  // Netlify par défaut
  build: {
    outDir: "dist",
    rollupOptions: {
      // Déclare TOUTES tes pages HTML (ajoute-en si besoin)
      input: {
        index:        resolve(__dirname, "index.html"),
        produits:     resolve(__dirname, "produits.html"),
        produit:      resolve(__dirname, "produit.html"),
        panier:       resolve(__dirname, "panier.html"),
        checkout:     resolve(__dirname, "checkout.html"),
        confirmation: resolve(__dirname, "confirmation.html"),
        admin:        resolve(__dirname, "admin.html"),
      },
    },
  },
  // très important: laisse le publicDir par défaut (= "public")
  publicDir: "public",
  // Le bloc "server.allowedHosts" ne sert qu'en dev; tu peux le retirer
});
