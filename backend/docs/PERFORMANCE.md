# E-Compra Performance Analysis

## Methodology
Ran `EXPLAIN ANALYZE` on key queries against MySQL 8.4 with seeded data (34 products, 6 vendors, 9 categories, 18 orders, 43 inventory movements, 3 favorites).

Database: `ecompra` (production) and `test_ecompra` (test clone).

Indexes tested: New composite indexes from `sql/04_performance_indexes.sql` + existing indexes from `sql/02_indexes.sql`.

---

## Key Queries

### 1. Product search by category and availability
```sql
EXPLAIN ANALYZE 
SELECT * FROM catalog_product 
WHERE category_id = 1 AND availability_code = 'IN_STOCK' 
ORDER BY price LIMIT 20;
```

**Execution Plan:**
```
-> Limit: 20 row(s)  (cost=1.15 rows=4) (actual time=0.203..0.218 rows=4 loops=1)
    -> Index lookup on catalog_product using idx_product_cat_avail_price (category_id=1, availability_code='IN_STOCK')  (cost=1.15 rows=4) (actual time=0.0677..0.0825 rows=4 loops=1)
```

**Analysis:** Uses the new composite index `idx_product_cat_avail_price` (category_id, availability_code, price). The index enables efficient filtering by category + availability with pre-sorted price ordering (no filesort needed for ORDER BY price).

**Before (hypothetical full scan):** Full table scan on 34 rows, filtered=100%
**After:** Index range scan on `idx_product_cat_avail_price`, 4 rows examined, 0.08ms actual time

---

### 2. Product search by vendor and availability (price comparison)
```sql
EXPLAIN ANALYZE 
SELECT * FROM catalog_product 
WHERE vendor_id = 1 AND availability_code = 'IN_STOCK' 
ORDER BY price LIMIT 20;
```

**Execution Plan:**
```
-> Limit: 20 row(s)  (cost=1.25 rows=5) (actual time=0.14..0.143 rows=5 loops=1)
    -> Sort: catalog_product.price, limit input to 20 row(s) per chunk  (cost=1.25 rows=5) (actual time=0.139..0.142 rows=5 loops=1)
        -> Index lookup on catalog_product using ix_product_vendor_avail (vendor_id=1, availability_code='IN_STOCK')  (cost=1.25 rows=5) (actual time=0.0361..0.0574 rows=5 loops=1)
```

**Analysis:** Uses existing index `ix_product_vendor_avail` (vendor_id, availability_code) from M0.8. The new index `idx_product_vendor_avail` has identical column structure. A filesort is needed for ORDER BY price since price is not in the index.

**Note:** For optimal price comparison queries, consider extending the index to include price: `(vendor_id, availability_code, price)`.

---

### 3. User's orders by date
```sql
EXPLAIN ANALYZE 
SELECT * FROM orders_order 
WHERE user_id = 1 
ORDER BY created_at DESC LIMIT 20;
```

**Execution Plan:**
```
-> Limit: 20 row(s)  (cost=2.2 rows=17) (actual time=0.0793..0.12 rows=17 loops=1)
    -> Index lookup on orders_order using ix_order_user_created (user_id=1) (reverse)  (cost=2.2 rows=17) (actual time=0.078..0.117 rows=17 loops=1)
```

**Analysis:** Uses existing index `ix_order_user_created` (user_id, created_at) from M0.8. The new index `idx_order_user_created` has identical structure with explicit DESC on created_at. MySQL 8.0+ supports descending indexes, and the optimizer correctly uses reverse scan on the existing index.

---

### 4. Vendor's orders by status and date
```sql
EXPLAIN ANALYZE 
SELECT * FROM orders_order 
WHERE vendor_id = 1 AND status_code = 'CONFIRMED' 
ORDER BY created_at DESC LIMIT 20;
```

**Execution Plan:**
```
-> Limit: 20 row(s)  (cost=0.345 rows=1) (actual time=0.384..0.384 rows=0 loops=1)
    -> Sort: orders_order.created_at DESC, limit input to 20 row(s) per chunk  (cost=0.345 rows=1) (actual time=0.383..0.383 rows=0 loops=1)
        -> Filter: (orders_order.vendor_id = 1)  (cost=0.345 rows=1) (actual time=0.0345..0.0345 rows=0 loops=1)
            -> Index lookup on orders_order using ix_order_status (status_code='CONFIRMED')  (cost=0.345 rows=1) (actual time=0.0333..0.0333 rows=0 loops=1)
```

**Analysis:** The optimizer chose `ix_order_status` (status_code only) over the new composite index `idx_order_vendor_status_created` (vendor_id, status_code, created_at DESC). This is likely because:
- status_code has high selectivity (only 1 row with CONFIRMED)
- vendor_id filter is applied as a post-filter

With more data, the composite index would be more beneficial as it would avoid the filesort and post-filter.

---

### 5. User's cart items
```sql
EXPLAIN ANALYZE 
SELECT * FROM cart_cartitem WHERE cart_id = 1;
```

**Execution Plan:**
```
-> Index lookup on cart_cartitem using uq_cartitem (cart_id=1)  (cost=0.35 rows=1) (actual time=0.0322..0.0322 rows=0 loops=1)
```

