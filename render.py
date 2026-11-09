"""Render the mockup pages to PNG with headless Chrome (Playwright)."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.resolve()
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)


def url(name):
    return (ROOT / name).as_uri()


def main(which):
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--font-render-hinting=none"])

        def page(width, height, dpr):
            ctx = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=dpr)
            return ctx.new_page()

        if which in ("all", "desktop"):
            pg = page(1440, 900, 1)
            pg.goto(url("index.html"))
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(OUT / "02_homepage_desktop_1440_full.png"), full_page=True)
            pg.close()

        if which in ("all", "cover"):
            pg = page(1440, 900, 2)
            pg.goto(url("index.html"))
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(OUT / "01_hero_desktop_1440x900@2x.png"), full_page=False)
            pg.close()

        if which in ("all", "mobile"):
            pg = page(390, 844, 2)
            pg.goto(url("index.html"))
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(300)
            bottom = pg.evaluate("Math.ceil(document.querySelector('#wege').getBoundingClientRect().bottom + window.scrollY)")
            pg.screenshot(path=str(OUT / "03_mobile_390_hero_branchen_wege@2x.png"), full_page=True,
                          clip={"x": 0, "y": 0, "width": 390, "height": bottom})
            pg.close()

        if which in ("all", "styletile"):
            pg = page(1440, 900, 1)
            pg.goto(url("styletile.html"))
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(OUT / "04_style_tile.png"), full_page=True)
            pg.close()

        if which in ("all", "waechter"):
            pg = page(1600, 900, 1)
            pg.goto(url("waechter.html"))
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(OUT / "05_waechter_ablauf.png"), full_page=True)
            pg.close()

        browser.close()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
