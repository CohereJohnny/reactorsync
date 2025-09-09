# Container Specifications for ReactorSync

## Container List
- **frontend-container**: Node.js/NextJS; ports: 3000; volumes: /app/src; depends_on: backend.
- **backend-container**: Python/FastAPI; ports: 8000; env: COHERE_API_KEY; depends_on: db, streaming.
- **mcp-server-container**: Python with north-mcp-python-sdk; ports: 5222; env: SERVER_SECRET; depends_on: backend.
- **db-container**: Postgres/pgvector; ports: 5432; volumes: /var/lib/postgresql/data.
- **streaming-container**: Kafka (bitnami/kafka); ports: 9092; volumes: /bitnami/kafka.
- **data-generator-container**: Python scripts; runs loops; depends_on: streaming.

## Docker Compose Guidance
- **YAML**: Services with build contexts; networks: default bridge.
- **Local Run**: `docker-compose up -d`; healthchecks for readiness.

## Helm Chart Guidance
- **Charts**: Separate YAML per deployment (e.g., backend-deployment.yaml); values.yaml for configs (e.g., replicas: 1).
- **Scaling**: HPA on CPU; StatefulSets for db/streaming.