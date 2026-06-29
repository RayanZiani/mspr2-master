FROM node:20-alpine AS builder

WORKDIR /app

ARG VITE_API_BASE_URL=https://mspr2-master.onrender.com

COPY siege/frontend/package.json siege/frontend/package-lock.json ./
RUN npm ci

COPY siege/frontend/index.html siege/frontend/vite.config.js ./
COPY siege/frontend/src/ ./src/

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM nginx:alpine

COPY siege/frontend/nginx.main.conf /etc/nginx/nginx.conf
COPY siege/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx en non-root (SonarQube docker:S6471) — port 5173 ne nécessite pas de privilèges.
RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/log/nginx /etc/nginx/conf.d /etc/nginx/nginx.conf \
    && chmod -R a+rX /usr/share/nginx/html

USER nginx

EXPOSE 5173

CMD ["nginx", "-g", "daemon off;"]
