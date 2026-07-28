FROM node:22

WORKDIR /workspace/frontend

COPY package*.json ./

RUN npm ci

COPY . .

EXPOSE 5173
