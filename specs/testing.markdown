# Testing Specifications for ReactorSync

## Overview
Testing ensures ReactorSync’s reliability for demo scenarios, covering frontend, backend, and MCP interactions.

## Test Types
- **Unit**: Pytest for backend (API logic, data generation); Jest for frontend components.
- **Integration**: Test API-WebSocket flows; Cohere pipeline (mocked API calls).
- **E2E**: Cypress for UI flows (e.g., toggle views, trigger anomaly).
- **MCP**: Test tool calls via MCP Inspector (streamable-http).

## Key Scenarios
- Dashboard toggles update without errors.
- Telemetry charts render with synthetic data.
- Anomaly triggers change status to yellow/red.
- AI diagnostics return valid JSON via MCP.

## Tools
- **Backend**: Pytest, pytest-asyncio, httpx (mock Cohere).
- **Frontend**: Jest, React Testing Library, Cypress.
- **Coverage**: 80% for backend; 60% for frontend (demo-focused).