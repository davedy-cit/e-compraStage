# E-Compra — Design Decisions (rulings on `DESIGN_REVIEW.md`)

| | |
|---|---|
| **Purpose** | Record the ruling on every finding in `docs/DESIGN_REVIEW.md`, with the reason, so each change is defensible |
| **Applied to** | `docs/uml/*.puml` revision 2 (revision 1 preserved in `docs/uml/archive-v1-original/`) |
| **Date applied** | 2026-11-12 |
| **Status** | coach-applied — §8 signed off by student, November 17, 2026 |

---

## 0. Read this before you defend it

**These rulings were applied by the coach at your instruction** ("apply the recommended fix for the findings").
They are recommendations made concrete, not facts. You must:

1. **Read every row below.** Each one changes a table, a status transition, or a screen.
2. **Disagree where you disagree.** Change the `.puml` and record your own reason here. A design you cannot
   defend is worse than a design with a known weakness you can.
3. **Sign off at §8.** Until you do, treat the diagrams as provisional.

> 📌 **CCS630 lesson:** in a database course, the *justification* is the deliverable. "I chose X because Y, and
> the alternative Z costs W" is what earns marks — not the diagram on its own.

**Three rulings are mine, not the review's, and are marked `[coach's call]`.** Review those hardest.

---

## 1. Critical rulings

### C1 · Pickup order flow — one flow, and cash is a payment event

**Ruling.** The pickup lifecycle is:

```
CONFIRMED ──prepare──▶ PREPARING ──ready──▶ READY_FOR_PICKUP ──confirm pickup──▶ COMPLETED
    ▲                          │
    │                          └── cash tendered at any point ──▶ Payment(CASH, VERIFIED)
    └── pickup reservation is created directly in CONFIRMED
