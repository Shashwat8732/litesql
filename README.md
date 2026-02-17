# 🗄️⚡ LiteSQL

> A lightweight SQL-like database engine built with Python — fast, simple, and powerful.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-18-blue)](https://react.dev)
[![Live Demo](https://img.shields.io/badge/Demo-Live-brightgreen)](https://litesql.vercel.app)

## 🌐 Live Demo

🔗 **Frontend:** [https://litesql.vercel.app](https://litesql.vercel.app)

🔗 **Backend API:** [https://litesql.onrender.com](https://litesql.onrender.com)

> ⚠️ **Note:** Backend is hosted on Render free tier.
> First request may take **30-60 seconds** to wake up the server.
> Please wait after first login — it's free hosting! 😄

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [SQL Commands](#-sql-commands)
  - [CREATE TABLE](#1-create-table)
  - [INSERT](#2-insert)
  - [SELECT](#3-select)
  - [WHERE](#4-where)
  - [ORDER BY](#5-order-by)
  - [LIMIT & OFFSET](#6-limit--offset)
  - [DISTINCT ON](#7-distinct-on)
  - [GROUP BY](#8-group-by)
  - [UPDATE](#9-update)
  - [DELETE](#10-delete)
  - [DROP](#11-drop)
  - [ADD COLUMNS](#12-add-columns)
  - [SHOW INDEXES](#13-show-indexes)
  - [File Import](#14-file-import)
- [Authentication](#-authentication)
- [Deployment](#-deployment)

---

## 🚀 Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
# Server: http://localhost:5001
```

### Frontend
```bash
cd frontend
npm install
npm start
# App: http://localhost:3000
```

---

## 📝 SQL Commands

---

### 1. CREATE TABLE

Create a new table with columns and types.

**Syntax:**
```sql
CREATE TABLE tablename (col1 TYPE, col2 TYPE, ...)
```

**Supported Types:** `INT` `FLOAT` `TEXT` `DATE`

**Examples:**
```sql
CREATE TABLE users (id INT, name TEXT, age INT)

CREATE TABLE orders (id INT, customer_id INT, date TEXT, amount FLOAT)

CREATE TABLE products (id INT, name TEXT, price FLOAT, stock INT)
```

---

### 2. INSERT

Insert one or multiple rows into a table.

**Syntax:**
```sql
INSERT INTO tablename VALUES (val1, val2, ...), (val1, val2, ...)
```

**Examples:**
```sql
-- Single row
INSERT INTO users VALUES (1, 'Alice', 25)

-- Multiple rows
INSERT INTO users VALUES (1, 'Alice', 25), (2, 'Bob', 30), (3, 'Charlie', 22)

-- With text values
INSERT INTO orders VALUES (1, 101, '2026-01-20', 500)
```

---

### 3. SELECT

Fetch all rows or specific columns from a table.

**Syntax:**
```sql
SELECT * FROM tablename

SELECT col1, col2 FROM tablename
```

**Examples:**
```sql
-- All columns
SELECT * FROM users

-- Specific columns
SELECT name, age FROM users
```

---

### 4. WHERE

Filter rows based on a condition.

**Syntax:**
```sql
SELECT * FROM tablename WHERE column OPERATOR value
```

**Supported Operators:** `=` `>` `<` `>=` `<=` `!=`

**Examples:**
```sql
SELECT * FROM users WHERE age = 25

SELECT * FROM users WHERE age > 20

SELECT * FROM orders WHERE amount < 500

SELECT * FROM users WHERE name != 'Alice'

SELECT * FROM orders WHERE amount >= 300
```

---

### 5. ORDER BY

Sort results by a column.

**Syntax:**
```sql
SELECT * FROM tablename ORDER BY column ASC

SELECT * FROM tablename ORDER BY column DESC

SELECT * FROM tablename ORDER BY column ASC LIMIT 10

SELECT * FROM tablename ORDER BY column DESC LIMIT 10 OFFSET 5
```

**Examples:**
```sql
SELECT * FROM users ORDER BY age ASC

SELECT * FROM orders ORDER BY amount DESC

SELECT * FROM users ORDER BY id ASC LIMIT 5

SELECT * FROM users ORDER BY id ASC LIMIT 5 OFFSET 10
```

---

### 6. LIMIT & OFFSET

Paginate results.

**Syntax:**
```sql
SELECT * FROM tablename LIMIT number

SELECT * FROM tablename LIMIT number OFFSET number
```

**Examples:**
```sql
-- First 10 rows
SELECT * FROM users LIMIT 10

-- Skip 5, get next 10
SELECT * FROM users LIMIT 10 OFFSET 5

-- Rows 21-30
SELECT * FROM users LIMIT 10 OFFSET 20
```

---

### 7. DISTINCT ON

Get unique rows based on specific columns.

**Syntax:**
```sql
SELECT DISTINCT ON (column) * FROM tablename

SELECT DISTINCT ON (column) col1, col2 FROM tablename

SELECT DISTINCT ON (column) * FROM tablename ORDER BY column ASC
```

**Examples:**
```sql
-- Unique customers
SELECT DISTINCT ON (customer_id) * FROM orders

-- Unique with specific columns
SELECT DISTINCT ON (customer_id) customer_id, amount FROM orders

-- Unique ordered ascending
SELECT DISTINCT ON (customer_id) * FROM orders ORDER BY customer_id ASC

-- Unique ordered descending
SELECT DISTINCT ON (customer_id) * FROM orders ORDER BY customer_id DESC

-- Multiple column distinct
SELECT DISTINCT ON (customer_id, date) * FROM orders
```

---

### 8. GROUP BY

Aggregate data by a column.

**Syntax:**
```sql
SELECT col, AGGREGATE(col) FROM tablename GROUP BY column
```

**Supported Aggregates:** `COUNT(*)` `SUM(col)` `AVG(col)` `MIN(col)` `MAX(col)`

**Examples:**
```sql
-- Count per group
SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id

-- Sum per group
SELECT customer_id, SUM(amount) FROM orders GROUP BY customer_id

-- Average per group
SELECT customer_id, AVG(amount) FROM orders GROUP BY customer_id

-- Min and Max
SELECT customer_id, MIN(amount), MAX(amount) FROM orders GROUP BY customer_id

-- Multiple aggregates
SELECT customer_id, COUNT(*), SUM(amount), AVG(amount) FROM orders GROUP BY customer_id

-- With WHERE filter
SELECT customer_id, SUM(amount) FROM orders WHERE amount > 100 GROUP BY customer_id
```

---

### 9. UPDATE

Update existing rows based on a condition.

**Syntax:**
```sql
UPDATE tablename SET column = value WHERE column OPERATOR value
```

**Examples:**
```sql
UPDATE users SET age = 26 WHERE name = 'Alice'

UPDATE orders SET amount = 600 WHERE id = 1

UPDATE users SET name = 'Alicia' WHERE id = 1
```

---

### 10. DELETE

Delete rows from a table.

**Syntax:**
```sql
-- Delete with condition
DELETE FROM tablename WHERE column OPERATOR value

-- Delete all rows (keep table)
DELETE ALL ROWS OF tablename

-- Delete all columns
DELETE * COLUMNS OF tablename
```

**Examples:**
```sql
DELETE FROM users WHERE id = 1

DELETE FROM orders WHERE amount < 100

DELETE ALL ROWS OF users

DELETE * COLUMNS OF users
```

---

### 11. DROP

Delete an entire table permanently.

**Syntax:**
```sql
DROP tablename
```

**Examples:**
```sql
DROP users

DROP orders
```

> ⚠️ **Warning:** This permanently deletes the table and all its data!

---

### 12. ADD COLUMNS

Add new columns to an existing table.

**Syntax:**
```sql
ADD COLUMNS INTO tablename (col1 TYPE, col2 TYPE, ...)
```

**Examples:**
```sql
-- Single column
ADD COLUMNS INTO users (email TEXT)

-- Multiple columns
ADD COLUMNS INTO users (email TEXT, phone INT, city TEXT)
```

---

### 13. SHOW INDEXES

View hash and B-tree indexes for a table.

**Syntax:**
```sql
SHOW PICKLE FILE OF tablename
```

**Examples:**
```sql
SHOW PICKLE FILE OF users

SHOW PICKLE FILE OF orders
```

> 💡 Click the **📦 Indexes** button in the UI!

---

### 14. File Import

Import data from CSV or Excel files via UI or SQL.

**Via UI:** Use **📁 Import Data** panel in the sidebar.

**Via SQL:**
```sql
-- CSV file
INSERT FROM 'users.csv' INTO users

-- Excel file
INSERT FROM 'orders.xlsx' INTO orders

-- Excel with specific sheet
INSERT FROM 'data.xlsx' INTO sales SHEET Sheet1
```

---

## 📊 Complete Example

```sql
-- 1. Create table
CREATE TABLE orders (id INT, customer_id INT, date TEXT, amount FLOAT)

-- 2. Insert data
INSERT INTO orders VALUES (1, 1, '2026-01-20', 500), (2, 1, '2026-01-25', 300), (3, 2, '2026-01-22', 750), (4, 3, '2026-01-28', 1000)

-- 3. View all
SELECT * FROM orders

-- 4. Filter
SELECT * FROM orders WHERE amount > 400

-- 5. Sort
SELECT * FROM orders ORDER BY amount DESC

-- 6. Group
SELECT customer_id, SUM(amount) FROM orders GROUP BY customer_id

-- 7. Distinct
SELECT DISTINCT ON (customer_id) * FROM orders ORDER BY customer_id ASC

-- 8. Update
UPDATE orders SET amount = 600 WHERE id = 1

-- 9. Delete
DELETE FROM orders WHERE amount < 200

-- 10. Drop
DROP orders
```

---

## 🔐 Authentication

- Register with username (min 3 chars) and password (min 6 chars)
- Session valid for **7 days**
- Each user has **isolated private database**
- Other users **cannot see** your tables ✅

---

## 🗂️ Data Types

| Type | Description | Example |
|------|-------------|---------|
| `INT` | Integer | `1`, `100`, `-5` |
| `FLOAT` | Decimal | `3.14`, `99.99` |
| `TEXT` | String | `'Alice'` |
| `DATE` | Date | `'2026-01-20'` |

---

## ⚡ Operators

| Operator | Meaning |
|----------|---------|
| `=` | Equal |
| `>` | Greater than |
| `<` | Less than |
| `>=` | Greater or equal |
| `<=` | Less or equal |
| `!=` | Not equal |

---

## 🚀 Deployment

| Service | Purpose | URL | Cost |
|---------|---------|-----|------|
| [Render](https://render.com) | Backend | [litesql.onrender.com](https://litesql.onrender.com) | Free |
| [Vercel](https://vercel.com) | Frontend | [litesql.vercel.app](https://litesql.vercel.app) | Free |
| [UptimeRobot](https://uptimerobot.com) | Keep alive | - | Free |

> ⚠️ **Render Free Tier Sleep Issue:**
> The backend goes to sleep after **15 minutes** of inactivity.
> First request after sleep takes **30-60 seconds** to wake up.
> To fix this, use [UptimeRobot](https://uptimerobot.com) to ping every 5 minutes.

---

## 🛠️ Tech Stack

**Backend:** Python 3.11 · Flask · JSON Storage · SHA256 Auth

**Frontend:** React 18 · CSS3 · Fetch API

---

## ⭐ Support

Give a ⭐ if you like this project!
