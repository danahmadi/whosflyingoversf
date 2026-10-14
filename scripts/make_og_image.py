"""Render site/og.png — the 1200x630 Open Graph / Twitter card image.

Renders an HTML page with headless Chrome so the image reuses the site's
real font, colours and banner-headline motif (see site/style.css) instead
of drifting out of sync with the design by hand-crafting pixels elsewhere.

Usage: python3 scripts/make_og_image.py
Requires a Chrome/Chromium binary (CHROME_BIN env var, or one of the
common names, is auto-detected) and no other third-party dependencies.
"""
import base64
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
OUT = os.path.join(SITE, "og.png")

W, H = 1200, 630

# Same palette as site/style.css (:root).
SKY = "#E9EDF0"
PAPER = "#FFFFFF"
INK = "#0E1A24"
INK2 = "#3F4C57"
ACCENT = "#C2380B"

# Logos shown in the advertiser row, left to right. A representative subset
# (not all nine) keeps each mark legible at small/thumbnail sizes.
LOGO_ROW = ["monaco.png", "paid.png", "artisan.png", "apify.png", "vendo.png", "pocketfm.png", "openai.png"]


def b64(path, mime):
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode("ascii")


def find_chrome():
    env = os.environ.get("CHROME_BIN")
    if env and shutil.which(env):
        return env
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(name)
        if p:
            return p
    raise SystemExit("No Chrome/Chromium binary found. Set CHROME_BIN or install one.")


def build_html():
    font_uri = b64(os.path.join(SITE, "fonts", "schibsted-grotesk.woff2"), "font/woff2")
    logos_html = "".join(
        f'<div class="logo"><img src="{b64(os.path.join(SITE, "logos", name), "image/png")}" alt=""></div>'
        for name in LOGO_ROW
    )

    # The plane-icon path matches the one used sitewide for "ADS-B flight"
    # mentions in scripts/theme.py, so the OG card and the live pages share
    # the same little-plane glyph.
    plane_svg = (
        '<svg class="plane" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M2 16l20-6-20-6 3 6-3 6z"/><path d="M5 10h17"/></svg>'
    )

    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<style>
@font-face{{
  font-family:"Schibsted Grotesk";
  src:url({font_uri}) format("woff2");
  font-weight:400 800;
}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{
  background:{SKY};
  font-family:"Schibsted Grotesk",system-ui,sans-serif;
  color:{INK};
  -webkit-font-smoothing:antialiased;
}}
.wrap{{
  width:{W}px;height:{H}px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:30px;
}}
.tow{{display:flex;align-items:center;gap:16px}}
.plane{{width:70px;height:70px;color:{ACCENT};flex:none}}
.line{{width:52px;height:4px;background:{ACCENT};border-radius:2px;flex:none}}
.banner{{
  background:{INK};color:{PAPER};
  text-transform:uppercase;font-weight:800;letter-spacing:.01em;
  border-radius:6px;
  padding:26px 40px 20px;
  text-align:center;
}}
.banner .l1,.banner .l2{{display:block;line-height:1.04;font-size:84px;white-space:nowrap}}
.banner .l2{{margin-top:2px}}
.sub{{
  font-size:32px;font-weight:500;color:{INK};
  text-align:center;max-width:920px;line-height:1.35;
}}
.rule{{width:84px;height:4px;background:{ACCENT};border-radius:2px}}
.logos{{display:flex;gap:14px;margin-top:2px}}
.logo{{
  width:58px;height:58px;border-radius:12px;background:{PAPER};
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 0 0 1px rgba(14,26,36,.08);
}}
.logo img{{width:40px;height:40px;object-fit:contain}}
</style></head>
<body>
<div class="wrap">
  <div class="tow">
    <div class="banner"><span class="l1">Who's flying</span><span class="l2">over SF?</span></div>
    <div class="line"></div>
    {plane_svg}
  </div>
  <div class="sub">A calendar of every banner plane over San Francisco</div>
  <div class="rule"></div>
  <div class="logos">{logos_html}</div>
</div>
</body></html>"""


def main():
    chrome = find_chrome()
    html = build_html()
    with tempfile.TemporaryDirectory() as tmp:
        html_path = os.path.join(tmp, "og.html")
        with open(html_path, "w") as f:
            f.write(html)
        profile = os.path.join(tmp, "chrome-profile")
        os.makedirs(profile, exist_ok=True)
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            "--disable-extensions",
            "--disable-dev-shm-usage",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-default-apps",
            "--no-first-run",
            "--mute-audio",
            "--force-color-profile=srgb",
            "--virtual-time-budget=2000",
            "--run-all-compositor-stages-before-draw",
            f"--user-data-dir={profile}",
            f"--screenshot={OUT}",
            f"--window-size={W},{H}",
            "file://" + html_path,
        ]
        try:
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=25,
            )
        except subprocess.TimeoutExpired:
            # Chrome can leave a zygote/renderer process holding stdio open
            # even after the screenshot file is fully written; treat a
            # present, non-empty output file as success.
            if not (os.path.exists(OUT) and os.path.getsize(OUT) > 0):
                raise

    size = os.path.getsize(OUT)
    print(f"wrote {OUT} ({size/1024:.1f} KB)")
    if size > 300_000:
        print("warning: og.png exceeds ~300KB target", file=sys.stderr)


if __name__ == "__main__":
    main()
