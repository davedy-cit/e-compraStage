-- ============================================================================
--  E-Compra â€” Indexes
--  Run after 01_schema.sql:  mysql -u root -p ecompra < sql/02_indexes.sql
--
--  Note: InnoDB already creates an index for every FOREIGN KEY, so the FK
--  indexes are declared inline in 01_schema.sql. This file adds the indexes
--  that serve actual QUERIES - search, filtering and reporting.
-- ============================================================================
USE ecompra;

-- ============================================================================
--  Why this file exists separately from 01_schema.sql
--  ---------------------------------------------------------------------------
--  InnoDB automatically creates an index for every FOREIGN KEY, and
--  01_schema.sql also declares the obvious single-column indexes. That is the
--  minimum needed for the schema to be VALID. This file adds the indexes needed
--  for the schema to be FAST - one composite index per real query shape.
--
--  A composite index (a, b, c) can also serve queries that filter on a alone,
--  or on a and b (the "leftmost prefix" rule). So when a composite replaces a
--  single-column index, the single-column one becomes dead weight: it costs
--  writes and disk for nothing. Those are retired in section 8.
--
--  Section 8 comes LAST on purpose. MySQL refuses to drop an index that is the
--  only one able to serve a FOREIGN KEY, so every replacement must already
--  exist before its predecessor is dropped.
--
--  Run:  mysql -u root -p ecompra < sql/02_indexes.sql
--  Verify: EXPLAIN every query in sql/07_verification_queries.sql and confirm
--          the key column names one of these indexes, not NULL or a full scan.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. Product search (idea doc feature 1 - "Product Search and Marketplace")
-- ---------------------------------------------------------------------------
-- Keyword search over name and description. FULLTEXT is an inverted index:
-- it matches whole words and stems, not substrings, so "tomato" finds
-- "Tomatoes" but "toma" does not. That is the correct trade-off for a search
-- box, and it is far faster than LIKE '%...%' (which cannot use any index).
CREATE FULLTEXT INDEX ft_product_search ON catalog_product (name, description);

-- Category chip + "sort by price" is the second most common browse path.
CREATE INDEX ix_product_cat_price ON catalog_product (category_id, price);

-- ---------------------------------------------------------------------------
-- 2. Price comparison (idea doc feature 2 - the Tomatoes example)
-- ---------------------------------------------------------------------------
-- The flagship query joins a product to its comparison group's unit
-- conversions and sorts by price-per-base-unit:
--   WHERE p.comparison_group = ? ORDER BY p.price / cgu.factor_to_base
-- comparison_group alone was indexed; adding unit_code and price lets MySQL
-- satisfy the group lookup from the index and read prices in sorted order.
CREATE INDEX ix_product_cgroup_unit_price
  ON catalog_product (comparison_group, unit_code, price);

-- ---------------------------------------------------------------------------
-- 3. Vendor storefront (idea doc feature 6) and the market map (feature 4)
-- ---------------------------------------------------------------------------
-- Storefront: "this vendor's products, optionally filtered by availability".
CREATE INDEX ix_product_vendor_avail ON catalog_product (vendor_id, availability_code);

-- Market map / vendor directory: group stalls by section, alphabetical inside.
CREATE INDEX ix_vendor_section_name ON catalog_vendor (market_section, name);

-- ---------------------------------------------------------------------------
-- 4. Order history (idea doc feature 5) - newest first, per customer
-- ---------------------------------------------------------------------------
CREATE INDEX ix_order_user_created ON orders_order (user_id, created_at);

-- ---------------------------------------------------------------------------
-- 5. Vendor POS queue and sales dashboard (idea doc features 6 and 7)
-- ---------------------------------------------------------------------------
-- POS queue: "this vendor's orders in status X, oldest first" (FIFO).
CREATE INDEX ix_order_vendor_status_created
  ON orders_order (vendor_id, status_code, created_at);

-- Dashboard: "this vendor's sales between two dates" - no status filter, so
-- the leftmost prefix above does NOT serve it. It needs its own index.
CREATE INDEX ix_order_vendor_created ON orders_order (vendor_id, created_at);

-- ---------------------------------------------------------------------------
-- 6. Reporting and reconciliation
-- ---------------------------------------------------------------------------
CREATE INDEX ix_transaction_created ON orders_transaction (created_at);
CREATE INDEX ix_payment_status_paid ON orders_payment (status_code, paid_at);
CREATE INDEX ix_delivery_status_booked ON orders_deliverybooking (status_code, booked_at);

-- ---------------------------------------------------------------------------
-- 7. Inventory ledger history (idea doc feature 6 - "inventory automatically
--    updates"). Reading one product's movement history, newest first.
-- ---------------------------------------------------------------------------
CREATE INDEX ix_invmov_product_created
  ON catalog_inventorymovement (product_id, created_at);

-- ---------------------------------------------------------------------------
-- 8. Retire the single-column indexes the composites above replace.
--
--    ORDER IS LOAD-BEARING. These DROPs sit after every CREATE, and that is
--    not style - it is a hard requirement. InnoDB refuses to drop an index
--    that is the only one able to serve a FOREIGN KEY:
--
--      ERROR 1553 (HY000): Cannot drop index 'ix_product_category':
--                          needed in a foreign key constraint
--
--    MySQL will accept ANY index whose leftmost columns are the FK columns, so
--    the composite must already exist when the old index goes. Written as a
--    tidy DROP/CREATE pair inside each section - which reads far more
--    naturally - this file fails on the very first statement. Create, then
--    drop, then verify with SHOW INDEX FROM catalog_product;
-- ---------------------------------------------------------------------------
DROP INDEX ix_product_category     ON catalog_product;
DROP INDEX ix_product_cgroup       ON catalog_product;
DROP INDEX ix_product_vendor       ON catalog_product;
DROP INDEX ix_order_user           ON orders_order;
DROP INDEX ix_order_vendor_status  ON orders_order;
DROP INDEX ix_invmov_product       ON catalog_inventorymovement;

-- ---------------------------------------------------------------------------
-- 9. Refresh the optimizer's statistics so EXPLAIN reflects reality.
-- ---------------------------------------------------------------------------
ANALYZE TABLE catalog_product, catalog_vendor, orders_order,
              orders_transaction, orders_payment, orders_deliverybooking,
              catalog_inventorymovement;