```

- A **pickup reservation is created already `CONFIRMED`** — the vendor accepted it, no online payment involved.
- **Cash payment no longer changes `Order.status`.** It records a `Payment` row (`provider = CASH`,
  `status = VERIFIED`) and generates the receipt serial. This is the fix for the chicken-and-egg flaw.
- `confirm-pickup` accepts `CONFIRMED`, `PREPARING` **or** `READY_FOR_PICKUP` and advances to `COMPLETED`.
- The "skips PREPARING/READY_FOR_PICKUP" clause is **deleted** — the vendor can prepare in advance, which is
  what the idea document describes and what the POS screen needs.

**Reason.** The previous version made cash the trigger for `CONFIRMED`, so the vendor could not see or prepare
an order until the customer had already arrived and paid — making the idea document's "Preparing" step
unreachable. It also contradicted `sequence-diagram.puml`, which queued `CONFIRMED` orders for the POS.

**Applied in:** `activity-diagram.puml` (Flow B), `sequence-diagram.puml` (POS section), `use-case.puml`
(UC23, UC25 notes).

---

### C2 · Inventory model added

**Ruling.** Add to `Product`: `stock_quantity INT NOT NULL DEFAULT 0`, `low_stock_threshold INT NOT NULL DEFAULT 5`.
Add two tables:

- `InventoryReason(code PK, description, direction)` — `IN | OUT | ADJUST`
- `InventoryMovement(id, product FK, delta INT, reason FK, order FK NULL, note, created_at)`

**Reason.** Idea document key feature 6 promises real-time inventory that decrements on both walk-in and online
sales, and the course's trigger lesson needs a target. Neither was buildable. The **ledger** is the trigger
target and the audit trail; `stock_quantity` is the running balance the trigger maintains.

**Ownership rule (fixes R8):** the **database trigger is the single enforcement point** for `stock_quantity`.
Application code writes `InventoryMovement` rows; it never writes `stock_quantity` directly. The dashboard reads
the ledger for "inventory movement".

**Applied in:** `er-diagram.puml`, `class-diagram.puml`.

---

### C3 · Frozen status vocabularies

**Ruling.** The five lookup tables are seeded with fixed codes — see **§4**. No other code may be used in any
diagram, model, guard or screen.

**Reason.** Codes were previously scattered and mutually inconsistent (`SUCCESSFUL` in one diagram,
`VERIFIED` in another, `OUT_FOR_DELIVERY` nowhere). Every status guard, seed script and Django `choices` depends
on this list, so it must be frozen before DDL (M0.7).

**Applied in:** all five diagrams (as notes), and §4 below.

---

### C4 · Multi-vendor checkout — one payment per order (Option A)

**Ruling.** Keep `Payment` 1:1 per `Order`. A 3-vendor cart creates **3 orders, 3 transactions, 3 payments**
(and, for delivery, 3 delivery bookings). The UI shows "3 orders — pay each" and groups them visually.

**Reason.** Option B (a `CheckoutGroup` table spanning orders) is better product design but costs ~3 h of schema
plus M3 rework, and it is not required by the idea document. **This is the deliberate simplest-acceptable
version** in the pre-agreed cut list.

> ⚠️ **This is the weakest ruling in this document.** It is a real UX cost. If you have spare time in M4, revisit
> it — but not before the core flows are done.

**Applied in:** `er-diagram.puml` (Order note).

---

### C5 · Walk-in sales are representable

**Ruling.** A walk-in POS sale is an `Order` with:
- `user = NULL` (anonymous buyer) — `Order.user` becomes nullable
- `customer_label` (nullable) — optional walk-in name
- `fulfillment_type = WALK_IN`
- `Transaction.transaction_type = POS_WALKIN`

**Reason.** The POS must "record walk-in/pickup purchases" (idea doc line 129) and decrement inventory for them
(line 135), but `Order.user` was a non-null FK, so an anonymous buyer had nowhere to go. Half of key feature 6
was unmodelled.

**Applied in:** `er-diagram.puml`, `class-diagram.puml`, `sequence-diagram.puml`.

---

### C6 · Delivery orders can now reach `COMPLETED`

**Ruling.** Add `OUT_FOR_DELIVERY` to `TransactionStatus`. Add two vendor-scoped endpoints:
- `POST /api/pos/orders/{id}/out-for-delivery/` → `Order.status = OUT_FOR_DELIVERY`, `DeliveryBooking.status = IN_TRANSIT`
- `POST /api/pos/orders/{id}/delivered/` → `Order.status = COMPLETED`, `DeliveryBooking.status = DELIVERED`, `delivered_at = NOW()`

**Reason.** `confirm-pickup` was the only path to `COMPLETED` and is pickup-only, so **every delivery order was
permanently stuck at `PREPARING`**, and `delivered_at` was never written by anything.

**Applied in:** `sequence-diagram.puml` (new section), `activity-diagram.puml` (Flow B), `use-case.puml` (UC26),
`er-diagram.puml` (DeliveryBooking note).

---

### C7 · Receipt serial standardised

**Ruling.** `receipt_serial = RC-{transaction.reference_no}-{receipt_attempt}`, stored on
`vendors.VendorTransaction`. Add `receipt_attempt INT NOT NULL DEFAULT 1`, incremented on every reprint.

**Reason.** Two formats were in use (`RC-{ref}-{attempt}` and `R-{id}-{uuid}`). Worse, neither was buildable:
`{attempt}` had no column, and `{uuid}` is non-deterministic — **a reprinted receipt got a different serial**,
which is not an auditable receipt. Storing the attempt makes reprints reproducible.

**Applied in:** all five diagrams.

---

### C8 · `TransactionType` given its job

**Ruling.** `Transaction` gains `transaction_type FK` with codes `ONLINE_ORDER`, `PICKUP_RESERVATION`,
`POS_WALKIN`. Document explicitly: **a reservation is an `Order`** — there is no separate entity — and
`Transaction.reference_no` is the reference shown to the customer.

**Reason.** The system is titled a "Reservation System" but nothing distinguished a reservation from a paid
order; `TransactionType` existed and was referenced by nothing, which is a schema smell an examiner will find.

**Applied in:** `er-diagram.puml`, `class-diagram.puml`, `sequence-diagram.puml`, `activity-diagram.puml`.

---

## 2. Major rulings

| Ref | Ruling | Reason | Applied in |
|---|---|---|---|
| **M1** | `Cart \|\|--o{ CartItem` (**0..\***); `Order \|\|--\|{ OrderItem` (**1..\***). Both diagrams aligned. | The ERD said `1..*` for both and the class diagram said `0..*` for both — each was wrong about one. A cart with no items is the normal initial state, and the sequence diagram explicitly clears the cart. An order with no lines is meaningless. | ER + class |
| **M2** | `Favorite` **split** into `FavoriteProduct(user, product)` and `FavoriteVendor(user, vendor)`, both `NOT NULL`, each with a working `unique_together`. | With both columns nullable, `unique_together` enforced nothing: MySQL treats `NULL` as distinct, so a user could favourite the same vendor unlimited times. | ER + class |
| **M3** | `Order.vendor` **`NOT NULL`**. | It is the one vendor that defines the order; nullable contradicted the diagram's own note and the split logic. | ER + class |
| **M4** | `Product.availability` promoted to an **`AvailabilityStatus`** lookup (`code`, `description`, `sort_order`, `is_orderable`). | It was the only status in the schema stored as free text while four others were lookup tables. | ER + class |
| **M5** | Added **`ComparisonGroupUnit(comparison_group, unit, factor_to_base)`**. A product's unit must be a member of its comparison group's allowed units; comparison normalises through the factor. | Nothing stopped ₱75/piece being "compared" against ₱80/kg in one group — silently producing a wrong best-value answer. | ER + class |
| **M6** | `catalog.Vendor.user` becomes **`NOT NULL`** and is the single vendor identity. `vendors.Vendor` becomes a **1:1 extension** keyed by `catalog_vendor`, not a second `user` link. | Vendor name and stall location were duplicated across two tables joined only implicitly through `user` — update one, the other goes stale. `is_vendor = true` with no vendor row passed login then failed every POS call. | ER + class |
| **M7** | The POS queue lists **`CONFIRMED`** orders. | It listed `CONFIRMED` while the cash panel required `PENDING_PAYMENT`, so the cash panel was unreachable from the screen offering it. Resolved by C1 (reservations are `CONFIRMED`). | sequence |
| **M8** | One path: **`POST /api/pos/orders/{id}/cash-payment/`**. | Two paths existed for one operation. The contract must be frozen before M4's Vue work (risk R4). | sequence + activity |
| **M9** | **`Order.status` is the single lifecycle authority.** `Payment.status` holds settlement. `DeliveryBooking.status` holds courier progress. **`Transaction.status` is removed.** `[coach's call]` | Both `Order.status` and `Transaction.status` were advanced in lockstep by the same events, in the same vocabulary, with nothing keeping them equal. `Transaction` is 1:1 with `Order`, so its status was a pure duplicate. Removing it means **no fact is stored twice**, and every guard reads one column. | ER + class + sequence + activity + use-case |
| **M10** | `POST /api/orders/` requires an **`Idempotency-Key`** header (client-generated UUID, unique per user). Replay returns the original orders, not new ones. | A double-clicked or retried checkout created two sets of orders and two charges. Payment was protected; order creation was not. Excellent material for the transactions/concurrency lesson. | sequence + activity |
| **M11** | Cash is recorded as a **`Payment` row** (`provider = CASH`, `provider_reference = receipt_serial`, `status = VERIFIED`). | Cash was recorded only on `VendorTransaction`, so "total cash collected today" was unanswerable from `Payment` — the one table that holds money received. | ER + class + sequence + activity |
| **M12** | Added the five missing `<<include>>`/`<<extend>>` links (UC3→UC2, UC4→UC3, UC9/UC10→UC8/UC7, UC10→UC11). | Five use cases floated with no relationships at all — UC8 and UC9 had no arrow of any kind. | use-case |
| **M13** | Added five use cases: **View Interactive Market Map**, **View Sales Dashboard**, **Manage Own Products & Inventory**, **View Order History / Quick Reorder**, **Vendor Sign In**. | All five are required by the idea document's key features 4, 5, 6 and 7 and had no use case. The vendor could not even sign in on paper. | use-case |
| **M14** | **Vendor self-service product management** (UC21) — create/update own products, price, availability, stock, images. Admin retains oversight (UC30). | The use-case diagram gave product management to Admin and explicitly ruled out vendor self-service, directly contradicting idea doc line 16 and key feature 6. **This adds ~3 h of M3 work** — see §6. | use-case |
| **M15** | Covered by M1. | — | — |

---

## 3. Minor rulings

| Ref | Ruling | Applied in |
|---|---|---|
| **m1** | Cart is validated **before** any order or transaction is created. | activity |
| **m2** | Activity diagram now says "create one **Order AND one Transaction** per vendor". | activity |
| **m3** | Class diagram carries an explicit scope note: **domain layer only**; services and views are modelled in the sequence diagram. | class |
| **m4** | `unique_together` shown on `CartItem`, `FavoriteProduct`, `FavoriteVendor` in the class diagram. | class |
| **m5** | `Product.stall_location` **kept** and documented as a per-listing override of the vendor's stall. | ER (comment) |
| **m6** | `Product.image_url` left singular. **Open:** if the product detail screen needs a gallery, add a `ProductImage` table in M2. | — |
| **m7** | `created_at`/`updated_at` added to `Product`, `OrderItem`, `Transaction`, `CartItem`, `Category`, `VendorTransaction` for uniform audit coverage. | ER + class |
| **m8** | `CANCELLED` and `REFUNDED` codes are seeded, but the cancel/refund **flows are deferred** to M4 if time permits. Documented as a known gap. | §4 |
| **m9** | Provider enumerations documented as comments: payments `GCASH \| MAYA \| BANK \| CARD \| CASH`; delivery `GRABEXPRESS \| LALAMOVE \| MAXIM \| LOCAL`. | ER |
| **m10** | Two `start` nodes kept in one activity diagram (renders fine; splitting is cosmetic). | activity |

---

## 4. Frozen vocabularies (ruling C3)

These exact codes go into `sql/03_seed.sql` and the Django `choices`.

**`TransactionStatus`** — the order lifecycle. Used by `Order.status` **only**.

| code | sort | meaning |
|---|---|---|
| `PENDING_PAYMENT` | 10 | awaiting online payment |
| `CONFIRMED` | 20 | accepted; reservations start here |
| `PREPARING` | 30 | vendor is preparing |
| `READY_FOR_PICKUP` | 40 | waiting at the stall |
| `OUT_FOR_DELIVERY` | 50 | with the courier |
| `COMPLETED` | 60 | fulfilled (terminal) |
| `CANCELLED` | 99 | cancelled (terminal) |

**`PaymentStatus`** — settlement of one attempt.

| code | terminal | meaning |
|---|---|---|
| `PENDING` | no | initiated, not yet confirmed |
| `VERIFIED` | no | confirmed paid (may still be refunded) |
| `FAILED` | yes | attempt failed |
| `REFUNDED` | yes | money returned |

**`DeliveryStatus`** — courier progress.

| code | terminal |
|---|---|
| `BOOKED` | no |
| `IN_TRANSIT` | no |
| `DELIVERED` | yes |
| `FAILED` | yes |
| `CANCELLED` | yes |

**`FulfillmentMethod`** — how the goods reach the buyer: `PICKUP`, `DELIVERY`, `WALK_IN`.

**`TransactionType`** — how the sale originated: `ONLINE_ORDER`, `PICKUP_RESERVATION`, `POS_WALKIN`.

**`AvailabilityStatus`** — `is_orderable` in brackets: `IN_STOCK` (yes), `LOW_STOCK` (yes), `OUT_OF_STOCK` (no), `HIDDEN` (no).

**`InventoryReason`** — direction in brackets: `RECEIVED` (IN), `SOLD_ONLINE` (OUT), `SOLD_WALKIN` (OUT), `SPOILAGE` (OUT), `ADJUSTMENT` (ADJUST).

### Order status state machine

| From | To | Trigger | Guard |
|---|---|---|---|
| `PENDING_PAYMENT` | `CONFIRMED` | payment verified | `Payment.status = VERIFIED` |
| `PENDING_PAYMENT` | `CANCELLED` | payment failed / abandoned | — |
| `CONFIRMED` | `PREPARING` | vendor marks preparing | vendor owns the order |
| `CONFIRMED` | `COMPLETED` | confirm pickup | `fulfillment = PICKUP` |
| `PREPARING` | `READY_FOR_PICKUP` | vendor marks ready | `fulfillment = PICKUP` |
| `PREPARING` | `OUT_FOR_DELIVERY` | vendor marks dispatched | `fulfillment = DELIVERY` |
| `READY_FOR_PICKUP` | `COMPLETED` | confirm pickup | `fulfillment = PICKUP` |
| `OUT_FOR_DELIVERY` | `COMPLETED` | vendor marks delivered | `fulfillment = DELIVERY` |
| any non-terminal | `CANCELLED` | cancel (admin/vendor) | m8 — deferred |

Anything not in this table is an **invalid transition** and must return HTTP 400. That single rule is the whole
of `UC22`.

---

## 5. Timeline impact

| Where the cost lands | Added work | Note |
|---|---|---|
| M0.7 DDL | **+2 h** | more tables and lookups |
| M2 models & migrations | **+4 h** | new models, lookups, seed rows |
| M3 flows | **+6 h** | out-for-delivery endpoints, cash `Payment`, vendor product CRUD (M14), idempotency (M10), inventory ledger + trigger (C2) |
| M4 Vue | **+3 h** | vendor products screen, market map, dashboard |
| **Total** | **~15 h** | against a 1-day M0 buffer and the M4 3-day buffer |

**Assessment:** the design work itself is done — this cost is implementation, and it lands in milestones that have
their own buffers. It fits, **but only if M0.3 is not reopened.** If you want to trim, the cheapest cut is
**M14 (vendor self-service, ~3 h)** — revert UC21 to admin-only and adjust the idea-document wording instead.

---

## 6. What changed, file by file

| File | Changes |
|---|---|
| `er-diagram.puml` | +6 tables (`AvailabilityStatus`, `ComparisonGroupUnit`, `InventoryReason`, `InventoryMovement`, `FavoriteProduct`, `FavoriteVendor`); −1 (`Favorite`); `Transaction.status` removed; `Product` gains stock/unit-FK/availability-FK/timestamps; `Order` gains `customer_label`, `updated_at`, vendor NOT NULL, user nullable; `VendorTx` gains `receipt_attempt`; `PosVendor` rekeyed to `catalog_vendor`; 8 seeded-code notes added |
| `class-diagram.puml` | Mirrors the ERD exactly; scope note (m3); `unique_together` shown (m4) |
| `sequence-diagram.puml` | Pickup flow rewritten (C1); `Idempotency-Key` branch (M10); cash → `Payment` row (M11); receipt serial (C7); out-for-delivery + delivered sections (C6); status-ownership header note (M9) |
| `activity-diagram.puml` | Validate-before-create (m1); one Order + one Transaction per vendor (m2); pickup flow rewritten (C1); delivery branch added (C6) |
| `use-case.puml` | 8 include/extend links (M12); +5 use cases (M13); UC21 vendor self-service (M14); notes rewritten for C1/C6/C7/M9 |

**Originals:** `docs/uml/archive-v1-original/` (all five `.puml` and `.svg` as they were before this revision).

---

## 7. Still open

| # | Open item | Decide by |
|---|---|---|
| 1 | `Product.image_url` singular vs a `ProductImage` gallery table (m6) | M2 models |
| 2 | Cancel / refund flows (m8) — seeded but unimplemented | M4, if time permits |
| 3 | Revisit C4 (multi-vendor = N payments) if M4 finishes early | M4 |

---

## 8. Student sign-off

Tick each line only when you can explain it out loud without notes.

- [✅] I have read all 32 rulings in §1–§3.
- [✅] I understand why cash is no longer the trigger for `CONFIRMED` (C1), and I agree.
- [✅] I understand why `Transaction.status` was removed (M9) — and I agree, or I am restoring it with a reason.
- [✅] I accept the ~15 h of added implementation cost (§5), or I have cut M14.
- [✅] I can justify the C4 trade-off (3 vendors → 3 payments).
- [✅] I can name the five frozen vocabularies and where they are seeded (§4).
- [✅] I have re-exported the SVGs and confirmed the diagrams render.

**Signed off by:** Daved  **Date:** November 17, 2026

**Rulings I changed or rejected:** _(write them here, with your reason — this is the strongest material you have)_

| Ref | My ruling | My reason |
|---|---|---|
| | | |
| | | |
