# Normalization Analysis

## 1. Method

For each relation: state the candidate keys, then test 1NF $\rightarrow$ 2NF $\rightarrow$ 3NF $\rightarrow$ BCNF, naming the functional dependencies. Where a relation is not in BCNF, say why and whether that is acceptable.

* **1NF (First Normal Form):** Every attribute contains atomic, single-valued data with no repeating groups and a well-defined primary key.
* **2NF (Second Normal Form):** The relation is in 1NF and no non-prime attribute is functionally dependent on a proper subset of any candidate key (no partial dependencies).
* **3NF (Third Normal Form):** The relation is in 2NF and for every non-trivial functional dependency $X \rightarrow A$, either $X$ is a superkey or $A$ is a prime attribute (no transitive dependencies).
* **BCNF (Boyce-Codd Normal Form):** For every non-trivial functional dependency $X \rightarrow A$, $X$ must be a superkey.

---

## 2. Functional dependencies per relation

### `orders_order`

* **Candidate keys:** `id` (surrogate PK)
* **FDs:** `id` $\rightarrow$ `user_id, customer_label, vendor_id, status_code, fulfillment_type_code, total_amount, notes, created_at, updated_at`
* **1NF:** All attributes are atomic; each row represents a single vendor-scoped order.
* **2NF:** Single-attribute primary key (`id`), so partial dependencies are impossible.
* **3NF:** Every non-key attribute describes the order directly (`status_code` holds the single lifecycle authority, and `total_amount` is an order-time snapshot); no non-key attribute determines another non-key attribute.
* **BCNF:** The only determinant (`id`) is a superkey.
* **Verdict:** **3NF, BCNF**

### `orders_orderitem`

* **Candidate keys:** `id` (surrogate PK), `(order_id, product_id)` — assuming a product appears once per order
* **FDs:**
  * `id` $\rightarrow$ `order_id, product_id, quantity, unit_price, created_at`
  * `order_id, product_id` $\rightarrow$ `id, quantity, unit_price, created_at`
* **1NF:** All attributes are atomic; each line item is stored as an individual tuple.
* **2NF:** No partial dependency — `quantity`, `unit_price`, and `created_at` depend on the whole composite key `(order_id, product_id)` (and trivially on `id`).
* **3NF:** No transitive dependency — `unit_price` is the historical price agreed at order time rather than a transitive lookup from `product_id`.
* **BCNF:** Every determinant (`id` and `(order_id, product_id)`) is a superkey.
* **Verdict:** **3NF, BCNF**

### `orders_transaction`

* **Candidate keys:** `id` (surrogate PK), `order_id` (1:1 UK), `reference_no` (UK)
* **FDs:**
  * `id` $\rightarrow$ `order_id, transaction_type_code, reference_no, created_at, updated_at`
  * `order_id` $\rightarrow$ `id, transaction_type_code, reference_no, created_at, updated_at`
  * `reference_no` $\rightarrow$ `id, order_id, transaction_type_code, created_at, updated_at`
* **1NF:** All attributes are atomic.
* **2NF:** All three candidate keys are single attributes, preventing partial dependencies.
* **3NF:** No transitive dependency — `Transaction` intentionally carries no duplicated status column (`Order.status` owns lifecycle; `Payment.status` owns settlement).
* **BCNF:** Every determinant (`id`, `order_id`, `reference_no`) is a candidate key and therefore a superkey.
* **Verdict:** **3NF, BCNF**

### `orders_payment`

* **Candidate keys:** `id` (surrogate PK), `(provider, provider_reference)` (`unique_together`)
* **FDs:**
  * `id` $\rightarrow$ `transaction_id, provider, provider_reference, amount, status_code, raw_response, paid_at, created_at`
  * `provider, provider_reference` $\rightarrow$ `id, transaction_id, amount, status_code, raw_response, paid_at, created_at`
* **1NF:** All scalar attributes are atomic (`raw_response` is stored as a single opaque JSON document rather than a repeating relational group).
* **2NF:** No partial dependency — `amount`, `status_code`, `paid_at`, and `transaction_id` depend on the full pair `(provider, provider_reference)` because gateway reference IDs are only unique per provider.
* **3NF:** No transitive dependency — every non-key attribute depends directly on the payment attempt identity.
* **BCNF:** Both determinants (`id` and `(provider, provider_reference)`) are candidate keys.
* **Verdict:** **3NF, BCNF**

### `orders_deliverybooking`

