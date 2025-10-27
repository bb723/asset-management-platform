-- Asset Management Platform Database Schema
-- Database: your-database-name
-- Schema: PUBLIC

-- ============================================================================
-- Entities Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS entities (
    entity_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- Buildings Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS buildings (
    building_id VARCHAR(36) PRIMARY KEY,
    entity_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
);

-- ============================================================================
-- Budget Items Table
-- Stores budget data for 24 months per building
-- ============================================================================
CREATE TABLE IF NOT EXISTS budget_items (
    budget_item_id VARCHAR(36) PRIMARY KEY,
    building_id VARCHAR(36) NOT NULL,
    month_year DATE NOT NULL,
    category VARCHAR(100) NOT NULL,  -- Revenue, Rent, Operating Expenses, Debt Service, Capital Expenses
    amount DECIMAL(12,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (building_id) REFERENCES buildings(building_id),
    UNIQUE (building_id, month_year, category)
);

-- ============================================================================
-- Documents Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS documents (
    document_id VARCHAR(36) PRIMARY KEY,
    building_id VARCHAR(36) NOT NULL,
    category VARCHAR(100) NOT NULL,  -- Insurance, Loan, HVAC, Lawn/Plow, Tax, Water, Electric, etc.
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    uploaded_by VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (building_id) REFERENCES buildings(building_id)
);

-- ============================================================================
-- Share Tokens Table
-- For public shareable links (no authentication required)
-- ============================================================================
CREATE TABLE IF NOT EXISTS share_tokens (
    token VARCHAR(64) PRIMARY KEY,
    entity_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    expires_at TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_buildings_entity ON buildings(entity_id);
CREATE INDEX IF NOT EXISTS idx_budget_items_building ON budget_items(building_id);
CREATE INDEX IF NOT EXISTS idx_budget_items_month ON budget_items(month_year);
CREATE INDEX IF NOT EXISTS idx_documents_building ON documents(building_id);
CREATE INDEX IF NOT EXISTS idx_share_tokens_entity ON share_tokens(entity_id);
CREATE INDEX IF NOT EXISTS idx_share_tokens_expires ON share_tokens(expires_at);
