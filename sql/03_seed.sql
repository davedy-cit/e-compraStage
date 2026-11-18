-- ============================================================================
--  E-Compra â€” Seed data (development)
--  Mandaue Public Market, Cebu Â· all amounts in PHP (â‚±)
--  Run:  mysql -u root -p ecompra < sql/03_seed.sql
--
--  Sample data is drawn from the project idea document:
--    - the 9 search categories (feature 1)
--    - the Tomatoes comparison: â‚±80 / â‚±75 / â‚±78 (feature 2)
--    - personas Maria Santos (customer) and Pedro Reyes (fish vendor)
-- ============================================================================
USE ecompra;
SET NAMES utf8mb4;

-- ---------------------------------------------------------------------------
-- 1. Users. Django's auth_user. Explicit ids so later inserts can reference them.
--    All passwords: ecompra123  (PBKDF2-SHA256, 600000 iterations)
-- ---------------------------------------------------------------------------
INSERT INTO auth_user
  (id, password, last_login, is_superuser, username, first_name, last_name,
   email, is_staff, is_active, date_joined)
VALUES
  (1, 'pbkdf2_sha256$600000$5d9e264e422d$VwWJ9pG3uT1vRIxi0nUYYD3iex4PRAMEhsnID6u93a8=',
      NULL, 1, 'admin', 'Market', 'Administrator', 'admin@ecompra.local', 1, 1, '2026-11-01 08:00:00.000000'),
  (2, 'pbkdf2_sha256$600000$ac05abda2b27$eYIM2DENFFNMawQEPJ30P69WetE4yjWclI7RPqwM8oU=',
      NULL, 0, 'maria.santos', 'Maria', 'Santos', 'maria.santos@example.ph', 0, 1, '2026-11-02 09:15:00.000000'),
  (3, 'pbkdf2_sha256$600000$811e4a24f499$k2m0mtUQXXZNPfBOuXj/xrVYIqrnzakmJEGNBM+SxMs=',
      NULL, 0, 'juan.reyes', 'Juan', 'Reyes', 'juan.reyes@example.ph', 0, 1, '2026-11-03 10:40:00.000000'),
  (4, 'pbkdf2_sha256$600000$b68a3d39df51$m7V921MaD4KqyNn1KKP5ULjlCZBeSFcEF32m8n/37Yc=',
      NULL, 0, 'pedro.reyes', 'Pedro', 'Reyes', 'pedro.reyes@example.ph', 0, 1, '2026-11-01 08:30:00.000000'),
  (5, 'pbkdf2_sha256$600000$c5a9fe01ec81$zyw1sGZMD3w7NUR5ln9M6BVdItbTSVUGa7WtOu1cSVQ=',
      NULL, 0, 'rosa.delacruz', 'Rosa', 'Dela Cruz', 'rosa.delacruz@example.ph', 0, 1, '2026-11-01 08:35:00.000000'),
  (6, 'pbkdf2_sha256$600000$4c0c3e7fba2e$PeNDm/Lt0VQ64s9l4oX2F3AqRElHgGXcbHzAEi26l08=',
      NULL, 0, 'jose.bautista', 'Jose', 'Bautista', 'jose.bautista@example.ph', 0, 1, '2026-11-01 08:40:00.000000'),
  (7, 'pbkdf2_sha256$600000$6e7f06e724e8$L1MGPegeHXyHV1cYJx7IsjiF97gu1Xn87nmSYlr2Y2E=',
      NULL, 0, 'luzviminda.tan', 'Luzviminda', 'Tan', 'luzviminda.tan@example.ph', 0, 1, '2026-11-01 08:45:00.000000'),
  (8, 'pbkdf2_sha256$600000$1c328d50adea$eA47+Ip/hak1VgRiMuFEuWmOzFPvcOb9f0FL8aw3kpM=',
      NULL, 0, 'andres.villamor', 'Andres', 'Villamor', 'andres.villamor@example.ph', 0, 1, '2026-11-01 08:50:00.000000'),
  (9, 'pbkdf2_sha256$600000$e47bb6e3562c$KmIOZGWJxdhOjFH9j1qgUeuCd4beJeuaCxBvmewHYo0=',
      NULL, 0, 'nena.abellana', 'Nena', 'Abellana', 'nena.abellana@example.ph', 0, 1, '2026-11-01 08:55:00.000000');

