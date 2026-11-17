# ER-to-Relational Mapping

## Mapping rules applied
- Strong entity $\rightarrow$ its own relation, primary key = the entity's identifier.
- 1:1 relationship $\rightarrow$ the primary key of one side becomes a FK (unique) on the other.
- 1:N relationship $\rightarrow$ the primary key of the "1" side becomes a FK on the "N" side.
- M:N relationship $\rightarrow$ a new relation whose primary key is the pair of FKs.
- Multivalued attribute $\rightarrow$ its own relation.
- Weak entity $\rightarrow$ a relation whose primary key includes the owner's key.

---

## Tables

### Users & Profiles

#### `auth_user`
| | |
|---|---|
| Source entity | User (Django built-in) |
| Primary key | `id` (surrogate) |
| Foreign keys | none |
| Nullable FKs | none |
| Unique constraints | `username` |
| Check constraints | none |
| Cardinality justification | Root identity entity extended 1:0..1 by profiles, storefront, and cart; 1:N with orders and favorites |
| Normal form | 3NF — atomic user attributes (`username`, `email`, `password_hash`) depend solely on `id` |

#### `users_userprofile`
| | |
|---|---|
| Source entity | UserProfile |
| Primary key | `user_id` (FK, PK — shared primary key) |
| Foreign keys | `user_id` $\rightarrow$ `auth_user(id)` |
| Nullable FKs | none |
| Unique constraints | `user_id` (enforced by PK) |
| Check constraints | none |
| Cardinality justification | 1:0..1 extension of `User` storing role flag (`is_vendor`) |
| Normal form | 3NF — `is_vendor` and timestamps depend exclusively on `user_id` |

#### `users_customerprofile`
| | |
|---|---|
| Source entity | CustomerProfile |
| Primary key | `user_id` (FK, PK — shared primary key) |
| Foreign keys | `user_id` $\rightarrow$ `auth_user(id)` |
| Nullable FKs | none |
| Unique constraints | `user_id` (enforced by PK) |
| Check constraints | none |
| Cardinality justification | 1:0..1 extension of `User` storing customer contact/delivery info (`phone`, `address`) |
| Normal form | 3NF — `phone` and `address` depend solely on `user_id` |

---

### Catalog & Inventory

#### `catalog_vendor`
| | |
|---|---|
| Source entity | Market Vendor (`catalog.Vendor`) |
| Primary key | `id` (surrogate) |
| Foreign keys | `user_id` $\rightarrow$ `auth_user(id)` |
| Nullable FKs | none — every storefront has an owner (`NOT NULL`) |
| Unique constraints | `user_id` (UK — one user owns at most one storefront) |
| Check constraints | none |
| Cardinality justification | 1:0..1 with `User` (`user_id` UK); 1:N with `Product`, `Order`, and `FavoriteVendor` |
| Normal form | 3NF — single source of vendor identity (`name`, `stall_location`, `market_section`, contact details) dependent only on `id` |

#### `catalog_category`
| | |
|---|---|
| Source entity | Category |
| Primary key | `id` (surrogate) |
| Foreign keys | none |
| Nullable FKs | none |
| Unique constraints | `slug` (UK) |
| Check constraints | none |
| Cardinality justification | One category classifies many products (1:N) |
| Normal form | 3NF — `name`, `slug`, `is_active`, and timestamps depend solely on `id` |

#### `catalog_unitofmeasure`
| | |
|---|---|
| Source entity | UnitOfMeasure |
| Primary key | `code` (natural string PK) |
| Foreign keys | none |
| Nullable FKs | none |
| Unique constraints | `code` (enforced by PK) |
| Check constraints | none |
| Cardinality justification | One unit prices many products (1:N), acts as `base_unit` for comparison groups (1:N), and participates in `ComparisonGroupUnit` (1:N) |
| Normal form | 3NF — lookup table where `name`, `description`, and `is_active` depend directly on `code` |

