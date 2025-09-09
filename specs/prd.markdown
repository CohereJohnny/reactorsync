# Product Requirements Document (PRD) for ReactorSync

## Executive Summary
ReactorSync is a Generative AI-enabled Nuclear Reactor Management Application designed to demonstrate collaborative excellence in managing CANDU reactors and Small Modular Reactors (SMRs), aligned with Conexus Nuclear's mission of "excellence through collaboration." This demo-focused tool simulates reactor oversight, predictive maintenance, and SMR deployment planning using Cohere's foundation models (Command A for generation, Embed for semantic search, Rerank for prioritization). The application emphasizes a containerized architecture for local Docker Compose development and scalable production deployment via Helm charts. Key features include a multi-view dashboard (card, table, map) with drill-down capabilities, anomaly simulation for demos, and MCP-exposed APIs for AI agents. Security is deprioritized for demo purposes, but separation of concerns is maintained between frontend, backend, and AI layers.

## Product Vision
To empower nuclear professionals (operators, engineers, managers) with an intuitive, AI-augmented platform that simulates real-world reactor management challenges, fostering knowledge sharing and innovation in line with Conexus Nuclear's global collaboration model. The demo narrative: Start with healthy reactors, trigger anomalies/faults, diagnose via UI or AI agents, restore to normal—highlighting AI’s role in reducing downtime and risks.

## Target Audience and Personas
- **Primary Users**: Nuclear operators, maintenance engineers, SMR project managers, compliance officers (detailed in personas.md).
- **Demo Audience**: Conexus members, stakeholders, potential partners showcasing AI in nuclear tech.

## Key Features and Functionality
### Core Dashboard
- Switchable views: Card (visual summaries), Table (sortable data), Map (geospatial with status markers).
- Reactor Status: Red/Yellow/Green indicators based on health metrics.
- Drill-Down: Per-reactor views with telemetry charts, fault logs, AI diagnostics.

### Predictive Maintenance
- Real-time telemetry monitoring (e.g., neutron flux, core temperature).
- Anomaly detection and alerts using synthetic data streams.

### SMR Deployment Simulator
- Generative scenarios for site selection, planning, and regulatory checklists.

### AI Integration
- **Cohere Models**: Command A for reports/plans, Embed/Rerank for knowledge base queries.
- **MCP Server**: Exposes all APIs as tools for building AI agents (e.g., troubleshooting agents).

### Demo Admin Tools
- Trigger anomalies/faults to simulate unhealthy states.
- Reset to healthy defaults.

### Non-Functional Requirements
- **Performance**: Handle 10-20 simulated reactors with real-time updates (<5s latency).
- **Scalability**: Containerized for local Docker Compose; Helm for Kubernetes.
- **Usability**: Intuitive UI, mobile-responsive.
- **Data**: Synthetic only; no real nuclear data.
- **Out of Scope**: Real integrations (e.g., live sensors), full security (e.g., auth beyond demo).

## Success Metrics
- **Demo Engagement**: Time to diagnose/resolve simulated faults (<2 min via AI).
- **AI Utility**: Reduction in manual analysis (e.g., 50% via generative reports).
- **Adoption**: Positive feedback from Conexus-like personas on collaboration features.

## Dependencies and Risks
- **Dependencies**: Cohere API keys, Docker/Kubernetes environments.
- **Risks**: AI hallucinations (mitigate with Rerank); demo data realism (use physics-informed synthetics).
- **Assumptions**: Users have basic nuclear knowledge; demo runs on standard hardware.

## Release Plan
- **MVP**: Dashboard with basic views, telemetry, anomaly triggers.
- **Iterations**: Add SMR simulator, full MCP exposure.
- **Timeline**: Prototype in 2 weeks; full demo in 1 month (vibe coding focused).