-- ---------------------------------------------------------------------------
-- 2. Profiles
-- ---------------------------------------------------------------------------
INSERT INTO accounts_userprofile (user_id, is_vendor) VALUES
  (1, 0), (2, 0), (3, 0), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1);

INSERT INTO accounts_customerprofile (user_id, phone, address) VALUES
  (2, '0917-555-0110', 'Unit 4B, A.C. Cortes Ave., Mandaue City, Cebu'),
  (3, '0917-555-0111', '12 Lopez Jaena St., Mandaue City, Cebu');

-- ---------------------------------------------------------------------------
-- 3. Lookup tables - the frozen vocabularies from docs/DESIGN_DECISIONS.md Â§4
-- ---------------------------------------------------------------------------
INSERT INTO catalog_unitofmeasure (code, name, description) VALUES
  ('KG',     'Kilogram', 'Weight - metric base unit'),
  ('G',      'Gram',     'Weight - 1/1000 kilogram'),
  ('L',      'Liter',    'Volume - metric base unit'),
  ('ML',     'Milliliter','Volume - 1/1000 liter'),
  ('PIECE',  'Piece',    'Counted individually'),
  ('BUNDLE', 'Bundle',   'Tied bunch, as sold in the market'),
  ('TRAY',   'Tray',     'Flat tray of eggs (30 pieces)'),
  ('SACK',   'Sack',     'Woven sack (25 kg of rice)'),
  ('PACK',   'Pack',     'Pre-packed retail unit');

INSERT INTO catalog_category (id, name, slug) VALUES
  (1, 'Fish',       'fish'),
  (2, 'Meat',       'meat'),
  (3, 'Poultry',    'poultry'),
  (4, 'Fruits',     'fruits'),
  (5, 'Vegetables', 'vegetables'),
  (6, 'Rice',       'rice'),
  (7, 'Dry goods',  'dry-goods'),
  (8, 'Spices',     'spices'),
  (9, 'Others',     'others');

INSERT INTO catalog_availabilitystatus (code, description, sort_order, is_orderable) VALUES
  ('IN_STOCK',     'Available in stock',            10, 1),
  ('LOW_STOCK',    'Available, running low',        20, 1),
  ('OUT_OF_STOCK', 'Temporarily unavailable',       30, 0),
  ('HIDDEN',       'Delisted by the vendor',        40, 0);

INSERT INTO orders_transactionstatus (code, description, sort_order) VALUES
  ('PENDING_PAYMENT',  'Awaiting payment or down payment',        10),
  ('CONFIRMED',        'Paid or reserved; vendor has accepted',   20),
  ('PREPARING',        'Vendor is preparing the order',           30),
  ('READY_FOR_PICKUP', 'Prepared and waiting at the stall',       40),
  ('OUT_FOR_DELIVERY', 'Handed to the delivery provider',         50),
  ('COMPLETED',        'Picked up or delivered and settled',      60),
  ('CANCELLED',        'Cancelled before completion',             70);

INSERT INTO orders_transactiontype (code, description) VALUES
  ('ONLINE_ORDER',       'Fully paid online order with delivery'),
  ('PICKUP_RESERVATION', 'Reservation settled at the stall'),
  ('POS_WALKIN',         'Walk-in sale recorded at the vendor POS');

INSERT INTO orders_fulfillmentmethod (code, description) VALUES
  ('PICKUP',   'Customer collects at the stall'),
  ('DELIVERY', 'Delivered to the customer address'),
  ('WALK_IN',  'Over-the-counter sale, no online order');

