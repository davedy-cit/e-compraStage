# E-Compra — Design Consistency Review

**Scope:** `docs/uml/er-diagram.puml`, `class-diagram.puml`, `sequence-diagram.puml`, `activity-diagram.puml`,
`use-case.puml` — cross-checked against each other and against `docs/Project Idea Development-e-Compra.docx`.

**Date:** 2026-11-12 · **Reviewer:** project coach · **Status:** findings only — decisions are the student's (step M0.3)

---

## Method

Every entity, attribute, relationship, cardinality, status code, API endpoint and use case in the five diagrams
was extracted and compared on four axes:

1. **ERD ↔ class diagram** — same entities? same attributes? same cardinalities?
2. **ERD ↔ sequence diagram** — does every object the sequence writes to actually exist in the ERD, with the fields it writes?
3. **ERD/class ↔ activity + use-case** — do the status transitions and preconditions agree?
4. **All five ↔ the idea document** — is every stated feature modelled, and does the described behaviour match?

**Totals: 32 findings — 8 critical, 14 major, 10 minor.**

---

## Verdict summary

| Severity | Count | Meaning |
|---|---|---|
| 🔴 **Critical** | 8 | The design cannot be implemented consistently as written. **Must be decided in M0.3 before DDL (M0.7).** |
| 🟠 **Major** | 14 | A real defect or a required design decision. Fix during M0.3/M0.4, or the defect propagates into M2 models. |
| 🟡 **Minor** | 10 | Cosmetic or documentary. Fix in M0.4 or note in `NORMALIZATION.md`. |

**Headline:** the five diagrams are individually well made and share one schema faithfully — the ERD and class
diagram agree on every entity and attribute. The problems are in **behaviour**: the order-status model is
specified three different ways, the pickup flow has a genuine logical flaw, and two idea-document features
(inventory tracking, walk-in POS sales) have **no data model at all**.

---

## 🔴 Critical findings

### C1 · The pickup order flow is specified three different ways — and two of them are self-contradictory

| Source | Pickup flow |
|---|---|
| Idea doc (lines 87–96) | Pending → **Down-Payment Confirmed** → Preparing → **Full payment confirmed upon Pickup** → Completed |
| `activity-diagram.puml:72-83` | `PENDING_PAYMENT` → *(cash tendered)* → `CONFIRMED` → *(confirm pickup)* → `COMPLETED`, **"skips PREPARING/READY_FOR_PICKUP"** |
| `use-case.puml:60,62` | UC16: cash only for PICKUP in `PENDING_PAYMENT`. UC18: confirm pickup only for CONFIRMED; **skips PREPARING / READY_FOR_PICKUP** |
| `sequence-diagram.puml:94,133` | POS queue lists **`CONFIRMED`** orders → `PREPARING` → `READY_FOR_PICKUP` → confirm pickup from **any** of the three → `COMPLETED` |

**Two distinct conflicts here, not one:**

**(a) Does the pickup flow have a Preparing/Ready stage at all?**
Activity + use-case say no (direct `CONFIRMED → COMPLETED`). Sequence + idea doc + the POS screen spec say yes.
The UML contradicts itself, so "the UML is the design of record" does not resolve it.

**(b) The chicken-and-egg flaw.** `activity-diagram.puml:72` only lets a vendor act on an order that is
`PICKUP + PENDING_PAYMENT`, and `:77` advances it to `CONFIRMED` **when cash is received**. But cash is received
**at the stall, at pickup** — by which time the goods should already be prepared. So as drawn, the vendor cannot
see or prepare the order until the customer has already arrived and paid. The "Preparing" step the idea doc
describes is unreachable in that flow.

`sequence-diagram.puml` has the mirror-image problem: its POS queue lists **`CONFIRMED`** orders
(`:94`) and never mentions `PENDING_PAYMENT`, so a pickup reservation would never appear in the queue the
cash-payment endpoint is supposed to serve.

**Impact:** this is the single most visible flow in the demo (the vendor POS is key feature 6). Blocks M3.

---

### C2 · There is no inventory model — but the idea doc and the course matrix both require one

