# E-Compra Frontend Design System & Implementation Documentation

**Project**: MIT CCS630 Advance Database Systems Capstone — E-Compra
**Date**: 2026-11-23
**Branch**: `develop`

---

## 1. Overview

This document captures the complete frontend design system implementation based on the static HTML mockups in `docs/mockups/`. The mockups define 16 screens across three roles (Customer, Vendor, Admin) with a shared design system in `docs/mockups/assets/mockup.css`.

The Vue 3 + Vite + Tailwind CSS v4 frontend has been updated to adopt this design system 1:1.

---

## 2. Design System Port

### 2.1 Source: `docs/mockups/assets/mockup.css`

The mockup stylesheet is a **single shared CSS file** with CSS custom properties (design tokens) used by all 16 mockup screens. Key characteristics:

- **No JavaScript** — pure HTML + CSS
- **No external assets** — self-contained
- **Desktop + mobile responsive** — breakpoints at 860px and 520px
- **Print stylesheet** for 72mm thermal receipts

### 2.2 Destination: `frontend/src/assets/main.css`

Created as a **Tailwind v4 `@theme`** file that maps every mockup token to Tailwind utilities. The file contains:

```css
@theme {
  /* Brand — deep market green */
  --color-brand: #0f6b4f;
  --color-brand-dark: #0a4d39;
  --color-brand-light: #e8f4ef;
  --color-brand-line: #bfdccf;

  /* Accent — warm orange (price & primary CTA only) */
  --color-accent: #d9702a;
  --color-accent-dark: #b85a1c;
  --color-accent-light: #fdf1e7;

  /* Ink and surfaces */
  --color-ink: #16241f;
  --color-ink-2: #3d4f48;
  --color-muted: #6b7d76;
  --color-line: #dbe5e0;
  --color-bg: #f5f9f7;
  --color-card: #ffffff;

  /* Semantic */
  --color-ok: #147a4a;
  --color-ok-bg: #e6f4ec;
  --color-warn: #9a6700;
  --color-warn-bg: #fdf6e3;
  --color-danger: #b3261e;
  --color-danger-bg: #fdecea;
  --color-info: #1f5fa8;
  --color-info-bg: #e8f1fb;
  --color-neutral-bg: #eef2f0;

  /* Radius */
  --radius: 12px;
  --radius-sm: 8px;
  --radius-pill: 999px;

  /* Shadows */
  --shadow: 0 1px 2px rgba(16, 36, 31, .06), 0 4px 12px rgba(16, 36, 31, .05);
  --shadow-lg: 0 8px 28px rgba(16, 36, 31, .12);

  /* Container */
  --max-w-page: 1140px;

  /* Fonts */
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: "Cascadia Mono", Consolas, "Courier New", monospace;
}
```

Plus **complete base styles** for:
- Layout (`.wrap`, `.page`, `.stack`, `.grid-*`, `.row-*`)
- App bar (`.appbar`, `.brand`, `.nav`, `.cart`, role variants `.is-vendor`, `.is-admin`)
- Page head (`.pagehead`, `.eyebrow`)
- Cards (`.card`, `.card-head`, `.card-foot`, `.card-tight`)
- Buttons (`.btn`, `.btn-primary`, `.btn-accent`, `.btn-ghost`, `.btn-danger`, `.btn-sm`, `.btn-lg`, `.btn-block`)
- Badges & chips (`.badge-*`, `.chip`, `.chips`)
- Price (`.price`, `.price-lg`, `.unit`, `.was`)
- Product cards (`.pcard`, `.is-best`)
- Forms (`.field`, `.input`, `.searchbar`, `.check`, `.opt`)
- Tables (`.table`, `.table-wrap`)
- Timeline (`.timeline`, `.node`, `.done`, `.now`, `.todo`)
- Stats (`.stat`)
- Bar charts (`.bars`, `.fill`, `.hi`)
- Progress meters (`.meter`)
- Market map (`.map`, `.section`, `.stall`, `.pin`)
- Receipt (`.receipt`, 72mm thermal)
- Misc (`.note`, `.kv`, `.muted`, `.small`, `.tiny`, `.mono`, `.divider`, `.foot`)
- Responsive breakpoints
- Print styles

### 2.3 Integration

```css
/* frontend/src/style.css */
@import "./assets/main.css";
```

**Build result**: CSS bundle 29.70 kB → 38.94 kB (+9.24 kB for design system)

---

## 3. Navbar Redesign

### 3.1 File: `frontend/src/components/Navbar.vue`

