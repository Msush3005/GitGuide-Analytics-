# Technical Guide: SQL Environment & Database Integration

This guide details database architecture options, SQLAlchemy abstraction layers, Pandas SQL read/write mechanics, schema validation frameworks, and database schema evolution strategies.

---

## 1. SQLite vs. PostgreSQL: When Each is Appropriate

| Feature | SQLite | PostgreSQL |
| :--- | :--- | :--- |
| **Architecture** | File-based, embedded engine (zero daemon setup) | Client-server architecture, dedicated database daemon |
| **Concurrency** | Single-writer lock (limited concurrent writes) | Multi-version concurrency control (MVCC) for high concurrency |
| **Scale Limit** | Best for datasets $< 1\text{GB}$ or local analysis | Scales to terabytes with advanced indexing and partitioning |
| **Use Cases** | Prototyping, desktop analytics, unit testing, mobile apps | Enterprise production, microservices, multi-user web apps |

---

## 2. Purpose of SQLAlchemy: Database Abstraction Layer

SQLAlchemy provides a **database abstraction layer** that decouples Python code from underlying SQL dialect specifics:
- **Unified API**: Connect to SQLite, PostgreSQL, MySQL, Snowflake, or Redshift using standardized connection strings without rewriting queries.
- **Connection Management & Pooling**: Handles connection lifecycle, pooling, and transaction rollbacks cleanly.
- **Type Mapping**: Automatically translates Python data types (`datetime`, `float`, `int`, `str`) into target database column types (`TIMESTAMP`, `DOUBLE PRECISION`, `BIGINT`, `VARCHAR`).

---

## 3. `pd.read_sql` and `pd.to_sql` Parameters & Behaviors

### Writing Data: `df.to_sql()`
- **`name`**: Target table name in SQL database.
- **`con`**: SQLAlchemy engine or connection object.
- **`if_exists`**:
  - `'fail'`: Default; raises `ValueError` if table already exists.
  - `'replace'`: Drops existing table and recreates schema before inserting data.
  - `'append'`: Inserts rows into existing table schema.
- **`index`**: `False` prevents Pandas index column from being written as an unnecessary table column.
- **`chunksize`**: Batch size for loading large datasets (e.g. `chunksize=10000` to prevent memory spikes).

### Reading Data: `pd.read_sql()`
- **`sql`**: SQL query string or table name.
- **`con`**: SQLAlchemy engine.
- **`parse_dates`**: List of date column names to parse directly into Pandas `datetime64` objects.

---

## 4. Schema Validation & Data Integrity

Before trusting database tables for reporting, execute schema validation via `sqlalchemy.inspect(engine)`:
1. **Column Name & Type Inspection**: Verify column names and target SQL data types (`INTEGER`, `VARCHAR`, `FLOAT`, `TIMESTAMP`).
2. **Nullability Constraints**: Ensure critical identifier columns (like `customer_id`) enforce `NOT NULL`.
3. **Data Integrity Checks**: Verify row counts (`SELECT COUNT(*)`) match expected input rows.

---

## 5. Schema Evolution Strategies

When underlying business schemas evolve (e.g. adding new tracking columns or splitting tables):
1. **Migration Tools (Alembic / Flyway)**: Version-control database schema migrations using SQL migration scripts.
2. **Non-Breaking Alterations**: Add new columns as `NULLABLE` or with explicit default values (`ALTER TABLE ... ADD COLUMN ... DEFAULT ...`).
3. **Database Views for Backward Compatibility**: Create SQL views mapping legacy column names to new table schemas so existing reporting pipelines continue to run without interruption.
