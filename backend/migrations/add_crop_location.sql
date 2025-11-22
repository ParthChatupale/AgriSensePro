-- Migration: Add crop and location fields to users table
-- Run this in your PostgreSQL database

-- Add crop column
ALTER TABLE users ADD COLUMN IF NOT EXISTS crop VARCHAR;

-- Add location column
ALTER TABLE users ADD COLUMN IF NOT EXISTS location VARCHAR;

-- Verify columns were added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('crop', 'location');