`er-diagram.puml:101` gives `Product` an `availability` **CharField** and nothing else. There is no quantity
anywhere in the schema.

Required by:
- Idea doc line 135: *"Inventory automatically updates whenever products are sold through either walk-in transactions or online orders."*
- Idea doc line 126: *"Real-time inventory tracking"*
- Idea doc line 138: *"Reduced inventory discrepancies"*
- Idea doc line 149: vendor dashboard must show *"Inventory movement"*
- `PROJECT_TIMELINE.md` §5: **"Trigger: automatic inventory decrement on sale"** — the stored-procedure/trigger lesson has no target object.

**Impact:** one of the seven key features and one of the nine course lessons are unbuildable. This is the
largest single hole in the design.

---

### C3 · No canonical status-code list exists anywhere

`TransactionStatus`, `PaymentStatus`, `DeliveryStatus` and `FulfillmentMethod` are lookup tables — but **no
diagram ever lists their rows.** The codes that *are* used are scattered and mutually inconsistent:

| Code | Where it appears |
|---|---|
| `PENDING_PAYMENT` | activity diagram only |
| `CONFIRMED` | sequence, activity, use-case |
| `PREPARING`, `READY_FOR_PICKUP` | sequence (and the POS screen spec) |
| `COMPLETED`, `CANCELLED` | sequence, activity |
| `SUCCESSFUL`, `FAILED` | **sequence diagram only — applied to `Transaction.status`** |
| `VERIFIED`, `FAILED` | sequence — applied to `Payment.status` |
| `BOOKED`, `FAILED` | sequence — applied to `DeliveryBooking.status` |
| **`OUT_FOR_DELIVERY`** | **nowhere in the UML — but required by the idea doc (line 84)** |

**Impact:** the seed data (`sql/03_seed.sql`), the Django `choices`, and every status guard depend on this list.
It must be frozen before DDL. Also note `Transaction.status` and `Payment.status` are **two parallel status
fields updated by the same event** (`sequence-diagram.puml:51-52` sets Payment `VERIFIED` *and* Transaction
`SUCCESSFUL`) — see M9.

---

### C4 · Multi-vendor checkout produces N orders, N payments and N deliveries — nothing groups them

`sequence-diagram.puml:28-35` splits a cart into **one `Order` per vendor**. The ERD then makes
`Payment → Transaction → Order` **1:1** (`er-diagram.puml:182,204`). Therefore a 3-vendor cart requires
**3 separate payments**, and `DeliveryBooking` is 1:1 with `Transaction` (`:204`) so it also requires
**3 separate delivery bookings**.

The idea doc describes **one** checkout with **one** payment (line 57: *"Customer completes payment"*) and
**one** delivery (lines 59–60: *"Delivery partner picks up the items. Customer receives delivery."*).

**Impact:** a customer buying fish, rice and spices in one checkout would have to pay three times and pay three
delivery fees, with three tracking links. This is a product-level defect, not a detail.

---

### C5 · Walk-in POS sales cannot be represented at all

Idea doc line 129 (key feature 6) requires the POS to *"Record walk-in/pickup purchases"*, and line 135 requires
inventory to decrement for **walk-in** as well as online sales.

In the ERD, the only POS record is `vendors.VendorTransaction`, which is **1:1 with `Order`**
(`er-diagram.puml:221`), and `Order.user` is an FK to `User` (`:161`) with no null noted — i.e. an order
requires a registered customer. **A walk-in buyer has no `User` row**, so the sale cannot be stored.

**Impact:** half of key feature 6 is unmodelled. Fixing this is also what gives the unused `TransactionType`
table (`:124-128`) a purpose — see C8.

---

### C6 · Delivery orders have no path to `COMPLETED`

`confirm-pickup` is the only endpoint that advances an order to `COMPLETED`, and it is explicitly pickup-only
(`use-case.puml:62`). For a DELIVERY order, the idea doc's flow is
*Pending → Payment Confirmed → Preparing → **Out for Delivery** → Completed* (lines 77–86).

