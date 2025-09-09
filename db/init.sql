-- ReactorSync Database Initialization Script
-- This script sets up the initial database schema and extensions

-- Create the pgvector extension for vector embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Create enum types
CREATE TYPE reactor_status AS ENUM ('healthy', 'warning', 'unhealthy');
CREATE TYPE reactor_type AS ENUM ('CANDU', 'SMR', 'PWR', 'BWR');
CREATE TYPE fault_severity AS ENUM ('yellow', 'red');

-- Create reactors table
CREATE TABLE IF NOT EXISTS reactors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    type reactor_type NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    status reactor_status DEFAULT 'healthy',
    health_score FLOAT DEFAULT 100.0 CHECK (health_score >= 0 AND health_score <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create telemetry table
CREATE TABLE IF NOT EXISTS telemetry (
    id SERIAL PRIMARY KEY,
    reactor_id INTEGER NOT NULL REFERENCES reactors(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    neutron_flux FLOAT,
    core_temperature FLOAT,
    pressure FLOAT,
    vibration FLOAT,
    tritium_level FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create faults table
CREATE TABLE IF NOT EXISTS faults (
    id SERIAL PRIMARY KEY,
    reactor_id INTEGER NOT NULL REFERENCES reactors(id) ON DELETE CASCADE,
    fault_type VARCHAR(255) NOT NULL,
    severity fault_severity NOT NULL,
    description TEXT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Create knowledge_base table for AI embeddings
CREATE TABLE IF NOT EXISTS knowledge_base (
    id SERIAL PRIMARY KEY,
    document_name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI/Cohere embedding dimension
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_telemetry_reactor_id ON telemetry(reactor_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry(timestamp);
CREATE INDEX IF NOT EXISTS idx_telemetry_reactor_timestamp ON telemetry(reactor_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_faults_reactor_id ON faults(reactor_id);
CREATE INDEX IF NOT EXISTS idx_faults_timestamp ON faults(timestamp);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);

-- Insert sample reactor data
INSERT INTO reactors (name, type, latitude, longitude, status, health_score) VALUES
    ('Bruce-A Unit 1', 'CANDU', 44.3167, -81.6000, 'healthy', 95.2),
    ('Bruce-A Unit 2', 'CANDU', 44.3167, -81.6000, 'healthy', 92.8),
    ('Bruce-B Unit 5', 'CANDU', 44.3167, -81.6000, 'warning', 78.5),
    ('Darlington Unit 1', 'CANDU', 43.8833, -78.7167, 'healthy', 96.1),
    ('Darlington Unit 2', 'CANDU', 43.8833, -78.7167, 'warning', 82.3),
    ('Pickering Unit 5', 'CANDU', 43.8108, -79.0653, 'healthy', 89.7),
    ('Pickering Unit 6', 'CANDU', 43.8108, -79.0653, 'unhealthy', 65.2),
    ('SMR Prototype Alpha', 'SMR', 45.4215, -75.6972, 'healthy', 98.5),
    ('SMR Prototype Beta', 'SMR', 45.4215, -75.6972, 'healthy', 94.3),
    ('SMR Demo Unit', 'SMR', 49.2827, -123.1207, 'warning', 76.9)
ON CONFLICT (name) DO NOTHING;

-- Insert sample telemetry data for the last hour
DO $$
DECLARE
    reactor_record RECORD;
    time_point TIMESTAMP WITH TIME ZONE;
    i INTEGER;
BEGIN
    FOR reactor_record IN SELECT id FROM reactors LOOP
        FOR i IN 0..59 LOOP
            time_point := NOW() - INTERVAL '1 hour' + (i * INTERVAL '1 minute');
            
            INSERT INTO telemetry (
                reactor_id, 
                timestamp, 
                neutron_flux, 
                core_temperature, 
                pressure, 
                vibration, 
                tritium_level
            ) VALUES (
                reactor_record.id,
                time_point,
                1.2e13 + (RANDOM() - 0.5) * 0.1e13, -- Neutron flux
                280 + (RANDOM() - 0.5) * 20,         -- Core temperature (°C)
                12.5 + (RANDOM() - 0.5) * 2,         -- Pressure (MPa)
                2.1 + (RANDOM() - 0.5) * 0.5,        -- Vibration (mm/s)
                450 + (RANDOM() - 0.5) * 100         -- Tritium level (pCi/L)
            );
        END LOOP;
    END LOOP;
END $$;

-- Insert sample fault data
INSERT INTO faults (reactor_id, fault_type, severity, description, timestamp) VALUES
    (3, 'temperature_spike', 'yellow', 'Core temperature exceeded normal operating range', NOW() - INTERVAL '30 minutes'),
    (5, 'pressure_anomaly', 'yellow', 'Primary coolant pressure fluctuation detected', NOW() - INTERVAL '2 hours'),
    (7, 'vibration_high', 'red', 'Excessive vibration in primary pump', NOW() - INTERVAL '1 hour'),
    (10, 'flux_instability', 'yellow', 'Neutron flux oscillations observed', NOW() - INTERVAL '45 minutes')
ON CONFLICT DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update the updated_at column
CREATE TRIGGER update_reactors_updated_at 
    BEFORE UPDATE ON reactors 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMIT;
