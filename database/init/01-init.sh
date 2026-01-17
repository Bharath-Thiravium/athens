#!/bin/bash
set -e

# Create database if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable required extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    -- Create indexes for better performance
    -- These will be created by Django migrations, but we can prepare the database
    
    -- Grant necessary permissions
    GRANT ALL PRIVILEGES ON DATABASE athens_ehs TO athens_user;
EOSQL

echo "Database initialization completed successfully for athens_ehs"