The UML has:
- **no `OUT_FOR_DELIVERY` status code** (C3),
- **no endpoint** that marks an order out for delivery or delivered,
- `DeliveryBooking.delivered_at` (`er-diagram.puml:212`) which **nothing ever writes**,
- `DeliveryStatus` used only as `BOOKED` / `FAILED` — no in-transit or delivered code.

**Impact:** every delivery order in the system is permanently stuck at `PREPARING`. The demo's order-tracking
screen (idea doc lines 77–86) cannot be shown truthfully.

---

### C7 · The receipt serial format is given two different definitions

| Source | Format |
|---|---|
| `activity-diagram.puml:78` | `RC-{ref}-{attempt}` |
| `use-case.puml:60` | `RC-{reference_no}-{attempt}` |
| `er-diagram.puml:296` | `R-{order.id}-{uuid}` |
| `sequence-diagram.puml:135` | `R-{id}-{uuid}` |

Two formats, 2–2 split. Worse, **neither is buildable from the current schema**:
- `{attempt}` implies a counter, but `VendorTransaction` (`er-diagram.puml:217-224`) has no attempt field.
- `{reference_no}` lives on `Transaction`, not on `VendorTransaction` — reachable only via a join.
- `{uuid}` is non-deterministic, so a reprint produces a **different** serial for the same sale.

**Impact:** a receipt serial that changes on reprint is not an auditable receipt. Blocks the POS receipt step (M3.14).

---

### C8 · Pickup reservations have no explicit representation — and the one table built for it is unused

The system is titled *"Marketplace, Ordering, and **Reservation** System"*, and `activity-diagram.puml:22-24`
has a whole branch for *"Pickup reservation without payment"* that *"Save[s] reservation and item price
snapshots"* and *"Generate[s] reference and confirmation"*.

But the ERD has **no `Reservation` entity and no `is_reservation` flag**. A reservation is implicitly an
`Order` with `fulfillment_type = PICKUP` and some status — and the only field that could distinguish a
reservation from a paid order is... nothing. `TransactionType` (`er-diagram.puml:124-128`) exists precisely for
this and **is referenced by no table in either the ERD or the class diagram**. It is a dead table.

**Impact:** you cannot write a query that answers "show me all reservations" without guessing from status.
An examiner will ask why a lookup table exists with no foreign key pointing at it.

---

## 🟠 Major findings

### M1 · The ERD and class diagram disagree on two cardinalities

| Relationship | ERD | Class diagram | Correct |
|---|---|---|---|
| Cart → CartItem | `Cart \|\|--\|{ CartItem` (`er-diagram.puml:245`) = **1..\*** | `Cart "1" *-- "0..*" CartItem` (`class-diagram.puml:210`) = **0..\*** | **0..\*** — a new user's cart is empty |
| Order → OrderItem | `Order \|\|--\|{ OrderItem` (`:257`) = **1..\*** | `Order "1" *-- "0..*" OrderItem` (`:220`) = **0..\*** | **1..\*** — an order with no lines is meaningless |

So each diagram is wrong about one of them, in opposite directions. Minor optionality drift also exists on the
status FKs (`Payment }o--|| PaymentStatus` in the ERD vs `"0..1"` in the class diagram).

### M2 · `Favorite`'s unique constraints do not enforce anything

`er-diagram.puml:231-236` declares `unique_together (user, product)` **and** `unique_together (user, vendor)`,
with **both** `product` and `vendor` nullable (`:232-233`). In MySQL/SQLite, `NULL` is distinct in a UNIQUE
index — so `(1, NULL)` can be inserted unlimited times. A customer can favourite the same vendor fifty times.
Two overlapping constraints also mean a row must be *either* a product-favourite *or* a vendor-favourite, which
no constraint actually enforces.

### M3 · `Order.vendor` is nullable, contradicting its own design note

`er-diagram.puml:162` — `vendor: CatalogVendor (FK, null, blank)`. But the note at `:272-276` says *"One Order
holds products from ONE vendor only"*, and `sequence-diagram.puml:29` always sets the vendor when splitting.
A nullable FK to the one vendor that defines the order permits vendor-less orders with no rule preventing them.

