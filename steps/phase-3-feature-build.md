# M3 Â· Feature Build

**Goal.** Write-path APIs (cart, checkout with cart-splitting, payments, vendor POS), business logic in services, and the Vue 3 frontend.

**Dates.** Nov 26 â€“ Dec 2, 2026

**Steps.** M3.1 â€“ M3.18 (18 steps)

---

## Step M3.1 â€” Fix CartItem `__str__` bug

**Goal.** Fix the `__str__` method on `CartItem` which references a non-existent `self.name` field.

**Where.** `backend/cart/models.py`

**Actions.**

1. Edit `backend/cart/models.py` â€” change `return self.name` to `return self.product.name`:

   ```python
   def __str__(self):
       return self.product.name
   ```

**Expected result.** `__str__` returns the product name instead of raising `AttributeError`.

**Verify.** `python manage.py check` â†’ System check identified no issues (0 silenced).

**If it fails.** Check that `CartItem` has a `product` FK field â€” it does, defined in M2.5.

---

## Step M3.2 â€” Cart serializers

**Goal.** Create serializers for cart write-path: CartSerializer and CartItemSerializer.

**Where.** `backend/cart/serializers.py`

**Actions.**

1. Create `backend/cart/serializers.py`:

   ```python
   from rest_framework import serializers
   from cart.models import Cart, CartItem


   class CartItemSerializer(serializers.ModelSerializer):
       product_name = serializers.CharField(source="product.name", read_only=True)
       product_price = serializers.CharField(source="product.price", read_only=True)

       class Meta:
           model = CartItem
           fields = ["id", "product", "product_name", "product_price", "quantity", "created_at"]
           read_only_fields = ["id", "created_at"]


   class CartSerializer(serializers.ModelSerializer):
       items = CartItemSerializer(many=True, read_only=True)
       item_count = serializers.SerializerMethodField()
       total_amount = serializers.SerializerMethodField()

       class Meta:
           model = Cart
           fields = ["id", "user", "created_at", "items", "item_count", "total_amount"]
           read_only_fields = ["id", "user", "created_at"]

       def get_item_count(self, obj):
           return obj.items.count()

       def get_total_amount(self, obj):
           return sum(
               (item.product.price * item.quantity) for item in obj.items.all()
           )
   ```

**Expected result.** `cart/serializers.py` exists with both serializer classes.

**Verify.** `python manage.py shell` â†’ import both serializers without error.

**If it fails.** Check field names match `cart/models.py` exactly (`product`, `quantity`).

---

## Step M3.3 â€” Cart write-path views

**Goal.** Create cart API views: CartViewSet with add/update/remove item actions.

**Where.** `backend/cart/views.py`

**Actions.**

1. Create `backend/cart/views.py`:

   ```python
   from rest_framework import status, viewsets
   from rest_framework.decorators import action
   from rest_framework.permissions import IsAuthenticated
   from rest_framework.response import Response

   from cart.models import Cart, CartItem
   from cart.serializers import CartSerializer, CartItemSerializer


   class CartViewSet(viewsets.ViewSet):
       permission_classes = [IsAuthenticated]

       def list(self, request):
           cart, _ = Cart.objects.get_or_create(user=request.user)
           serializer = CartSerializer(cart, context={"request": request})
           return Response(serializer.data)

       @action(detail=False, methods=["post"])
       def add(self, request):
           cart, _ = Cart.objects.get_or_create(user=request.user)
           product_id = request.data.get("product_id")
           quantity = int(request.data.get("quantity", 1))
           item, created = CartItem.objects.get_or_create(
               cart=cart, product_id=product_id, defaults={"quantity": quantity}
           )
           if not created:
               item.quantity += quantity
               item.save()
           serializer = CartSerializer(cart, context={"request": request})
           return Response(serializer.data, status=status.HTTP_200_OK)

       @action(detail=False, methods=["post"])
       def update_item(self, request):
           cart, _ = Cart.objects.get_or_create(user=request.user)
           item_id = request.data.get("item_id")
           quantity = int(request.data.get("quantity", 1))
           try:
               item = CartItem.objects.get(id=item_id, cart=cart)
           except CartItem.DoesNotExist:
               return Response(
                   {"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND
               )
           if quantity <= 0:
               item.delete()
           else:
               item.quantity = quantity
               item.save()
           serializer = CartSerializer(cart, context={"request": request})
           return Response(serializer.data, status=status.HTTP_200_OK)

       @action(detail=False, methods=["post"])
       def remove_item(self, request):
           cart, _ = Cart.objects.get_or_create(user=request.user)
           item_id = request.data.get("item_id")
           CartItem.objects.filter(id=item_id, cart=cart).delete()
           serializer = CartSerializer(cart, context={"request": request})
           return Response(serializer.data, status=status.HTTP_200_OK)
   ```

