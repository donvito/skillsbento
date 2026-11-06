#!/usr/bin/env python3
"""Screenshot real web pages (shopping flows, booking listings) to use as on-screen proof.

  web_capture.py <url> <out.png> [--mobile] [--scroll 300] [--wait 4000] [--click "text=Add to cart"]
--mobile renders at 390x845 @3x, i.e. exactly the phone() mockup's screen ratio (900:1950).
Desktop is 1440x900 @2x. Dismisses common cookie / sign-in / region popups. Lazy galleries need --wait and
a scroll (photos were blank on the first try). Some sites geo-redirect (amazon.com -> amazon.sg): say so on screen
or in the delivery note. These are real third-party pages: label them ("Real Amazon pages") and tell the user.
"""
import argparse, asyncio
from playwright.async_api import async_playwright
ap = argparse.ArgumentParser(); ap.add_argument('url'); ap.add_argument('out'); ap.add_argument('--mobile', action='store_true')
ap.add_argument('--scroll', type=int, default=0); ap.add_argument('--wait', type=int, default=3000); ap.add_argument('--click', action='append', default=[]); a = ap.parse_args()
DISMISS = ['text=Stay on Amazon.sg', 'text=Not now', 'text=Dismiss', '#onetrust-accept-btn-handler', 'button[aria-label="Dismiss sign-in info."]', 'button[aria-label="Dismiss sign in information."]', 'text=Accept all']
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        if a.mobile:
            d = dict(p.devices['iPhone 13']); d['viewport'] = {'width': 390, 'height': 845}; d['screen'] = {'width': 390, 'height': 845}
            ctx = await b.new_context(**d, locale='en-US')
        else:
            ctx = await b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=2, locale='en-US', user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36')
        pg = await ctx.new_page(); await pg.goto(a.url, timeout=60000, wait_until='networkidle')
        async def dismiss():
            for sel in DISMISS:
                try:
                    if await pg.locator(sel).first.is_visible(timeout=500): await pg.locator(sel).first.click(); await pg.wait_for_timeout(600)
                except Exception: pass
        await dismiss()
        for sel in a.click: await pg.locator(sel).first.click(timeout=8000); await pg.wait_for_timeout(2000); await dismiss()
        for _ in range(3): await pg.mouse.wheel(0, 600); await pg.wait_for_timeout(800)
        await pg.evaluate(f"window.scrollTo(0, {a.scroll})"); await pg.wait_for_timeout(a.wait)
        await pg.screenshot(path=a.out); print(a.out, '|', await pg.title()); await b.close()
asyncio.run(main())
