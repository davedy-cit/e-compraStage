# E-Compra User Manual

## For Customers (Maria Santos)

### Getting Started
1. Open the app at `https://your-domain.com` (or `http://localhost:5174` locally if port 5173 is in use)
2. Click **Login** and enter your credentials
3. New users: Contact admin for account creation (no self-registration in v1)

### Test Credentials (for demo/testing)
All test accounts share the same password: **`ecompra123`**

| Username | Email | Role | Vendor |
|----------|-------|------|--------|
| `maria.santos` | maria.santos@example.ph | Customer | — |
| `juan.reyes` | juan.reyes@example.ph | Customer | — |
| `admin` | admin@ecompra.local | Admin | — |
| `pedro.reyes` | pedro.reyes@example.ph | Vendor | Pedro's Fresh Catch (Fish) |
| `rosa.delacruz` | rosa.delacruz@example.ph | Vendor | Rosa's Gulay Stand (Vegetables) |
| `jose.bautista` | jose.bautista@example.ph | Vendor | Bautista Meat Shop (Meat/Poultry) |
| `luzviminda.tan` | luzviminda.tan@example.ph | Vendor | Tan's Rice & Dry Goods (Dry Goods) |
| `andres.villamor` | andres.villamor@example.ph | Vendor | Villamor Fruits & Gulay (Fruits) |
| `nena.abellana` | nena.abellana@example.ph | Vendor | Nena's Manok (Poultry) |

### Browsing Products
- **Search**: Type in the search bar (top of catalog) and press Enter
- **Filter by Category**: Use the dropdown next to search
- **Product Cards** show: Name, Price/Unit, Vendor, Stall Location, Availability
- **Click a product** to see details, description, and vendor info

### Adding to Cart
1. On product detail or catalog, click **Add** (or set quantity then Add)
2. Items are added to your cart — one cart per user
3. **Cart icon** (top right) shows item count

### Cart Management
- Visit **Cart** from header
- **Update Quantity**: Change number and press Enter / click Update
- **Remove Item**: Click Remove or set quantity to 0
- Cart shows items **grouped by vendor** — each vendor becomes a separate order

### Checkout
1. Click **Proceed to Checkout**
2. **Fulfillment**: Choose Delivery (to address) or Pickup (at vendor stall)
3. Review vendor-grouped order summary
4. Click **Place Order** → Creates one Order per vendor
5. Redirected to **Payment** screen

### Payment
- Select method: GCash, Maya, Online Banking, Card
- Enter provider reference (from your payment app)
- Submit → Payment recorded as **Verified** (sandbox mode)
- You receive Order ID and Transaction Reference

### Order Tracking
- Visit **Order Tracking** from order confirmation or history
- **Status Timeline** shows: Pending Payment → Confirmed → Preparing → Out for Delivery → Completed
- For Pickup orders: Pending Payment → Confirmed → Preparing → Ready for Pickup → Completed

### Favorites
- Click ♡ on any product to add to favorites
- View favorites from profile menu (future feature)

---

## For Vendors (Pedro Reyes)

### Vendor POS (Point of Sale)
1. Login with vendor account
2. Navigate to **Vendor POS** (`/vendor/pos`)
3. See all orders for your stall, grouped by status

### Order Status Flow
- **Confirmed** → Customer paid, order received
- **Preparing** → You're packing/preparing items
- **Ready for Pickup** → Customer can collect (pickup orders)
- **Out for Delivery** → Handed to delivery rider (delivery orders)
- **Completed** → Customer received order
- **Cancelled** → Order cancelled (any stage)

### Updating Status
1. Find the order in the queue
2. Click the **Next Status** button (only valid transitions shown)
3. System validates: Cannot skip steps (e.g., Confirmed → Out for Delivery blocked)

### Cash Payment & Receipt (Walk-in / POS)
- For walk-in customers: Use **POS Walk-in** flow
- Enter cash tendered → System calculates **Change Due**
- **Receipt** generated with serial `RC-{ref}-{attempt}` (BIR-style 72mm format)
- Print receipt → Hand to customer

### Inventory Management
- Visit **Products** (`/vendor/products`) — future feature
- Update stock quantities, prices, availability
- Stock auto-decrements on confirmed sales (database trigger)

### Sales Dashboard
- Visit **Dashboard** (`/vendor/dashboard`) — future feature
- Shows: Daily/Weekly/Monthly sales, Best sellers, Low stock alerts

---

## Troubleshooting

| Issue | Solution |
|---|---|
| "Invalid token" | Log out and log in again (token expired) |
| Cart empty after login | Cart is per-user; items don't persist across accounts |
| Payment failed | Check provider reference matches exactly |
| Status update blocked | Must follow sequence: Confirmed → Preparing → Ready/Out → Completed |
| Can't see orders | Ensure you're logged in as the correct vendor |