#### `catalog_comparisongroup`
| | |
|---|---|
| Source entity | ComparisonGroup |
| Primary key | `code` (natural string PK) |
| Foreign keys | `base_unit_code` $\rightarrow$ `catalog_unitofmeasure(code)` |
| Nullable FKs | none |
| Unique constraints | `code` (enforced by PK) |
| Check constraints | none |
| Cardinality justification | One base `UnitOfMeasure` defines many comparison groups (1:N); one comparison group groups many products (1:N) |
| Normal form | 3NF — `name`, `base_unit_code`, `description`, and `is_active` depend directly on `code` |

#### `catalog_comparisongroupunit`
| | |
|---|---|
| Source entity | ComparisonGroupUnit |
| Primary key | `id` (surrogate) |
| Foreign keys | `comparison_group_code` $\rightarrow$ `catalog_comparisongroup(code)`, `unit_code` $\rightarrow$ `catalog_unitofmeasure(code)` |
| Nullable FKs | none |
| Unique constraints | `unique_together (comparison_group_code, unit_code)` |
| Check constraints | `factor_to_base > 0` |
| Cardinality justification | Associative bridge resolving M:N between `ComparisonGroup` and `UnitOfMeasure` with conversion attribute `factor_to_base` |
| Normal form | 3NF — `factor_to_base` depends on the candidate key `(comparison_group_code, unit_code)` and surrogate `id` |

#### `catalog_availabilitystatus`
| | |
|---|---|
| Source entity | AvailabilityStatus |
| Primary key | `code` (natural string PK) |
| Foreign keys | none |
| Nullable FKs | none |
| Unique constraints | `code` (enforced by PK) |
| Check constraints | none |
| Cardinality justification | One availability status (`IN_STOCK`, `LOW_STOCK`, `OUT_OF_STOCK`, `HIDDEN`) describes many products (1:N) |
| Normal form | 3NF — lookup metadata (`description`, `sort_order`, `is_orderable`) depends solely on `code` |

#### `catalog_product`
| | |
|---|---|
| Source entity | Product |
| Primary key | `id` (surrogate) |
| Foreign keys | `vendor_id` $\rightarrow$ `catalog_vendor(id)`, `category_id` $\rightarrow$ `catalog_category(id)`, `unit_code` $\rightarrow$ `catalog_unitofmeasure(code)`, `availability_code` $\rightarrow$ `catalog_availabilitystatus(code)`, `comparison_group_code` $\rightarrow$ `catalog_comparisongroup(code)` NULL |
| Nullable FKs | `comparison_group_code` — a product need not be in a comparison group |
| Unique constraints | none |
| Check constraints | `price >= 0`, `stock_quantity >= 0` |
| Cardinality justification | One vendor sells many products (1:N); one category classifies many products (1:N); one unit prices many products (1:N) |
| Normal form | 3NF — no non-key attribute depends on another non-key attribute |

#### `catalog_inventoryreason`
| | |
|---|---|
| Source entity | InventoryReason |
| Primary key | `code` (natural string PK) |
| Foreign keys | none |
| Nullable FKs | none |
| Unique constraints | `code` (enforced by PK) |
| Check constraints | `direction IN ('IN', 'OUT', 'ADJUST')` |
| Cardinality justification | One reason (`RECEIVED`, `SOLD_ONLINE`, `SOLD_WALKIN`, `SPOILAGE`, `ADJUSTMENT`) classifies many inventory movements (1:N) |
| Normal form | 3NF — lookup attributes (`description`, `direction`) depend strictly on `code` |

#### `catalog_inventorymovement`
| | |
|---|---|
| Source entity | InventoryMovement |
| Primary key | `id` (surrogate) |
| Foreign keys | `product_id` $\rightarrow$ `catalog_product(id)`, `reason_code` $\rightarrow$ `catalog_inventoryreason(code)`, `order_id` $\rightarrow$ `orders_order(id)` NULL |
| Nullable FKs | `order_id` — set only when the stock movement came from an online or walk-in sale |
| Unique constraints | none |
| Check constraints | `delta != 0` |
| Cardinality justification | One product has many stock ledger entries (1:N); one reason classifies many movements (1:N); one order may cause multiple movements (1:N) |
| Normal form | 3NF — ledger entries (`delta`, `note`, `created_at`) depend only on `id` |

