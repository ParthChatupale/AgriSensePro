# Database Migration: Add crop and category columns to posts table

## Problem
The `posts` table is missing the `crop` and `category` columns that were added to the SQLAlchemy model.

## Solution
Run the following SQL commands in your PostgreSQL database to add the missing columns.

## Quick Fix (Run in PostgreSQL)

### Option 1: Using psql command line
```bash
psql -U agrisense_user -d agrisense_db -f migrations/add_post_crop_category.sql
```

### Option 2: Using pgAdmin or any PostgreSQL client
1. Connect to your database
2. Open a SQL query window
3. Copy and paste the SQL from `migrations/add_post_crop_category.sql`
4. Execute the query

### Option 3: Direct SQL commands
Run these commands in your PostgreSQL database:

```sql
-- Add crop column (nullable, for filtering posts by crop type)
ALTER TABLE posts 
ADD COLUMN IF NOT EXISTS crop VARCHAR;

-- Add category column (nullable, for categorizing posts)
ALTER TABLE posts 
ADD COLUMN IF NOT EXISTS category VARCHAR;

-- Add index on crop for faster filtering
CREATE INDEX IF NOT EXISTS idx_posts_crop ON posts(crop);

-- Add index on category for faster filtering
CREATE INDEX IF NOT EXISTS idx_posts_category ON posts(category);
```

## Verification
After running the migration, verify the columns were added:

```sql
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'posts' 
AND column_name IN ('crop', 'category');
```

You should see both `crop` and `category` columns listed.

## After Migration
Once the migration is complete, restart your backend server and the Community page should work correctly.


