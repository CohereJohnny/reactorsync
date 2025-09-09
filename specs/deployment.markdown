# Deployment Specifications for ReactorSync

## Overview
ReactorSync is deployed locally via Docker Compose for development and scaled to production via Helm charts for Kubernetes. This ensures portability and scalability while maintaining demo simplicity.

## Docker Compose Setup
- **File**: docker-compose.yml in root.
- **Services**: frontend, backend, mcp-server, db, streaming, data-generator.
- **Networking**: Bridge network; expose frontend (3000), backend (8000), mcp (5222).
- **Volumes**: Persist db, streaming data.
- **Run**: `docker-compose up -d`; healthchecks for readiness.

## Helm Chart Setup
- **Structure**: /helm/reactorsync/ with Chart.yaml, values.yaml, templates/.
- **Deployments**: One per container; replicas: 1 (frontend), 2 (backend), 1 (mcp).
- **StatefulSets**: db, streaming for persistence.
- **Services**: ClusterIP for internal; Ingress for external (optional).
- **Scaling**: HPA on CPU (threshold: 70%) for backend/mcp.
- **Secrets**: ConfigMap for env vars; Secret for COHERE_API_KEY, SERVER_SECRET.
- **Install**: `helm install reactorsync ./helm/reactorsync`.

## Best Practices
- **Local**: Hot-reload for dev (mount src).
- **Prod**: Immutable images; rolling updates; monitor via kubectl.