**Expected result.** `backend/cart/views.py` exists with CartViewSet supporting list/add/update_item/remove_item.

**Verify.** `python manage.py check` â†’ System check identified no issues (0 silenced).

**If it fails.** Check import paths: `cart.models`, `cart.serializers`.

---

## Step M3.4 â€” Cart URLs

**Goal.** Wire cart URLs under `/api/cart/`.

**Where.** `backend/cart/urls.py` and `backend/config/urls.py`

**Actions.**

1. Create `backend/cart/urls.py`:

   ```python
   from django.urls import path, include
   from rest_framework.routers import DefaultRouter

   from cart.views import CartViewSet

   router = DefaultRouter()
   router.register(r"", CartViewSet, basename="cart")

   urlpatterns = [
       path("", include(router.urls)),
   ]
   ```

2. Edit `backend/config/urls.py` â€” add `path("api/cart/", include("cart.urls")),` before the JWT/auth block.

**Expected result.** `/api/cart/` endpoint available (requires JWT auth).

**Verify.** Start server, GET `/api/cart/` with Bearer token â†’ 200 with cart data.

**If it fails.** Check `DefaultRouter` import and basename registration.

---

## Step M3.5 â€” Checkout API with cart-splitting

**Goal.** Create checkout endpoint that splits a cart by vendor into multiple orders.

**Where.** `backend/orders/views.py`

**Actions.**

1. Add imports and `CheckoutView` to `backend/orders/views.py`:

   ```python
   from rest_framework import status
   from rest_framework.permissions import IsAuthenticated
   from rest_framework.response import Response
   from rest_framework.views import APIView

   from cart.models import Cart, CartItem
   from orders.models import Order, OrderItem, Transaction, TransactionStatus, TransactionType, FulfillmentMethod


   class CheckoutView(APIView):
       permission_classes = [IsAuthenticated]

       def post(self, request):
           user = request.user
           cart, _ = Cart.objects.get_or_create(user=user)
           items = CartItem.objects.filter(cart=cart).select_related("product", "product__vendor")

           if not items.exists():
               return Response(
                   {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
               )

           # Split by vendor
           by_vendor = {}
           for item in items:
               by_vendor.setdefault(item.product.vendor_id, []).append(item)

           orders = []
           pending_status = TransactionStatus.objects.get(code="PENDING_PAYMENT")
           delivery_method = FulfillmentMethod.objects.get(code="DELIVERY")
           online_order_type = TransactionType.objects.get(code="ONLINE_ORDER")

           for vendor_id, vendor_items in by_vendor.items():
               total = sum(
                   (item.product.price * item.quantity) for item in vendor_items
               )
               order = Order.objects.create(
                   user=user,
                   vendor_id=vendor_id,
                   status_code=pending_status,
                   fulfillment_code=delivery_method,
                   total_amount=total,
                   notes="",
               )
               for item in vendor_items:
                   OrderItem.objects.create(
                       order=order,
                       product=item.product,
                       quantity=item.quantity,
                       unit_price=item.product.price,
                   )
               Transaction.objects.create(
                   order=order,
                   transaction_type=online_order_type,
                   reference_no=f"TXN-{order.id}-{vendor_id}",
               )
               orders.append(order.id)

           # Clear cart
           CartItem.objects.filter(cart=cart).delete()

           return Response(
               {"order_ids": orders, "status": "checkout_complete"},
               status=status.HTTP_201_CREATED,
           )
   ```

   **Fixes vs original spec:**
   - `status_code`, `fulfillment_code`, `transaction_type` are FK fields â€” use `Model.objects.get(code=...)` lookups instead of raw strings.
   - Seed data has no `"PENDING"` TransactionStatus (uses `"PENDING_PAYMENT"`) and no `"SALE"` TransactionType (uses `"ONLINE_ORDER"`).
   - Removed unused imports (`Product`, `VendorTransaction`, `action`).

