FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev
COPY src ./src
COPY docs ./docs
ENV PORT=8003
EXPOSE 8003
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost:8003/ms3/health || exit 1
CMD ["node", "src/server.js"]
