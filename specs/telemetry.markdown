# Telemetry Specifications for ReactorSync

## Metrics and KPIs
- **Core Metrics**: Neutron flux (n/cm²/s, KPI: >1e13 healthy), core temp (°C, KPI: <350), pressure (MPa, KPI: 10-15), vibration (mm/s, KPI: <5), tritium (pCi/L, KPI: <1000).
- **KPIs**: Health Score (aggregate 0-100), Uptime (%), Anomaly Rate (per hour).

## Dashboards
- **Main**: Aggregate charts (e.g., fleet health pie).
- **Drill-Down**: Time series plots with thresholds (red lines for alerts).

## Time Series Handling
- **Frequency**: 1-min intervals; retention: 24 hours synthetic.
- **Anomalies**: Spikes/drifts; detection via thresholds or ML (Darts).

## Exposure
- **APIs**: Streaming via Kafka/WS; queried in UI/MCP.