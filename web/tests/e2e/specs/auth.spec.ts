import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should display login page', async ({ page }) => {
    await page.goto('/');
    
    const heading = page.locator('h1');
    await expect(heading).toContainText(/login|welcome/i);
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.goto('/');
    
    // Fill login form
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="submit-button"]');
    
    // Verify redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('should show error on invalid credentials', async ({ page }) => {
    await page.goto('/');
    
    await page.fill('[data-testid="email-input"]', 'invalid@example.com');
    await page.fill('[data-testid="password-input"]', 'wrongpassword');
    await page.click('[data-testid="submit-button"]');
    
    const errorMessage = page.locator('[data-testid="error-message"]');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText(/invalid|incorrect|error/i);
  });

  test('should logout successfully', async ({ page }) => {
    await page.goto('/');
    
    // Login first
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="submit-button"]');
    await page.waitForURL(/\/dashboard/);
    
    // Logout
    await page.click('[data-testid="profile-menu"]');
    await page.click('[data-testid="logout-button"]');
    
    // Verify redirect to login
    await expect(page).toHaveURL('/');
  });
});

test.describe('Dashboard', () => {
  test('should display dashboard content for authenticated user', async ({ page }) => {
    await page.goto('/');
    
    // Login
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="submit-button"]');
    
    // Wait for dashboard to load
    await page.waitForURL(/\/dashboard/);
    
    // Verify dashboard elements are visible
    const dashboard = page.locator('[data-testid="dashboard-container"]');
    await expect(dashboard).toBeVisible();
  });
});

test.describe('Responsive Design', () => {
  test('should be mobile responsive', async ({ browser }) => {
    const context = await browser.newContext({
      viewport: { width: 375, height: 667 },
    });
    const page = await context.newPage();
    
    await page.goto('/');
    
    const heading = page.locator('h1');
    await expect(heading).toBeVisible();
    
    await context.close();
  });

  test('should be tablet responsive', async ({ browser }) => {
    const context = await browser.newContext({
      viewport: { width: 768, height: 1024 },
    });
    const page = await context.newPage();
    
    await page.goto('/');
    
    const heading = page.locator('h1');
    await expect(heading).toBeVisible();
    
    await context.close();
  });
});