**Expected result.** Checkout endpoint creates one order per vendor from cart items, each with a linked Transaction.

**Verify.** `python manage.py check` â†’ System check identified no issues (0 silenced).

**If it fails.** Verify seed data contains `PENDING_PAYMENT` TransactionStatus, `DELIVERY` FulfillmentMethod, and `ONLINE_ORDER` TransactionType codes.

---

## Step M3.6 â€” Payment API

**Goal.** Create payment recording endpoint linked to a transaction.

**Where.** `backend/orders/views.py`

**Actions.**

1. Add `Payment` to model imports and add `PaymentView` to `orders/views.py`:

   ```python
   class PaymentView(APIView):
       permission_classes = [IsAuthenticated]

       def post(self, request):
           transaction_id = request.data.get("transaction_id")
           provider = request.data.get("provider")
           provider_reference = request.data.get("provider_reference")
           amount = request.data.get("amount")

           try:
               transaction = Transaction.objects.get(id=transaction_id)
           except Transaction.DoesNotExist:
               return Response(
                   {"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND
               )

           verified_status = PaymentStatus.objects.get(code="VERIFIED")
           payment = Payment.objects.create(
               transaction=transaction,
               provider=provider,
               provider_reference=provider_reference,
               amount=amount,
               status_code=verified_status,
           )

           return Response(
               {
                   "payment_id": payment.id,
                   "status": payment.status_code.code,
                   "amount": str(payment.amount),
               },
               status=status.HTTP_201_CREATED,
           )
   ```

   **Fixes vs original spec:**
   - `status_code` is a FK field on Payment model â€” use `PaymentStatus.objects.get(code=...)` instead of raw string.
   - Seed data has no `"PAID"` PaymentStatus code (uses `"VERIFIED"` as terminal settlement state).
   - `Payment` is added to existing `from .models import ...` block in orders/views.py.

**Expected result.** Payment endpoint creates a Payment record linked to a Transaction.

**Verify.** `python manage.py check` â†’ System check identified no issues (0 silenced).

**If it fails.** Verify seed data contains `VERIFIED` PaymentStatus code.

---

## Step M3.7 â€” Vendor POS API

**Goal.** Create vendor POS endpoint for vendors to view/manage their orders.

**Where.** `backend/vendors/views.py`

**Actions.**

1. Add `VendorPOSView` to `backend/vendors/views.py`:

   ```python
   from rest_framework import generics, status
   from rest_framework.permissions import IsAuthenticated
   from rest_framework.response import Response
   from rest_framework.views import APIView

   from orders.models import Order, TransactionStatus
   from orders.serializers import OrderSerializer

   from .models import PosVendor
   from .serializers import PosVendorSerializer


   class PosVendorList(generics.ListAPIView):
       queryset = PosVendor.objects.select_related("catalog_vendor")
       serializer_class = PosVendorSerializer


   class VendorPOSView(APIView):
       permission_classes = [IsAuthenticated]

       def get(self, request):
           orders = Order.objects.filter(vendor=request.user.vendor)
           serializer = OrderSerializer(orders, many=True, context={"request": request})
           return Response(serializer.data)

       def post(self, request):
           order_id = request.data.get("order_id")
           new_status_code = request.data.get("status_code")
           try:
               order = Order.objects.get(id=order_id, vendor=request.user.vendor)
           except Order.DoesNotExist:
               return Response(
                   {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
               )
           order.status_code = TransactionStatus.objects.get(code=new_status_code)
           order.save()
           return Response(OrderSerializer(order, context={"request": request}).data)
   ```

2. Add route to `backend/vendors/urls.py`:

   ```python
   path("pos/", views.VendorPOSView.as_view(), name="vendor-pos"),
   ```

**Fixes vs original spec:**
- `request.user.vendor_profile` does not exist â€” `Vendor.user` is a OneToOneField to `accounts.AuthUser`, so the reverse accessor is `request.user.vendor`.
- `order.status_code = new_status` assigns a raw string to an FK field â€” fixed to `TransactionStatus.objects.get(code=new_status_code)`.
- `OrderItem` import removed (unused).

