-- E-Compra Performance Indexes
-- Composite indexes based on query patterns
-- Run: mysql -u root -pAdmin2627 ecompra < sql/04_performance_indexes.sql

-- Catalog search: products by category + price + availability
CREATE INDEX idx_product_cat_avail_price ON catalog_product (category_id, availability_code, price);

-- Catalog search: products by vendor + availability
CREATE INDEX idx_product_vendor_avail ON catalog_product (vendor_id, availability_code);

-- Orders: user's orders by date
CREATE INDEX idx_order_user_created ON orders_order (user_id, created_at DESC);

-- Orders: vendor's orders by status + date
CREATE INDEX idx_order_vendor_status_created ON orders_order (vendor_id, status_code, created_at DESC);

-- Cart items: user's cart
CREATE INDEX idx_cartitem_cart ON cart_cartitem (cart_id);

-- Payments: by transaction
CREATE INDEX idx_payment_transaction ON orders_payment (transaction_id);

-- Inventory movements: by product + date
CREATE INDEX idx_inventory_product_created ON catalog_inventorymovement (product_id, created_at DESC);

-- Favorites: user's favorites
CREATE INDEX idx_favorite_user ON favorites_favoriteproduct (user_id);