---

### Cart

#### `cart_cart`
| | |
|---|---|
| Source entity | Cart |
| Primary key | `user_id` (FK, PK — shared primary key) |
| Foreign keys | `user_id` $\rightarrow$ `auth_user(id)` |
| Nullable FKs | none |
| Unique constraints | `user_id` (enforced by PK) |
| Check constraints | none |
| Cardinality justification | 1:0..1 active cart per `User`; 1:N container for `CartItem` rows |
| Normal form | 3NF — `created_at` depends solely on `user_id` |

#### `cart_cartitem`
| | |
|---|---|
| Source entity | CartItem |
| Primary key | `id` (surrogate) |
| Foreign keys | `cart_id` $\rightarrow$ `cart_cart(user_id)`, `product_id` $\rightarrow$ `catalog_product(id)` |
| Nullable FKs | none |
| Unique constraints | `unique_together (cart_id, product_id)` |
| Check constraints | `quantity > 0` |
| Cardinality justification | Associative entity resolving M:N between `Cart` and `Product` |
| Normal form | 3NF — `quantity` and `created_at` depend on `id` and candidate key `(cart_id, product_id)` |

---

### Orders, Payments & Delivery Lookups

#### `orders_transactiontype`
| | |
|---|---|
| Source entity | TransactionType |
| Primary key | `code` (natural string PK) |
| Foreign keys | none |
| Nullable FKs | none |
| Unique constraints | `code` (enforced by PK) |
| Check constraints | none |
| Cardinality justification | One transaction type (`ONLINE_ORDER`, `PICKUP_RESERVATION`, `POS_WALKIN`) classifies many transactions (1:N) |
| Normal form | 3NF — lookup `description` depends directly on `code` |

#### `orders_transactionstatus`
| | |
|---|---|
| Source entity | TransactionStatus |
| Primary key | `code` (natural string PK) |
| Foreign keys | none |
| Nullable FKs | none |
| Unique constraints | `code` (enforced by PK) |
| Check constraints | none |
| Cardinality justification | One lifecycle status (`PENDING_PAYMENT`, `CONFIRMED`, `PREPARING`, `READY_FOR_PICKUP`, `OUT_FOR_DELIVERY`, `COMPLETED`, `CANCELLED`) applies to many orders and vendor POS records (1:N) |
| Normal form | 3NF — `description` and `sort_order` depend directly on `code` |

#### `orders_fulfillmentmethod`
| | |
|---|---|
| Source entity | FulfillmentMethod |
| Primary key | `code` (natural string PK) |
| Foreign keys | none |
| Nullable FKs | none |
| Unique constraints | `code` (enforced by PK) |
| Check constraints | none |
| Cardinality justification | One fulfillment method (`PICKUP`, `DELIVERY`, `WALK_IN`) classifies many orders (1:N) |
| Normal form | 3NF — lookup `description` depends directly on `code` |

#### `orders_paymentstatus`
| | |
|---|---|
| Source entity | PaymentStatus |
| Primary key | `code` (natural string PK) |
| Foreign keys | none |
| Nullable FKs | none |
| Unique constraints | `code` (enforced by PK) |
| Check constraints | none |
| Cardinality justification | One payment status (`PENDING`, `VERIFIED`, `FAILED`, `REFUNDED`) classifies many payment attempts (1:N) |
| Normal form | 3NF — `description` and `is_terminal` depend directly on `code` |

#### `orders_deliverystatus`
| | |
|---|---|
| Source entity | DeliveryStatus |
| Primary key | `code` (natural string PK) |
| Foreign keys | none |
| Nullable FKs | none |
| Unique constraints | `code` (enforced by PK) |
| Check constraints | none |
| Cardinality justification | One delivery status (`BOOKED`, `IN_TRANSIT`, `DELIVERED`, `FAILED`, `CANCELLED`) classifies many delivery bookings (1:N) |
| Normal form | 3NF — `description` and `is_terminal` depend directly on `code` |