### M4 · `Product.availability` is free text while every other status is a lookup table

`er-diagram.puml:101` — `availability: str ' CharField (not an enum/FK)`. Meanwhile `TransactionStatus`,
`PaymentStatus`, `DeliveryStatus`, `FulfillmentMethod` and `TransactionType` are all lookup tables. The
inconsistency is visible in the diagram itself (the comment flags it), and availability is exactly the value
the search filters and the availability badge depend on.

### M5 · Nothing ties `Product.unit` to `ComparisonGroup.base_unit`

Price comparison works by putting products in a `ComparisonGroup` whose `base_unit` is a `UnitOfMeasure`
(`er-diagram.puml:250`). But `Product.unit` is an unconstrained CharField (`:99`). Nothing stops a vendor
listing **₱75/piece** in the same comparison group as **₱80/kg** — the group would then "compare" prices that
are not comparable, silently producing a wrong "best value" answer. There is no conversion factor anywhere.

### M6 · Vendor identity is stored three times, with no link between the copies

| Where | Fields |
|---|---|
| `UserProfile.is_vendor` (`er-diagram.puml:28`) | boolean flag |
| `catalog.Vendor` (`:43-55`) | name, stall_location, market_section, contacts, `user` FK (nullable, unique) |
| `vendors.Vendor` (`:57-62`) | `user` FK (PK), stall_name, stall_location |

`sequence-diagram.puml:88` checks **both** `vendors.Vendor` **and** `UserProfile.is_vendor`. The two vendor
tables have **no foreign key to each other** — they are joined only implicitly through `user`. And
`stall_location` / the vendor name are **duplicated** between `catalog.Vendor` and `vendors.Vendor`: update one
and the other goes stale. `catalog.Vendor.user` being *nullable* means a vendor storefront can exist with no
user, while `is_vendor = true` with no `vendors.Vendor` row would pass login and then fail every POS call.

### M7 · The POS queue and the cash-payment precondition contradict each other

`sequence-diagram.puml:94` — the POS lists **`CONFIRMED`** orders.
`activity-diagram.puml:72` + `use-case.puml:60` — cash payment is **only** allowed for **`PENDING_PAYMENT`** orders.

An order in `PENDING_PAYMENT` never appears in the queue, so the cash panel is unreachable from the screen that
is supposed to offer it. (This is the mechanism behind C1(b).)

### M8 · The cash-payment endpoint is named two different things

`sequence-diagram.puml:120` — `POST /api/pos/orders/{id}/cash-payment/`
`activity-diagram.puml:76` — `POST /pay/cash/`

Same operation, two paths. The API contract must be frozen before M4's Vue work (risk R4).

### M9 · `Order.status` and `Transaction.status` are two authorities for one fact

`sequence-diagram.puml:51-53` advances **both** in lockstep on payment verification, and again at `:104-105`,
`:113-114`, `:134-135`. Both FKs point at the same `TransactionStatus` lookup (`er-diagram.puml:163,183`).
Nothing defines which one wins if they diverge, and no constraint keeps them equal. A customer-facing status
and a payment status are being stored in the same vocabulary in two places.

### M10 · Nothing prevents a duplicate order from a double-submitted checkout

`sequence-diagram.puml:23-37` creates orders, transactions and items on `POST /api/orders/` with no
idempotency key. `Payment` is protected (`unique (provider, provider_reference)`, `:198`) but order creation is
not — a double-click or a retried request creates **two sets of orders** and two charges. The traceability
matrix promises a concurrency demonstration; this is the case to demonstrate.

### M11 · Cash payments are never recorded as `Payment` rows

`activity-diagram.puml:76-78` records cash against the **`VendorTransaction`** (status + receipt serial) and
never creates a `Payment`. But the ERD makes `Payment` the only table holding money received
(`er-diagram.puml:187-199`), and `Payment.provider` is free text that could hold `CASH`. As drawn, "total cash
collected today" is unanswerable from `Payment` and only partly answerable from `VendorTransaction`.

### M12 · The use-case diagram is mostly a flat list — five use cases have no relationships at all