INSERT INTO orders_paymentstatus (code, description, is_terminal) VALUES
  ('PENDING',  'Initiated, not yet settled', 0),
  ('VERIFIED', 'Settlement confirmed',       1),
  ('FAILED',   'Settlement failed',          1),
  ('REFUNDED', 'Returned to the customer',   1);

INSERT INTO orders_deliverystatus (code, description, is_terminal) VALUES
  ('BOOKED',     'Booking accepted by the provider', 0),
  ('IN_TRANSIT', 'Rider is on the way',              0),
  ('DELIVERED',  'Received by the customer',         1),
  ('FAILED',     'Delivery attempt failed',          1),
  ('CANCELLED',  'Booking cancelled',                1);

INSERT INTO catalog_inventoryreason (code, description, direction) VALUES
  ('RECEIVED',    'Stock received from supplier',   'IN'),
  ('SOLD_ONLINE', 'Sold through an online order',   'OUT'),
  ('SOLD_WALKIN', 'Sold over the counter',          'OUT'),
  ('SPOILAGE',    'Spoiled or unsellable',          'OUT'),
  ('ADJUSTMENT',  'Physical recount correction',    'ADJUST');

-- ---------------------------------------------------------------------------
-- 4. Comparison groups (idea doc feature 2). base_unit is the unit every price
--    is normalised to before ranking.
-- ---------------------------------------------------------------------------
INSERT INTO catalog_comparisongroup (code, name, base_unit, description) VALUES
  ('TOMATO',             'Tomatoes',            'KG',    'Fresh tomatoes'),
  ('BANGUS',             'Bangus (Milkfish)',   'KG',    'Whole milkfish'),
  ('TILAPIA',            'Tilapia',             'KG',    'Whole tilapia'),
  ('GALUNGGONG',         'Galunggong',          'KG',    'Round scad'),
  ('TULINGAN',           'Tulingan',            'KG',    'Bullet tuna'),
  ('SHRIMP',             'Hipon (Shrimp)',      'KG',    'Fresh shrimp'),
  ('PORK_BELLY',         'Pork Belly (Liempo)', 'KG',    'Bone-in or boneless'),
  ('PORK_KASIM',         'Pork Kasim',          'KG',    'Pork shoulder'),
  ('PORK_GROUND',        'Ground Pork',         'KG',    'Freshly ground'),
  ('BEEF_BRISKET',       'Beef Brisket',        'KG',    'For soup and stews'),
  ('CHICKEN_WHOLE',      'Whole Chicken',       'KG',    'Dressed whole chicken'),
  ('CHICKEN_BREAST',     'Chicken Breast',      'KG',    'Boneless breast fillet'),
  ('CHICKEN_NATIVE',     'Native Chicken',      'KG',    'Bisaya free-range'),
  ('EGGS',               'Eggs',                'PIECE', 'Large chicken eggs'),
  ('RICE_WELL_MILLED',   'Well-Milled Rice',    'KG',    'Ordinary milled rice'),
  ('RICE_SINANDOMENG',   'Sinandomeng Rice',    'KG',    'Long-grain variety'),
  ('RICE_DINORADO',      'Dinorado Rice',       'KG',    'Aromatic variety'),
  ('RICE_MALAGKIT',      'Malagkit Rice',       'KG',    'Glutinous rice'),
  ('COOKING_OIL',        'Cooking Oil',         'L',     'Refined palm or coconut'),
  ('SUGAR_BROWN',        'Brown Sugar',         'KG',    'Washed brown sugar'),
  ('SUGAR_WHITE',        'White Sugar',         'KG',    'Refined white sugar'),
  ('GARLIC',             'Garlic (Bawang)',     'KG',    'Fresh garlic bulbs'),
  ('ONION_RED',          'Red Onion',           'KG',    'Sibuyas Bombay'),
  ('MANGO',              'Mango (Carabao)',     'KG',    'Ripe carabao mango'),
  ('BANANA',             'Banana (Cavendish)',  'KG',    'Cavendish banana');

