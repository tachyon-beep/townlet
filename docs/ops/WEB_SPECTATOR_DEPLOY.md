# Web Spectator Deployment Playbook

## Overview
This guide covers the operator steps to deploy the spectator web UI and telemetry gateway for demos.

## Prerequisites
- Container registry access (push `townlet-web` image).
- Kubernetes cluster with ingress (or Docker Compose for local runs).
- Access to telemetry shard (same host as Rich console).

## Build & Publish
```bash
# build frontend + gateway image
npm install --prefix townlet_web
npm run build --prefix townlet_web
podman build -f townlet_web/Dockerfile -t ghcr.io/townlet/townlet-web:demo .
podman push ghcr.io/townlet/townlet-web:demo
```

## Helm Deployment
```bash
helm upgrade --install townlet-web infra/helm/townlet-web \
  --set image.tag=demo \
  --set spectator.service.type=LoadBalancer \
  --set gateway.env.WEB_OBSERVER_ENABLED=1
```

## Docker Compose (local)
```bash
npm run build --prefix townlet_web
docker-compose -f docker-compose.spectator.yaml up
```

## Load Testing
```bash
k6 run docs/ops/k6_spectator_load.js \
  --env SPECTATOR_URL=http://localhost:8080/
```
Ensure p95 latency < 250 ms before demos.

## Caching Strategy
- Static assets served via Nginx with `Cache-Control: public, max-age=600`.
- WebSocket and metrics endpoints force `Cache-Control: no-store` to preserve real-time behaviour.

## Rollback
Refer to `docs/ops/WEB_UI_ROLLBACK_PLAN.md` for console fallback procedure.
