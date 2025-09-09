# Data Model for ReactorSync

## Data Subjects
- **Reactor**: ID, name, type (CANDU/SMR), location (lat/long), status (healthy/warning/unhealthy), health_score (0-100).
- **Telemetry**: Timestamp, reactor_id, metrics (flux: float, temp: float, pressure: float, vibration: float, tritium: float).
- **Fault**: ID, reactor_id, type (e.g., temp_spike), severity (yellow/red), description, timestamp.
- **KnowledgeBase**: Document embeddings (via pgvector) for Cohere searches.

## Schema (Platform-Independent)
- **Reactors**: PK(id), name(string), type(enum), lat(float), long(float), status(enum), health_score(float).
- **Telemetry**: PK(id), reactor_id(fk), timestamp(datetime), flux(float), temp(float), ... (indexes on timestamp/reactor_id).
- **Faults**: PK(id), reactor_id(fk), type(string), severity(enum), desc(text), timestamp(datetime).

## DDL Guidance
- Use SQLAlchemy migrations; add pgvector extension for embeddings.