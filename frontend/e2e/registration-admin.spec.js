import { test, expect } from '@playwright/test'

test.describe('Customer Registration Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/register')
  })

  test('should register new customer successfully', async ({ page }) => {
    const username = `testuser_${Date.now()}`
    const email = `${username}@test.com`

    await page.fill('input[placeholder="Juan"]', 'Test')
    await page.fill('input[placeholder="Dela Cruz"]', 'User')
    await page.fill('input[placeholder="username"]', username)
    await page.fill('input[placeholder="juan@example.com"]', email)
    await page.fill('input[placeholder="09171234567"]', '09171234567')
    await page.fill('input[placeholder="123 Mandaue City, Cebu"]', '123 Test St, Mandaue City')
    await page.locator('input[placeholder="••••••••"]').first().fill('SecurePass123!')
    await page.locator('input[placeholder="••••••••"]').last().fill('SecurePass123!')

    await page.click('button:has-text("Register")')

    // Should redirect to cart (per RegisterView implementation)
    await expect(page).toHaveURL(/\/cart/)

    // Should show user logged in
    await expect(page.locator('.who')).toContainText(username)
  })

  test('should show validation errors', async ({ page }) => {
    await page.click('button:has-text("Register")')
    // Check for required field validation - browser native validation
    const invalidInputs = page.locator('input:invalid')
    await expect(invalidInputs).not.toHaveCount(0)
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
    await page.click('button:has-text("+ Create Vendor")')

    const username = `vendor_${Date.now()}`
    // Use modal-specific selectors (scope to modal-overlay)
    const modal = page.locator('.modal-overlay')

    await modal.locator('input[placeholder="username"]').fill(username)
    await modal.locator('input[placeholder="vendor@example.com"]').fill(`${username}@stall.com`)
    await modal.locator('input[placeholder="First Name"]').fill('Test')
    await modal.locator('input[placeholder="Last Name"]').fill('Vendor')
    await modal.locator('input[placeholder="••••••••"]').fill('VendorPass123!')
    await modal.locator('input[placeholder="Rosa\'s Fresh Vegetables"]').fill(`${username}'s Stall`)
    await modal.locator('input[placeholder="Stall A-12"]').fill('Stall B-5')
    await modal.locator('input[placeholder="Vegetables Section"]').fill('Fish Section')
    await modal.locator('input[placeholder="09171112233"]').fill('09182223344')
    await modal.locator('input[placeholder="rosa@stall.com"]').fill(`${username}@contact.com`)

    await modal.locator('button:has-text("Create Vendor")').click()

    // Wait for modal to close and vendor list to refresh
    await expect(modal).toBeHidden({ timeout: 10000 })
    await expect(page.locator('text=Stall B-5').first()).toBeVisible({ timeout: 10000 })
  })
})