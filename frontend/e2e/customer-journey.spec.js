import { test, expect } from '@playwright/test'

test.describe('Customer Journey', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'Admin2627')
    await page.click('button:has-text("Login")')
    // After login, redirects to /cart
    await expect(page).toHaveURL('/cart')
    // Verify tokens are stored
    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'))
    const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'))
    expect(accessToken).toBeTruthy()
    expect(refreshToken).toBeTruthy()
  })

  test('browse catalog, add to cart, checkout', async ({ page }) => {
    // Listen to all console messages for debugging
    page.on('console', msg => console.log('BROWSER CONSOLE:', msg.type(), msg.text()))

    // Go to catalog first
    await page.goto('/catalog')
    await expect(page).toHaveURL('/catalog')

    // Search for a product that's in stock (Bangus/Milkfish)
    await page.fill('input[placeholder="Search products..."]', 'Bangus')
    await page.press('input[placeholder="Search products..."]', 'Enter')
    // Wait for search results
    await expect(page.locator('text=Bangus').first()).toBeVisible()

    // Add first product to cart (first "Add" button) - handle native alert
    let dialogHandled = false
    page.on('dialog', async dialog => {
      console.log('Dialog appeared:', dialog.message())
      await dialog.accept()
      dialogHandled = true
    })
    await page.click('button:has-text("Add") >> nth=0')
    // Wait for the alert to be handled (confirms API call completed)
    await expect.poll(() => dialogHandled, { timeout: 10000 }).toBe(true)

    // Go to cart
    await page.goto('/cart')
    // Wait for cart to load - wait for either items table or empty state
    await expect(page.locator('table').or(page.locator('text=Your cart is empty'))).toBeVisible({ timeout: 10000 })
    // Then verify the cart has the product (Bangus)
    await expect(page.locator('text=Bangus').first()).toBeVisible({ timeout: 10000 })

    // Check what's on the page
    const pageContent = await page.content()
    console.log('Cart page content:', pageContent.substring(0, 2000))

    // Check that cart loads without error
    await expect(page.locator('text=Failed to load cart')).not.toBeVisible({ timeout: 10000 })

    // Proceed to checkout
    await page.click('button:has-text("Checkout")')
    await expect(page).toHaveURL('/checkout')

    // Wait for checkout page to load - wait for loading to disappear
    await expect(page.locator('text=Loading checkout...')).not.toBeVisible({ timeout: 15000 })
    // Verify we have items on checkout page
    await expect(page.locator('text=Bangus').first()).toBeVisible({ timeout: 10000 })

    // Select fulfillment and place order
    await page.click('button:has-text("Place Order")')
    await expect(page).toHaveURL(/\/payment\//)
  })
})