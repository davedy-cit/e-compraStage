# Implementation Guide: Customer Self-Registration & Vendor Account Creation via Market Administrator

## Project: E-Compra System (CCS630 Capstone)
**Target Branch**: `develop` → `feature/registration-admin`
**Estimated Effort**: 21-29 hours across 6 phases

---

## Table of Contents
1. [Prerequisites & Setup](#prerequisites--setup)
2. [Phase 1: Customer Registration API (Backend)](#phase-1-customer-registration-api-backend)
3. [Phase 2: Customer Registration Page (Frontend)](#phase-2-customer-registration-page-frontend)
4. [Phase 3: Market Administrator Role](#phase-3-market-administrator-role)
5. [Phase 4: Admin Vendor Creation API](#phase-4-admin-vendor-creation-api)
6. [Phase 5: Admin Dashboard UI (Frontend)](#phase-5-admin-dashboard-ui-frontend)
7. [Phase 6: Integration Testing & Polish](#phase-6-integration-testing--polish)
8. [Verification Checklist](#verification-checklist)
9. [Rollback Plan](#rollback-plan)

---

## Prerequisites & Setup

### Environment Verification
```bash
# Backend
cd backend
source .venv/bin/activate
python manage.py check
python manage.py test accounts -v 2

# Frontend
cd frontend
npm test -- --run
npx playwright test --project=chromium
```

### Create Feature Branch
```bash
git checkout develop
git pull origin develop
git checkout -b feature/registration-admin
```

### Database Backup (Critical - models are managed=False)
```bash
# Backup current state before any manual SQL changes
mysqldump -u root -p ecompra auth_user accounts_customerprofile accounts_userprofile catalog_vendor vendors_vendor > backup_pre_registration.sql
```

---

## Phase 1: Customer Registration API (Backend)

### 1.1 Create Register Serializer
**File**: `backend/accounts/serializers.py`

```python
# ADD to existing file
from rest_framework import serializers
from django.db import transaction
from accounts.models import AuthUser, Customerprofile, Userprofile
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterSerializer(serializers.ModelSerializer):
    """Customer self-registration serializer."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=32)
    address = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = AuthUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'phone', 'address'
        ]

    def validate_username(self, value):
        if AuthUser.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if AuthUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match"})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        phone = validated_data.pop('phone')
        address = validated_data.pop('address', '')
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')

        # Create AuthUser
        user = AuthUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=1,
            is_staff=0,
            is_superuser=0,
            date_joined=timezone.now(),
        )
        user.set_password(password)
        user.save()

        # Create Customerprofile
        Customerprofile.objects.create(
            user=user,
            phone=phone,
            address=address,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        # Create Userprofile (default: not vendor)
        Userprofile.objects.create(
            user=user,
            is_vendor=0,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        return user


# ADD import at top
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
```

#### ✅ Verification Steps for 1.1
```bash
# 1. Syntax check - no import errors
cd backend
source .venv/bin/activate
python -c "from accounts.serializers import RegisterSerializer; print('Import OK')"

# 2. Validate serializer fields
python -c "
from accounts.serializers import RegisterSerializer
s = RegisterSerializer()
print('Fields:', list(s.fields.keys()))
print('Required:', [k for k,v in s.fields.items() if v.required])
"

# 3. Run Django system check
python manage.py check
# Expected: System check identified no issues (0 silenced).
```

### 1.2 Create Register View
**File**: `backend/accounts/views.py`

```python
# REPLACE entire file
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import CurrentUserSerializer, RegisterSerializer


class CurrentUserView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CurrentUserSerializer

    def get_object(self):
        return self.request.user


class RegisterView(generics.CreateAPIView):
    """Customer self-registration endpoint."""
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for immediate login
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': CurrentUserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)
```

#### ✅ Verification Steps for 1.2
```bash
# 1. Syntax check - no import errors
cd backend
source .venv/bin/activate
python -c "from accounts.views import RegisterView, CurrentUserView; print('Import OK')"

# 2. Run Django system check
python manage.py check

# 3. Verify URL pattern loads
python -c "
from django.urls import resolve
from accounts.views import RegisterView
match = resolve('/api/accounts/auth/register/')
print(f'View: {match.func.__name__}')
print(f'View class: {match.func.view_class}')
"
# Expected: View class: RegisterView
```

### 1.3 Add Register URL
**File**: `backend/accounts/urls.py`

```python
# REPLACE entire file
from django.urls import path
from accounts.views import CurrentUserView, RegisterView

urlpatterns = [
    path("auth/user/", CurrentUserView.as_view(), name="current-user"),
    path("auth/register/", RegisterView.as_view(), name="register"),
]
```

#### ✅ Verification Steps for 1.3
```bash
# 1. Verify URL patterns are registered
cd backend
source .venv/bin/activate
python -c "
from django.urls import get_resolver
resolver = get_resolver()
for pattern in resolver.url_patterns:
    if 'accounts' in str(pattern.pattern):
        print(pattern)
"

# 2. Test URL resolution
python -c "
from django.urls import reverse
try:
    url = reverse('register')
    print(f'Register URL: {url}')
except Exception as e:
    print(f'Error: {e}')
"

# 3. Run Django system check
python manage.py check
```

### 1.4 Backend Unit Tests for Registration
**File**: `backend/accounts/tests.py`

```python
# REPLACE or CREATE file
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import AuthUser, Customerprofile, Userprofile


class RegisterAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/accounts/auth/register/'
        self.valid_payload = {
            'username': 'newcustomer',
            'email': 'new@customer.com',
            'first_name': 'Juan',
            'last_name': 'Dela Cruz',
            'password': 'SecurePass123',
            'password_confirm': 'SecurePass123',
            'phone': '09171234567',
            'address': '123 Mandaue City, Cebu',
        }

    def test_register_success(self):
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'newcustomer')
        self.assertEqual(response.data['user']['role'], 'customer')

        # Verify profiles created
        user = AuthUser.objects.get(username='newcustomer')
        self.assertTrue(Customerprofile.objects.filter(user=user).exists())
        self.assertTrue(Userprofile.objects.filter(user=user, is_vendor=0).exists())

    def test_register_duplicate_username(self):
        AuthUser.objects.create_user(username='existing', email='e@e.com', password='pass')
        payload = {**self.valid_payload, 'username': 'existing'}
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_duplicate_email(self):
        AuthUser.objects.create_user(username='u1', email='exists@test.com', password='pass')
        payload = {**self.valid_payload, 'email': 'exists@test.com'}
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_password_mismatch(self):
        payload = {**self.valid_payload, 'password_confirm': 'DifferentPass123'}
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_register_short_password(self):
        payload = {**self.valid_payload, 'password': 'short', 'password_confirm': 'short'}
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_missing_phone(self):
        payload = {**self.valid_payload}
        del payload['phone']
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)
```

#### ✅ Verification Steps for 1.4
```bash
# 1. Verify test file syntax
cd backend
source .venv/bin/activate
python -m py_compile accounts/tests.py
echo "Syntax OK"

# 2. Run specific test class
python manage.py test accounts.tests.RegisterAPITest -v 2

# 3. Run with coverage (if coverage installed)
# python manage.py test accounts.tests.RegisterAPITest --coverage

# 4. Verify test database is created properly
python manage.py test accounts.tests.RegisterAPITest.test_register_success -v 3
```

### 1.5 Run Backend Tests
```bash
cd backend
source .venv/bin/activate
python manage.py test accounts.tests.RegisterAPITest -v 2
```

**Expected**: All 6 tests pass ✓

#### ✅ Phase 1 Integration Verification
```bash
# 1. Full backend test suite for accounts
cd backend
source .venv/bin/activate
python manage.py test accounts -v 2

# 2. Test registration endpoint manually with curl
curl -X POST http://localhost:8000/api/accounts/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser123",
    "email": "test123@example.com",
    "first_name": "Test",
    "last_name": "User",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "phone": "09171234567",
    "address": "123 Test St, Mandaue"
  }'

# Expected: 201 Created with access/refresh tokens and user data
# Verify in database:
python manage.py shell -c "
from accounts.models import AuthUser, Customerprofile, Userprofile
u = AuthUser.objects.get(username='testuser123')
print(f'User: {u.username}, email: {u.email}, active: {u.is_active}')
print(f'Customerprofile: {Customerprofile.objects.filter(user=u).exists()}')
print(f'Userprofile: {Userprofile.objects.filter(user=u, is_vendor=0).exists()}')
"
```

---

## Phase 2: Customer Registration Page (Frontend)

### 2.1 Create Register View Component
**File**: `frontend/src/views/RegisterView.vue`

```vue
<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Form state
const form = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  password_confirm: '',
  phone: '',
  address: '',
})

const errors = ref({})
const error = ref('')
const loading = ref(false)
const passwordStrength = ref(0)

const passwordRequirements = [
  { label: 'At least 8 characters', test: p => p.length >= 8 },
  { label: 'Uppercase letter', test: p => /[A-Z]/.test(p) },
  { label: 'Lowercase letter', test: p => /[a-z]/.test(p) },
  { label: 'Number', test: p => /[0-9]/.test(p) },
  { label: 'Special character', test: p => /[!@#$%^&*]/.test(p) },
]

function checkPasswordStrength() {
  const passed = passwordRequirements.filter(r => r.test(form.value.password)).length
  passwordStrength.value = Math.round((passed / passwordRequirements.length) * 100)
}

function validateForm() {
  errors.value = {}
  
  if (!form.value.username.trim()) errors.value.username = 'Username is required'
  if (!form.value.email.trim()) errors.value.email = 'Email is required'
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) errors.value.email = 'Invalid email format'
  if (!form.value.first_name.trim()) errors.value.first_name = 'First name is required'
  if (!form.value.last_name.trim()) errors.value.last_name = 'Last name is required'
  if (!form.value.password) errors.value.password = 'Password is required'
  else if (form.value.password.length < 8) errors.value.password = 'Password must be at least 8 characters'
  if (form.value.password !== form.value.password_confirm) errors.value.password_confirm = 'Passwords do not match'
  if (!form.value.phone.trim()) errors.value.phone = 'Phone number is required'
  else if (!/^09\d{9}$/.test(form.value.phone.replace(/\s/g, ''))) errors.value.phone = 'Enter valid PH mobile (09XXXXXXXXX)'

  return Object.keys(errors.value).length === 0
}

async function handleRegister() {
  if (!validateForm()) return
  
  loading.value = true
  error.value = ''
  
  try {
    await authStore.register(form.value)
    router.push('/catalog')
  } catch (e) {
    error.value = e.response?.data?.detail || e.response?.data?.error || 'Registration failed. Please try again.'
    // Map field errors
    if (e.response?.data) {
      Object.keys(e.response.data).forEach(key => {
        if (key !== 'detail' && key !== 'error') {
          errors.value[key] = Array.isArray(e.response.data[key]) ? e.response.data[key][0] : e.response.data[key]
        }
      })
    }
  } finally {
    loading.value = false
  }
}

function goToLogin() {
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-bg px-4 py-12">
    <div class="w-full max-w-md">
      <!-- Brand Header -->
      <div class="text-center mb-8">
        <router-link to="/catalog" class="brand inline-flex">
          <span class="mark">EC</span>
          <span>E-Compra<small>Mandaue Public Market</small></span>
        </router-link>
        <h1 class="text-2xl font-bold mt-4">Create Account</h1>
        <p class="muted mt-1">Join as a customer to start shopping</p>
      </div>

      <!-- Register Card -->
      <div class="card stack" style="gap: 16px;">
        <div v-if="error" class="p-3 rounded" style="background: var(--color-danger-bg); border: 1px solid var(--color-danger); color: var(--color-danger);">
          {{ error }}
        </div>

        <form @submit.prevent="handleRegister" class="stack" style="gap: 12px;">
          <!-- Name Row -->
          <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 12px;">
            <div class="field">
              <label class="small">First Name</label>
              <input v-model="form.first_name" type="text" class="input" :class="{ 'input-error': errors.first_name }" placeholder="Juan" autocomplete="given-name" required />
              <span v-if="errors.first_name" class="field-error">{{ errors.first_name }}</span>
            </div>
            <div class="field">
              <label class="small">Last Name</label>
              <input v-model="form.last_name" type="text" class="input" :class="{ 'input-error': errors.last_name }" placeholder="Dela Cruz" autocomplete="family-name" required />
              <span v-if="errors.last_name" class="field-error">{{ errors.last_name }}</span>
            </div>
          </div>

          <!-- Username -->
          <div class="field">
            <label class="small">Username</label>
            <input v-model="form.username" type="text" class="input" :class="{ 'input-error': errors.username }" placeholder="juandelacruz" autocomplete="username" required />
            <span v-if="errors.username" class="field-error">{{ errors.username }}</span>
          </div>

          <!-- Email -->
          <div class="field">
            <label class="small">Email</label>
            <input v-model="form.email" type="email" class="input" :class="{ 'input-error': errors.email }" placeholder="juan@email.com" autocomplete="email" required />
            <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
          </div>

          <!-- Phone -->
          <div class="field">
            <label class="small">Phone Number</label>
            <input v-model="form.phone" type="tel" class="input" :class="{ 'input-error': errors.phone }" placeholder="09171234567" autocomplete="tel" required />
            <span v-if="errors.phone" class="field-error">{{ errors.phone }}</span>
            <span class="field-hint">Philippine mobile format: 09XXXXXXXXX</span>
          </div>

          <!-- Address (Optional) -->
          <div class="field">
            <label class="small">Address <span class="muted">(optional)</span></label>
            <textarea v-model="form.address" class="input" rows="2" placeholder="Unit 4B, A.C. Cortes Ave., Mandaue City" autocomplete="address-line1"></textarea>
          </div>

          <!-- Password -->
          <div class="field">
            <label class="small">Password</label>
            <div style="position: relative;">
              <input v-model="form.password" type="password" class="input" :class="{ 'input-error': errors.password }" placeholder="••••••••" autocomplete="new-password" required @input="checkPasswordStrength" />
              <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
            </div>
            <!-- Password Strength Meter -->
            <div class="meter" style="height: 4px; margin-top: 6px;">
              <div class="fill" :class="passwordStrength < 40 ? 'hi' : passwordStrength < 80 ? 'mid' : 'ok'" :style="{ width: passwordStrength + '%' }"></div>
            </div>
            <div class="tiny muted" style="display: flex; justify-content: space-between; margin-top: 4px;">
              <span>{{ passwordStrength }}% strength</span>
              <span :class="passwordStrength >= 80 ? 'text-success' : 'text-warning'">{{ passwordStrength >= 80 ? 'Strong' : passwordStrength >= 40 ? 'Fair' : 'Weak' }}</span>
            </div>
          </div>

          <!-- Confirm Password -->
          <div class="field">
            <label class="small">Confirm Password</label>
            <input v-model="form.password_confirm" type="password" class="input" :class="{ 'input-error': errors.password_confirm }" placeholder="••••••••" autocomplete="new-password" required />
            <span v-if="errors.password_confirm" class="field-error">{{ errors.password_confirm }}</span>
          </div>

          <!-- Submit -->
          <button type="submit" :disabled="loading" class="btn btn-accent btn-lg btn-block" style="margin-top: 8px;">
            <span v-if="loading">Creating account…</span>
            <span v-else>Create Account</span>
          </button>
        </form>

        <!-- Login Link -->
        <p class="text-center muted mt-4">
          Already have an account? <router-link to="/login" class="link">Login</router-link>
        </p>
      </div>

      <footer class="foot">
        <div class="wrap row-between">
          <span>E-Compra · CCS630 Advance Database Systems capstone</span>
          <span>All prices in Philippine pesos (₱)</span>
        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.input-error {
  border-color: var(--color-danger) !important;
}
.field-error {
  color: var(--color-danger);
  font-size: 0.75rem;
  margin-top: 4px;
  display: block;
}
.field-hint {
  color: var(--color-muted);
  font-size: 0.7rem;
  margin-top: 4px;
  display: block;
}
.meter {
  background: var(--color-border);
  border-radius: 999px;
  overflow: hidden;
}
.fill {
  height: 100%;
  transition: width 0.3s ease, background 0.3s ease;
}
.fill.hi { background: var(--color-danger); }
.fill.mid { background: var(--color-warning); }
.fill.ok { background: var(--color-success); }
</style>
```

#### ✅ Verification Steps for 2.1
```bash
# 1. Verify component file exists and is valid Vue SFC
cd frontend
ls -la src/views/RegisterView.vue

# 2. Check for syntax errors with Vue compiler
npx vue-tsc --noEmit 2>&1 | head -20
# Or if no vue-tsc, just verify it's valid syntax:
node -e "
const fs = require('fs');
const content = fs.readFileSync('src/views/RegisterView.vue', 'utf8');
const hasScript = content.includes('<script setup>');
const hasTemplate = content.includes('<template>');
const hasStyle = content.includes('<style scoped>');
console.log('Script:', hasScript, 'Template:', hasTemplate, 'Style:', hasStyle);
"

# 3. Verify design system classes used
grep -E '\.(card|btn|field|input|meter|fill|badge|stack|grid)\b' src/views/RegisterView.vue
# Should show usage of: .card, .btn, .field, .input, .meter, .fill, .stack, .grid

# 4. Verify no inline styles except dynamic ones
grep -E 'style="[^"]*[^:}]"' src/views/RegisterView.vue | grep -v ':style'
# Should only show dynamic styles with :style or computed values
```

### 2.2 Add Register Action to Auth Store
**File**: `frontend/src/stores/auth.js`

```javascript
// ADD to actions object
async register(userData) {
  const res = await api.post('accounts/auth/register/', userData)
  localStorage.setItem('access_token', res.data.access)
  localStorage.setItem('refresh_token', res.data.refresh)
  this.isAuthenticated = true
  await this.fetchUser()
},
```

#### ✅ Verification Steps for 2.2
```bash
# 1. Verify auth store syntax
cd frontend
node -c src/stores/auth.js 2>&1 || echo "Syntax check (requires module)"

# 2. Verify register action exists
grep -A 7 "async register" src/stores/auth.js

# 3. Verify it calls correct API endpoint
grep "accounts/auth/register" src/stores/auth.js

# 4. Verify tokens stored and fetchUser called
grep -E "localStorage.setItem|fetchUser" src/stores/auth.js
```

### 2.3 Add Route and Import
**File**: `frontend/src/router/index.js`

```javascript
// ADD import
import RegisterView from '@/views/RegisterView.vue'

// ADD to routes array (after login route)
{ path: '/register', name: 'register', component: RegisterView, meta: { public: true } },
```

#### ✅ Verification Steps for 2.3
```bash
# 1. Verify router syntax
cd frontend
node -c src/router/index.js 2>&1 || echo "Module check"

# 2. Verify RegisterView import
grep "RegisterView" src/router/index.js

# 3. Verify route configuration
grep -A 2 "'register'" src/router/index.js
# Should show: path: '/register', name: 'register', component: RegisterView, meta: { public: true }

# 4. Test route resolution in dev server (after npm run dev)
# Navigate to http://localhost:5173/register - should load without 404
```

### 2.4 Update Navbar - Add Register Link
**File**: `frontend/src/components/Navbar.vue`

```vue
<!-- In desktop nav section, replace Login-only link (lines 45-52) with: -->
<div v-else class="flex items-center gap-2">
  <router-link to="/register" class="btn btn-sm" style="background: transparent; border-color: rgba(255,255,255,.3); color: #fff;">
    Register
  </router-link>
  <router-link to="/login" class="btn btn-sm" style="background: rgba(255,255,255,.16); border-color: transparent; color: #fff; padding: 5px 12px;">
    Login
  </router-link>
</div>

<!-- In mobile menu section, replace Login-only link (lines 110-117) with: -->
<div class="flex flex-col gap-2 pt-2">
  <router-link to="/register" class="w-full px-4 py-2 text-sm font-medium text-center rounded-lg" style="background: transparent; border: 1px solid rgba(255,255,255,.3); color: #fff;">
    Register
  </router-link>
  <router-link to="/login" class="w-full px-4 py-2 text-sm font-medium text-center rounded-lg" style="background: var(--color-accent); color: #fff; border: none;">
    Login
  </router-link>
</div>
```

#### ✅ Verification Steps for 2.4
```bash
# 1. Verify Register link exists in desktop nav
cd frontend
grep -A 5 "v-else class=\"flex items-center gap-2\"" src/components/Navbar.vue
# Should show Register and Login links

# 2. Verify Register link exists in mobile menu
grep -A 8 "flex flex-col gap-2 pt-2" src/components/Navbar.vue
# Should show Register and Login links

# 3. Verify no duplicate Login links
grep -c "to=\"/login\"" src/components/Navbar.vue
# Should be 2 (desktop + mobile)

# 4. Visual check: Start dev server
npm run dev
# Navigate to http://localhost:5173/ - should see "Register" button in navbar when logged out
```

### 2.5 Run Frontend Unit Tests
```bash
cd frontend
npm test -- --run
```

**Expected**: 6 tests pass (existing) + any new register tests you add ✓

#### ✅ Verification Steps for 2.5
```bash
# 1. Run all unit tests
cd frontend
npm test -- --run

# 2. Run with coverage
npm test -- --run --coverage

# 3. Verify specific component tests (if added)
# Create RegisterView.test.js and run:
# npm test -- --run src/views/RegisterView.test.js

# 4. Check for console errors in test output
npm test -- --run 2>&1 | grep -E "(PASS|FAIL|Error|Warning)"

# 5. Run linting
npm run lint 2>&1 | head -20
```

#### ✅ Phase 2 Integration Verification
```bash
# 1. Start both backend and frontend
# Terminal 1:
cd backend && source .venv/bin/activate && python manage.py runserver

# Terminal 2:
cd frontend && npm run dev

# 2. Navigate to http://localhost:5173/register
# - Page loads with form
# - Fill valid data → submit → redirects to /catalog
# - Navbar shows username + "customer" role

# 3. Test validation:
# - Empty submit → shows field errors
# - Duplicate username → shows API error
# - Password mismatch → shows error
# - Short password → strength meter shows weak

# 4. Test login link from register page
# - Click "Login" → navigates to /login

# 5. Test register link from login page
# - Go to /login → click "Register" → navigates to /register
```

---

## Phase 3: Market Administrator Role

### 3.1 Update CurrentUserSerializer for Admin Role
**File**: `backend/accounts/serializers.py`

```python
# MODIFY get_role method in CurrentUserSerializer
def get_role(self, obj):
    # Check is_staff first (Market Admin)
    if obj.is_staff_bool:
        return "admin"
    # Then vendor
    if hasattr(obj, "vendor") and obj.vendor:
        return "vendor"
    # Default customer
    return "customer"
```

#### ✅ Verification Steps for 3.1
```bash
# 1. Verify get_role method updated
cd backend
source .venv/bin/activate
grep -A 10 "def get_role" accounts/serializers.py
# Should show is_staff_bool check first

# 2. Test role detection in shell
python manage.py shell -c "
from accounts.models import AuthUser
from accounts.serializers import CurrentUserSerializer

# Test admin user
admin = AuthUser.objects.filter(is_staff=1).first()
if admin:
    s = CurrentUserSerializer(admin)
    print(f'Admin user: {admin.username}, role: {s.data[\"role\"]}')

# Test vendor user
vendor_user = AuthUser.objects.filter(vendor__isnull=False).first()
if vendor_user:
    s = CurrentUserSerializer(vendor_user)
    print(f'Vendor user: {vendor_user.username}, role: {s.data[\"role\"]}')

# Test customer user
customer = AuthUser.objects.filter(is_staff=0).exclude(vendor__isnull=False).first()
if customer:
    s = CurrentUserSerializer(customer)
    print(f'Customer user: {customer.username}, role: {s.data[\"role\"]}')
"
```

### 3.2 Create Admin Permission Class
**File**: `backend/accounts/permissions.py` (NEW FILE)

```python
from rest_framework import permissions


class IsMarketAdmin(permissions.BasePermission):
    """
    Allows access only to Market Administrators (is_staff=True).
    """
    message = "Market Administrator privileges required."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'is_staff_bool', False)
        )


class IsMarketAdminOrReadOnly(permissions.BasePermission):
    """
    Allows read access to all authenticated users, write access only to Market Admins.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'is_staff_bool', False)
        )
```

#### ✅ Verification Steps for 3.2
```bash
# 1. Verify file created and syntax
cd backend
source .venv/bin/activate
python -c "from accounts.permissions import IsMarketAdmin, IsMarketAdminOrReadOnly; print('Import OK')"

# 2. Test permission logic in shell
python manage.py shell -c "
from accounts.permissions import IsMarketAdmin
from accounts.models import AuthUser
from rest_framework.request import Request
from django.test import RequestFactory

factory = RequestFactory()
perm = IsMarketAdmin()

# Test admin user
admin = AuthUser.objects.filter(is_staff=1).first()
if admin:
    request = factory.get('/')
    request.user = admin
    print(f'Admin ({admin.username}): {perm.has_permission(request, None)}')

# Test customer user
customer = AuthUser.objects.filter(is_staff=0).first()
if customer:
    request = factory.get('/')
    request.user = customer
    print(f'Customer ({customer.username}): {perm.has_permission(request, None)}')

# Test unauthenticated
request = factory.get('/')
request.user = None
print(f'Unauthenticated: {perm.has_permission(request, None)}')
"

# 3. Run Django system check
python manage.py check
```

### 3.3 Update Navbar for Admin Link
**File**: `frontend/src/components/Navbar.vue`

```javascript
// ADD to computed (after isVendor)
const isAdmin = computed(() => authStore.user?.role === 'admin')

// In navItems array, ADD admin item (only visible to admins):
const adminNavItems = [
  { name: 'admin-dashboard', label: 'Admin Dashboard', to: '/admin' },
  { name: 'admin-vendors', label: 'Manage Vendors', to: '/admin/vendors' },
]

// Update visibleNavItems computed:
const visibleNavItems = computed(() => {
  if (isAdmin.value) {
    return [...navItems, ...adminNavItems]  // Or create separate admin layout
  }
  if (isVendor.value) {
    return vendorNavItems
  }
  return navItems
})
```

**Note**: For better UX, consider a separate admin layout. For now, we'll add to existing nav.

#### ✅ Verification Steps for 3.3
```bash
# 1. Verify isAdmin computed property
cd frontend
grep -A 3 "const isAdmin" src/components/Navbar.vue

# 2. Verify adminNavItems array
grep -A 5 "const adminNavItems" src/components/Navbar.vue

# 3. Verify visibleNavItems logic
grep -A 10 "const visibleNavItems" src/components/Navbar.vue

# 4. Visual check with admin user:
# - Login as admin (is_staff=1)
# - Navbar should show "Admin Dashboard" and "Manage Vendors" links
# - Non-admin users should NOT see these links
```

### 3.4 Test Role Detection
```bash
cd backend
source .venv/bin/activate
python manage.py shell -c "
from accounts.models import AuthUser
u = AuthUser.objects.first()
print(f'User: {u.username}, is_staff: {u.is_staff}, is_staff_bool: {u.is_staff_bool}')
"
```

#### ✅ Verification Steps for 3.4
```bash
# 1. Test role detection for all user types
cd backend
source .venv/bin/activate
python manage.py shell -c "
from accounts.models import AuthUser
from accounts.serializers import CurrentUserSerializer

users = AuthUser.objects.all()
for u in users:
    s = CurrentUserSerializer(u)
    print(f'{u.username}: is_staff={u.is_staff}, role={s.data[\"role\"]}')
"

# 2. Verify API returns correct role
# Start backend server
python manage.py runserver &

# Test with curl (replace TOKEN with actual JWT)
# curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/api/accounts/auth/user/
# Should return: {"role": "admin"} for staff users

# 3. Run any existing tests to ensure no regression
python manage.py test accounts -v 2
```

#### ✅ Phase 3 Integration Verification
```bash
# 1. Create admin user if not exists
cd backend
source .venv/bin/activate
python manage.py shell -c "
from accounts.models import AuthUser, Userprofile
from django.utils import timezone

if not AuthUser.objects.filter(username='marketadmin').exists():
    admin = AuthUser.objects.create(
        username='marketadmin',
        email='admin@market.com',
        first_name='Market',
        last_name='Admin',
        is_active=1,
        is_staff=1,
        is_superuser=0,
        date_joined=timezone.now(),
    )
    admin.set_password('adminpass123')
    admin.save()
    Userprofile.objects.create(user=admin, is_vendor=0)
    print('Admin created')
else:
    print('Admin exists')
"

# 2. Full backend test suite
python manage.py test accounts -v 2

# 3. Frontend visual check:
# - Login as marketadmin/adminpass123
# - Navbar shows Admin Dashboard + Manage Vendors
# - Navigate to /admin/vendors → should load (not redirect)
```

---

## Phase 4: Admin Vendor Creation API

### 4.1 Create Vendor Create Serializer
**File**: `backend/vendors/serializers.py`

```python
# REPLACE or CREATE file
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from accounts.models import AuthUser, Userprofile
from catalog.models import Vendor
from vendors.models import PosVendor


class VendorCreateSerializer(serializers.Serializer):
    """Serializer for Market Admin to create vendor accounts."""
    # User account fields
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)

    # Vendor business fields
    name = serializers.CharField(max_length=150, help_text="Business/Stall name")
    stall_location = serializers.CharField(max_length=120)
    market_section = serializers.CharField(max_length=120)
    contact_phone = serializers.CharField(max_length=32)
    contact_email = serializers.EmailField()

    def validate_username(self, value):
        if AuthUser.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if AuthUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate_contact_email(self, value):
        if Vendor.objects.filter(contact_email__iexact=value).exists():
            raise serializers.ValidationError("Vendor contact email already in use")
        return value

    @transaction.atomic
    def create(self, validated_data):
        # Extract user fields
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'password': validated_data.pop('password'),
        }
        vendor_data = validated_data

        # Create AuthUser
        user = AuthUser.objects.create(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_active=1,
            is_staff=0,  # Not admin
            is_superuser=0,
            date_joined=timezone.now(),
        )
        user.set_password(user_data['password'])
        user.save()

        # Create Userprofile (is_vendor=1)
        Userprofile.objects.create(
            user=user,
            is_vendor=1,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        # Create Catalog Vendor (links to user)
        vendor = Vendor.objects.create(
            name=vendor_data['name'],
            stall_location=vendor_data['stall_location'],
            market_section=vendor_data['market_section'],
            contact_phone=vendor_data['contact_phone'],
            contact_email=vendor_data['contact_email'],
            is_active=1,
            user=user,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        # Create PosVendor (links to catalog Vendor)
        PosVendor.objects.create(
            catalog_vendor=vendor,
            stall_name=vendor_data['name'],
            stall_location=vendor_data['stall_location'],
        )

        return vendor


class VendorListSerializer(serializers.ModelSerializer):
    """Serializer for admin vendor list view."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_is_active = serializers.IntegerField(source='user.is_active', read_only=True)

    class Meta:
        model = Vendor
        fields = [
            'id', 'name', 'stall_location', 'market_section',
            'contact_phone', 'contact_email', 'is_active',
            'user_email', 'user_username', 'user_is_active',
            'created_at', 'updated_at',
        ]


class VendorDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single vendor."""
    user = serializers.SerializerMethodField()
    pos_vendor = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = '__all__'

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'is_active': obj.user.is_active,
            'date_joined': obj.user.date_joined,
        }

    def get_pos_vendor(self, obj):
        try:
            pv = obj.posvendor  # reverse OneToOne
            return {
                'id': pv.catalog_vendor_id,
                'stall_name': pv.stall_name,
                'stall_location': pv.stall_location,
            }
        except PosVendor.DoesNotExist:
            return None
```

#### ✅ Verification Steps for 4.1
```bash
# 1. Verify file created and imports work
cd backend
source .venv/bin/activate
python -c "from vendors.serializers import VendorCreateSerializer, VendorListSerializer, VendorDetailSerializer; print('Import OK')"

# 2. Verify serializer fields
python -c "
from vendors.serializers import VendorCreateSerializer
s = VendorCreateSerializer()
print('Fields:', list(s.fields.keys()))
print('Required:', [k for k,v in s.fields.items() if v.required])
"

# 3. Test validation logic in shell
python manage.py shell -c "
from vendors.serializers import VendorCreateSerializer

# Test valid data
data = {
    'username': 'testvendor',
    'email': 'test@vendor.com',
    'first_name': 'Test',
    'last_name': 'Vendor',
    'password': 'VendorPass123',
    'name': 'Test Stall',
    'stall_location': 'Stall A-1',
    'market_section': 'Fish',
    'contact_phone': '09171112233',
    'contact_email': 'stall@vendor.com',
}
s = VendorCreateSerializer(data=data)
print('Valid:', s.is_valid())
if not s.is_valid():
    print('Errors:', s.errors)

# Test duplicate username
s2 = VendorCreateSerializer(data=data)
print('Duplicate username valid:', s2.is_valid())
"
```

### 4.2 Create Admin Vendor Views
**File**: `backend/vendors/views.py`

```python
# REPLACE entire file
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.utils import timezone

from accounts.permissions import IsMarketAdmin
from orders.models import Order
from orders.serializers import OrderSerializer
from orders.services import transition_order_status
from vendors.models import PosVendor
from vendors.serializers import (
    VendorCreateSerializer,
    VendorListSerializer,
    VendorDetailSerializer,
    PosVendorSerializer,
)


class PosVendorList(generics.ListAPIView):
    queryset = PosVendor.objects.select_related("catalog_vendor")
    serializer_class = PosVendorSerializer
    permission_classes = [IsAuthenticated]


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
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            order = transition_order_status(order, new_status_code)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order, context={"request": request}).data)


# === NEW ADMIN ENDPOINTS ===

class AdminVendorListView(generics.ListAPIView):
    """List all vendors for Market Admin."""
    permission_classes = [IsAuthenticated, IsMarketAdmin]
    serializer_class = VendorListSerializer
    queryset = Vendor.objects.select_related('user').all().order_by('-created_at')


class AdminVendorCreateView(APIView):
    """Create vendor account with linked user and profiles."""
    permission_classes = [IsAuthenticated, IsMarketAdmin]

    def post(self, request):
        serializer = VendorCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vendor = serializer.save()
        
        # Return detailed vendor info
        detail_serializer = VendorDetailSerializer(vendor)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)


class AdminVendorDetailView(generics.RetrieveUpdateAPIView):
    """Get or update vendor details."""
    permission_classes = [IsAuthenticated, IsMarketAdmin]
    serializer_class = VendorDetailSerializer
    queryset = Vendor.objects.select_related('user').all()
    lookup_field = 'id'


class AdminVendorDeactivateView(APIView):
    """Soft deactivate vendor (sets is_active=0 on vendor and user)."""
    permission_classes = [IsAuthenticated, IsMarketAdmin]

    @transaction.atomic
    def post(self, request, id):
        try:
            vendor = Vendor.objects.select_related('user').get(id=id)
        except Vendor.DoesNotExist:
            return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

        vendor.is_active = 0
        vendor.updated_at = timezone.now()
        vendor.save()

        vendor.user.is_active = 0
        vendor.user.save()

        return Response({"message": "Vendor deactivated successfully"})
```

#### ✅ Verification Steps for 4.2
```bash
# 1. Verify imports and syntax
cd backend
source .venv/bin/activate
python -c "from vendors.views import AdminVendorListView, AdminVendorCreateView, AdminVendorDetailView, AdminVendorDeactivateView; print('Import OK')"

# 2. Verify permission classes
grep -A 2 "class AdminVendor" vendors/views.py | grep -E "permission_classes|IsMarketAdmin"

# 3. Test view instantiation
python manage.py shell -c "
from vendors.views import AdminVendorListView, AdminVendorCreateView
print('List view:', AdminVendorListView)
print('Create view:', AdminVendorCreateView)
"

# 4. Run Django system check
python manage.py check
```

### 4.3 Add Admin Vendor URLs
**File**: `backend/vendors/urls.py`

```python
# REPLACE entire file
from django.urls import path
from vendors.views import (
    PosVendorList,
    VendorPOSView,
    AdminVendorListView,
    AdminVendorCreateView,
    AdminVendorDetailView,
    AdminVendorDeactivateView,
)

urlpatterns = [
    # Vendor POS (existing)
    path("", PosVendorList.as_view(), name="pos-vendor-list"),
    path("pos/", VendorPOSView.as_view(), name="vendor-pos"),
    
    # Market Admin endpoints (NEW)
    path("admin/", AdminVendorListView.as_view(), name="admin-vendor-list"),
    path("admin/create/", AdminVendorCreateView.as_view(), name="admin-vendor-create"),
    path("admin/<int:id>/", AdminVendorDetailView.as_view(), name="admin-vendor-detail"),
    path("admin/<int:id>/deactivate/", AdminVendorDeactivateView.as_view(), name="admin-vendor-deactivate"),
]
```

#### ✅ Verification Steps for 4.3
```bash
# 1. Verify URL patterns
cd backend
source .venv/bin/activate
python -c "
from django.urls import get_resolver
resolver = get_resolver()
for pattern in resolver.url_patterns:
    if 'vendors' in str(pattern.pattern):
        print(pattern)
        if hasattr(pattern, 'url_patterns'):
            for p in pattern.url_patterns:
                print('  ', p)
"

# 2. Test URL resolution
python -c "
from django.urls import reverse
urls = [
    'admin-vendor-list',
    'admin-vendor-create',
]
for name in urls:
    try:
        url = reverse(name)
        print(f'{name}: {url}')
    except Exception as e:
        print(f'{name}: ERROR - {e}')
"

# 3. Run Django system check
python manage.py check
```

### 4.4 Backend Tests for Admin Vendor API
**File**: `backend/vendors/tests.py` (NEW FILE)

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import AuthUser, Userprofile
from catalog.models import Vendor
from vendors.models import PosVendor


class AdminVendorAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create Market Admin user
        self.admin = AuthUser.objects.create(
            username='marketadmin',
            email='admin@market.com',
            first_name='Market',
            last_name='Admin',
            is_active=1,
            is_staff=1,
            is_superuser=0,
        )
        self.admin.set_password('adminpass123')
        self.admin.save()
        Userprofile.objects.create(user=self.admin, is_vendor=0)
        
        # Create regular customer
        self.customer = AuthUser.objects.create(
            username='customer1',
            email='cust@test.com',
            first_name='Customer',
            last_name='One',
            is_active=1,
            is_staff=0,
        )
        self.customer.set_password('custpass123')
        self.customer.save()
        Userprofile.objects.create(user=self.customer, is_vendor=0)
        
        self.list_url = '/api/vendors/admin/'
        self.create_url = '/api/vendors/admin/create/'
        
        self.valid_vendor_data = {
            'username': 'vendor_rosa',
            'email': 'rosa@vendor.com',
            'first_name': 'Rosa',
            'last_name': 'Vegetables',
            'password': 'VendorPass123',
            'name': 'Rosa\'s Fresh Vegetables',
            'stall_location': 'Stall A-12',
            'market_section': 'Vegetables Section',
            'contact_phone': '09171112233',
            'contact_email': 'rosa@stall.com',
        }

    def authenticate_admin(self):
        self.client.force_authenticate(user=self.admin)

    def authenticate_customer(self):
        self.client.force_authenticate(user=self.customer)

    def test_admin_can_list_vendors(self):
        self.authenticate_admin()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_customer_cannot_list_vendors(self):
        self.authenticate_customer()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_vendors(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_create_vendor(self):
        self.authenticate_admin()
        response = self.client.post(self.create_url, self.valid_vendor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], "Rosa's Fresh Vegetables")
        self.assertEqual(response.data['user']['username'], 'vendor_rosa')
        
        # Verify all models created
        vendor = Vendor.objects.get(name="Rosa's Fresh Vegetables")
        self.assertEqual(vendor.user.username, 'vendor_rosa')
        self.assertTrue(Userprofile.objects.filter(user=vendor.user, is_vendor=1).exists())
        self.assertTrue(PosVendor.objects.filter(catalog_vendor=vendor).exists())

    def test_admin_create_vendor_duplicate_username(self):
        self.authenticate_admin()
        # Create once
        self.client.post(self.create_url, self.valid_vendor_data, format='json')
        # Try again
        response = self.client.post(self.create_url, self.valid_vendor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_admin_create_vendor_duplicate_email(self):
        self.authenticate_admin()
        self.client.post(self.create_url, self.valid_vendor_data, format='json')
        # Different username, same email
        data = {**self.valid_vendor_data, 'username': 'vendor_rosa2'}
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_customer_cannot_create_vendor(self):
        self.authenticate_customer()
        response = self.client.post(self.create_url, self.valid_vendor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_deactivate_vendor(self):
        self.authenticate_admin()
        create_resp = self.client.post(self.create_url, self.valid_vendor_data, format='json')
        vendor_id = create_resp.data['id']
        
        deactivate_url = f'/api/vendors/admin/{vendor_id}/deactivate/'
        response = self.client.post(deactivate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        vendor = Vendor.objects.get(id=vendor_id)
        self.assertEqual(vendor.is_active, 0)
        self.assertEqual(vendor.user.is_active, 0)
```

#### ✅ Verification Steps for 4.4
```bash
# 1. Verify test file syntax
cd backend
source .venv/bin/activate
python -m py_compile vendors/tests.py
echo "Syntax OK"

# 2. Verify test class and methods
grep -E "class|def test_" vendors/tests.py

# 3. Run specific test class
python manage.py test vendors.tests.AdminVendorAPITest -v 2

# 4. Run with verbose output for each test
python manage.py test vendors.tests.AdminVendorAPITest -v 3

# 5. Test individual methods
python manage.py test vendors.tests.AdminVendorAPITest.test_admin_can_create_vendor -v 3
python manage.py test vendors.tests.AdminVendorAPITest.test_customer_cannot_create_vendor -v 3
```

### 4.5 Run Backend Tests
```bash
cd backend
source .venv/bin/activate
python manage.py test vendors.tests.AdminVendorAPITest -v 2
python manage.py test accounts.tests.RegisterAPITest -v 2
```

**Expected**: All tests pass ✓

#### ✅ Verification Steps for 4.5
```bash
# 1. Run all vendor tests
cd backend
source .venv/bin/activate
python manage.py test vendors -v 2

# 2. Run all accounts tests
python manage.py test accounts -v 2

# 3. Run combined test suite
python manage.py test accounts vendors -v 2

# 4. Test manual API calls with curl (with admin token)
# First login as admin to get token:
# curl -X POST http://localhost:8000/api/auth/token/ -H "Content-Type: application/json" -d '{"username":"marketadmin","password":"adminpass123"}'
# Save the access token, then:
# curl -X GET http://localhost:8000/api/vendors/admin/ -H "Authorization: Bearer <TOKEN>"
# curl -X POST http://localhost:8000/api/vendors/admin/create/ -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{"username":"vendor_test","email":"vendor@test.com","first_name":"Test","last_name":"Vendor","password":"VendorPass123","name":"Test Stall","stall_location":"Stall B-1","market_section":"Fish","contact_phone":"09182223344","contact_email":"stall@test.com"}'

# 5. Verify database state after API calls
python manage.py shell -c "
from accounts.models import AuthUser, Userprofile
from catalog.models import Vendor
from vendors.models import PosVendor

# Check created vendor
v = Vendor.objects.filter(name='Test Stall').first()
if v:
    print(f'Vendor: {v.name}, user: {v.user.username}')
    print(f'Userprofile is_vendor=1: {Userprofile.objects.filter(user=v.user, is_vendor=1).exists()}')
    print(f'PosVendor exists: {PosVendor.objects.filter(catalog_vendor=v).exists()}')
"
```

#### ✅ Phase 4 Integration Verification
```bash
# 1. Full backend test suite
cd backend
source .venv/bin/activate
python manage.py test accounts vendors -v 2

# 2. Verify no regressions in existing functionality
python manage.py test catalog orders cart favorites -v 2

# 3. Manual end-to-end test:
# - Login as admin → get token
# - POST /api/vendors/admin/create/ → creates vendor + user + profiles
# - Verify vendor can login with created credentials
# - Verify vendor sees vendor navbar (Dashboard, Products, Orders, POS)
# - Admin can deactivate vendor → vendor cannot login

# 4. Check API documentation (Swagger)
# Open http://localhost:8000/api/schema/swagger-ui/
# Verify new endpoints appear under /api/vendors/admin/
```

---

## Phase 5: Admin Dashboard UI (Frontend)

### 5.1 Create Admin Dashboard View
**File**: `frontend/src/views/AdminDashboardView.vue`

```vue
<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const stats = ref({
  totalVendors: 0,
  activeVendors: 0,
  totalCustomers: 0,
  totalOrders: 0,
})
const loading = ref(true)
const error = ref('')

async function fetchStats() {
  try {
    loading.value = true
    const [vendorsRes, customersRes, ordersRes] = await Promise.all([
      api.get('/vendors/admin/'),
      api.get('/accounts/auth/user/'), // Not ideal, need admin user count endpoint
      api.get('/orders/'), // Adjust based on actual endpoint
    ])
    stats.value.totalVendors = vendorsRes.data.length
    stats.value.activeVendors = vendorsRes.data.filter(v => v.is_active === 1).length
    // Add more stats as needed
  } catch (e) {
    error.value = 'Failed to load dashboard'
  } finally {
    loading.value = false
  }
}

function navigateToVendors() {
  router.push('/admin/vendors')
}

onMounted(() => {
  if (!authStore.isAuthenticated || authStore.user?.role !== 'admin') {
    router.push('/catalog')
    return
  }
  fetchStats()
})
</script>

<template>
  <div class="min-h-screen bg-bg">
    <div class="page">
      <div class="wrap stack">
        <div class="pagehead">
          <h1>Admin Dashboard</h1>
          <p>Market Administrator overview</p>
        </div>

        <div v-if="loading" class="text-center py-12">Loading…</div>

        <div v-else-if="error" class="card" style="background: var(--color-danger-bg); border-color: var(--color-danger);">
          <p>{{ error }}</p>
        </div>

        <div v-else class="grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
          <div class="card stat">
            <div class="stat-label">Total Vendors</div>
            <div class="stat-value">{{ stats.totalVendors }}</div>
          </div>
          <div class="card stat">
            <div class="stat-label">Active Vendors</div>
            <div class="stat-value">{{ stats.activeVendors }}</div>
          </div>
          <div class="card stat">
            <div class="stat-label">Total Customers</div>
            <div class="stat-value">{{ stats.totalCustomers }}</div>
          </div>
          <div class="card stat">
            <div class="stat-label">Total Orders</div>
            <div class="stat-value">{{ stats.totalOrders }}</div>
          </div>
        </div>

        <div class="card">
          <div class="card-head row-between">
            <h3>Quick Actions</h3>
          </div>
          <div class="stack" style="gap: 12px;">
            <button @click="navigateToVendors" class="btn btn-accent">
              ➕ Add New Vendor
            </button>
            <router-link to="/admin/vendors" class="btn">
              📋 View All Vendors
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
```

#### ✅ Verification Steps for 5.1
```bash
# 1. Verify component file exists
cd frontend
ls -la src/views/AdminDashboardView.vue

# 2. Check for syntax validity
node -e "
const fs = require('fs');
const content = fs.readFileSync('src/views/AdminDashboardView.vue', 'utf8');
const checks = [
  ['script setup', content.includes('<script setup>')],
  ['template', content.includes('<template>')],
  ['onMounted', content.includes('onMounted')],
  ['useAuthStore', content.includes('useAuthStore')],
  ['role check', content.includes('role !==')],
  ['stat classes', content.includes('class=\"card stat\"')],
];
checks.forEach(([name, pass]) => console.log(name + ':', pass ? '✓' : '✗'));
"

# 3. Verify design system classes used
grep -E '\.(card|btn|stat|grid|stack|pagehead|wrap)\b' src/views/AdminDashboardView.vue | sort -u
# Should show: .card, .btn, .stat, .grid, .stack, .pagehead, .wrap
```

### 5.2 Create Admin Vendors Management View
**File**: `frontend/src/views/AdminVendorsView.vue`

```vue
<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const vendors = ref([])
const loading = ref(true)
const error = ref('')
const showCreateModal = ref(false)
const creating = ref(false)

// Create form
const form = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  name: '',
  stall_location: '',
  market_section: '',
  contact_phone: '',
  contact_email: '',
})
const formErrors = ref({})

async function fetchVendors() {
  try {
    loading.value = true
    const res = await api.get('/vendors/admin/')
    vendors.value = res.data
  } catch (e) {
    error.value = 'Failed to load vendors'
  } finally {
    loading.value = false
  }
}

function validateForm() {
  formErrors.value = {}
  const required = ['username', 'email', 'first_name', 'last_name', 'password', 'name', 'stall_location', 'market_section', 'contact_phone', 'contact_email']
  required.forEach(field => {
    if (!form.value[field]?.trim()) formErrors.value[field] = 'Required'
  })
  if (form.value.password && form.value.password.length < 8) formErrors.value.password = 'Min 8 characters'
  if (form.value.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) formErrors.value.email = 'Invalid email'
  if (form.value.contact_phone && !/^09\d{9}$/.test(form.value.contact_phone.replace(/\s/g, ''))) formErrors.value.contact_phone = 'Valid PH mobile required'
  return Object.keys(formErrors.value).length === 0
}

async function handleCreateVendor() {
  if (!validateForm()) return
  creating.value = true
  try {
    await api.post('/vendors/admin/create/', form.value)
    showCreateModal.value = false
    resetForm()
    await fetchVendors()
  } catch (e) {
    const data = e.response?.data
    if (data) {
      Object.keys(data).forEach(key => {
        if (key !== 'detail') formErrors.value[key] = Array.isArray(data[key]) ? data[key][0] : data[key]
      })
    } else {
      error.value = 'Failed to create vendor'
    }
  } finally {
    creating.value = false
  }
}

async function handleDeactivate(vendorId, vendorName) {
  if (!confirm(`Deactivate "${vendorName}"? This will disable their account.`)) return
  try {
    await api.post(`/vendors/admin/${vendorId}/deactivate/`)
    await fetchVendors()
  } catch (e) {
    error.value = 'Failed to deactivate vendor'
  }
}

function resetForm() {
  Object.keys(form.value).forEach(k => form.value[k] = '')
  formErrors.value = {}
}

function editVendor(vendor) {
  router.push(`/admin/vendors/${vendor.id}/edit`)
}

onMounted(() => {
  if (!authStore.isAuthenticated || authStore.user?.role !== 'admin') {
    router.push('/catalog')
    return
  }
  fetchVendors()
})
</script>

<template>
  <div class="min-h-screen bg-bg">
    <div class="page">
      <div class="wrap stack">
        <div class="pagehead row-between">
          <div>
            <h1>Manage Vendors</h1>
            <p>{{ vendors.length }} vendor{{ vendors.length !== 1 ? 's' : '' }} registered</p>
          </div>
          <button @click="showCreateModal = true" class="btn btn-accent">+ Add Vendor</button>
        </div>

        <div v-if="loading" class="text-center py-12">Loading…</div>

        <div v-else-if="error" class="card" style="background: var(--color-danger-bg); border-color: var(--color-danger);">
          <p>{{ error }}</p>
          <button @click="fetchVendors" class="btn btn-primary mt12">Retry</button>
        </div>

        <div v-else class="card">
          <div class="table-wrap">
            <table class="table">
              <thead>
                <tr>
                  <th>Vendor Name</th>
                  <th>Stall</th>
                  <th>Section</th>
                  <th>Contact</th>
                  <th>Account</th>
                  <th>Status</th>
                  <th class="actions">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="v in vendors" :key="v.id">
                  <td>
                    <strong>{{ v.name }}</strong>
                    <br><span class="tiny muted">{{ v.user_username }}</span>
                  </td>
                  <td>{{ v.stall_location }}</td>
                  <td>{{ v.market_section }}</td>
                  <td>
                    {{ v.contact_phone }}<br>
                    <span class="tiny muted">{{ v.contact_email }}</span>
                  </td>
                  <td>
                    {{ v.user_email }}<br>
                    <span class="tiny muted">{{ v.user_is_active === 1 ? 'Active' : 'Inactive' }}</span>
                  </td>
                  <td>
                    <span class="badge" :class="v.is_active === 1 ? 'badge-ok' : 'badge-warn'">
                      {{ v.is_active === 1 ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="actions">
                    <button @click="editVendor(v)" class="btn btn-sm" style="margin-right: 4px;">Edit</button>
                    <button v-if="v.is_active === 1" @click="handleDeactivate(v.id, v.name)" class="btn btn-sm" style="background: var(--color-danger-bg); border-color: var(--color-danger); color: var(--color-danger);">Deactivate</button>
                    <button v-else class="btn btn-sm" disabled style="opacity: 0.5;">Deactivated</button>
                  </td>
                </tr>
                <tr v-if="vendors.length === 0">
                  <td colspan="7" class="text-center py-8 muted">No vendors registered yet</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Vendor Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal card" style="max-width: 560px; width: 90%; max-height: 90vh; overflow-y: auto;">
        <div class="card-head row-between">
          <h3>Create New Vendor Account</h3>
          <button @click="showCreateModal = false" class="btn btn-ghost btn-sm">✕</button>
        </div>
        <form @submit.prevent="handleCreateVendor" class="stack" style="gap: 12px; padding: 16px;">
          <!-- Account Details -->
          <div class="card" style="padding: 16px;">
            <h4 class="mb12" style="border-bottom: 1px solid var(--color-border); padding-bottom: 8px;">Account Credentials</h4>
            <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 12px;">
              <div class="field">
                <label class="small">Username *</label>
                <input v-model="form.username" type="text" class="input" :class="{ 'input-error': formErrors.username }" />
                <span v-if="formErrors.username" class="field-error">{{ formErrors.username }}</span>
              </div>
              <div class="field">
                <label class="small">Email *</label>
                <input v-model="form.email" type="email" class="input" :class="{ 'input-error': formErrors.email }" />
                <span v-if="formErrors.email" class="field-error">{{ formErrors.email }}</span>
              </div>
            </div>
            <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 12px;">
              <div class="field">
                <label class="small">First Name *</label>
                <input v-model="form.first_name" type="text" class="input" :class="{ 'input-error': formErrors.first_name }" />
              </div>
              <div class="field">
                <label class="small">Last Name *</label>
                <input v-model="form.last_name" type="text" class="input" :class="{ 'input-error': formErrors.last_name }" />
              </div>
            </div>
            <div class="field">
              <label class="small">Password *</label>
              <input v-model="form.password" type="password" class="input" :class="{ 'input-error': formErrors.password }" />
              <span v-if="formErrors.password" class="field-error">{{ formErrors.password }}</span>
            </div>
          </div>

          <!-- Vendor Details -->
          <div class="card" style="padding: 16px;">
            <h4 class="mb12" style="border-bottom: 1px solid var(--color-border); padding-bottom: 8px;">Stall Information</h4>
            <div class="field">
              <label class="small">Business Name *</label>
              <input v-model="form.name" type="text" class="input" :class="{ 'input-error': formErrors.name }" placeholder="Rosa's Fresh Vegetables" />
              <span v-if="formErrors.name" class="field-error">{{ formErrors.name }}</span>
            </div>
            <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 12px;">
              <div class="field">
                <label class="small">Stall Location *</label>
                <input v-model="form.stall_location" type="text" class="input" :class="{ 'input-error': formErrors.stall_location }" placeholder="Stall A-12" />
                <span v-if="formErrors.stall_location" class="field-error">{{ formErrors.stall_location }}</span>
              </div>
              <div class="field">
                <label class="small">Market Section *</label>
                <input v-model="form.market_section" type="text" class="input" :class="{ 'input-error': formErrors.market_section }" placeholder="Vegetables Section" />
                <span v-if="formErrors.market_section" class="field-error">{{ formErrors.market_section }}</span>
              </div>
            </div>
            <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 12px;">
              <div class="field">
                <label class="small">Contact Phone *</label>
                <input v-model="form.contact_phone" type="tel" class="input" :class="{ 'input-error': formErrors.contact_phone }" placeholder="09171112233" />
                <span v-if="formErrors.contact_phone" class="field-error">{{ formErrors.contact_phone }}</span>
              </div>
              <div class="field">
                <label class="small">Contact Email *</label>
                <input v-model="form.contact_email" type="email" class="input" :class="{ 'input-error': formErrors.contact_email }" placeholder="rosa@stall.com" />
                <span v-if="formErrors.contact_email" class="field-error">{{ formErrors.contact_email }}</span>
              </div>
            </div>
          </div>

          <div class="row" style="justify-content: flex-end; gap: 8px; margin-top: 8px;">
            <button type="button" @click="showCreateModal = false" class="btn">Cancel</button>
            <button type="submit" :disabled="creating" class="btn btn-accent">
              <span v-if="creating">Creating…</span>
              <span v-else>Create Vendor</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}
.modal {
  animation: slideUp 0.2s ease;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.input-error { border-color: var(--color-danger) !important; }
.field-error { color: var(--color-danger); font-size: 0.75rem; margin-top: 4px; display: block; }
.actions { white-space: nowrap; }
</style>
```

#### ✅ Verification Steps for 5.2
```bash
# 1. Verify component file exists
cd frontend
ls -la src/views/AdminVendorsView.vue

# 2. Check for syntax validity
node -e "
const fs = require('fs');
const content = fs.readFileSync('src/views/AdminVendorsView.vue', 'utf8');
const checks = [
  ['script setup', content.includes('<script setup>')],
  ['template', content.includes('<template>')],
  ['onMounted', content.includes('onMounted')],
  ['useAuthStore', content.includes('useAuthStore')],
  ['role check', content.includes('role !==')],
  ['modal overlay', content.includes('modal-overlay')],
  ['table classes', content.includes('class=\"table\"')],
  ['badge classes', content.includes('badge-ok') && content.includes('badge-warn')],
  ['form validation', content.includes('validateForm')],
  ['API calls', content.includes('/vendors/admin/')],
];
checks.forEach(([name, pass]) => console.log(name + ':', pass ? '✓' : '✗'));
"

# 3. Verify design system classes used
grep -E '\.(card|btn|field|input|table|badge|grid|stack|modal|overlay)\b' src/views/AdminVendorsView.vue | sort -u
# Should show: .card, .btn, .field, .input, .table, .badge, .grid, .stack, .modal, .overlay
```

### 5.3 Add Admin Routes
**File**: `frontend/src/router/index.js`

```javascript
// ADD imports
import AdminDashboardView from '@/views/AdminDashboardView.vue'
import AdminVendorsView from '@/views/AdminVendorsView.vue'

// ADD to routes array
{ path: '/admin', name: 'admin-dashboard', component: AdminDashboardView, meta: { requiresAuth: true, role: 'admin' } },
{ path: '/admin/vendors', name: 'admin-vendors', component: AdminVendorsView, meta: { requiresAuth: true, role: 'admin' } },
```

#### ✅ Verification Steps for 5.3
```bash
# 1. Verify router syntax
cd frontend
node -c src/router/index.js 2>&1 || echo "Module syntax check"

# 2. Verify imports
grep "AdminDashboardView\|AdminVendorsView" src/router/index.js

# 3. Verify route definitions
grep -A 2 "'admin-dashboard'\|'admin-vendors'" src/router/index.js
# Should show path, name, component, meta with requiresAuth: true, role: 'admin'

# 4. Test route resolution in dev server
# Start: npm run dev
# Navigate to http://localhost:5173/admin (as admin) → should load dashboard
# Navigate to http://localhost:5173/admin/vendors (as admin) → should load vendor list
# Navigate as non-admin → should redirect to /catalog
```

### 5.4 Add Admin Styles to Main CSS
**File**: `frontend/src/assets/main.css`

```css
/* ADD to end of file */

/* Admin Stat Cards */
.stat {
  text-align: center;
  padding: 20px 16px;
}
.stat-label {
  font-size: 0.75rem;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}
.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

/* Table Actions */
.actions .btn {
  margin-right: 4px;
}

/* Responsive Admin Table */
@media (max-width: 768px) {
  .admin-table-responsive {
    display: block;
    overflow-x: auto;
  }
}
```

#### ✅ Verification Steps for 5.4
```bash
# 1. Verify CSS additions
cd frontend
grep -A 5 "\.stat {" src/assets/main.css
grep -A 5 "\.modal-overlay" src/assets/main.css

# 2. Check for CSS syntax (no obvious errors)
# The styles should use CSS custom properties (var(--color-*))

# 3. Visual check in browser dev tools:
# - Open http://localhost:5173/admin as admin
# - Inspect stat cards → should have .stat, .stat-label, .stat-value classes
# - Open vendor modal → should have .modal-overlay centered

# 4. Responsive check:
# - Resize browser to < 768px
# - Verify modal still centered and readable
# - Verify table has horizontal scroll if needed
```

---

## Phase 6: Integration Testing & Polish

### 6.1 Create Playwright E2E Tests
**File**: `frontend/e2e/registration-admin.spec.js`

```javascript
const { test, expect } = require('@playwright/test')

test.describe('Customer Registration Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/register')
  })

  test('should register new customer successfully', async ({ page }) => {
    const username = `testuser_${Date.now()}`
    const email = `${username}@test.com`
    
    await page.fill('input[placeholder="Juan"]', 'Test')
    await page.fill('input[placeholder="Dela Cruz"]', 'User')
    await page.fill('input[placeholder="juandelacruz"]', username)
    await page.fill('input[placeholder="juan@email.com"]', email)
    await page.fill('input[placeholder="09171234567"]', '09171234567')
    await page.fill('textarea[placeholder*="Mandaue"]', '123 Test St, Mandaue City')
    await page.fill('input[placeholder="••••••••"]', 'SecurePass123!')
    await page.fill('input[placeholder="••••••••"]', 'SecurePass123!') // confirm
    
    await page.click('button:has-text("Create Account")')
    
    // Should redirect to catalog
    await expect(page).toHaveURL(/\/catalog/)
    
    // Should show user logged in
    await expect(page.locator('.who')).toContainText(username)
  })

  test('should show validation errors', async ({ page }) => {
    await page.click('button:has-text("Create Account")')
    await expect(page.locator('.field-error')).toBeVisible()
  })

  test('should navigate to login from register page', async ({ page }) => {
    await page.click('a:has-text("Login")')
    await expect(page).toHaveURL(/\/login/)
  })
})

test.describe('Market Admin Vendor Creation', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin (assumes admin user exists)
    await page.goto('/login')
    await page.fill('input[type="text"]', 'marketadmin')
    await page.fill('input[type="password"]', 'adminpass123')
    await page.click('button:has-text("Login")')
    await expect(page).toHaveURL(/\/cart/)
    
    // Navigate to admin vendors
    await page.goto('/admin/vendors')
  })

  test('should display vendor list', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Manage Vendors')
  })

  test('should create new vendor', async ({ page }) => {
    await page.click('button:has-text("Add Vendor")')
    
    const username = `vendor_${Date.now()}`
    await page.fill('input[placeholder*="vendor"]', username)
    await page.fill('input[type="email"]', `${username}@stall.com`)
    await page.fill('input[placeholder="First Name"]', 'Test')
    await page.fill('input[placeholder="Last Name"]', 'Vendor')
    await page.fill('input[type="password"]', 'VendorPass123!')
    await page.fill('input[placeholder="Rosa\'s"]', `${username}'s Stall`)
    await page.fill('input[placeholder="Stall A-12"]', 'Stall B-5')
    await page.fill('input[placeholder="Vegetables Section"]', 'Fish Section')
    await page.fill('input[placeholder="09171112233"]', '09182223344')
    await page.fill('input[placeholder="rosa@stall.com"]', `${username}@contact.com`)
    
    await page.click('button:has-text("Create Vendor")')
    
    // Should close modal and show new vendor in list
    await expect(page.locator('text=Stall B-5')).toBeVisible()
  })
})
```

#### ✅ Verification Steps for 6.1
```bash
# 1. Verify test file exists
cd frontend
ls -la e2e/registration-admin.spec.js

# 2. Check test syntax
npx playwright test --list 2>&1 | grep -E "registration-admin|Customer Registration|Market Admin"

# 3. Run specific test file
npx playwright test e2e/registration-admin.spec.js --project=chromium

# 4. Run with headed mode for debugging
npx playwright test e2e/registration-admin.spec.js --project=chromium --headed

# 5. Run specific test
npx playwright test e2e/registration-admin.spec.js -g "should register new customer" --project=chromium
```

### 6.2 Run Full Test Suite
```bash
# Backend
cd backend
source .venv/bin/activate
python manage.py test accounts vendors -v 2

# Frontend Unit
cd frontend
npm test -- --run

# Frontend E2E
npx playwright test --project=chromium
npx playwright test --project=mobile
```

#### ✅ Verification Steps for 6.2
```bash
# 1. Backend full test suite
cd backend
source .venv/bin/activate
python manage.py test accounts vendors -v 2
# Expected: All tests pass

# 2. Run all backend tests (regression check)
python manage.py test -v 2 2>&1 | tail -20
# Expected: No failures

# 3. Frontend unit tests
cd frontend
npm test -- --run
# Expected: All tests pass

# 4. Frontend E2E - Chromium
npx playwright test --project=chromium
# Expected: All tests pass

# 5. Frontend E2E - Mobile
npx playwright test --project=mobile
# Expected: All tests pass

# 6. Generate test reports
npx playwright test --project=chromium --reporter=html
# Open playwright-report/index.html
```

### 6.3 Manual Verification Checklist

#### Customer Registration
- [ ] Navigate to `/register` → page loads correctly
- [ ] Fill valid form → creates account, logs in, redirects to `/catalog`
- [ ] Duplicate username → shows error inline
- [ ] Duplicate email → shows error inline
- [ ] Password mismatch → shows error inline
- [ ] Short password → shows strength meter + error
- [ ] Invalid phone format → shows error
- [ ] Missing required fields → shows errors
- [ ] Navbar shows "Register" link when logged out
- [ ] After registration, navbar shows username + role "customer"

##### Detailed Registration Test Steps:
```
1. Open http://localhost:5173/register
2. Verify: Page title "Create Account", form with all fields
3. Test empty submit:
   - Click "Create Account" without filling
   - Verify: Red error messages on all required fields
4. Test valid registration:
   - Fill: First Name="Juan", Last Name="Dela Cruz"
   - Username="juandelacruz2024", Email="juan2024@test.com"
   - Phone="09171234567", Address="123 Test St"
   - Password="SecurePass123!", Confirm="SecurePass123!"
   - Click "Create Account"
   - Verify: Redirects to /catalog, navbar shows "Juan Dela Cruz" + "customer"
5. Test duplicate:
   - Logout, go to /register
   - Use same username/email
   - Verify: Inline error "Username already exists" / "Email already registered"
6. Test password strength meter:
   - Type "weak" → meter shows red "Weak"
   - Type "MediumPass1" → meter shows yellow "Fair"  
   - Type "StrongPass123!" → meter shows green "Strong"
7. Test phone validation:
   - Enter "123" → error "Enter valid PH mobile"
   - Enter "09171234567" → no error
```

#### Market Admin Vendor Creation
- [ ] Create admin user in DB: `is_staff=1`
- [ ] Login as admin → navbar shows "Admin Dashboard" and "Manage Vendors"
- [ ] Navigate to `/admin/vendors` → list loads
- [ ] Click "Add Vendor" → modal opens
- [ ] Fill all fields → creates vendor, user, profiles
- [ ] Verify vendor appears in list with correct details
- [ ] Verify vendor can login at `/login` with created credentials
- [ ] Verify vendor sees vendor navbar (Dashboard, Products, Orders, POS)
- [ ] Deactivate vendor → sets is_active=0 on vendor and user
- [ ] Deactivated vendor cannot login

##### Detailed Admin Vendor Creation Test Steps:
```
1. Create admin user (if not exists):
   python manage.py shell -c "
   from accounts.models import AuthUser, Userprofile
   from django.utils import timezone
   if not AuthUser.objects.filter(username='marketadmin').exists():
       a = AuthUser.objects.create(username='marketadmin', email='admin@test.com',
           first_name='Market', last_name='Admin', is_active=1, is_staff=1, is_superuser=0, date_joined=timezone.now())
       a.set_password('adminpass123'); a.save()
       Userprofile.objects.create(user=a, is_vendor=0)
   "

2. Login as admin:
   - Go to http://localhost:5173/login
   - Username: marketadmin, Password: adminpass123
   - Verify: Navbar shows "Admin Dashboard" and "Manage Vendors"

3. Navigate to /admin/vendors:
   - Verify: Page loads, shows "Manage Vendors", "Add Vendor" button

4. Create vendor:
   - Click "Add Vendor"
   - Fill ALL fields in modal (Account Credentials + Stall Information)
   - Click "Create Vendor"
   - Verify: Modal closes, new vendor appears in table

5. Verify vendor login:
   - Logout, go to /login
   - Use vendor credentials created
   - Verify: Login succeeds, navbar shows vendor links (Dashboard, Products, Orders, POS)

6. Deactivate vendor:
   - Login as admin, go to /admin/vendors
   - Click "Deactivate" on vendor row
   - Confirm dialog
   - Verify: Status badge changes to "Inactive", button shows "Deactivated"

7. Verify deactivated vendor cannot login:
   - Logout, try vendor credentials
   - Verify: Login fails with "Invalid credentials"
```

#### Permissions
- [ ] Customer cannot access `/admin/vendors` → redirects to `/cart`
- [ ] Vendor cannot access `/admin/vendors` → redirects to `/cart`
- [ ] Unauthenticated cannot access admin endpoints → 401
- [ ] API returns 403 for non-admin users on admin endpoints

##### Detailed Permission Test Steps:
```
1. Test customer access:
   - Login as regular customer
   - Navigate to /admin/vendors
   - Verify: Redirects to /cart (or /catalog)

2. Test vendor access:
   - Login as vendor
   - Navigate to /admin/vendors
   - Verify: Redirects to /cart

3. Test unauthenticated API:
   - curl -X GET http://localhost:8000/api/vendors/admin/
   - Verify: 401 Unauthorized

4. Test non-admin API access:
   - Get customer token (login as customer)
   - curl -X GET http://localhost:8000/api/vendors/admin/ -H "Authorization: Bearer <customer_token>"
   - Verify: 403 Forbidden

5. Test admin API access:
   - Get admin token (login as marketadmin)
   - curl -X GET http://localhost:8000/api/vendors/admin/ -H "Authorization: Bearer <admin_token>"
   - Verify: 200 OK with vendor list
```

---

## Verification Checklist

### Code Quality
- [ ] All new backend code follows existing patterns (serializers, views, permissions)
- [ ] All new frontend components use design system classes (.card, .btn, .field, .badge, .stat, .meter)
- [ ] No inline styles except for dynamic values
- [ ] All forms have client-side validation + server-side validation
- [ ] Error handling with user-friendly messages
- [ ] Loading states on all async actions
- [ ] Responsive design (mobile ≤768px)

#### Code Quality Verification Commands:
```bash
# Backend: Check for common issues
cd backend
source .venv/bin/activate
python -m flake8 accounts/ vendors/ --ignore=E501,W503 2>&1 | head -20

# Frontend: Lint check
cd frontend
npm run lint 2>&1 | head -30

# Design system class usage verification
cd frontend
grep -r "\.card\|\.btn\|\.field\|\.input\|\.badge\|\.stat\|\.meter\|\.grid\|\.stack" src/views/RegisterView.vue src/views/AdminDashboardView.vue src/views/AdminVendorsView.vue | wc -l
# Should show significant usage
```

### Security
- [ ] Passwords never logged or exposed
- [ ] JWT tokens only returned on successful auth
- [ ] Admin endpoints protected by `IsMarketAdmin` permission
- [ ] Input validation on all fields (length, format, uniqueness)
- [ ] SQL injection prevented via ORM
- [ ] XSS prevented via Vue's auto-escaping

#### Security Verification Commands:
```bash
# 1. Verify no console.log with sensitive data
cd frontend
grep -r "console.log.*password\|console.log.*token" src/ --include="*.vue" --include="*.js"
# Should return nothing

# 2. Verify JWT only returned on success
cd backend
grep -r "access_token\|refresh_token" accounts/views.py vendors/views.py
# Should only be in RegisterView and login flow

# 3. Verify permission classes on admin endpoints
grep -A 3 "class AdminVendor" vendors/views.py | grep "permission_classes"
# Should show [IsAuthenticated, IsMarketAdmin]

# 4. Test XSS prevention (Vue auto-escapes)
# Try injecting <script>alert(1)</script> in form fields - should render as text
```

### Database Integrity
- [ ] All creates wrapped in `transaction.atomic()`
- [ ] User + Customerprofile + Userprofile created together (registration)
- [ ] User + Userprofile + Vendor + PosVendor created together (admin vendor creation)
- [ ] Deactivate sets `is_active=0` on both vendor and user
- [ ] No orphaned records possible

#### Database Integrity Verification Commands:
```bash
# 1. Verify transaction.atomic usage
cd backend
grep -n "transaction.atomic" accounts/serializers.py vendors/serializers.py vendors/views.py

# 2. Test registration creates all profiles
python manage.py shell -c "
from accounts.models import AuthUser, Customerprofile, Userprofile
u = AuthUser.objects.filter(username__startswith='testuser').last()
if u:
    print(f'User: {u.username}')
    print(f'Customerprofile: {Customerprofile.objects.filter(user=u).exists()}')
    print(f'Userprofile (customer): {Userprofile.objects.filter(user=u, is_vendor=0).exists()}')
"

# 3. Test admin vendor creation creates all models
python manage.py shell -c "
from accounts.models import AuthUser, Userprofile
from catalog.models import Vendor
from vendors.models import PosVendor
v = Vendor.objects.last()
if v:
    print(f'Vendor: {v.name}')
    print(f'User: {v.user.username}')
    print(f'Userprofile (vendor): {Userprofile.objects.filter(user=v.user, is_vendor=1).exists()}')
    print(f'PosVendor: {PosVendor.objects.filter(catalog_vendor=v).exists()}')
"

# 4. Test deactivate sets both inactive
python manage.py shell -c "
from catalog.models import Vendor
v = Vendor.objects.filter(is_active=0).last()
if v:
    print(f'Vendor inactive: {v.is_active}')
    print(f'User inactive: {v.user.is_active}')
"
```

### Performance
- [ ] Admin vendor list uses `select_related('user')`
- [ ] No N+1 queries in serializers
- [ ] Frontend modal lazy-loaded (already via route)

#### Performance Verification Commands:
```bash
# 1. Verify select_related usage
cd backend
grep "select_related" vendors/views.py

# 2. Check for N+1 in serializers (should not have nested queries in loops)
grep -n "SerializerMethodField" vendors/serializers.py
# get_user and get_pos_vendor are okay - single queries per object

# 3. Django Debug Toolbar (if installed) - check query count on /admin/vendors/
# Should be ~2 queries: 1 for vendors + 1 for related users

# 4. Frontend bundle size check
cd frontend
npm run build 2>&1 | grep -E "dist/|size"
```

---

## Rollback Plan

### If Issues Arise During Development

1. **Backend Migration Issues** (models are managed=False):
   ```bash
   # Restore from backup
   mysql -u root -p ecompra < backup_pre_registration.sql
   ```

2. **Git Rollback**:
   ```bash
   git stash  # Save current changes
   git checkout develop
   git branch -D feature/registration-admin
   ```

3. **Partial Rollback** (keep some commits):
   ```bash
   git log --oneline -10
   git reset --hard <commit-hash-before-issue>
   ```

### If Issues in Production (Post-Merge)

1. **Disable Feature via Feature Flag** (add to settings):
   ```python
   # settings.py
   FEATURE_REGISTRATION_ENABLED = False
   FEATURE_ADMIN_VENDORS_ENABLED = False
   ```

2. **Hotfix Branch**:
   ```bash
   git checkout master
   git checkout -b hotfix/registration-issue
   # Revert specific commits or fix
   git push origin hotfix/registration-issue
   # Create PR to master
   ```

---

## Deployment Notes

### Environment Variables
No new environment variables required. Uses existing:
- `JWT_SECRET_KEY` (for token signing)
- Database credentials

### Database Requirements
- Tables must exist (managed=False): `auth_user`, `accounts_customerprofile`, `accounts_userprofile`, `catalog_vendor`, `vendors_vendor`
- Ensure `auth_user.is_staff` column exists (it does)
- Ensure `accounts_userprofile.is_vendor` column exists (it does)

### Initial Admin User Creation
```bash
# Run once after deployment to create first Market Admin
cd backend
source .venv/bin/activate
python manage.py shell -c "
from accounts.models import AuthUser, Userprofile
from django.utils import timezone

admin = AuthUser.objects.create(
    username='marketadmin',
    email='admin@mandauemarket.gov.ph',
    first_name='Market',
    last_name='Administrator',
    is_active=1,
    is_staff=1,
    is_superuser=0,
    date_joined=timezone.now(),
)
admin.set_password('CHANGE_THIS_SECURE_PASSWORD')
admin.save()
Userprofile.objects.create(user=admin, is_vendor=0)
print('Market Admin created:', admin.username)
"
```

---

## Appendix: File Summary

### New Files Created
```
backend/
├── accounts/
│   ├── permissions.py          # IsMarketAdmin permission
│   └── tests.py                # Extended with RegisterAPITest
├── vendors/
│   ├── serializers.py          # VendorCreateSerializer, VendorListSerializer, VendorDetailSerializer
│   ├── views.py                # Extended with AdminVendor* views
│   ├── urls.py                 # Extended with admin endpoints
│   └── tests.py                # AdminVendorAPITest

frontend/
├── src/
│   ├── views/
│   │   ├── RegisterView.vue    # Customer registration page
│   │   ├── AdminDashboardView.vue  # Admin overview
│   │   └── AdminVendorsView.vue    # Vendor management
│   ├── stores/
│   │   └── auth.js             # Added register action
│   ├── router/
│   │   └── index.js            # Added /register, /admin, /admin/vendors routes
│   ├── components/
│   │   └── Navbar.vue          # Added Register link, Admin nav items
│   └── assets/
│       └── main.css            # Added admin stat/modal styles
└── e2e/
    └── registration-admin.spec.js  # Playwright E2E tests
```

### Modified Files
```
backend/
├── accounts/
│   ├── serializers.py          # Added RegisterSerializer, updated get_role
│   ├── views.py                # Added RegisterView
│   └── urls.py                 # Added /auth/register/
├── vendors/
│   ├── serializers.py          # (replaced/extended)
│   ├── views.py                # (replaced/extended)
│   └── urls.py                 # (replaced/extended)

frontend/
├── src/
│   ├── stores/auth.js          # Added register()
│   ├── router/index.js         # Added routes
│   ├── components/Navbar.vue   # Added Register/Admin links
│   └── assets/main.css         # Added admin styles
```

---

## Support & Questions

**Reference Documents**:
- `FRONTEND_DESIGN_SYSTEM.md` - Design system classes
- `CLAUDE.md` - Project conventions
- `PHASE_3_FEATURE_BUILD.md` - Previous phase patterns

**Key Patterns to Follow**:
- Vue 3 Composition API with `<script setup>`
- Pinia stores for state management
- Design system semantic classes (not Tailwind utilities)
- Django REST Framework generic views + custom permissions
- JWT via `djangorestframework-simplejwt`
- `managed=False` models - no migrations, direct table ops

---

---

## Complete Verification Summary

### Phase-by-Phase Verification Checklist

| Phase | Component | Unit Tests | Integration Tests | Manual Verification | Status |
|-------|-----------|------------|-------------------|---------------------|--------|
| **1** | RegisterSerializer | ✅ 1.1 | ✅ 1.5 | ✅ 1.5 curl test | ⬜ |
| **1** | RegisterView | ✅ 1.2 | ✅ 1.5 | ✅ 1.5 curl test | ⬜ |
| **1** | URLs | ✅ 1.3 | ✅ 1.5 | ✅ 1.5 reverse() | ⬜ |
| **1** | RegisterAPITest | ✅ 1.4 | ✅ 1.5 | ✅ 1.5 test run | ⬜ |
| **2** | RegisterView.vue | ✅ 2.1 | ✅ 2.5 | ✅ 2.5 browser | ⬜ |
| **2** | Auth Store register() | ✅ 2.2 | ✅ 2.5 | ✅ 2.5 flow | ⬜ |
| **2** | Router | ✅ 2.3 | ✅ 2.5 | ✅ 2.5 navigation | ⬜ |
| **2** | Navbar | ✅ 2.4 | ✅ 2.5 | ✅ 2.5 visual | ⬜ |
| **3** | CurrentUserSerializer | ✅ 3.1 | ✅ 3.4 | ✅ 3.4 shell | ⬜ |
| **3** | IsMarketAdmin | ✅ 3.2 | ✅ 3.4 | ✅ 3.4 shell | ⬜ |
| **3** | Navbar Admin Links | ✅ 3.3 | ✅ 3.4 | ✅ 3.4 visual | ⬜ |
| **4** | VendorCreateSerializer | ✅ 4.1 | ✅ 4.5 | ✅ 4.5 shell | ⬜ |
| **4** | Admin Vendor Views | ✅ 4.2 | ✅ 4.5 | ✅ 4.5 curl | ⬜ |
| **4** | Admin Vendor URLs | ✅ 4.3 | ✅ 4.5 | ✅ 4.5 reverse() | ⬜ |
| **4** | AdminVendorAPITest | ✅ 4.4 | ✅ 4.5 | ✅ 4.5 test run | ⬜ |
| **5** | AdminDashboardView | ✅ 5.1 | ✅ 6.2 | ✅ 6.3 browser | ⬜ |
| **5** | AdminVendorsView | ✅ 5.2 | ✅ 6.2 | ✅ 6.3 browser | ⬜ |
| **5** | Admin Routes | ✅ 5.3 | ✅ 6.2 | ✅ 6.3 navigation | ⬜ |
| **5** | Admin CSS | ✅ 5.4 | ✅ 6.2 | ✅ 6.3 visual | ⬜ |
| **6** | E2E Tests | ✅ 6.1 | ✅ 6.2 | ✅ 6.2 playwright | ⬜ |

### Final Pre-Merge Checklist
```bash
# Run all these before creating PR:

# 1. Backend - Full test suite
cd backend && source .venv/bin/activate && python manage.py test -v 2

# 2. Frontend - Unit tests + Lint
cd frontend && npm test -- --run && npm run lint

# 3. Frontend - E2E tests
cd frontend && npx playwright test --project=chromium && npx playwright test --project=mobile

# 4. Build verification
cd frontend && npm run build

# 5. Database integrity check
cd backend && python manage.py shell -c "
from accounts.models import AuthUser, Customerprofile, Userprofile
from catalog.models import Vendor
from vendors.models import PosVendor

# Count all records
print(f'Users: {AuthUser.objects.count()}')
print(f'Customerprofiles: {Customerprofile.objects.count()}')
print(f'Userprofiles: {Userprofile.objects.count()}')
print(f'Vendors: {Vendor.objects.count()}')
print(f'PosVendors: {PosVendor.objects.count()}')
"

# 6. Git status clean
git status
# Should show only intended changes
```

### Quick Reference: Key Commands by Phase

| Phase | Key Verification Command |
|-------|-------------------------|
| 1 | `python manage.py test accounts.tests.RegisterAPITest -v 2` |
| 2 | `npm test -- --run` + manual `/register` flow |
| 3 | `python manage.py shell -c "from accounts.serializers import CurrentUserSerializer; ..."` |
| 4 | `python manage.py test vendors.tests.AdminVendorAPITest -v 2` |
| 5 | `npm run dev` + manual `/admin/vendors` flow as admin |
| 6 | `npx playwright test e2e/registration-admin.spec.js --project=chromium` |

---

*Generated for E-Compra Capstone Project (CCS630)*
*Implementation Guide Version 1.1 (with detailed verification steps)*
*Date: 2026-11-24*