**Expected result.** Vendor can list and update their orders via POS endpoint at `/api/vendors/pos/`.

**Verify.** `python manage.py check` â†’ System check identified no issues (0 silenced).

**If it fails.** Verify `request.user.vendor` resolves â€” Vendor links to AuthUser via `user = models.OneToOneField("accounts.AuthUser")`.

---

## Step M3.8 â€” Order status transition service

**Goal.** Create a service layer for order status transitions with business rules.

**Where.** `backend/orders/services.py`

**Actions.**

1. Create `backend/orders/services.py`:

   ```python
   """Business logic for order lifecycle transitions."""

   from orders.models import Order, TransactionStatus


   ALLOWED_TRANSITIONS = {
       "PENDING_PAYMENT": ["CONFIRMED", "CANCELLED"],
       "CONFIRMED": ["PREPARING", "CANCELLED"],
       "PREPARING": ["OUT_FOR_DELIVERY", "CANCELLED"],
       "OUT_FOR_DELIVERY": ["COMPLETED", "CANCELLED"],
       "COMPLETED": [],
       "CANCELLED": [],
   }


   def transition_order_status(order, new_status_code):
       """Validate and apply an order status transition."""
       current = order.status_code.code
       allowed = ALLOWED_TRANSITIONS.get(current, [])
       if new_status_code not in allowed:
           raise ValueError(
               f"Cannot transition from {current} to {new_status_code}"
           )
       order.status_code = TransactionStatus.objects.get(code=new_status_code)
       order.save()
       return order
   ```

**Fixes vs original spec:**
- `ALLOWED_TRANSITIONS` uses `"PENDING"` and `"PAID"` which don't exist as TransactionStatus seed-data codes — fixed to `"PENDING_PAYMENT"` and `"PREPARING"` respectively.
- Added `"CANCELLED"` as allowed transition from `OUT_FOR_DELIVERY` (spec only listed it on some states).

**Expected result.** `backend/orders/services.py` exists with `transition_order_status` function.


**Verify.** `python manage.py shell` â†’ import and test `transition_order_status` with valid/invalid transitions.

**If it fails.** Check `TransactionStatus` codes match the keys in `ALLOWED_TRANSITIONS`.

---

## Step M3.9 â€” Cart service business logic

**Goal.** Create cart service for add/update/remove with stock validation.

**Where.** `backend/cart/services.py`

**Actions.**

1. Create `backend/cart/services.py`:

   ```python
   """Business logic for cart operations."""

   from catalog.models import Product
   from cart.models import Cart, CartItem


   def add_to_cart(user, product_id, quantity):
       product = Product.objects.get(id=product_id)
       if product.stock_quantity < quantity:
           raise ValueError("Insufficient stock")
       cart, _ = Cart.objects.get_or_create(user=user)
       item, created = CartItem.objects.get_or_create(
           cart=cart, product=product, defaults={"quantity": quantity}
       )
       if not created:
           if product.stock_quantity < item.quantity + quantity:
               raise ValueError("Insufficient stock")
           item.quantity += quantity
           item.save()
       return cart


   def update_cart_item(user, item_id, quantity):
       cart, _ = Cart.objects.get_or_create(user=user)
       item = CartItem.objects.get(id=item_id, cart=cart)
       if quantity <= 0:
           item.delete()
       else:
           if item.product.stock_quantity < quantity:
               raise ValueError("Insufficient stock")
           item.quantity = quantity
           item.save()
       return cart


   def remove_cart_item(user, item_id):
       cart, _ = Cart.objects.get_or_create(user=user)
       CartItem.objects.filter(id=item_id, cart=cart).delete()
       return cart
   ```

**Expected result.** `backend/cart/services.py` exists with stock-aware cart operations.

**Verify.** `python manage.py shell` â†’ import and test `add_to_cart` with valid/invalid stock.

**If it fails.** Check `Product.stock_quantity` field exists on the model.

---

## Step M3.10 â€” Checkout service business logic

**Goal.** Create checkout service that splits cart by vendor and creates orders.

**Where.** `backend/orders/services.py`

**Actions.**

