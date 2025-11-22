-- Migration: Add crop and category columns to posts table
-- Date: 2024
-- Description: Adds crop and category fields to posts table for filtering and categorization

-- Add crop column (nullable, for filtering posts by crop type)
ALTER TABLE posts 
ADD COLUMN IF NOT EXISTS crop VARCHAR;

-- Add category column (nullable, for categorizing posts: question, tip, issue, success_story)
ALTER TABLE posts 
ADD COLUMN IF NOT EXISTS category VARCHAR;

-- Add index on crop for faster filtering
CREATE INDEX IF NOT EXISTS idx_posts_crop ON posts(crop);

-- Add index on category for faster filtering
CREATE INDEX IF NOT EXISTS idx_posts_category ON posts(category);


