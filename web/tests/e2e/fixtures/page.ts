import { test as base, Page } from '@playwright/test';

export type TestFixtures = {
  authenticatedPage: Page;
};

export const test = base.extend<TestFixtures>({
  authenticatedPage: async ({ page }, use) => {
    // Navigate to app
    await page.goto('/');
    
    // Check if already logged in
    const loginButton = page.locator('[data-testid="login-button"]');
    if (await loginButton.isVisible()) {
      // Perform login
      await loginButton.click();
      
      // Fill credentials (using demo account)
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'password123');
      await page.click('[data-testid="submit-button"]');
      
      // Wait for navigation to dashboard
      await page.waitForURL(/\/dashboard/);
    }
    
    await use(page);
    
    // Cleanup: logout
    const profileMenu = page.locator('[data-testid="profile-menu"]');
    if (await profileMenu.isVisible()) {
      await profileMenu.click();
      await page.click('[data-testid="logout-button"]');
    }
  },
});

export { expect } from '@playwright/test';