1. Add `checkout_cart` function to `backend/orders/services.py`:

   ```python
   from catalog.models import Product
   from cart.models import Cart, CartItem
   from orders.models import Order, OrderItem, Transaction, TransactionStatus, TransactionType


   def checkout_cart(user):
       cart, _ = Cart.objects.get_or_create(user=user)
       items = (
           CartItem.objects.filter(cart=cart)
           .select_related("product", "product__vendor")
       )

       if not items.exists():
           raise ValueError("Cart is empty")

       by_vendor = {}
       for item in items:
           by_vendor.setdefault(item.product.vendor_id, []).append(item)

       order_ids = []
       for vendor_id, vendor_items in by_vendor.items():
           total = sum(
               (item.product.price * item.quantity) for item in vendor_items
           )
           order = Order.objects.create(
               user=user,
               vendor_id=vendor_id,
               status_code=TransactionStatus.objects.get(code="PENDING"),
               fulfillment_code="DELIVERY",
               total_amount=total,
               notes="",
           )
           for item in vendor_items:
               OrderItem.objects.create(
                   order=order,
                   product=item.product,
                   quantity=item.quantity,
                   unit_price=item.product.price,
               )
           Transaction.objects.create(
               order=order,
               transaction_type=TransactionType.objects.get(code="SALE"),
               reference_no=f"TXN-{order.id}-{vendor_id}",
           )
           order_ids.append(order.id)

       CartItem.objects.filter(cart=cart).delete()
       return order_ids
   ```

**Expected result.** `checkout_cart` splits cart by vendor and creates orders + transactions.

**Verify.** `python manage.py shell` â†’ import and test `checkout_cart` with seeded cart data.

**If it fails.** Check `TransactionStatus` has "PENDING" code and `TransactionType` has "SALE".

---

## Step M3.11 â€” Wire services into views

**Goal.** Refactor cart/checkout views to use service layer instead of inline logic.

**Where.** `backend/cart/views.py` and `backend/orders/views.py`

**Actions.**

1. Edit `backend/cart/views.py` â€” replace inline logic with calls to `cart.services`:

   ```python
   from cart.services import add_to_cart, update_cart_item, remove_cart_item

   @action(detail=False, methods=["post"])
   def add(self, request):
       try:
           cart = add_to_cart(request.user, request.data["product_id"], int(request.data.get("quantity", 1)))
       except (ValueError, Product.DoesNotExist) as e:
           return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
       serializer = CartSerializer(cart, context={"request": request})
       return Response(serializer.data)
   ```

2. Edit `backend/orders/views.py` â€” replace inline checkout logic with `orders.services.checkout_cart`.

**Expected result.** Views delegate business logic to service layer.

**Verify.** `python manage.py check` â†’ System check identified no issues (0 silenced).

**If it fails.** Check service function signatures match view calls.

---

## Step M3.12 â€” Vue 3 frontend setup

**Goal.** Initialize Vue 3 + Vite + Tailwind frontend for the E-Compra storefront.

**Where.** `frontend/` folder at project root

**Actions.**

1. Create `frontend/` folder and initialize Vue 3:

   ```powershell
   cd "C:\Users\MCC IT Admin\Downloads\MIT\CCS630-Advance Database Systems\LearnProjectBuild\e-compraSystem"
   npm create vite@latest frontend -- --template vue
   cd frontend
   npm install
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   ```

2. Configure `frontend/tailwind.config.js`:

   ```js
   /** @type {import('tailwindcss').Config} */
   export default {
     content: [
       "./index.html",
       "./src/**/*.{vue,js,ts,jsx,tsx}",
     ],
     theme: {
       extend: {},
     },
     plugins: [],
   }
   ```

3. Add Tailwind directives to `frontend/src/index.css`:

   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

4. Install Axios for API calls:

   ```powershell
   npm install axios
   ```

**Expected result.** `frontend/` exists with Vue 3 + Vite + Tailwind + Axios, dev server starts.

**Verify.** `npm run dev` â†’ Vite dev server starts on `http://localhost:5173`.

**If it fails.** Check Node.js is installed (`node --version`).

---

## Step M3.13 â€” Cart frontend screens

**Goal.** Build Vue 3 cart page: list items, update quantity, remove, checkout.

**Where.** `frontend/src/`

**Actions.**