---

### Orders, Payments & Delivery

#### `orders_order`
| | |
|---|---|
| Source entity | Order |
| Primary key | `id` (surrogate) |
| Foreign keys | `user_id` $\rightarrow$ `auth_user(id)` NULL, `vendor_id` $\rightarrow$ `catalog_vendor(id)`, `status_code` $\rightarrow$ `orders_transactionstatus(code)`, `fulfillment_type_code` $\rightarrow$ `orders_fulfillmentmethod(code)` |
| Nullable FKs | `user_id` — `NULL` only for anonymous `WALK_IN` sales at vendor POS |
| Unique constraints | none |
| Check constraints | `total_amount >= 0` |
| Cardinality justification | One order belongs to at most one user (0..1:N) and strictly one vendor (1:N); contains 1..N `OrderItem` rows; extended 1:0..1 by `Transaction` and `VendorTx` |
| Normal form | 3NF — single lifecycle authority (`status_code`); order-level attributes (`customer_label`, `total_amount`, `notes`) depend solely on `id` |

#### `orders_orderitem`
| | |
|---|---|
| Source entity | OrderItem |
| Primary key | `id` (surrogate) |
| Foreign keys | `order_id` $\rightarrow$ `orders_order(id)`, `product_id` $\rightarrow$ `catalog_product(id)` |
| Nullable FKs | none |
| Unique constraints | none |
| Check constraints | `quantity > 0`, `unit_price >= 0` |
| Cardinality justification | Associative line-item entity resolving M:N between `Order` and `Product` (`1..*` items per order) |
| Normal form | 3NF — `unit_price` is a point-in-time snapshot at order creation (not transitively dependent on current `Product.price`), and line total is not stored |

#### `orders_transaction`
| | |
|---|---|
| Source entity | Transaction |
| Primary key | `id` (surrogate) |
| Foreign keys | `order_id` $\rightarrow$ `orders_order(id)`, `transaction_type_code` $\rightarrow$ `orders_transactiontype(code)` |
| Nullable FKs | none |
| Unique constraints | `order_id` (1:1 with `Order`), `reference_no` (UK) |
| Check constraints | none |
| Cardinality justification | 1:0..1 commercial record linked to `Order`; 1:N parent of `Payment` attempts; 1:0..1 parent of `DeliveryBooking` |
| Normal form | 3NF — carries no duplicated status column; `reference_no` and `transaction_type_code` depend only on `id` |

#### `orders_payment`
| | |
|---|---|
| Source entity | Payment |
| Primary key | `id` (surrogate) |
| Foreign keys | `transaction_id` $\rightarrow$ `orders_transaction(id)`, `status_code` $\rightarrow$ `orders_paymentstatus(code)` |
| Nullable FKs | none |
| Unique constraints | `unique_together (provider, provider_reference)` |
| Check constraints | `amount >= 0` |
| Cardinality justification | One transaction can have multiple payment attempts (1:N); one payment status classifies many payment records (1:N) |
| Normal form | 3NF — settlement authority (`status_code`, `amount`, `provider`, `raw_response`, `paid_at`) depends solely on `id` |

#### `orders_deliverybooking`
| | |
|---|---|
| Source entity | DeliveryBooking |
| Primary key | `id` (surrogate) |
| Foreign keys | `transaction_id` $\rightarrow$ `orders_transaction(id)`, `status_code` $\rightarrow$ `orders_deliverystatus(code)` |
| Nullable FKs | none |
| Unique constraints | `transaction_id` (1:1 with `Transaction`) |
| Check constraints | `fee >= 0` |
| Cardinality justification | 1:0..1 with `Transaction` (created only for `DELIVERY` orders after payment verification); 1:N from `DeliveryStatus` |
| Normal form | 3NF — courier progress (`status_code`, `provider`, `booking_reference`, `tracking_url`, `fee`, `delivered_at`) depends only on `id` |

