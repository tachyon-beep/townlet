import { test, expect } from "@playwright/test";

test.describe("Spectator dashboard", () => {
  test("renders snapshot data from telemetry stream", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("domcontentloaded");
    await page.waitForTimeout(200);
    await expect(page.getByRole("heading", { name: "Perturbations" })).toBeVisible();
    await expect(page.locator("text=Bob yielded the shower queue")).toBeVisible();
    await expect(page.getByText(/queue_conflict_intensity/i)).toBeVisible();
  });

  test("skip link focuses main content", async ({ page }) => {
    await page.goto("/");
    await page.keyboard.press("Tab");
    await expect(page.locator(".skip-link")).toBeVisible();
    await page.keyboard.press("Enter");
    await expect(page.locator("main")).toBeFocused();
  });
});