-- Allowed units per group, with the factor that converts them to the base unit.
-- The kg-based groups all take the same two rows, so derive them with
-- INSERT ... SELECT instead of writing 23 near-identical pairs by hand.
INSERT INTO catalog_comparisongroupunit (comparison_group, unit, factor_to_base)
SELECT code, 'KG', 1.0000 FROM catalog_comparisongroup WHERE base_unit = 'KG'
UNION ALL
SELECT code, 'G',  0.0010 FROM catalog_comparisongroup WHERE base_unit = 'KG';

-- The two groups whose base unit is not the kilogram.
INSERT INTO catalog_comparisongroupunit (comparison_group, unit, factor_to_base) VALUES
  ('EGGS',        'PIECE', 1.0000),
  ('EGGS',        'TRAY',  30.0000),
  ('COOKING_OIL', 'L',     1.0000),
  ('COOKING_OIL', 'ML',    0.0010);

-- ---------------------------------------------------------------------------
-- 5. Vendors - one catalog_vendor per vendor user, plus its POS extension
-- ---------------------------------------------------------------------------
INSERT INTO catalog_vendor
  (id, name, stall_location, market_section, contact_phone, contact_email, user_id) VALUES
  (1, 'Pedro''s Fresh Catch',        'Stall A-12', 'Section A - Fish',            '0917-555-0101', 'pedro@ecompra.local',     4),
  (2, 'Rosa''s Gulay Stand',         'Stall B-07', 'Section B - Vegetables',      '0917-555-0102', 'rosa@ecompra.local',      5),
  (3, 'Bautista Meat Shop',          'Stall C-03', 'Section C - Meat & Poultry',  '0917-555-0103', 'jose@ecompra.local',      6),
  (4, 'Tan''s Rice & Dry Goods',     'Stall E-01', 'Section E - Dry Goods',       '0917-555-0104', 'luz@ecompra.local',       7),
  (5, 'Villamor Fruits & Gulay',     'Stall D-02', 'Section D - Fruits',          '0917-555-0105', 'andres@ecompra.local',    8),
  (6, 'Nena''s Manok',               'Stall C-09', 'Section C - Meat & Poultry',  '0917-555-0106', 'nena@ecompra.local',      9);

INSERT INTO vendors_vendor (catalog_vendor_id, stall_name, stall_location) VALUES
  (1, 'Pedro''s Fresh Catch',    'Stall A-12'),
  (2, 'Rosa''s Gulay Stand',     'Stall B-07'),
  (3, 'Bautista Meat Shop',      'Stall C-03'),
  (4, 'Tan''s Rice & Dry Goods', 'Stall E-01'),
  (5, 'Villamor Fruits & Gulay', 'Stall D-02'),
  (6, 'Nena''s Manok',           'Stall C-09');

