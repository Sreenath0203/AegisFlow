-- AegisFlow PostgreSQL Database DDL Schema

CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    country VARCHAR(100) NOT NULL,
    reliability_score FLOAT DEFAULT 95.0,
    on_time_delivery FLOAT DEFAULT 92.0,
    quality_score FLOAT DEFAULT 98.0,
    current_risk_level VARCHAR(20) DEFAULT 'LOW',
    contact_email VARCHAR(100),
    category VARCHAR(100) DEFAULT 'Electronics & Components'
);

CREATE TABLE IF NOT EXISTS shipments (
    id SERIAL PRIMARY KEY,
    shipment_code VARCHAR(50) UNIQUE NOT NULL,
    supplier_id INT REFERENCES suppliers(id),
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'IN_TRANSIT',
    delay_days INT DEFAULT 0,
    risk_level VARCHAR(20) DEFAULT 'LOW',
    cargo_description TEXT,
    carrier VARCHAR(100) DEFAULT 'Pacific Cargo Fleet'
);

CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    sku VARCHAR(50) UNIQUE NOT NULL,
    current_stock INT DEFAULT 1000,
    daily_demand INT DEFAULT 50,
    days_remaining INT DEFAULT 20,
    reorder_level INT DEFAULT 300,
    stockout_risk_level VARCHAR(20) DEFAULT 'LOW',
    unit_cost FLOAT DEFAULT 45.0
);

CREATE TABLE IF NOT EXISTS risks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    risk_score INT DEFAULT 50,
    risk_type VARCHAR(50) NOT NULL,
    probability FLOAT DEFAULT 0.5,
    severity VARCHAR(20) DEFAULT 'MEDIUM',
    financial_impact FLOAT DEFAULT 100000.0,
    affected_supplier_id INT REFERENCES suppliers(id),
    affected_shipment_id INT REFERENCES shipments(id),
    evidence TEXT,
    ai_explanation TEXT,
    status VARCHAR(30) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    action_title VARCHAR(200) NOT NULL,
    reason TEXT NOT NULL,
    confidence_score FLOAT DEFAULT 0.85,
    expected_impact TEXT,
    financial_saving FLOAT DEFAULT 50000.0,
    delay_reduction_days INT DEFAULT 3,
    alternative_actions TEXT,
    status VARCHAR(30) DEFAULT 'PROPOSED',
    risk_id INT REFERENCES risks(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS compliance (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(100) DEFAULT 'CONTRACT',
    entity_name VARCHAR(150),
    compliance_status VARCHAR(30) DEFAULT 'COMPLIANT',
    penalty_risk FLOAT DEFAULT 0.0,
    force_majeure_clause TEXT,
    required_action TEXT,
    last_audited TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS news_events (
    id SERIAL PRIMARY KEY,
    headline VARCHAR(250) NOT NULL,
    source VARCHAR(100) DEFAULT 'Reuters Supply Chain',
    location VARCHAR(100),
    severity VARCHAR(20) DEFAULT 'MEDIUM',
    supply_chain_impact TEXT,
    affected_suppliers VARCHAR(200),
    date_published TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scenario_results (
    id SERIAL PRIMARY KEY,
    scenario_name VARCHAR(100) NOT NULL,
    option_key VARCHAR(50) NOT NULL,
    cost_delta FLOAT DEFAULT 0.0,
    delay_days INT DEFAULT 0,
    risk_score INT DEFAULT 50,
    net_impact VARCHAR(100),
    is_recommended BOOLEAN DEFAULT FALSE,
    details TEXT
);