Only three relationships exist (`use-case.puml:35-37`): UC11→UC7, UC16→UC15, UC18→UC15.

Orphans with **no `<<include>>`, `<<extend>>` or actor association**:
- **UC8** "Validate Cart, Prices, and Availability" — should be `<<include>>`d by UC6 and UC7
- **UC9** "Choose Pickup or Delivery" — should be `<<include>>`d by UC7
- **UC10** "Initiate and Verify Online Payment" — should be `<<include>>`d by UC7 (it has an actor, PayGateway, but no link to the use case it serves)
- **UC3** "View Product Details" — should be `<<include>>`d by UC2 or UC4
- **UC4** "Compare Equivalent Prices" — no link to UC2/UC3, though it depends on both

### M13 · Five use cases required by the idea document are missing entirely

| Idea-doc feature | Use case present? |
|---|---|
| Feature 4 — Interactive Market Map (stall numbers, sections, vendor locations) | **No** — UC2 covers search/filter only |
| Feature 7 — Vendor Sales Dashboard (daily/weekly/monthly sales, best sellers, inventory movement) | **No** — the vendor has no reporting use case at all |
| Feature 6 — Vendor product & inventory management (CRUD with images, price, availability, stock) | **No** — see M14 |
| Feature 5 — Order history & quick reorder | **Partial** — UC13 covers favourites; history/reorder has no use case (UC12 is status viewing) |
| Vendor sign-in (used throughout `sequence-diagram.puml:86-90`) | **No** — UC1 "Register / Sign In" is associated with Customer only |

### M14 · UC14 contradicts the idea document on who manages products

`use-case.puml:30` — **UC14 "Maintain Vendor / Product Demonstration Data"**, associated with **Admin**, with the
note *"Controlled Django administration, not vendor self-service"* (`:59`).

Idea doc line 16: *"Market Vendors also can create digital stores, **manage products**, process sales…"* and
lines 118–127: *"Each vendor receives a personalized digital storefront where products and services can be
managed in real time"*, with *"Product listings with images and descriptions"* and *"Price management"*.

The idea doc gives product management to **vendors**; the use-case diagram gives it to **admins** and explicitly
rules out vendor self-service. Direct conflict — and it changes the size of the vendor app in M3.

### M15 · The `Cart ||--|{ CartItem` cardinality makes an empty cart illegal (see M1)

Restated here because it is a *semantic* defect, not just a drawing error: with `1..*`, creating a cart for a
new user is invalid until an item is added, and clearing a cart after checkout (`sequence-diagram.puml:33`)
would delete the cart or violate the constraint. The sequence diagram explicitly clears the cart, so the two
artifacts cannot both be right.

---

## 🟡 Minor findings

| # | Finding |
|---|---|
| m1 | **Activity diagram creates transactions before validating the cart.** `activity-diagram.puml:19` creates one transaction per vendor, but the `Cart valid?` check is at `:20` — after. The failure branch at `:55` then says "do not create fulfillable order" for rows already created. Order the validate-then-create steps. |
| m2 | **The activity diagram says "one Transaction per vendor" where the sequence says "one Order per vendor".** `:19` vs `sequence-diagram.puml:29`. Both are created, but the activity diagram never mentions creating the `Order`. |
| m3 | **The class diagram omits the service and view classes** that `sequence-diagram.puml` depends on (`OrderSvc`, `PosSvc`). Its own header note (`class-diagram.puml:10-13`) says the logic lives in `apps/orders/services.py` and APIViews, but models neither. Either add them or add an explicit scope note ("domain model only"). |
| m4 | **`unique_together` is documented in the ERD but missing from the class diagram** for `CartItem` (`er-diagram.puml:120`) and `Favorite` (`:234-235`). |
| m5 | **`Product.stall_location` duplicates `catalog.Vendor.stall_location`** (`er-diagram.puml:100` vs `:46`). Same update-anomaly risk as M6. Defensible as a per-listing override — but say so. |
| m6 | **`Product.image_url` is singular** (`:97`) while the mockup spec calls for *"images"* (plural) on the product detail screen. One image per product, or a `ProductImage` table. |
| m7 | **Timestamp coverage is inconsistent.** `Product`, `OrderItem`, `Transaction`, `CartItem` and `Category` have no `created_at`/`updated_at`, while `Vendor`, `UnitOfMeasure`, `ComparisonGroup`, `DeliveryBooking` and the profiles do. |
| m8 | **No cancel and no refund flow**, although `CANCELLED` appears as a status (`activity-diagram.puml:93`) and `PaymentStatus.is_terminal` (`er-diagram.puml:146`) implies a terminal refund state. |
| m9 | **`Payment.provider` is free text** (`:190`) with no enumeration of the idea doc's four methods (GCash, Maya, online banking, card, line 61–65). Same for `DeliveryBooking.provider` vs the four partners (line 66–70). |
| m10 | **The activity diagram has two `start` nodes** (`activity-diagram.puml:11` and `:65`) in one diagram. Acceptable, but two diagrams (Customer Checkout / Vendor POS) would render and present better. |