-- ---------------------------------------------------------------------------
-- 6. Products - 34 items across the 9 categories.
--    stock_quantity is the CURRENT balance; section 9 writes the ledger rows
--    that explain how it got there.
-- ---------------------------------------------------------------------------
INSERT INTO catalog_product
  (id, name, description, price, unit_code, availability_code, stock_quantity,
   low_stock_threshold, category_id, vendor_id, comparison_group, stall_location) VALUES
  -- Pedro's Fresh Catch (vendor 1)
  (1,  'Bangus (Milkfish)',            'Whole milkfish, cleaned on request',        180.00, 'KG',     'IN_STOCK',  12, 5, 1, 1, 'BANGUS',     'Stall A-12'),
  (2,  'Tilapia',                      'Farm-raised tilapia, medium size',          140.00, 'KG',     'IN_STOCK',  10, 5, 1, 1, 'TILAPIA',    'Stall A-12'),
  (3,  'Galunggong (Round Scad)',      'Fresh catch, landed this morning',          160.00, 'KG',     'IN_STOCK',   8, 5, 1, 1, 'GALUNGGONG', 'Stall A-12'),
  (4,  'Tulingan (Bullet Tuna)',       'Good for grilling and paksiw',              190.00, 'KG',     'IN_STOCK',   6, 5, 1, 1, 'TULINGAN',   'Stall A-12'),
  (5,  'Hipon (Shrimp)',               'Medium shrimp, fresh',                      380.00, 'KG',     'LOW_STOCK',  6, 5, 1, 1, 'SHRIMP',     'Stall A-12'),
  (6,  'Dried Fish (Tuyo)',            'Sun-dried, sold by weight',                 420.00, 'KG',     'IN_STOCK',   5, 3, 7, 1, NULL,         'Stall A-12'),
  -- Rosa's Gulay Stand (vendor 2)
  (7,  'Tomatoes',                     'Ripe native tomatoes',                       80.00, 'KG',     'IN_STOCK',  15, 5, 5, 2, 'TOMATO',     'Stall B-07'),
  (8,  'Kangkong (Water Spinach)',     'Bundled, ready to cook',                     15.00, 'BUNDLE', 'IN_STOCK',  20, 8, 5, 2, NULL,         'Stall B-07'),
  (9,  'Pechay (Chinese Cabbage)',     'Bundled, crisp leaves',                      20.00, 'BUNDLE', 'IN_STOCK',  25, 8, 5, 2, NULL,         'Stall B-07'),
  (10, 'Ampalaya (Bitter Gourd)',      'Medium size, dark green',                    90.00, 'KG',     'IN_STOCK',   9, 4, 5, 2, NULL,         'Stall B-07'),
  (11, 'Talong (Eggplant)',            'Long purple variety',                        70.00, 'KG',     'IN_STOCK',  11, 4, 5, 2, NULL,         'Stall B-07'),
  (12, 'Garlic (Bawang)',              'Imported garlic, whole bulbs',              160.00, 'KG',     'IN_STOCK',   7, 3, 8, 2, 'GARLIC',     'Stall B-07'),
  (13, 'Red Onion (Sibuyas Bombay)',   'Locally grown red onion',                   190.00, 'KG',     'IN_STOCK',  14, 4, 8, 2, 'ONION_RED',  'Stall B-07'),
  -- Bautista Meat Shop (vendor 3)
  (14, 'Pork Belly (Liempo)',          'Fresh pork belly, sliced on request',       320.00, 'KG',     'IN_STOCK',  10, 4, 2, 3, 'PORK_BELLY', 'Stall C-03'),
  (15, 'Pork Kasim',                   'Pork shoulder, good for adobo',             280.00, 'KG',     'IN_STOCK',  12, 4, 2, 3, 'PORK_KASIM', 'Stall C-03'),
  (16, 'Ground Pork',                  'Ground fresh daily',                        290.00, 'KG',     'IN_STOCK',   8, 3, 2, 3, 'PORK_GROUND','Stall C-03'),
  (17, 'Beef Brisket',                 'For bulalo and nilaga',                     420.00, 'KG',     'LOW_STOCK',  5, 3, 2, 3, 'BEEF_BRISKET','Stall C-03'),
  -- Tan's Rice & Dry Goods (vendor 4)
  (18, 'Well-Milled Rice',             'Everyday rice, per kilo',                    52.00, 'KG',     'IN_STOCK', 100, 20, 6, 4, 'RICE_WELL_MILLED',  'Stall E-01'),
  (19, 'Sinandomeng Rice',             'Long-grain, per kilo',                       58.00, 'KG',     'IN_STOCK',  80, 20, 6, 4, 'RICE_SINANDOMENG',  'Stall E-01'),
  (20, 'Dinorado Rice',                'Aromatic, per kilo',                         68.00, 'KG',     'IN_STOCK',  60, 15, 6, 4, 'RICE_DINORADO',     'Stall E-01'),
  (21, 'Malagkit (Glutinous Rice)',    'For bibingka and suman',                     75.00, 'KG',     'IN_STOCK',  30, 10, 6, 4, 'RICE_MALAGKIT',     'Stall E-01'),
  (22, 'Cooking Oil',                  'Refined palm oil, per liter',                95.00, 'L',      'IN_STOCK',  24, 8, 7, 4, 'COOKING_OIL',       'Stall E-01'),
  (23, 'Brown Sugar',                  'Washed brown sugar, per kilo',               85.00, 'KG',     'IN_STOCK',  20, 6, 7, 4, 'SUGAR_BROWN',       'Stall E-01'),
  (24, 'White Sugar',                  'Refined white sugar, per kilo',              78.00, 'KG',     'IN_STOCK',  25, 6, 7, 4, 'SUGAR_WHITE',       'Stall E-01'),
  (25, 'Tomatoes',                     'Firm tomatoes, good for sauteing',           78.00, 'KG',     'IN_STOCK',  12, 5, 5, 4, 'TOMATO',            'Stall E-01'),
  -- Villamor Fruits & Gulay (vendor 5)
  (26, 'Tomatoes',                     'Vine-ripened tomatoes',                      75.00, 'KG',     'IN_STOCK',  18, 5, 5, 5, 'TOMATO',     'Stall D-02'),
  (27, 'Mango (Carabao)',              'Sweet ripe carabao mango',                  160.00, 'KG',     'IN_STOCK',  15, 5, 4, 5, 'MANGO',      'Stall D-02'),
  (28, 'Banana (Cavendish)',           'Ripe Cavendish banana',                      65.00, 'KG',     'IN_STOCK',  20, 6, 4, 5, 'BANANA',     'Stall D-02'),
  (29, 'Pineapple',                    'Sweet variety, per piece',                   85.00, 'PIECE',  'IN_STOCK',  10, 4, 4, 5, NULL,         'Stall D-02'),
  (30, 'Watermelon',                   'Whole, seedless',                            45.00, 'KG',     'IN_STOCK',   8, 3, 4, 5, NULL,         'Stall D-02'),
  -- Nena's Manok (vendor 6)
  (31, 'Whole Chicken',                'Dressed whole chicken',                     210.00, 'KG',     'IN_STOCK',  12, 4, 3, 6, 'CHICKEN_WHOLE',  'Stall C-09'),
  (32, 'Chicken Breast',               'Boneless breast fillet',                    260.00, 'KG',     'IN_STOCK',   8, 3, 3, 6, 'CHICKEN_BREAST', 'Stall C-09'),
  (33, 'Native Chicken (Bisaya)',      'Free-range native chicken',                 330.00, 'KG',     'LOW_STOCK',  6, 3, 3, 6, 'CHICKEN_NATIVE', 'Stall C-09'),
  (34, 'Eggs (Large)',                 'Large chicken eggs, per tray of 30',        240.00, 'TRAY',   'IN_STOCK',  20, 5, 3, 6, 'EGGS',           'Stall C-09');