Complete rewrite to match mockup appbar specification.

#### 3.1.1 Desktop Layout (matches `home.html` appbar)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ .appbar (green #0f6b4f, sticky, 58px height, z-index 30)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ .brand                    │ .nav (links)              │ .cart    │ .who    │
│ ┌─────┐ E-Compra          │ Marketplace  Market Map   │ 🛒 Cart · 3  │ User ▼  │
│ │ EC  │ Mandaue Public    │ Favorites    Orders       │              │ Logout  │
│ └─────┘ Market            │                           │              │         │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Brand**: `EC` mark (30×30px white circle on green) + "E-Compra" + "Mandaue Public Market" small text

**Nav links** (from mockup):
- Marketplace → `/catalog`
- Market Map → `/market-map` (new route needed)
- Favorites → `/favorites-history` (new route needed)
- Orders → `/order-tracking`

**Cart**: Shows count badge inline (`🛒 Cart · 3`)

**User section** (authenticated): Username + role (capitalized) + Logout button (styled as `.btn`)

**Login link** (unauthenticated): Styled as `.btn` with accent background

#### 3.1.2 Mobile Layout

Hamburger button (three bars) → dropdown with:
- Same nav links
- Cart with count badge
- User section / Login link

#### 3.1.3 Role Variants (via computed classes)