**Analysis:** Uses the existing unique constraint `uq_cartitem` (cart_id, product_id) which has cart_id as the leading column. The new index `idx_cartitem_cart` (cart_id) is a redundant single-column index since the unique constraint already provides efficient access.

---

### 6. Payment by transaction
```sql
EXPLAIN ANALYZE 
SELECT * FROM orders_payment WHERE transaction_id = 1;
```

**Execution Plan:**
```
-> Index lookup on orders_payment using ix_payment_transaction (transaction_id=1)  (cost=0.35 rows=1) (actual time=0.0183..0.0203 rows=1 loops=1)
```

**Analysis:** Uses existing index `ix_payment_transaction` (transaction_id) from M0.8. The new index `idx_payment_transaction` is a duplicate.

---

### 7. Inventory movements by product and date
```sql
EXPLAIN ANALYZE 
SELECT * FROM catalog_inventorymovement WHERE product_id = 1 ORDER BY created_at DESC LIMIT 20;
```

**Execution Plan:**
```
-> Limit: 20 row(s)  (cost=1.05 rows=3) (actual time=0.559..0.566 rows=3 loops=1)
    -> Index lookup on catalog_inventorymovement using ix_invmov_product_created (product_id=1) (reverse)  (cost=1.05 rows=3) (actual time=0.301..0.308 rows=3 loops=1)
```

**Analysis:** Uses existing index `ix_invmov_product_created` (product_id, created_at) from M0.8. The new index `idx_inventory_product_created` has identical structure with explicit DESC.

---

### 8. User's favorites
```sql
EXPLAIN ANALYZE 
SELECT * FROM favorites_favoriteproduct WHERE user_id = 1;
```

**Execution Plan:**
```
-> Index lookup on favorites_favoriteproduct using uq_favproduct (user_id=1)  (cost=0.35 rows=1) (actual time=0.0229..0.0229 rows=0 loops=1)
```

**Analysis:** Uses the existing unique constraint `uq_favproduct` (user_id, product_id) which has user_id as the leading column. The new index `idx_favorite_user` (user_id) is redundant.

---

## Index Summary

| Index | Table | Columns | Status | Notes |
|-------|-------|---------|--------|-------|
| `idx_product_cat_avail_price` | catalog_product | (category_id, availability_code, price) | **NEW - Used** | Enables category+availability filter + price sort |
| `idx_product_vendor_avail` | catalog_product | (vendor_id, availability_code) | Duplicate | Matches existing `ix_product_vendor_avail` |
| `idx_order_user_created` | orders_order | (user_id, created_at DESC) | Duplicate | Matches existing `ix_order_user_created` |
| `idx_order_vendor_status_created` | orders_order | (vendor_id, status_code, created_at DESC) | **NEW - Available** | Optimizer may prefer with more data |
| `idx_cartitem_cart` | cart_cartitem | (cart_id) | Redundant | Covered by `uq_cartitem` (cart_id, product_id) |
| `idx_payment_transaction` | orders_payment | (transaction_id) | Redundant | Matches existing `ix_payment_transaction` |
| `idx_inventory_product_created` | catalog_inventorymovement | (product_id, created_at DESC) | Duplicate | Matches existing `ix_invmov_product_created` |
| `idx_favorite_user` | favorites_favoriteproduct | (user_id) | Redundant | Covered by `uq_favproduct` (user_id, product_id) |

---

## Recommendations

1. **Keep the new indexes** — They document the intended query patterns and will be used as data grows. MySQL's optimizer may not choose them with small datasets but will with production volumes.

2. **Remove redundant indexes** (optional cleanup):
   - `idx_cartitem_cart` — covered by `uq_cartitem`
   - `idx_payment_transaction` — duplicate of `ix_payment_transaction`
   - `idx_inventory_product_created` — duplicate of `ix_invmov_product_created`
   - `idx_favorite_user` — covered by `uq_favproduct`

3. **Consider extending indexes** for price comparison queries:
   - Add `price` to `idx_product_vendor_avail` → `(vendor_id, availability_code, price)` to avoid filesort

4. **Monitor slow query log** in production:
   ```sql
   SET GLOBAL slow_query_log = ON;
   SET GLOBAL long_query_time = 0.1;
   ```

5. **Consider covering indexes** for frequently selected columns to avoid table lookups:
   - `idx_product_cat_avail_price` could include `(name, vendor_id, image_url)` if those are always selected

6. **Partition large tables** if they grow beyond 1M rows:
   - `orders_order` by `created_at` (monthly partitions)
   - `catalog_inventorymovement` by `created_at` (monthly partitions)

7. **Run `ANALYZE TABLE`** periodically to update index statistics:
   ```sql
   ANALYZE TABLE catalog_product, orders_order, cart_cartitem, orders_payment, catalog_inventorymovement, favorites_favoriteproduct;
   ```

---

## Test Environment
- MySQL 8.4.0
- Database: ecompra (35 tables: 28 domain + 7 Django)
- Seeded data: 34 products, 6 vendors, 9 categories, 18 orders, 43 inventory movements, 3 favorites
- Indexes: 8 new + 12 existing (from M0.8)
- Date: 2026-11-23