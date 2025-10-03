# Stage 1: build spectator frontend
FROM node:20-alpine AS web-build
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN npm install --no-audit --no-fund
COPY . .
RUN npm run build

# Stage 2: build FastAPI gateway
FROM python:3.12-slim AS api-build
WORKDIR /app
COPY ../pyproject.toml ../README.md ./
RUN pip install --no-cache-dir "townlet[dev] @ ../" fastapi uvicorn[standard]

# Stage 3: runtime image combining gateway + static assets
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PORT=8000
COPY --from=api-build /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=api-build /usr/local/bin /usr/local/bin
COPY --from=web-build /app/dist /app/static
COPY ../src ./src
CMD ["uvicorn", "townlet.web.gateway:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