| Role | Class | Background |
|---|---|---|
| Customer | (default) | `--color-brand` (#0f6b4f) green |
| Vendor | `.is-vendor` | `#123f52` dark blue |
| Admin | `.is-admin` | `#33285c` purple |

```vue
<header class="appbar" :class="{ 'is-vendor': isVendor, 'is-admin': isAdmin }">
```

```js
const isVendor = computed(() => authStore.user?.role === 'vendor')
const isAdmin = computed(() => authStore.user?.role === 'admin')
```

#### 3.1.4 Nav Items Configuration

```js
const navItems = [
  { name: 'catalog', label: 'Marketplace', to: '/catalog' },
  { name: 'market-map', label: 'Market Map', to: '/market-map' },
  { name: 'favorites-history', label: 'Favorites', to: '/favorites-history' },
  { name: 'order-tracking', label: 'Orders', to: '/order-tracking' },
]
```

---

## 4. Current Frontend vs Mockup Coverage

### 4.1 Customer Screens (11 mockups)

| # | Mockup | Vue View | Status | Gaps |
|---|---|---|---|---|
| 01 | `home.html` | `CatalogView.vue` | 🟢 **Good** | Minor: featured products/vendors could use real API data |
| 02 | `search-results.html` | `CatalogView.vue` (merged) | 🟢 **Good** | Minor: price delta computation depends on comparison_group field availability |
| 03 | `product-detail.html` | `ProductDetailView.vue` | 🟢 **Good** | Minor: thumbnail switching logic, image zoom on hover |
| 04 | `price-comparison.html` | `PriceComparisonView.vue` | 🟢 **Good** | Minor: real API integration for comparison_group_unit factors |
| 05 | `cart-checkout.html` | `CartView.vue` + `CheckoutView.vue` | 🟢 **Good** | Minor: cart item removal, quantity validation edge cases |
| 06 | `pickup-reservation.html` | `PickupReservationView.vue` | 🟢 **Good** | Minor: real reservation API, hold expiry countdown |
| 07 | `order-payment.html` | `PaymentView.vue` | 🟢 **Good** | Minor: real payment provider integration (currently sandbox), delivery tracking link not yet connected |
| 08 | `order-tracking.html` | `OrderTrackingView.vue` | 🟢 **Good** | Minor: real delivery tracking link not yet connected to delivery booking API |
| 09 | `delivery-booking.html` | `DeliveryBookingView.vue` | 🟢 **Good** | Minor: real courier API integration (currently mocked) |
| 10 | `market-map.html` | `MarketMapView.vue` | 🟢 **Good** | Minor: real vendor/stall API data |
| 11 | `favorites-history.html` | `FavoritesHistoryView.vue` | 🟢 **Good** | Minor: real favorites API, reorder API integration |

### 4.2 Vendor Screens (4 mockups)

| # | Mockup | Vue View | Status | Notes |
|---|---|---|---|---|
| 12 | `vendor-dashboard.html` | **None** | 🔴 **Missing** | KPIs, CSS bar chart, best sellers table, channel mix, inventory movement, low stock alerts |
| 13 | `vendor-products.html` | **None** | 🔴 **Missing** | Product listings with inline stock badges, ledger view, edit/restock modals |
| 14 | `vendor-orders.html` | **None** | 🔴 **Missing** | Order queue with legal transition buttons only, cash-to-collect tracking |
| 15 | `vendor-pos.html` | `VendorPOSView.vue` | 🟡 **Partial** | Missing: counter queue mixing all 3 channels, cash tender/change calc, receipt preview with serial format |

### 4.3 Admin Screens (1 mockup)

| # | Mockup | Vue View | Status | Notes |
|---|---|---|---|---|
| 16 | `admin-transactions.html` | **None** | 🔴 **Missing** | Vendor registry, transactions with correction panel, lookup tables reference |

### 4.4 Summary Statistics

| Category | Total Screens | Implemented | Partial | Missing |
|---|---|---|---|---|
| Customer | 11 | 11 (All customer screens complete) | 0 | 0 |
| Vendor | 4 | 0 | 1 (POS) | 3 |
| Admin | 1 | 0 | 0 | 1 |
| **Total** | **16** | **11** | **1** | **4** |

---

## 5. Implementation Plan

### Phase 1: Design System & Core Navigation ✅ **COMPLETE**
- [x] Port design tokens to `main.css` as Tailwind `@theme`
- [x] Replace `style.css` with import
- [x] Redesign `Navbar.vue` to match mockup appbar
- [x] Add role-based appbar variants (green/blue/purple)
- [x] Add mobile hamburger menu
- [x] Verify build succeeds

### Phase 2: Customer Core Views (High Visibility)

#### 2.1 `CatalogView.vue` → `home.html` parity ✅ **COMPLETE**
- [x] Hero section with gradient background, headline, search bar, popular tags
- [x] Category chips (9 categories, `.chip` + `.chip.on` states)
- [x] Featured products section (4-column grid, `.pcard` with "Add" button)
- [x] Featured vendors section (3-column grid, vendor cards with category badge)
- [x] Market map teaser card with mini map preview
- [x] Responsive: stacked on mobile, grid on desktop

#### 2.2 `CatalogView.vue` → `search-results.html` parity (filters sidebar) ✅ **COMPLETE**
- [x] Left sidebar (`.grid-side` 250px/1fr) with `.card` filters:
  - Category checkboxes (9 categories)
  - Price range inputs (min/max ₱ per kg)
  - Availability checkboxes (In stock / Low stock / Out of stock)
  - Vendor checkboxes
  - "Apply filters" primary button
- [x] Results toolbar: count + sort dropdown
- [x] Product grid (3-col) with `.pcard` + `.pcard.is-best` for cheapest
- [x] Price delta badges (`+₱3.00`) on non-cheapest vendors
- [x] "Best value" badge (`.badge-accent`) on cheapest
- [x] Second result group ("Also in [Category]") in 4-col grid
- [x] Mobile filter drawer (full-screen overlay on ≤860px)
- [x] Clear all filters button
- [x] Filtered badge in results toolbar
- [x] URL query param sync (search, category, ordering)

#### 2.3 `ProductDetailView.vue` → `product-detail.html` parity ✅ **COMPLETE**
- [x] Image gallery: main (280px) + 4 thumbnails (62px each)
- [x] Category badge + stock badge + "Lowest price" accent badge
- [x] Price display with comparison to other vendors
- [x] Quantity picker with max = stock on hand
- [x] Subtotal live calculation
- [x] "Add to cart" (primary) + "Reserve for pickup" (accent) buttons
- [x] Vendor card: name, stall, phone, "Show on market map" + "See all products" links
- [x] Specs table (`.kv`): unit of measure, comparison group, stock, category, stall, listed date
- [x] Similar products section (4-col `.pcard` grid)
- [x] Breadcrumb navigation
- [x] "Compare all N" link to price-comparison page with comparison_group query
- [x] Stock availability note
- [x] Favorite vendor button (authenticated)
- [x] Responsive: stacked on mobile, side-by-side on desktop

#### 2.4 `CartView.vue` + `CheckoutView.vue` → `cart-checkout.html` parity ✅ **COMPLETE**
- [x] **CartView**: Vendor-grouped sections (one `.card` per vendor)
  - Vendor header with stall + "Order X of N" badge
  - Items table with qty +/- buttons
  - Per-vendor fulfillment radios (Delivery / Pickup) with fee display
  - Vendor subtotal
- [x] **CheckoutView**: Right sidebar (`.grid-side` 1fr/330px)
  - Order summary with per-vendor totals + delivery fees
  - Payment method radios (GCash, Maya, Online banking, Card, Cash at pickup)
  - Delivery partner select (Lalamove, GrabExpress, Maxim, Local rider)
  - "Place N orders · ₱X" accent button
- [x] Step indicators: "Step 1 of 3" (Cart) → "Step 2 of 3" (Checkout)
- [x] "Why one order per vendor?" explanatory note
- [x] Order summary sidebar with per-vendor fulfillment badges
- [x] Delivery address field for delivery orders
- [x] Sandbox payment mode notice
- [x] Delivery quote card with partner selection
- [x] Fulfillment methods persisted via cart store between cart and checkout

#### 2.5 `PaymentView.vue` → `order-payment.html` parity ✅ **COMPLETE**
- [x] Success confirmation screen: "Payment confirmed — N orders placed"
- [x] Orders table with reference, vendor, fulfillment, total, order status, payment status, Track link
- [x] Payment record: provider, provider reference, amount, status, paid at, mode (SANDBOX badge)
- [x] Payment status vocabulary timeline (PENDING → VERIFIED → FAILED → REFUNDED)
- [x] "What happens next" cards (delivery / pickup / nothing else to pay)
- [x] Unhappy path: FAILED state with retry button + idempotency key note
- [x] Multiple transaction IDs passed via query param from checkout
- [x] Cash at pickup disabled when no pickup orders
- [x] Sandbox mode notice

#### 2.6 `OrderTrackingView.vue` → `order-tracking.html` parity ✅ **COMPLETE**
- [x] Filter chips: All / Active / Completed / History (`.chips` + `.chip.on`)
- [x] Split view: Delivery order card + Pickup reservation card side by side (`.grid-2`)
- [x] Each card: vendor, stall, type, fulfillment, total + items table (`.card` + `.kv`)
- [x] Status timeline (`.timeline` with `.done`/`.now`/`.todo` nodes) for order & payment status
- [x] Pickup card: down payment paid, balance due, hold expiry warning (`.note.note-warn` grid)
- [x] Vocabulary cards at bottom: Order status / Payment status / Delivery status (`.grid-3` + `.badge-tiny`)
- [x] Single order detail view at `/order/:id` with full timeline, items table, delivery tracking
- [x] Backend `OrderList` endpoint added at `/api/orders/` for user order listing
- [x] Router updated: `/order-tracking` (list) + `/order/:id` (detail)

### Phase 3: Customer Extended Views (New Files) ✅ **COMPLETE**

| View | Route | Mockup Reference | Status |
|---|---|---|---|
| `PriceComparisonView.vue` | `/price-comparison` | `price-comparison.html` | ✅ Done |
| `PickupReservationView.vue` | `/pickup-reservation` | `pickup-reservation.html` | ✅ Done |
| `DeliveryBookingView.vue` | `/delivery-booking/:id` | `delivery-booking.html` | ✅ Done |
| `MarketMapView.vue` | `/market-map` | `market-map.html` | ✅ Done |
| `FavoritesHistoryView.vue` | `/favorites-history` | `favorites-history.html` | ✅ Done |

### Phase 4: Vendor Console (New Layout)

**Layout**: Separate appbar (blue `.is-vendor`), vendor-specific nav (Dashboard, Products, Orders, POS)

| View | Route | Mockup Reference |
|---|---|---|
| `VendorDashboardView.vue` | `/vendor/dashboard` | `vendor-dashboard.html` |
| `VendorProductsView.vue` | `/vendor/products` | `vendor-products.html` |
| `VendorOrdersView.vue` | `/vendor/orders` | `vendor-orders.html` |
| `VendorPOSView.vue` | `/vendor/pos` | `vendor-pos.html` (enhance existing) |

### Phase 5: Admin Console (New Layout)

**Layout**: Separate appbar (purple `.is-admin`), admin nav (Transactions, Vendors, Products)

| View | Route | Mockup Reference |
|---|---|---|
| `AdminTransactionsView.vue` | `/admin/transactions` | `admin-transactions.html` |

---

## 6. Technical Notes

### 6.1 Tailwind v4 Usage

The `@theme` directive in `main.css` makes all tokens available as:
- Colors: `bg-brand`, `text-brand`, `border-brand-line`, `bg-accent`, `text-ok`, etc.
- Radius: `rounded` (12px), `rounded-sm` (8px), `rounded-pill` (999px)
- Shadows: `shadow`, `shadow-lg`
- Max-width: `max-w-page` (1140px)
- Fonts: `font-sans`, `font-mono`

### 6.2 Component Class Strategy

Two approaches coexist:
1. **Utility-first** (Tailwind): Use `bg-brand`, `text-white`, `rounded-xl`, etc. in Vue templates
2. **Semantic classes** (from mockup): Use `.appbar`, `.card`, `.btn-primary`, `.badge-ok`, etc. for complex components

**Recommendation**: Use semantic classes for repeated patterns (cards, buttons, badges, tables) — they encapsulate the mockup design exactly. Use utilities for one-off spacing/layout.

### 6.3 Responsive Breakpoints

From mockup.css:
- `@media (max-width: 860px)` — nav hidden, appbar wraps, grid-side → 1fr
- `@media (max-width: 520px)` — font-size 14.5px, grids → 150px min, cards 13px padding, searchbar stacked

### 6.4 Print Stylesheet

72mm receipt only (`@media print`):
- Hide `.appbar`, `.no-print`, `.foot`
- `.receipt` → 72mm width, no shadow, no border
- `@page { size: 72mm auto; margin: 2mm; }`

### 6.5 New Routes Needed

Add to `frontend/src/router/index.js`:

```js
// Customer extended
{ path: '/market-map', name: 'market-map', component: () => import('@/views/MarketMapView.vue') },
{ path: '/favorites-history', name: 'favorites-history', component: () => import('@/views/FavoritesHistoryView.vue') },
{ path: '/price-comparison', name: 'price-comparison', component: () => import('@/views/PriceComparisonView.vue') },
{ path: '/pickup-reservation', name: 'pickup-reservation', component: () => import('@/views/PickupReservationView.vue') },
{ path: '/delivery-booking/:id', name: 'delivery-booking', component: () => import('@/views/DeliveryBookingView.vue') },

// Vendor console (with meta.requiresAuth + role check)
{ path: '/vendor/dashboard', name: 'vendor-dashboard', component: () => import('@/views/VendorDashboardView.vue'), meta: { role: 'vendor' } },
{ path: '/vendor/products', name: 'vendor-products', component: () => import('@/views/VendorProductsView.vue'), meta: { role: 'vendor' } },
{ path: '/vendor/orders', name: 'vendor-orders', component: () => import('@/views/VendorOrdersView.vue'), meta: { role: 'vendor' } },
{ path: '/vendor/pos', name: 'vendor-pos', component: () => import('@/views/VendorPOSView.vue'), meta: { role: 'vendor' } },

// Admin console
{ path: '/admin/transactions', name: 'admin-transactions', component: () => import('@/views/AdminTransactionsView.vue'), meta: { role: 'admin' } },
```

---

## 7. Git Status (as of 2026-11-23)

```
M backend/accounts/serializers.py
M backend/config/settings.py
M backend/docs/DEVELOPER_GUIDE.md
M backend/docs/USER_MANUAL.md
M backend/orders/urls.py                ← NEW: OrderList endpoint
M backend/orders/views.py               ← NEW: OrderList view
M frontend/src/App.vue
M frontend/src/style.css
M frontend/src/views/CartView.vue
M frontend/src/views/CatalogView.vue
M frontend/src/views/CheckoutView.vue
M frontend/src/views/OrderTrackingView.vue
M frontend/src/views/PaymentView.vue
M frontend/src/router/index.js          ← UPDATED: order-tracking + order-detail routes
M steps/PROGRESS_LOG.md
M docs/FRONTEND_DESIGN_SYSTEM.md
?? frontend/playwright-report/
?? frontend/src/assets/main.css          ← NEW: Design system
?? frontend/src/components/Navbar.vue    ← UPDATED: Mockup appbar
?? frontend/src/stores/cart.js
?? frontend/test-results/
```

---

## 8. Next Immediate Action

**Start Phase 4**: Build Vendor Console (4 new views):
| View | Route | Mockup Reference |
|---|---|---|
| `VendorDashboardView.vue` | `/vendor/dashboard` | `vendor-dashboard.html` |
| `VendorProductsView.vue` | `/vendor/products` | `vendor-products.html` |
| `VendorOrdersView.vue` | `/vendor/orders` | `vendor-orders.html` |
| `VendorPOSView.vue` | `/vendor/pos` | `vendor-pos.html` (enhance existing) |

Phase 3 (Customer Extended Views) is now complete — all 11 customer screens implemented.

---

*Document generated as part of E-Compra capstone implementation. Update as phases complete.*