FROM node:20-alpine AS build
WORKDIR /app/frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY --from=build /app/frontend/dist ./frontend/dist
ENV PORT=5000
CMD gunicorn -b 0.0.0.0:${PORT} backend.app:app
