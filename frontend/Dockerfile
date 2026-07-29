FROM node:22

WORKDIR /workspace/frontend

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 5173