-- ---------------------------------------------------------------------------
-- 7. Sample orders. Three shapes, one per TransactionType:
--      order 1 - online order, paid online, delivered
--      order 2 - pickup reservation, down payment made, awaiting collection
--      order 3 - anonymous walk-in sale at the POS
-- ---------------------------------------------------------------------------
INSERT INTO orders_order
  (id, user_id, customer_label, vendor_id, status_code, fulfillment_code,
   total_amount, notes, created_at, updated_at) VALUES
  (1, 2, NULL, 1, 'COMPLETED',        'DELIVERY', 520.00, 'Please clean the fish.', '2026-11-10 09:12:04.000000', '2026-11-10 15:40:11.000000'),
  (2, 2, NULL, 2, 'READY_FOR_PICKUP', 'PICKUP',   290.00, 'Will collect before 6pm.', '2026-11-12 07:45:19.000000', '2026-11-12 11:05:00.000000'),
  (3, NULL, 'Walk-in customer', 1, 'COMPLETED',  'WALK_IN',  320.00, NULL, '2026-11-11 06:58:33.000000', '2026-11-11 06:59:02.000000');

INSERT INTO orders_orderitem (order_id, product_id, quantity, unit_price) VALUES
  (1, 1,  2, 180.00),   -- Bangus    2 kg
  (1, 3,  1, 160.00),   -- Galunggong 1 kg
  (2, 7,  3,  80.00),   -- Tomatoes  3 kg
  (2, 8,  2,  15.00),   -- Kangkong  2 bundles
  (2, 9,  1,  20.00),   -- Pechay    1 bundle
  (3, 2,  1, 140.00),   -- Tilapia   1 kg
  (3, 1,  1, 180.00);   -- Bangus    1 kg

