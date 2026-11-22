
-- ============================================================================
--  E-Compra â€” Schema v1
--  MySQL 8.0 Â· InnoDB Â· utf8mb4
--  Derived from docs/uml/er-diagram.puml revision 2 (design of record),
--  as refined by docs/DESIGN_REVIEW.md and docs/DESIGN_DECISIONS.md.
--  Run:  mysql -u root -p < sql/01_schema.sql
-- ============================================================================

DROP DATABASE IF EXISTS ecompra;
CREATE DATABASE ecompra CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecompra;

-- auth_user is created by Django migrations (M2.6); see 04b_auth_user_fks.sql.

-- ---------------------------------------------------------------------------
-- 1. Profiles
-- ---------------------------------------------------------------------------
CREATE TABLE accounts_userprofile (
  user_id     BIGINT UNSIGNED NOT NULL,
  is_vendor   TINYINT(1)      NOT NULL DEFAULT 0,
  created_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (user_id),
  CONSTRAINT fk_userprofile_user FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE accounts_customerprofile (
  user_id     BIGINT UNSIGNED NOT NULL,
  phone       VARCHAR(32)     NOT NULL DEFAULT '',
  address     TEXT            NULL,
  created_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (user_id),
  CONSTRAINT fk_customerprofile_user FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 2. Lookup tables (frozen vocabularies - DESIGN_DECISIONS.md section 4)
-- ---------------------------------------------------------------------------
CREATE TABLE catalog_unitofmeasure (
  code        VARCHAR(16)  NOT NULL,
  name        VARCHAR(64)  NOT NULL,
  description VARCHAR(255) NOT NULL DEFAULT '',
  is_active   TINYINT(1)   NOT NULL DEFAULT 1,
  created_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (code)
) ENGINE=InnoDB;

CREATE TABLE catalog_category (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name        VARCHAR(80)     NOT NULL,
  slug        VARCHAR(80)     NOT NULL,
  is_active   TINYINT(1)      NOT NULL DEFAULT 1,
  created_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_category_slug (slug)
) ENGINE=InnoDB;

-- D-4 / M4: availability is a lookup, not free text
CREATE TABLE catalog_availabilitystatus (
  code         VARCHAR(24)  NOT NULL,
  description  VARCHAR(120) NOT NULL,
  sort_order   INT          NOT NULL DEFAULT 0,
  is_orderable TINYINT(1)   NOT NULL DEFAULT 0,
  PRIMARY KEY (code)
) ENGINE=InnoDB;

CREATE TABLE catalog_comparisongroup (
  code        VARCHAR(32)  NOT NULL,
  name        VARCHAR(120) NOT NULL,
  base_unit   VARCHAR(16)  NOT NULL,
  description VARCHAR(255) NOT NULL DEFAULT '',
  is_active   TINYINT(1)   NOT NULL DEFAULT 1,
  created_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (code),
  CONSTRAINT fk_cgroup_baseunit FOREIGN KEY (base_unit) REFERENCES catalog_unitofmeasure (code)
) ENGINE=InnoDB;

-- M5: the units a comparison group is allowed to compare, with a conversion factor
CREATE TABLE catalog_comparisongroupunit (
  id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  comparison_group VARCHAR(32)     NOT NULL,
  unit             VARCHAR(16)     NOT NULL,
  factor_to_base   DECIMAL(12,4)   NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_cgu_group_unit (comparison_group, unit),
  CONSTRAINT fk_cgu_group FOREIGN KEY (comparison_group) REFERENCES catalog_comparisongroup (code) ON DELETE CASCADE,
  CONSTRAINT fk_cgu_unit  FOREIGN KEY (unit)             REFERENCES catalog_unitofmeasure (code),
  CONSTRAINT ck_cgu_factor CHECK (factor_to_base > 0)
) ENGINE=InnoDB;

CREATE TABLE orders_transactionstatus (
  code        VARCHAR(24)  NOT NULL,
  description VARCHAR(120) NOT NULL,
  sort_order  INT          NOT NULL DEFAULT 0,
  PRIMARY KEY (code)
) ENGINE=InnoDB;

CREATE TABLE orders_transactiontype (
  code        VARCHAR(24)  NOT NULL,
  description VARCHAR(120) NOT NULL,
  PRIMARY KEY (code)
) ENGINE=InnoDB;

CREATE TABLE orders_fulfillmentmethod (
  code        VARCHAR(16)  NOT NULL,
  description VARCHAR(120) NOT NULL,
  PRIMARY KEY (code)
) ENGINE=InnoDB;

CREATE TABLE orders_paymentstatus (
  code        VARCHAR(16)  NOT NULL,
  description VARCHAR(120) NOT NULL,
  is_terminal TINYINT(1)   NOT NULL DEFAULT 0,
  PRIMARY KEY (code)
) ENGINE=InnoDB;

CREATE TABLE orders_deliverystatus (
  code        VARCHAR(16)  NOT NULL,
  description VARCHAR(120) NOT NULL,
  is_terminal TINYINT(1)   NOT NULL DEFAULT 0,
  PRIMARY KEY (code)
) ENGINE=InnoDB;

CREATE TABLE catalog_inventoryreason (
  code        VARCHAR(24)  NOT NULL,
  description VARCHAR(120) NOT NULL,
  direction   VARCHAR(8)   NOT NULL,          -- IN | OUT | ADJUST
  PRIMARY KEY (code),
  CONSTRAINT ck_invreason_direction CHECK (direction IN ('IN','OUT','ADJUST'))
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 3. Catalog
-- ---------------------------------------------------------------------------
-- M6: catalog.Vendor is the single vendor identity. user_id NOT NULL.
CREATE TABLE catalog_vendor (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name          VARCHAR(150)    NOT NULL,
  stall_location VARCHAR(120)   NOT NULL,
  market_section VARCHAR(120)   NOT NULL DEFAULT '',
  contact_phone VARCHAR(32)     NOT NULL DEFAULT '',
  contact_email VARCHAR(254)    NOT NULL DEFAULT '',
  is_active     TINYINT(1)      NOT NULL DEFAULT 1,
  user_id       BIGINT UNSIGNED NOT NULL,
  created_at    DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at    DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_vendor_user (user_id),
  CONSTRAINT fk_vendor_user FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE catalog_product (
  id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name                VARCHAR(180)    NOT NULL,
  description         TEXT            NULL,
  image_url           VARCHAR(500)    NOT NULL DEFAULT '',
  price               DECIMAL(12,2)   NOT NULL,
  unit_code           VARCHAR(16)     NOT NULL,
  stall_location      VARCHAR(120)    NOT NULL DEFAULT '',
  availability_code   VARCHAR(24)     NOT NULL,
  stock_quantity      INT             NOT NULL DEFAULT 0,
  low_stock_threshold INT             NOT NULL DEFAULT 5,
  category_id         BIGINT UNSIGNED NOT NULL,
  vendor_id           BIGINT UNSIGNED NOT NULL,
  comparison_group    VARCHAR(32)     NULL,
  created_at          DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at          DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY ix_product_name (name),
  KEY ix_product_vendor (vendor_id),
  KEY ix_product_category (category_id),
  KEY ix_product_cgroup (comparison_group),
  CONSTRAINT fk_product_unit    FOREIGN KEY (unit_code)         REFERENCES catalog_unitofmeasure (code),
  CONSTRAINT fk_product_avail   FOREIGN KEY (availability_code) REFERENCES catalog_availabilitystatus (code),
  CONSTRAINT fk_product_cat     FOREIGN KEY (category_id)       REFERENCES catalog_category (id),
  CONSTRAINT fk_product_vendor  FOREIGN KEY (vendor_id)         REFERENCES catalog_vendor (id) ON DELETE CASCADE,
  CONSTRAINT fk_product_cgroup  FOREIGN KEY (comparison_group)  REFERENCES catalog_comparisongroup (code),
  CONSTRAINT ck_product_price   CHECK (price >= 0),
  CONSTRAINT ck_product_stock   CHECK (stock_quantity >= 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 4. Cart
-- ---------------------------------------------------------------------------
CREATE TABLE cart_cart (
  user_id    BIGINT UNSIGNED NOT NULL,
  created_at DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (user_id),
  CONSTRAINT fk_cart_user FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE cart_cartitem (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  cart_id    BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  quantity   INT             NOT NULL,
  created_at DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_cartitem (cart_id, product_id),
  CONSTRAINT fk_cartitem_cart    FOREIGN KEY (cart_id)    REFERENCES cart_cart (user_id) ON DELETE CASCADE,
  CONSTRAINT fk_cartitem_product FOREIGN KEY (product_id) REFERENCES catalog_product (id) ON DELETE CASCADE,
  CONSTRAINT ck_cartitem_qty CHECK (quantity > 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 5. Orders
-- ---------------------------------------------------------------------------
-- C5: user_id NULL only for anonymous WALK_IN sales.
-- M3: vendor_id NOT NULL - one order = one vendor.
CREATE TABLE orders_order (
  id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id          BIGINT UNSIGNED NULL,
  customer_label   VARCHAR(120)    NULL,
  vendor_id        BIGINT UNSIGNED NOT NULL,
  status_code      VARCHAR(24)     NOT NULL,
  fulfillment_code VARCHAR(16)     NOT NULL,
  total_amount     DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
  notes            TEXT            NULL,
  created_at       DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at       DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY ix_order_user (user_id),
  KEY ix_order_vendor_status (vendor_id, status_code),
  KEY ix_order_status (status_code),
  CONSTRAINT fk_order_user   FOREIGN KEY (user_id)          REFERENCES auth_user (id) ON DELETE SET NULL,
  CONSTRAINT fk_order_vendor FOREIGN KEY (vendor_id)        REFERENCES catalog_vendor (id) ON DELETE RESTRICT,
  CONSTRAINT fk_order_status FOREIGN KEY (status_code)      REFERENCES orders_transactionstatus (code),
  CONSTRAINT fk_order_fulfil FOREIGN KEY (fulfillment_code) REFERENCES orders_fulfillmentmethod (code),
  CONSTRAINT ck_order_total  CHECK (total_amount >= 0)
) ENGINE=InnoDB;

CREATE TABLE orders_orderitem (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  order_id   BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  quantity   INT             NOT NULL,
  unit_price DECIMAL(12,2)   NOT NULL,        -- price snapshot at order time
  created_at DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_orderitem (order_id, product_id),
  CONSTRAINT fk_orderitem_order   FOREIGN KEY (order_id)   REFERENCES orders_order (id) ON DELETE CASCADE,
  CONSTRAINT fk_orderitem_product FOREIGN KEY (product_id) REFERENCES catalog_product (id) ON DELETE RESTRICT,
  CONSTRAINT ck_orderitem_qty   CHECK (quantity > 0),
  CONSTRAINT ck_orderitem_price CHECK (unit_price >= 0)
) ENGINE=InnoDB;

-- C8: transaction_type makes reservations queryable. No status column (M9).
CREATE TABLE orders_transaction (
  id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  order_id         BIGINT UNSIGNED NOT NULL,
  transaction_type VARCHAR(24)     NOT NULL,
  reference_no     VARCHAR(40)     NOT NULL,
  created_at       DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at       DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_transaction_order (order_id),
  UNIQUE KEY uq_transaction_ref (reference_no),
  CONSTRAINT fk_transaction_order FOREIGN KEY (order_id)         REFERENCES orders_order (id) ON DELETE CASCADE,
  CONSTRAINT fk_transaction_type  FOREIGN KEY (transaction_type) REFERENCES orders_transactiontype (code)
) ENGINE=InnoDB;

-- M11: cash is recorded here too (provider = 'CASH').
CREATE TABLE orders_payment (
  id                 BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  transaction_id     BIGINT UNSIGNED NOT NULL,
  provider           VARCHAR(24)     NOT NULL,
  provider_reference VARCHAR(120)    NOT NULL,
  amount             DECIMAL(12,2)   NOT NULL,
  status_code        VARCHAR(16)     NOT NULL,
  raw_response       JSON            NULL,
  paid_at            DATETIME(6)     NULL,
  created_at         DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_payment_provider_ref (provider, provider_reference),
  KEY ix_payment_transaction (transaction_id),
  CONSTRAINT fk_payment_transaction FOREIGN KEY (transaction_id) REFERENCES orders_transaction (id) ON DELETE CASCADE,
  CONSTRAINT fk_payment_status      FOREIGN KEY (status_code)    REFERENCES orders_paymentstatus (code),
  CONSTRAINT ck_payment_amount CHECK (amount >= 0)
) ENGINE=InnoDB;

CREATE TABLE orders_deliverybooking (
  id                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  transaction_id    BIGINT UNSIGNED NOT NULL,
  provider          VARCHAR(24)     NOT NULL,
  booking_reference VARCHAR(120)    NOT NULL,
  tracking_url      VARCHAR(500)    NOT NULL DEFAULT '',
  fee               DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
  status_code       VARCHAR(16)     NOT NULL,
  raw_response      JSON            NULL,
  booked_at         DATETIME(6)     NULL,
  delivered_at      DATETIME(6)     NULL,
  created_at        DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at        DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_delivery_transaction (transaction_id),
  CONSTRAINT fk_delivery_transaction FOREIGN KEY (transaction_id) REFERENCES orders_transaction (id) ON DELETE CASCADE,
  CONSTRAINT fk_delivery_status      FOREIGN KEY (status_code)    REFERENCES orders_deliverystatus (code),
  CONSTRAINT ck_delivery_fee CHECK (fee >= 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 6. Inventory ledger (C2). The trigger target and the audit trail.
--    stock_quantity on catalog_product is the cached balance; this is truth.
-- ---------------------------------------------------------------------------
CREATE TABLE catalog_inventorymovement (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  product_id BIGINT UNSIGNED NOT NULL,
  delta      INT             NOT NULL,
  reason_code VARCHAR(24)    NOT NULL,
  order_id   BIGINT UNSIGNED NULL,
  note       VARCHAR(255)    NOT NULL DEFAULT '',
  created_at DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY ix_invmov_product (product_id),
  KEY ix_invmov_order (order_id),
  CONSTRAINT fk_invmov_product FOREIGN KEY (product_id)  REFERENCES catalog_product (id) ON DELETE CASCADE,
  CONSTRAINT fk_invmov_reason  FOREIGN KEY (reason_code) REFERENCES catalog_inventoryreason (code),
  CONSTRAINT fk_invmov_order   FOREIGN KEY (order_id)    REFERENCES orders_order (id) ON DELETE SET NULL,
  CONSTRAINT ck_invmov_delta CHECK (delta <> 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 7. Vendor POS (M6: 1:1 extension of catalog_vendor, not a second identity)
-- ---------------------------------------------------------------------------
CREATE TABLE vendors_vendor (
  catalog_vendor_id BIGINT UNSIGNED NOT NULL,
  stall_name        VARCHAR(150)    NOT NULL,
  stall_location    VARCHAR(120)    NOT NULL DEFAULT '',
  PRIMARY KEY (catalog_vendor_id),
  CONSTRAINT fk_posvendor_catalog FOREIGN KEY (catalog_vendor_id)
    REFERENCES catalog_vendor (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- C7: receipt_attempt makes the receipt serial stable across reprints.
CREATE TABLE vendors_vendortransaction (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  vendor_id       BIGINT UNSIGNED NOT NULL,
  order_id        BIGINT UNSIGNED NOT NULL,
  status_code     VARCHAR(24)     NOT NULL,
  receipt_serial  VARCHAR(80)     NULL,
  receipt_attempt INT             NOT NULL DEFAULT 1,
  created_at      DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_vendortx_order (order_id),
  KEY ix_vendortx_vendor (vendor_id),
  CONSTRAINT fk_vendortx_vendor FOREIGN KEY (vendor_id)   REFERENCES vendors_vendor (catalog_vendor_id) ON DELETE CASCADE,
  CONSTRAINT fk_vendortx_order  FOREIGN KEY (order_id)    REFERENCES orders_order (id) ON DELETE CASCADE,
  CONSTRAINT fk_vendortx_status FOREIGN KEY (status_code) REFERENCES orders_transactionstatus (code),
  CONSTRAINT ck_vendortx_attempt CHECK (receipt_attempt >= 1)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 8. Favorites (M2: split so the UNIQUE constraints actually enforce)
-- ---------------------------------------------------------------------------
CREATE TABLE favorites_favoriteproduct (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id    BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  created_at DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_favproduct (user_id, product_id),
  CONSTRAINT fk_favproduct_user    FOREIGN KEY (user_id)    REFERENCES auth_user (id) ON DELETE CASCADE,
  CONSTRAINT fk_favproduct_product FOREIGN KEY (product_id) REFERENCES catalog_product (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE favorites_favoritevendor (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id    BIGINT UNSIGNED NOT NULL,
  vendor_id  BIGINT UNSIGNED NOT NULL,
  created_at DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_favvendor (user_id, vendor_id),
  CONSTRAINT fk_favvendor_user   FOREIGN KEY (user_id)   REFERENCES auth_user (id) ON DELETE CASCADE,
  CONSTRAINT fk_favvendor_vendor FOREIGN KEY (vendor_id) REFERENCES catalog_vendor (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
--  End of schema. 28 tables.
--  Objects Django does not manage (views, triggers, procedures, roles) live in
--  sql/04_views.sql, sql/05_procedures_triggers.sql and sql/06_roles_grants.sql.
-- ============================================================================
