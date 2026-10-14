"""Generate the site favicon from the same brand marks used elsewhere
(ink background, Golden Gate orange accent, little paper-plane glyph —
see the "plane" icon in scripts/theme.py and the og.png tow scene).

Outputs:
  site/favicon.svg        vector icon, used by modern browsers
  site/favicon.ico        16/32/48 px, legacy fallback
  site/favicon-180.png    apple-touch-icon

Usage: python3 scripts/make_favicon.py
Requires only Pillow (for the .ico/.png rasters); the .svg is hand-written.
"""
import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

INK = (14, 26, 36, 255)       # #0E1A24
ACCENT = (194, 56, 11, 255)   # #C2380B
PAPER = (255, 255, 255, 255)  # #FFFFFF

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#0E1A24"/>
<path d="M14 33h14" stroke="#C2380B" stroke-width="3.4" stroke-linecap="round"/>
<path d="M30 33l20-9.5-5 9.5 5 9.5z" fill="#C2380B"/>
</svg>
"""


def draw_icon(size):
    """Ink rounded-square with the orange tow-line + paper-plane mark,
    scaled from a 64x64 design grid so it stays crisp at every size."""
    scale = size / 64
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = max(2, round(14 * scale))
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=INK)

    def pt(x, y):
        return (x * scale, y * scale)

    line_w = max(1, round(3.4 * scale))
    d.line([pt(14, 33), pt(28, 33)], fill=ACCENT, width=line_w)
    d.polygon([pt(30, 33), pt(50, 23.5), pt(45, 33), pt(50, 42.5)], fill=ACCENT)
    return im


def main():
    with open(os.path.join(SITE, "favicon.svg"), "w") as f:
        f.write(SVG)

    sizes = [16, 32, 48]
    imgs = [draw_icon(s) for s in sizes]
    imgs[0].save(
        os.path.join(SITE, "favicon.ico"),
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=imgs[1:],
    )

    draw_icon(180).save(os.path.join(SITE, "favicon-180.png"))

    for name in ("favicon.svg", "favicon.ico", "favicon-180.png"):
        p = os.path.join(SITE, name)
        print(f"wrote {p} ({os.path.getsize(p)} bytes)")


if __name__ == "__main__":
    main()
