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

COPY siege/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 5173

CMD ["nginx", "-g", "daemon off;"]
