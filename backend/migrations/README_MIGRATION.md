# Database Migration: add crop + category columns

The `posts` table is missing the `crop` and `category` fields that already exist in the SQLAlchemy model. This quick migration keeps the database in sync.

---

## Problem

- `posts` lacks `crop` and `category` columns.
- ORM expects these fields, so we need to update PostgreSQL.

---

## Solution

Run a small SQL migration—just a few commands in PostgreSQL.

---

## Quick Fix Options

### 1. psql terminal

```bash
psql -U agrisense_user -d agrisense_db -f migrations/add_post_crop_category.sql
```

### 2. pgAdmin or any DB GUI

1. Connect to the database.
2. Open an SQL window.
3. Paste the contents of `migrations/add_post_crop_category.sql`.
4. Run it.

### 3. Manual SQL (no comments)

```sql
ALTER TABLE posts 
ADD COLUMN IF NOT EXISTS crop VARCHAR;

ALTER TABLE posts 
ADD COLUMN IF NOT EXISTS category VARCHAR;

CREATE INDEX IF NOT EXISTS idx_posts_crop ON posts(crop);

CREATE INDEX IF NOT EXISTS idx_posts_category ON posts(category);
```

---

## Verification

Check that PostgreSQL added the columns:

```sql
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'posts' 
AND column_name IN ('crop', 'category');
```

If both rows show up, the migration worked.

---

## After Migration

Restart the backend service. The community feed and filters (crop/category) should work normally again.