INSERT INTO orders_transaction (id, order_id, transaction_type, reference_no, created_at) VALUES
  (1, 1, 'ONLINE_ORDER',       'ECO-20261110-0001', '2026-11-10 09:12:04.000000'),
  (2, 2, 'PICKUP_RESERVATION', 'ECO-20261112-0002', '2026-11-12 07:45:19.000000'),
  (3, 3, 'POS_WALKIN',         'ECO-20261111-0003', '2026-11-11 06:58:33.000000');

-- Payments. Order 2's row is the DOWN PAYMENT only (half of â‚±290). The balance
-- is settled in cash at the stall, which records a second Payment row
-- (provider 'CASH') at that moment - it is deliberately not seeded, because it
-- has not happened yet. This is the idea doc's pickup flow:
--   Pending -> Down-Payment Confirmed -> Preparing -> Full payment -> Completed
INSERT INTO orders_payment
  (id, transaction_id, provider, provider_reference, amount, status_code, paid_at) VALUES
  (1, 1, 'PAYMAYA', 'SBX-PM-20261110-8F31A2C4', 520.00, 'VERIFIED', '2026-11-10 09:14:22.000000'),
  (2, 2, 'PAYMAYA', 'SBX-PM-20261112-C19D4E77', 145.00, 'VERIFIED', '2026-11-12 07:47:41.000000'),
  (3, 3, 'CASH',    'CASH-ECO-20261111-0003-1', 320.00, 'VERIFIED', '2026-11-11 06:59:02.000000');

-- Delivery booking exists only for the delivery order. The provider name is a
-- sandbox/mock - see the ground rules: delivery is mocked, never a live account.
INSERT INTO orders_deliverybooking
  (id, transaction_id, provider, booking_reference, tracking_url, fee,
   status_code, booked_at, delivered_at) VALUES
  (1, 1, 'LALAMOVE', 'SBX-LM-77120', 'https://sandbox.example/track/SBX-LM-77120',
      95.00, 'DELIVERED', '2026-11-10 09:20:00.000000', '2026-11-10 15:40:11.000000');

-- Vendor-side record. receipt_serial is RC-{reference_no}-{receipt_attempt};
-- reprinting increments receipt_attempt instead of minting a new serial.
INSERT INTO vendors_vendortransaction
  (id, vendor_id, order_id, status_code, receipt_serial, receipt_attempt) VALUES
  (1, 1, 1, 'COMPLETED',        'RC-ECO-20261110-0001-1', 1),
  (2, 2, 2, 'READY_FOR_PICKUP', NULL,                     1),
  (3, 1, 3, 'COMPLETED',        'RC-ECO-20261111-0003-1', 1);

-- ---------------------------------------------------------------------------
-- 8. Cart and favorites for Maria Santos (user 2)
-- ---------------------------------------------------------------------------
INSERT INTO cart_cart (user_id) VALUES (2);

INSERT INTO cart_cartitem (cart_id, product_id, quantity) VALUES
  (2, 27, 2),   -- Mango 2 kg
  (2, 18, 5),   -- Well-Milled Rice 5 kg
  (2, 31, 1);   -- Whole Chicken 1 kg