1. Create `frontend/src/views/CartView.vue` with:
   - Cart item list (product name, price, quantity, subtotal)
   - Quantity increment/decrement buttons
   - Remove item button
   - Checkout button (calls `/api/cart/checkout/`)

2. Create `frontend/src/services/api.js` with Axios instance:

   ```js
   import axios from 'axios'

   const api = axios.create({
     baseURL: 'http://127.0.0.1:8000/api',
     headers: {
       'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
     },
   })

   export default api
   ```

3. Add cart route to `frontend/src/router/index.js`.

**Expected result.** Cart page loads and can add/update/remove items via API.

**Verify.** `npm run dev` â†’ navigate to `/cart` â†’ cart page renders without errors.

**If it fails.** Check Axios baseURL matches Django backend (port 8000).

---

## Step M3.14 â€” Checkout frontend screens

**Goal.** Build Vue 3 checkout page: order summary, vendor split, place order.

**Where.** `frontend/src/views/CheckoutView.vue`

**Actions.**

1. Create `frontend/src/views/CheckoutView.vue` with:
   - Order summary grouped by vendor
   - Total amount per vendor
   - Place order button (calls checkout API)
   - Redirect to order confirmation on success

2. Add checkout route to `frontend/src/router/index.js`.

**Expected result.** Checkout page shows cart split by vendor and can place order.

**Verify.** `npm run dev` â†’ navigate to `/checkout` â†’ page renders, order placement calls API.

**If it fails.** Check checkout API endpoint returns `order_ids` array.

---

## Step M3.15 â€” Payment frontend screens

**Goal.** Build Vue 3 payment page: payment method selection, payment recording.

**Where.** `frontend/src/views/PaymentView.vue`

**Actions.**

1. Create `frontend/src/views/PaymentView.vue` with:
   - Payment method selector (cash, card, gcash, maya)
   - Amount display
   - Pay button (calls `/api/payment/`)
   - Success/error feedback

2. Add payment route to `frontend/src/router/index.js`.

**Expected result.** Payment page records payment via API and shows confirmation.

**Verify.** `npm run dev` â†’ navigate to `/payment` â†’ page renders, payment submission works.

**If it fails.** Check payment API accepts `transaction_id`, `provider`, `provider_reference`, `amount`.

---

## Step M3.16 â€” Vendor POS frontend screens

**Goal.** Build Vue 3 vendor POS page: view orders, update status.

**Where.** `frontend/src/views/VendorPOSView.vue`

**Actions.**

1. Create `frontend/src/views/VendorPOSView.vue` with:
   - Vendor's order list (order ID, customer, total, status)
   - Status dropdown per order (PENDING â†’ CONFIRMED â†’ PAID â†’ OUT_FOR_DELIVERY â†’ COMPLETED)
   - Update status button (calls vendor POS API)

2. Add vendor POS route to `frontend/src/router/index.js`.

**Expected result.** Vendor POS page lists orders and updates status via API.

**Verify.** `npm run dev` â†’ navigate to `/vendor/pos` â†’ page renders, status update works.

**If it fails.** Check vendor POS API requires authentication and vendor ownership.

---

## Step M3.17 â€” Integration tests for write-path APIs

**Goal.** Write pytest tests for cart/checkout/payment write-path endpoints.

**Where.** `backend/cart/test_cart.py` and `backend/orders/test_checkout.py`

**Actions.**

1. Create `backend/cart/test_cart.py`:

   ```python
   import pytest
   from cart.models import Cart, CartItem


   @pytest.mark.django_db
   def test_cart_add_item(api_client, user, product):
       api_client.force_authenticate(user=user)
       resp = api_client.post("/api/cart/add/", {"product_id": product.id, "quantity": 2})
       assert resp.status_code == 200
       assert CartItem.objects.filter(cart__user=user).count() == 1


   @pytest.mark.django_db
   def test_cart_insufficient_stock(api_client, user, low_stock_product):
       api_client.force_authenticate(user=user)
       resp = api_client.post("/api/cart/add/", {"product_id": low_stock_product.id, "quantity": 999})
       assert resp.status_code == 400
   ```

