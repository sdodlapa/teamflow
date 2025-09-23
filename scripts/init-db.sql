-- Initialize TeamFlow development database

-- Create test database if it doesn't exist
SELECT 'CREATE DATABASE teamflow_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'teamflow_test');

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For full-text search

-- Create indexes for common queries (will be added as we develop)
-- This file can be expanded as we add more initialization scripts