INSERT INTO favorites_favoriteproduct (user_id, product_id) VALUES (2, 1), (2, 7), (3, 26);
INSERT INTO favorites_favoritevendor  (user_id, vendor_id)  VALUES (2, 1), (2, 2), (3, 2);

-- ---------------------------------------------------------------------------
-- 9. Inventory ledger.
--    Every product gets a RECEIVED opening balance. For the seven products the
--    sample orders touch, the opening is set so that the ledger sums EXACTLY to
--    the stock_quantity in section 6:
--
--      opening = current stock + everything that leaves in this section
--
--      product 1  Bangus      12 + 2 (order 1) + 1 (order 3)          = 15
--      product 2  Tilapia     10 + 1 (order 3)                        = 11
--      product 3  Galunggong   8 + 1 (order 1)                        =  9
--      product 5  Hipon        6 - 1 (recount adjustment below)       =  5
--      product 7  Tomatoes    15 + 3 (order 2)                        = 18
--      product 8  Kangkong    20 + 2 (order 2) + 1 (spoilage below)   = 23
--      product 9  Pechay      25 + 1 (order 2)                        = 26
-- ---------------------------------------------------------------------------
INSERT INTO catalog_inventorymovement (product_id, delta, reason_code, order_id, note, created_at) VALUES
  (1, 15, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000'),
  (2, 11, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000'),
  (3,  9, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000'),
  (5,  5, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000'),
  (7, 18, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000'),
  (8, 23, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000'),
  (9, 26, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000');

INSERT INTO catalog_inventorymovement (product_id, delta, reason_code, order_id, note, created_at)
SELECT id, stock_quantity, 'RECEIVED', NULL, 'Opening balance', '2026-11-09 06:00:00.000000'
FROM catalog_product
WHERE id NOT IN (1, 2, 3, 5, 7, 8, 9);

-- The movements that bring each balance to its current value.
INSERT INTO catalog_inventorymovement (product_id, delta, reason_code, order_id, note, created_at) VALUES
  (1,  -2, 'SOLD_ONLINE', 1, 'Order ECO-20261110-0001', '2026-11-10 09:12:04.000000'),
  (3,  -1, 'SOLD_ONLINE', 1, 'Order ECO-20261110-0001', '2026-11-10 09:12:04.000000'),
  (7,  -3, 'SOLD_ONLINE', 2, 'Order ECO-20261112-0002', '2026-11-12 07:45:19.000000'),
  (8,  -2, 'SOLD_ONLINE', 2, 'Order ECO-20261112-0002', '2026-11-12 07:45:19.000000'),
  (9,  -1, 'SOLD_ONLINE', 2, 'Order ECO-20261112-0002', '2026-11-12 07:45:19.000000'),
  (2,  -1, 'SOLD_WALKIN', 3, 'Walk-in sale ECO-20261111-0003', '2026-11-11 06:58:33.000000'),
  (1,  -1, 'SOLD_WALKIN', 3, 'Walk-in sale ECO-20261111-0003', '2026-11-11 06:58:33.000000'),
  (8,  -1, 'SPOILAGE', NULL, 'Wilted, pulled from display', '2026-11-11 17:30:00.000000'),
  (5,   1, 'ADJUSTMENT', NULL, 'Physical recount: 1 kg found', '2026-11-12 06:15:00.000000');

-- ---------------------------------------------------------------------------
-- 10. Self-check. This SELECT must return ZERO rows.
--     If it returns anything, the ledger and the cached stock disagree, and
--     section 9's arithmetic needs fixing before you build anything on top.
-- ---------------------------------------------------------------------------
SELECT p.id,
       p.name,
       p.stock_quantity                              AS cached_stock,
       COALESCE(SUM(m.delta), 0)                     AS ledger_stock,
       p.stock_quantity - COALESCE(SUM(m.delta), 0)  AS difference
FROM catalog_product p
LEFT JOIN catalog_inventorymovement m ON m.product_id = p.id
GROUP BY p.id, p.name, p.stock_quantity
HAVING difference <> 0;
