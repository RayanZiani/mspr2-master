FROM node:20-alpine AS builder

WORKDIR /app

# Argument de build pour l'URL de l'API
ARG VITE_API_BASE_URL=https://mspr2-master.onrender.com

# Copie les fichiers de dépendances depuis siege/frontend (contexte Docker = racine)
COPY siege/frontend/package.json siege/frontend/package-lock.json ./
RUN npm ci

# Copie le code source depuis siege/frontend
COPY siege/frontend/ ./

# Build l'application pour la production avec la variable d'environnement
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Stage 2 : Serveur de production léger
FROM node:20-alpine

WORKDIR /app

# Installe 'serve' pour servir les fichiers statiques
RUN npm install -g serve

# Copie les fichiers buildés depuis le stage builder
COPY --from=builder /app/dist ./dist

# Expose le port 5173
EXPOSE 5173

# Sert les fichiers statiques
CMD ["serve", "-s", "dist", "-l", "5173"]