---

### Vendors POS

#### `vendors_vendor`
| | |
|---|---|
| Source entity | POS Vendor (`vendors.Vendor`) |
| Primary key | `catalog_vendor_id` (FK, PK — shared primary key) |
| Foreign keys | `catalog_vendor_id` $\rightarrow$ `catalog_vendor(id)` |
| Nullable FKs | none |
| Unique constraints | `catalog_vendor_id` (enforced by PK) |
| Check constraints | none |
| Cardinality justification | 1:0..1 POS extension of `CatalogVendor` (not a second link to `User`); 1:N with `VendorTransaction` |
| Normal form | 3NF — POS-specific attributes (`stall_name`, `stall_location`) depend directly on `catalog_vendor_id` |

#### `vendors_vendortransaction`
| | |
|---|---|
| Source entity | Vendor POS Transaction (`vendors.VendorTransaction`) |
| Primary key | `id` (surrogate) |
| Foreign keys | `vendor_id` $\rightarrow$ `vendors_vendor(catalog_vendor_id)`, `order_id` $\rightarrow$ `orders_order(id)`, `status_code` $\rightarrow$ `orders_transactionstatus(code)` |
| Nullable FKs | none |
| Unique constraints | `order_id` (1:1 with `Order`) |
| Check constraints | `receipt_attempt >= 1` |
| Cardinality justification | 1:0..1 POS audit/receipt record per `Order`; 1:N handled by a `PosVendor` |
| Normal form | 3NF — receipt auditing attributes (`receipt_serial`, `receipt_attempt`, `status_code`) depend solely on `id` |

---

### Favorites

#### `favorites_favoriteproduct`
| | |
|---|---|
| Source entity | FavoriteProduct |
| Primary key | `id` (surrogate) |
| Foreign keys | `user_id` $\rightarrow$ `auth_user(id)`, `product_id` $\rightarrow$ `catalog_product(id)` |
| Nullable FKs | none |
| Unique constraints | `unique_together (user_id, product_id)` |
| Check constraints | none |
| Cardinality justification | Associative bridge resolving M:N wishlist/favorites relationship between `User` and `Product` |
| Normal form | 3NF — `created_at` depends strictly on `id` and candidate key `(user_id, product_id)` |

#### `favorites_favoritevendor`
| | |
|---|---|
| Source entity | FavoriteVendor |
| Primary key | `id` (surrogate) |
| Foreign keys | `user_id` $\rightarrow$ `auth_user(id)`, `vendor_id` $\rightarrow$ `catalog_vendor(id)` |
| Nullable FKs | none |
| Unique constraints | `unique_together (user_id, vendor_id)` |
| Check constraints | none |
| Cardinality justification | Associative bridge resolving M:N saved-vendor relationship between `User` and `CatalogVendor` |
| Normal form | 3NF — `created_at` depends strictly on `id` and candidate key `(user_id, vendor_id)` |

---

## Deferred / derived values
| Value | Stored? | Why |
|---|---|---|
| `orders_orderitem.unit_price` | stored | price snapshot — the price at order time must not change later |
| `orders_order.total_amount` | stored | same reason; also the amount the payment must match |
| line total (`qty` $\times$ `unit_price`) | **not** stored | derived attribute — storing it risks update anomalies; compute it |
| `catalog_product.stock_quantity` | stored | running balance maintained by the trigger, from the `InventoryMovement` ledger |
| `change_due` (`cash_tendered` $-$ `total_amount`) | **not** stored | derived at POS checkout from tendered cash and `orders_order.total_amount` — storing it would duplicate arithmetic |
| equivalent unit price (`price` $\div$ `factor_to_base`) | **not** stored | derived dynamically using `ComparisonGroupUnit.factor_to_base` — storing it would go stale whenever `Product.price` updates |