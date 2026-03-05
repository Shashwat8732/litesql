# 🗄️⚡ LiteSQL

> A lightweight SQL database engine with intelligent indexing — fast, simple, and powerful.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-18-blue)](https://react.dev)
[![Live Demo](https://img.shields.io/badge/Demo-Live-brightgreen)](https://litesql.vercel.app)

**LiteSQL** is a custom SQL database engine featuring hybrid Hash + B-tree indexing, smart auto-detection, and multi-user persistence with MongoDB. Built from scratch to understand core database concepts.

---

## 🌟 Key Features

- 🚀 **Hybrid Indexing**: Hash indexes (O(1) lookups) + B-tree indexes (range queries)
- 🧠 **Smart Auto-Indexing**: Automatically selects optimal index type based on column patterns
- 🎯 **User Index Hints**: Manual control with `HASH`, `BTREE`, `NONE` keywords (like MySQL)
- 💾 **Dual Persistence**: JSON files (local) + MongoDB (cloud) — survives backend restarts
- 👥 **Multi-User Support**: Isolated databases per user with session-based auth
- 📊 **Index Visualization**: Inspect hash maps and B-tree structures with `SHOW PICKLE`
- 📁 **Bulk Import**: CSV/Excel file uploads with automatic table creation
- 🔧 **Schema Evolution**: Add columns with automatic index rebuild

---

## 🌐 Live Demo

🔗 **Frontend:** [https://litesql.vercel.app](https://litesql.vercel.app)

🔗 **Backend API:** [https://litesql.onrender.com](https://litesql.onrender.com)

> ⚠️ **Note:** Backend hosted on Render free tier.
> First request may take **1-2 minutes** to wake up.
> Please wait after login — it's free hosting! 😄

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Smart Indexing](#-smart-indexing)
- [SQL Commands](#-sql-commands)
- [Authentication](#-authentication)
- [Tech Stack](#-tech-stack)
- [Deployment](#-deployment)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB (optional, for persistence)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Set environment variables (optional)
export MONGO_URL="your_mongodb_connection_string"

# Run server
python app.py
# Server: http://localhost:5001
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
# App: http://localhost:5173
```

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────┐
│  Frontend (React)                                       │
│  ├─ SQL Terminal                                        │
│  ├─ Table Browser                                       │
│  ├─ Query Results Viewer                               │
│  └─ CSV/Excel Upload                                   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────┐
│  Backend (Flask)                                        │
│  ├─ SQL Parser (Regex-based)                           │
│  ├─ Query Executor                                     │
│  ├─ Table Manager                                      │
│  └─ Authentication                                     │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴──────────────┐
        │                           │
┌───────▼────────┐         ┌────────▼─────────┐
│  JSON Storage  │         │  MongoDB Atlas   │
│  (Local Cache) │         │  (Persistence)   │
└────────────────┘         └──────────────────┘
        │                           │
┌───────▼────────┐         ┌────────▼─────────┐
│ Pickle Indexes │         │  Index Schema    │
│ (Hash + B-tree)│         │  (Rebuild Ready) │
└────────────────┘         └──────────────────┘
```

---

## 🧠 Smart Indexing

### How It Works

LiteSQL automatically chooses the optimal index type based on column characteristics:

**Hash Indexes (O(1) lookup):**
- Columns with unique patterns: `id`, `email`, `username`, `phone`, `uuid`, `token`
- Perfect for: `WHERE id = 5` (exact match queries)

**B-tree Indexes (O(log n) range queries):**
- Numeric types: `INT`, `FLOAT`
- Duplicate-prone columns: `name`, `age`, `price`, `city`, `status`
- Perfect for: `WHERE age > 25` (range queries)

### Auto-Detection Example
```sql
CREATE TABLE users (id INT, email TEXT, name TEXT, age INT)
```

**LiteSQL automatically creates:**
- 🚀 Hash index on `id` (unique pattern)
- 🚀 Hash index on `email` (unique pattern)
- 🌳 B-tree index on `name` (duplicate values expected)
- 🌳 B-tree index on `age` (numeric range queries)

### Manual Override with Hints
```sql
-- Force specific index types
CREATE TABLE products (
    sku TEXT HASH,        -- Hash index (user specified)
    name TEXT BTREE,      -- B-tree index (user specified)
    description TEXT NONE -- No index (user specified)
)

-- Add columns with hints
ADD COLUMNS INTO products (
    barcode TEXT HASH,
    tags TEXT NONE
)
```

**Supported Hints:**
- `HASH` - Force hash index (fast exact lookups)
- `BTREE` - Force B-tree index (range queries)
- `NONE` - No index (save space, faster inserts)

### Index Visualization
```sql
SHOW PICKLE FILE OF users
```

**Output:**
```
============================================================
📦 PICKLE FILE: users_indexes.pkl
============================================================

🚀 Hash Indexes (2):
   id: 150 entries
      1 → {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}
      2 → {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'}
      ...

🌳 B-tree Indexes (2):
   name: 85 unique keys
      Keys: ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
      Alice → [{'id': 1, 'name': 'Alice', ...}]
      Bob → [{'id': 2, 'name': 'Bob', ...}, {'id': 15, 'name': 'Bob', ...}]
      ...
   
   age: 45 unique keys
      Keys: [18, 19, 20, 21, 22, ...]
      25 → [{'id': 5, 'age': 25, ...}, {'id': 12, 'age': 25, ...}]
      ...

============================================================
```

---

## 📝 SQL Commands

### Table Management

#### CREATE TABLE
```sql
CREATE TABLE tablename (col1 TYPE, col2 TYPE, ...)

-- With index hints
CREATE TABLE tablename (
    col1 TYPE HASH,
    col2 TYPE BTREE,
    col3 TYPE NONE
)
```

**Supported Types:** `INT`, `FLOAT`, `STR` (or `TEXT`)

**Examples:**
```sql
-- Auto-indexing
CREATE TABLE users (id INT, name STR, age INT)

-- Manual control
CREATE TABLE products (
    id INT HASH,
    sku STR HASH,
    name STR BTREE,
    description STR NONE,
    price FLOAT BTREE
)
```

#### DROP TABLE
```sql
DROP tablename
```

#### ADD COLUMNS
```sql
ADD COLUMNS INTO tablename (col1 TYPE, col2 TYPE, ...)

-- With hints
ADD COLUMNS INTO tablename (
    col1 TYPE HASH,
    col2 TYPE NONE
)
```

**Examples:**
```sql
-- Auto-indexing
ADD COLUMNS INTO users (email STR, phone STR)

-- Manual control
ADD COLUMNS INTO users (
    email STR HASH,
    bio STR NONE
)
```

#### SHOW INDEXES
```sql
SHOW INDEXES OF tablename
SHOW PICKLE FILE OF tablename
```

---

### Data Operations

#### INSERT
```sql
-- Single row
INSERT INTO tablename VALUES (val1, val2, ...)

-- Multiple rows
INSERT INTO tablename VALUES (val1, val2, ...), (val3, val4, ...)
```

**Examples:**
```sql
INSERT INTO users VALUES (1, 'Alice', 25)

INSERT INTO users VALUES 
    (1, 'Alice', 25), 
    (2, 'Bob', 30), 
    (3, 'Charlie', 22)
```

#### SELECT
```sql
SELECT * FROM tablename
```

#### WHERE
```sql
SELECT * FROM tablename WHERE column OPERATOR value
```

**Operators:** `=`, `>`, `<`, `>=`, `<=`, `!=`, `IS NULL`, `IS NOT NULL`

**Examples:**
```sql
-- Exact match (uses hash index if available)
SELECT * FROM users WHERE id = 5

-- Range query (uses B-tree index)
SELECT * FROM users WHERE age > 25

-- Text with spaces (quotes optional)
SELECT * FROM regions WHERE name = Central America and the Caribbean
SELECT * FROM regions WHERE name = 'Central America and the Caribbean'

-- NULL checks
SELECT * FROM users WHERE email IS NULL
SELECT * FROM users WHERE email IS NOT NULL

-- Special characters
SELECT * FROM contacts WHERE phone = +91-9876543210
SELECT * FROM users WHERE email = john@example.com
```

#### UPDATE
```sql
UPDATE tablename SET column = value WHERE column OPERATOR value
```

**Example:**
```sql
UPDATE users SET age = 26 WHERE name = 'Alice'
```

#### DELETE
```sql
-- Delete specific rows
DELETE FROM tablename WHERE column OPERATOR value

-- Delete all rows (keep structure)
DELETE ALL ROWS OF tablename

-- Delete all columns
DELETE * COLUMNS OF tablename
```

---

### Sorting & Filtering

#### ORDER BY
```sql
SELECT * FROM tablename ORDER BY column ASC
SELECT * FROM tablename ORDER BY column DESC
```

#### LIMIT & OFFSET
```sql
SELECT * FROM tablename LIMIT 10
SELECT * FROM tablename LIMIT 10 OFFSET 5
```

#### DISTINCT ON
```sql
SELECT DISTINCT ON (column) * FROM tablename
SELECT DISTINCT ON (column) * FROM tablename ORDER BY column ASC
```

#### GROUP BY
```sql
SELECT col, AGGREGATE(col) FROM tablename GROUP BY column
```

**Aggregates:** `COUNT(*)`, `SUM(col)`, `AVG(col)`, `MIN(col)`, `MAX(col)`

**Example:**
```sql
SELECT customer_id, COUNT(*), SUM(amount) 
FROM orders 
GROUP BY customer_id
```

---

### File Import

#### Via UI
Use **📁 Import Data** panel in sidebar

#### Via SQL
```sql
-- CSV
INSERT FROM 'users.csv' INTO users

-- Excel
INSERT FROM 'orders.xlsx' INTO orders

-- Specific sheet
INSERT FROM 'data.xlsx' INTO sales SHEET Sheet1
```

---

## 📊 Complete Example
```sql
-- 1. Create table with smart indexing
CREATE TABLE orders (
    id INT,
    customer_id INT,
    date STR,
    amount FLOAT
)
-- Auto-creates: id → Hash, customer_id → Hash, date → B-tree, amount → B-tree

-- 2. Insert data
INSERT INTO orders VALUES 
    (1, 101, '2026-01-20', 500),
    (2, 101, '2026-01-25', 300),
    (3, 102, '2026-01-22', 750),
    (4, 103, '2026-01-28', 1000)

-- 3. View indexes
SHOW PICKLE FILE OF orders

-- 4. Exact lookup (O(1) via hash index)
SELECT * FROM orders WHERE id = 2

-- 5. Range query (O(log n) via B-tree)
SELECT * FROM orders WHERE amount > 400

-- 6. Add column with hint
ADD COLUMNS INTO orders (status STR HASH)

-- 7. Group by
SELECT customer_id, SUM(amount) FROM orders GROUP BY customer_id

-- 8. Update
UPDATE orders SET status = 'completed' WHERE id = 1

-- 9. Cleanup
DROP orders
```

---

## 🔐 Authentication

- **Registration**: Username (min 3 chars) + Password (min 6 chars)
- **Isolation**: Each user has private database
- **Security**: SHA256 password hashing

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.11
- Flask 3.0 (REST API)
- Regex-based SQL Parser
- Pickle (Index Serialization)
- MongoDB Atlas (Persistence)
- SHA256 (Authentication)

**Frontend:**
- React 18
- Vite (Build Tool)
- CSS3 (Styling)
- Fetch API

**Storage:**
- JSON (Table Data)
- Pickle (Index Structures)
- MongoDB (Cloud Backup)

---

## 🚀 Deployment

| Service | Purpose | URL | Cost |
|---------|---------|-----|------|
| **Render** | Backend API | [litesql.onrender.com](https://litesql.onrender.com) | Free |
| **Vercel** | Frontend | [litesql.vercel.app](https://litesql.vercel.app) | Free |
| **MongoDB Atlas** | Database | - | Free (512MB) |
| **UptimeRobot** | Keep Alive | - | Free |

### Render Sleep Fix

Backend sleeps after 15 min inactivity. Use [UptimeRobot](https://uptimerobot.com):
1. Create monitor: HTTP(s)
2. URL: `https://litesql.onrender.com`
3. Interval: 5 minutes
4. Done! Backend stays awake ✅

---

## 📚 Implementation Details

### Indexing Strategy

**Pattern-based Auto-detection:**
```python
unique_patterns = {
    "id", "email", "username", "phone", "uuid", "token", ...
}

duplicate_patterns = {
    "name", "age", "price", "city", "status", ...
}

# Decision logic
if col_name in unique_patterns:
    create_hash_index()
elif col_type in ["INT", "FLOAT"]:
    create_btree_index()
elif col_name in duplicate_patterns:
    create_btree_index()
else:
    create_btree_index()  # Safe default
```

### Schema Evolution

When adding columns, LiteSQL:
1. Updates all existing rows with `NULL` for new columns
2. Clears existing index data
3. Rebuilds indexes from updated rows
4. Maintains index type consistency

This ensures old and new rows have identical schemas in indexes.

### Persistence Flow
```
User Action → Table Manager → JSON File → MongoDB Sync
                    ↓
              Index Update → Pickle File
```

On backend restart:
```
MongoDB → Load Tables → Load Index Schema → Rebuild Indexes from Rows
```

---

## 🎯 Future Enhancements

- [ ] JOIN operations
- [ ] Transactions (BEGIN/COMMIT/ROLLBACK)
- [ ] Query execution planner (EXPLAIN)
- [ ] Full-text search indexes
- [ ] Concurrent user access control
- [ ] Query performance analytics

---

## 📄 License

MIT License - Feel free to use for learning!

---

## ⭐ Support

Give a ⭐ if this helped you understand databases better!

Built with 💙 to learn database internals from scratch.

---

## 🤝 Contributing

This is a learning project. Suggestions welcome!

---

**Made by Shashwat Raj** | [GitHub](https://github.com/Shashwat8732) | [LinkedIn](https://www.linkedin.com/in/shashwat-raj-67146327a)
