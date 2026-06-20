FROM node:20-alpine AS builder

WORKDIR /app

ARG VITE_API_BASE_URL=https://mspr2-master.onrender.com

COPY package.json package-lock.json ./
RUN npm ci

COPY . ./

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM node:20-alpine

WORKDIR /app

RUN npm install -g serve

COPY --from=builder /app/dist ./dist

EXPOSE 5173

CMD ["serve", "-s", "dist", "-l", "5173"]