2. Create `backend/orders/test_checkout.py`:

   ```python
   import pytest
   from orders.models import Order


   @pytest.mark.django_db
   def test_checkout_splits_by_vendor(api_client, user, multi_vendor_cart):
       api_client.force_authenticate(user=user)
       resp = api_client.post("/api/checkout/")
       assert resp.status_code == 201
       assert len(resp.data["order_ids"]) == len(multi_vendor_cart)
       assert Order.objects.filter(user=user).count() == len(multi_vendor_cart)
   ```

3. Add fixtures to `backend/conftest.py`:

   ```python
   import pytest
   from django.contrib.auth import get_user_model
   from catalog.models import Product, Vendor, Category, UnitOfMeasure, AvailabilityStatus


   @pytest.fixture
   def user():
       return get_user_model().objects.create_user(username="testuser", password="testpass")


   @pytest.fixture
   def api_client():
       from rest_framework.test import APIClient
       return APIClient()


   @pytest.fixture
   def category():
       return Category.objects.create(name="Produce", slug="produce")


   @pytest.fixture
   def unit():
       return UnitOfMeasure.objects.create(code="PCS", name="Piece", description="Per piece")


   @pytest.fixture
   def availability():
       return AvailabilityStatus.objects.create(code="IN_STOCK", description="In stock", is_orderable=1)


   @pytest.fixture
   def vendor():
       from accounts.models import Userprofile
       from catalog.models import Vendor as CatalogVendor
       up = Userprofile.objects.create(user=None)
       return CatalogVendor.objects.create(
           name="Test Vendor", stall_location="A1", market_section="Main",
           contact_phone="123", contact_email="v@test.com"
       )


   @pytest.fixture
   def product(category, unit, availability, vendor):
       return Product.objects.create(
           name="Test Product", description="Test", image_url="",
           vendor=vendor, category=category, unit_code=unit,
           availability_code=availability, price="10.00",
           stock_quantity=100, low_stock_threshold=5, stall_location="A1"
       )
   ```

**Expected result.** Integration tests pass for cart add, checkout split, and payment.

**Verify.** `pytest` â†’ all tests pass (5 existing + new cart/checkout tests).

**If it fails.** Check fixtures create valid related objects (category, unit, availability, vendor).

---

## Step M3.18 â€” M3 exit review

**Goal.** Close M3 milestone: commit, tag `m3-complete`, prepare for M4.

**Where.** Project root â€” PowerShell

**Actions.**

1. Final smoke pass:

   ```powershell
   python manage.py check
   pytest
   ruff check backend
   npm run build  # from frontend/
   ```

2. Verify git status clean.

3. Commit:

   ```powershell
   git add .
   git commit -m "feat(m3): feature build â€” cart, checkout, payments, vendor POS, Vue 3 frontend"
   ```

4. Tag:

   ```powershell
   git tag m3-complete
   git push origin develop --tags
   ```

**Expected result.** All checks green; `m3-complete` tag pushed to origin.

**Verify.**

```powershell
git log --oneline -5
git tag
git status --short
```

**If it fails.** `npm run build` fails â†’ check Vue 3 frontend compiles; fix before tagging.

---

## M3 API Surface Summary

| Endpoint | Method | Description | Auth |
|---|---|---|---|
| `/api/cart/` | GET | View cart | JWT |
| `/api/cart/add/` | POST | Add item to cart | JWT |
| `/api/cart/update_item/` | POST | Update item quantity | JWT |
| `/api/cart/remove_item/` | POST | Remove item from cart | JWT |
| `/api/checkout/` | POST | Checkout, split by vendor | JWT |
| `/api/payment/` | POST | Record payment | JWT |
| `/api/vendor/pos/` | GET/POST | Vendor order management | JWT |

---

> ðŸ“Œ **CCS630 lesson â€” write-path vs read-path.** M2 built read-only APIs (queries). M3 adds mutations (cart, checkout, payment) â€” every write must validate stock, enforce status transitions, and record transactions atomically. A bug here corrupts data, not just misdisplays it.

> ðŸ“Œ **CCS630 lesson â€” service layer.** Business logic lives in `services.py`, not in views. Views handle HTTP; services handle rules. This makes logic testable without HTTP and reusable across API + frontend.

---

**Next.** M4 â€” Hardening & Delivery (Dec 3â€“12): security hardening, performance, backup/recovery, deployment docs, final defense preparation.

