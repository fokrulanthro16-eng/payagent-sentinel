"""Playwright script to capture 6 high-resolution (1920x1080) screenshots for hackathon submission."""
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "screenshots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

URL = "http://localhost:5173"

def capture_all():
    print(f"[1/7] Initializing Playwright Chromium viewport 1920x1080...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
        )
        page = context.new_page()

        # Clear localStorage to start fresh
        page.goto(URL, wait_until="networkidle")
        page.evaluate("localStorage.clear()")
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(2000)

        # ---------------------------------------------------------
        # 1. Clean Main Cockpit Overview
        # ---------------------------------------------------------
        print("[2/7] Capturing 01_main_cockpit_overview.png...")
        path_01 = OUTPUT_DIR / "01_main_cockpit_overview.png"
        page.screenshot(path=str(path_01), full_page=False)
        print(f" -> Saved: {path_01}")

        # ---------------------------------------------------------
        # 2. Policy Vault Governance Drawer Open
        # ---------------------------------------------------------
        print("[3/7] Capturing 02_policy_vault_governance.png...")
        # Click the Policy Vault button
        vault_button = page.locator("button:has-text('Policy Vault')").first
        vault_button.click()
        page.wait_for_timeout(1000)
        path_02 = OUTPUT_DIR / "02_policy_vault_governance.png"
        page.screenshot(path=str(path_02), full_page=False)
        print(f" -> Saved: {path_02}")

        # Close the drawer
        close_button = page.locator("button:has-text('Cancel')").first
        if close_button.is_visible():
            close_button.click()
        else:
            page.keyboard.press("Escape")
        page.wait_for_timeout(600)

        # ---------------------------------------------------------
        # 3. Tier 1 Autonomous Settled ($14.50)
        # ---------------------------------------------------------
        print("[4/7] Capturing 03_tier1_autonomous_settled.png...")
        tier1_button = page.locator("button:has-text('Tier 1 Autonomous')").first
        tier1_button.click()
        page.wait_for_timeout(4500)  # Wait for full settlement and capture
        path_03 = OUTPUT_DIR / "03_tier1_autonomous_settled.png"
        page.screenshot(path=str(path_03), full_page=False)
        print(f" -> Saved: {path_03}")

        # ---------------------------------------------------------
        # 4. Multi-LLM Reasoning Stream Focused View
        # ---------------------------------------------------------
        print("[5/7] Capturing 04_multi_llm_reasoning_stream.png...")
        # Capture the terminal feed element directly
        reasoning_panel = page.locator("text=Multi-LLM Reasoning & Telemetry Stream").locator("xpath=ancestor::div[contains(@class, 'glass-panel')]").first
        path_04 = OUTPUT_DIR / "04_multi_llm_reasoning_stream.png"
        if reasoning_panel.is_visible():
            reasoning_panel.screenshot(path=str(path_04))
        else:
            page.screenshot(path=str(path_04), full_page=False)
        print(f" -> Saved: {path_04}")

        # ---------------------------------------------------------
        # 5. Rogue Drain Intercepted ($1,850)
        # ---------------------------------------------------------
        print("[6/7] Capturing 05_rogue_drain_intercepted.png...")
        rogue_button = page.locator("button:has-text('Rogue Drain')").first
        rogue_button.click()
        page.wait_for_timeout(2500)  # Wait for arbiter interception
        path_05 = OUTPUT_DIR / "05_rogue_drain_intercepted.png"
        page.screenshot(path=str(path_05), full_page=False)
        print(f" -> Saved: {path_05}")

        # ---------------------------------------------------------
        # 6. SLA Auto-Refund Enforcement
        # ---------------------------------------------------------
        print("[7/7] Capturing 06_sla_auto_refund_enforcement.png...")
        sla_button = page.locator("button:has-text('Simulate SLA Auto-Refund')").first
        sla_button.click()
        page.wait_for_timeout(5000)  # Wait for auto-refund execution & refund badge
        path_06 = OUTPUT_DIR / "06_sla_auto_refund_enforcement.png"
        page.screenshot(path=str(path_06), full_page=False)
        print(f" -> Saved: {path_06}")

        browser.close()
        print("\nAll 6 high-res screenshots captured successfully!")

if __name__ == "__main__":
    capture_all()