---

## Recommended resolutions (for decision in M0.3)

These are **recommendations**, not decisions. Each becomes a row in `docs/DESIGN_DECISIONS.md` with your ruling
and your reason — that file is what you defend.

| Ref | Recommendation | Cost |
|---|---|---|
| **C1** | Adopt one pickup flow and delete the other two: reservation → `CONFIRMED` → `PREPARING` → `READY_FOR_PICKUP` → *(cash tendered, recorded as a Payment)* → `COMPLETED`. Cash becomes a **payment event**, not the trigger for `CONFIRMED`. This removes the chicken-and-egg flaw, matches the idea doc, the sequence diagram and the POS screen spec, and keeps a single guard on `confirm-pickup` (`CONFIRMED\|PREPARING\|READY_FOR_PICKUP → COMPLETED`). Requires editing `activity-diagram.puml:72-83` and `use-case.puml:60,62`. | ~1 h |
| **C2** | Add `Product.stock_quantity INT NOT NULL DEFAULT 0` and `low_stock_threshold INT NOT NULL DEFAULT 5`, plus an **`InventoryMovement`** ledger (`product`, `delta`, `reason` FK, `order` FK null, `note`, `created_at`). The ledger is the trigger target and the source of the dashboard's "inventory movement". | ~2 h |
| **C3** | Freeze four code lists in `docs/DESIGN_DECISIONS.md` and seed them in `sql/03_seed.sql`: `TransactionStatus` = `PENDING_PAYMENT, CONFIRMED, PREPARING, READY_FOR_PICKUP, OUT_FOR_DELIVERY, COMPLETED, CANCELLED`; `PaymentStatus` = `PENDING, VERIFIED, FAILED, REFUNDED`; `DeliveryStatus` = `BOOKED, IN_TRANSIT, DELIVERED, FAILED, CANCELLED`; `FulfillmentMethod` = `PICKUP, DELIVERY, WALK_IN`. | ~1 h |
| **C4** | Simplest acceptable: keep `Payment` 1:1 per order and show the customer "3 orders — pay each", **or** add a lightweight `Checkout`/`CheckoutGroup` table that groups the orders from one checkout so one payment and one delivery booking can span them. Option A is free and matches the schema; option B is better product design and costs ~3 h plus M3 work. | 0 h / ~3 h |
| **C5** | Model a walk-in sale as an `Order` with `fulfillment_type = WALK_IN` and a nullable `Order.user` (walk-in customers are anonymous) — or add `Order.customer_label` for a walk-in name. Set `Transaction.transaction_type = POS_WALKIN`. | ~1 h |
| **C6** | Add `OUT_FOR_DELIVERY` to `TransactionStatus`, add `POST /api/pos/orders/{id}/out-for-delivery/` and `POST /api/pos/orders/{id}/delivered/` (vendor-scoped), and use `DeliveryStatus.IN_TRANSIT`/`DELIVERED` plus `delivered_at`. | ~2 h |
| **C7** | Standardise on **`RC-{reference_no}-{attempt}`**, and add `VendorTransaction.receipt_attempt SMALLINT NOT NULL DEFAULT 1` so a reprint is deterministic and auditable. Delete the `R-{order.id}-{uuid}` notes from the ERD and sequence diagram. | ~30 min |
| **C8** | Give `TransactionType` its job: add `Transaction.transaction_type` FK with `ONLINE_ORDER`, `PICKUP_RESERVATION`, `POS_WALKIN`. Document explicitly that **a reservation is an `Order`** — there is no separate entity — and that `Transaction.reference_no` is the reference shown to the customer. | ~1 h |
| **M1** | `Cart \|\|--o{ CartItem` (0..\*) and `Order \|\|--\|{ OrderItem` (1..\*); align the class diagram to both. | 15 min |
| **M2** | Split into `FavoriteProduct(user, product)` and `FavoriteVendor(user, vendor)`, both `NOT NULL` with a working `unique_together`. Clean 3NF and the constraints actually enforce. | ~30 min |
| **M3** | Make `Order.vendor` `NOT NULL` unless admin/system orders are planned. | 10 min |
| **M4** | Promote to an `AvailabilityStatus` lookup (`code`, `description`, `sort_order`, `is_orderable`), consistent with the other four status tables — and let it be maintained from `stock_quantity`. | ~30 min |
| **M5** | Add `ComparisonGroupUnit(comparison_group, unit_code, factor_to_base)` so a product's unit must be a member of its group's allowed units, and comparison normalises through the factor. Without this the comparison tool can silently compare incomparable prices. | ~1 h |
| **M6** | One canonical vendor identity: keep `catalog.Vendor` as the storefront (make `user` `NOT NULL` and unique), make `vendors.Vendor` a **1:1 extension** with a FK to `catalog.Vendor` instead of a second `user` FK, and treat `UserProfile.is_vendor` as a derived convenience flag kept in sync — or drop it. Removes the duplicated `stall_location`/name. | ~1.5 h |
| **M7/M8** | Fix the POS queue to list the statuses the cash panel serves (per C1's resolution), and freeze one endpoint path — `POST /api/pos/orders/{id}/cash-payment/`. | 20 min |
| **M9** | Declare `Order.status` the **customer-facing** state and `Transaction.status` the **payment/settlement** state, with a single documented mapping function in `apps/orders/services.py`. Never set one without the other. | ~1 h |
| **M10** | Add an idempotency key to `POST /api/orders/` (client-generated UUID, unique per user) so a retried checkout cannot double-create. Excellent material for the transactions/concurrency lesson. | ~1 h |
| **M11** | Record cash as a `Payment` row with `provider = 'CASH'` and `provider_reference = <receipt_serial>`, so all money received lives in one table. | ~30 min |
| **M12** | Add the five missing `<<include>>`/`<<extend>>` links to the use-case diagram. | 20 min |
| **M13** | Add the five missing use cases: View Market Map, View Sales Dashboard, Manage Products & Inventory, View Order History / Quick Reorder, Vendor Sign In. | ~1 h |
| **M14** | **Your call, and it changes the scope.** Either give vendors self-service product management (matches the idea doc, more M3 work), or keep UC14 admin-only and change the idea doc wording. Recommend vendor self-service for create/update/price/availability, with admin retaining oversight. | 0 h / ~3 h |
| **M15** | Covered by M1. | — |

**Estimated total to apply every recommendation: 18–22 hours.** Applying only C1–C8 + M1–M4 (the ones that block
DDL and the M3 flows) is **~9–10 hours**, which fits the M0 buffer in `PROJECT_TIMELINE.md` §7 (R1).

---

## What happens next

1. **Step M0.3** settles every finding above into `docs/DESIGN_DECISIONS.md` — one row per finding: the ruling,
   the reason, and the timeline cost. **Your decisions, in your words** — that file is your defense material.
2. **Step M0.4** applies the rulings to the five `.puml` files and re-exports the SVGs, so the design of record
   becomes internally consistent.
3. **Step M0.7** writes `sql/01_schema.sql` **once**, against the settled design — not twice.

Do not start DDL before M0.3 is closed. Every critical finding above changes a table.