* **Candidate keys:** `id` (surrogate PK), `transaction_id` (1:1 UK)
* **FDs:**
  * `id` $\rightarrow$ `transaction_id, provider, booking_reference, tracking_url, fee, status_code, raw_response, booked_at, delivered_at, created_at, updated_at`
  * `transaction_id` $\rightarrow$ `id, provider, booking_reference, tracking_url, fee, status_code, raw_response, booked_at, delivered_at, created_at, updated_at`
  * *(Note: `(provider, booking_reference)` is functionally a business identifier if external couriers issue unique booking IDs per provider, though not declared `UNIQUE` in the schema.)*
* **1NF:** All attributes are atomic (`raw_response` treated as a single JSON payload).
* **2NF:** Candidate keys (`id`, `transaction_id`) are single-attribute keys; no partial dependencies exist.
* **3NF:** No transitive dependency — courier progress (`status_code`, `delivered_at`) and booking metadata belong directly to the booking.
* **BCNF:** Every declared determinant (`id`, `transaction_id`) is a superkey.
* **Verdict:** **3NF, BCNF**

### `catalog_product`

* **Candidate keys:** `id` (surrogate PK)
* **FDs:** `id` $\rightarrow$ `name, description, image_url, price, unit_code, stall_location, availability_code, stock_quantity, low_stock_threshold, category_id, vendor_id, comparison_group_code, created_at, updated_at`
* **1NF:** All attributes are atomic.
* **2NF:** Single-attribute primary key (`id`), so no partial dependencies exist.
* **3NF:** No transitive dependency — `unit_code` is the product's selling unit (not transitively fixed by `comparison_group_code`), `stall_location` is a listing-level location (not transitively determined by `vendor_id`), and `availability_code` is explicitly stored rather than derived solely from `stock_quantity` (e.g., `HIDDEN` state).
* **BCNF:** The sole determinant (`id`) is a superkey.
* **Verdict:** **3NF, BCNF**

### `catalog_comparisongroup`

* **Candidate keys:** `code` (natural PK)
* **FDs:** `code` $\rightarrow$ `name, base_unit_code, description, is_active, created_at, updated_at`
* **1NF:** All attributes are atomic.
* **2NF:** Single-attribute primary key (`code`), so no partial dependencies exist.
* **3NF:** No transitive dependency — `name`, `base_unit_code`, `description`, and `is_active` all describe the comparison group directly.
* **BCNF:** The sole determinant (`code`) is a superkey.
* **Verdict:** **3NF, BCNF**

### `catalog_comparisongroupunit`

* **Candidate keys:** `id` (surrogate PK), `(comparison_group_code, unit_code)` (`unique_together`)
* **FDs:**
  * `id` $\rightarrow$ `comparison_group_code, unit_code, factor_to_base`
  * `comparison_group_code, unit_code` $\rightarrow$ `id, factor_to_base`
* **1NF:** All attributes are atomic.
* **2NF:** `factor_to_base` depends on the entire composite key `(comparison_group_code, unit_code)` (e.g., `1 pc = 0.25 kg` depends on both the group and the unit).
* **3NF:** No transitive dependency.
* **BCNF:** Every determinant (`id` and `(comparison_group_code, unit_code)`) is a superkey.
* **Verdict:** **3NF, BCNF**

### `cart_cartitem`

* **Candidate keys:** `id` (surrogate PK), `(cart_id, product_id)` (`unique_together`)
* **FDs:**
  * `id` $\rightarrow$ `cart_id, product_id, quantity, created_at`
  * `cart_id, product_id` $\rightarrow$ `id, quantity, created_at`
* **1NF:** All attributes are atomic; no repeating product arrays inside `Cart`.
* **2NF:** `quantity` and `created_at` depend on the full composite key `(cart_id, product_id)`.
* **3NF:** No transitive dependency — product price and vendor are not duplicated onto `CartItem`.
* **BCNF:** Both determinants (`id` and `(cart_id, product_id)`) are candidate keys.
* **Verdict:** **3NF, BCNF**

### `vendors_vendortransaction`

* **Candidate keys:** `id` (surrogate PK), `order_id` (1:1 UK)
* **FDs:**
  * `id` $\rightarrow$ `vendor_id, order_id, status_code, receipt_serial, receipt_attempt, created_at`
  * `order_id` $\rightarrow$ `id, vendor_id, status_code, receipt_serial, receipt_attempt, created_at`
  * *(Note: `receipt_serial` follows the format `RC-{reference_no}-{receipt_attempt}`, meaning `order_id` and `receipt_attempt` structurally generate `receipt_serial`, which is still determined by superkey `order_id`.)*
* **1NF:** All attributes are atomic.
* **2NF:** Candidate keys (`id`, `order_id`) are single attributes.
* **3NF:** No transitive dependency within the table (`vendor_id` identifies the `PosVendor` handling the transaction).
* **BCNF:** Every determinant (`id`, `order_id`) is a superkey.
* **Verdict:** **3NF, BCNF**

---

## 3. How the lookup tables serve normalization

`TransactionStatus`, `PaymentStatus`, `DeliveryStatus`, `FulfillmentMethod`, `TransactionType`, `AvailabilityStatus`, `UnitOfMeasure`, `InventoryReason`, and `Category` each hold one row per code. Storing the code on the fact table instead of the description means the description (and operational flags like `sort_order`, `is_terminal`, `is_orderable`, and `direction`) is stored once — removing a transitive dependency ($PK \rightarrow \text{code} \rightarrow \text{description}$) and preventing update, insertion, and deletion anomalies.

---

## 4. Deliberate denormalizations (documented, not accidental)

| Column | Denormalized from | Why it is safe |
| :--- | :--- | :--- |
| `catalog_product.unit` | `catalog_comparisongroup.base_unit` | The displayed selling unit legitimately differs from the comparison base unit (e.g., sold per piece or bundle, compared per kilogram). Writes go through the vendor product form, not ad-hoc. |
| `catalog_product.stall_location` | `catalog_vendor.stall_location` | A per-listing override; a vendor may sell a product from a different market stall than their primary storefront. |
| `orders_orderitem.unit_price`, `orders_order.total_amount` | Recomputable from product prices | **Intentional snapshot**: an order must record the price agreed at order time, not today's catalog price. This is not a normalization violation — it is a distinct historical fact. |
| `catalog_product.stock_quantity` | Sum of `catalog_inventorymovement.delta` | A cached balance for fast catalog read performance; the `InventoryMovement` ledger is the source of truth and the database trigger keeps them consistent. |

---

## 5. Why Order, Transaction and Payment are three relations

* **Order** — what the customer bought and its customer-facing lifecycle (`Order.status`), scoped to one vendor (changes rarely after creation).
* **Transaction** — the commercial reference (`reference_no`) and classification (`ONLINE_ORDER`, `PICKUP_RESERVATION`, `POS_WALKIN`), strictly 1:1 with `Order` and carrying no status of its own.
* **Payment** — one row per payment attempt (`0..N` per `Transaction`), isolating settlement status (`Payment.status`), gateway references (`provider`, `provider_reference`), and `CASH` receipts.

A single combined table would either require repeating columns/arrays for multiple failed or retried payment attempts (violating **1NF**) or repeat order and commercial header data across every payment attempt (introducing redundancy and **2NF/3NF** update anomalies).

---

## 6. Known weaknesses

* **Cross-table status redundancy (`vendors_vendortransaction.status_code` vs. `orders_order.status_code`):** `VendorTx` has a 1:1 relationship with `Order` (`order_id` UK) and carries its own `status` foreign key to `TransactionStatus`, even though the architecture rulings state that `Order.status` is the single lifecycle authority. Keeping `status_code` on `VendorTx` creates a cross-relation synchronization risk if one is updated without the other; it is accepted as a POS-scoped projection/audit state for `vendors.VendorTransaction`, guarded by application service methods (`PosSvc`).
* **Composite string encoding in `vendors_vendortransaction.receipt_serial`:** `receipt_serial` embeds both `Transaction.reference_no` and `receipt_attempt` (`RC-{reference_no}-{receipt_attempt}`), which technically encodes non-atomic sub-components inside a single string. It is accepted because BIR-style receipt serials must be persisted as an immutable, auditable string once printed.
* **Unenforced cross-table foreign key constraint on `catalog_product.unit`:** `Product.unit` must be one of the units allowed in `ComparisonGroupUnit` for that product's `comparison_group`, which cannot be enforced by a standard single-column FK without a composite FK `(comparison_group_code, unit_code)`. This is accepted because `comparison_group` is nullable (`NULL` for standalone products), so validation is enforced at the application/form layer instead.
* **Opaque JSON payloads (`orders_payment.raw_response` and `orders_deliverybooking.raw_response`):** Gateway and courier responses contain nested, provider-specific attributes stored in JSON columns rather than decomposed relational tables. This is accepted because third-party webhook payloads vary by provider (`GCASH`, `MAYA`, `GRABEXPRESS`, `LALAMOVE`, etc.) and are retained strictly for audit/debugging rather than relational querying.
* **Conditional nullability on `orders_order` (`user_id` vs. `customer_label`):** `user_id` is nullable exclusively when `fulfillment_type = WALK_IN` (where `customer_label` may be populated instead). Standard relational FDs do not express conditional domain rules (`fulfillment_type != WALK_IN` $\Rightarrow$ `user_id IS NOT NULL`), so this invariant must be enforced via a database `CHECK` constraint or service-layer validation.