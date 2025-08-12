# labels.py
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw
from lxml import etree

from utils import (
    PRINTER_WIDTH,
    load_font,
    add_bottom_margin,
    to_1bpp,
    sanitize_svg,
    flatten_png_bytes_to_gray,
    _embed_qr_png
)

# ---------- simple stacked text ----------
def simple_label_to_png(
    lines: list[str],
    out_png_path: str,
    width_px: int = PRINTER_WIDTH,
    padding: int = 8,
    line_spacing: int = 6,
    font_path: str | None = None,
    font_size: int = 24,
    bottom_margin_px: int = 80,
    threshold: int | None = 180,
) -> str:
    font = load_font(font_path, font_size)

    # measure height
    probe = ImageDraw.Draw(Image.new("L", (width_px, 10), 255))
    total_h = padding
    for t in lines:
        bbox = probe.textbbox((0, 0), t, font=font)
        total_h += (bbox[3] - bbox[1]) + line_spacing
    total_h += padding

    # draw
    gray = Image.new("L", (width_px, total_h), 255)
    draw = ImageDraw.Draw(gray)
    y = padding
    for t in lines:
        bbox = draw.textbbox((0, 0), t, font=font)
        h = bbox[3] - bbox[1]
        draw.text((padding, y), t, font=font, fill=0)
        y += h + line_spacing

    # finish
    out = add_bottom_margin(gray, bottom_margin_px)
    to_1bpp(out, threshold).save(out_png_path)
    return out_png_path

# ---------- svg template via CairoSVG ----------
def svg_to_png_label_cairo(
    svg_path: str,
    values: dict,
    out_png_path: str,
    width_px: int = PRINTER_WIDTH,
    bottom_margin_px: int = 80,
    threshold: int | None = 180,
) -> str:
    # lazy import so simple labels work even if cairosvg is not installed
    import cairosvg

    # fill text by id
    root = etree.fromstring(Path(svg_path).read_bytes())
    for k, v in values.items():
        nodes = root.xpath(f"//*[@id='{k}']")
        if nodes:
            node = nodes[0]
            for c in list(node):
                node.remove(c)
            node.text = str(v)

    _embed_qr_png(root, "qr", values["qr"] if "qr" in values and values["qr"] != "" else f"{values['food']}, {values['weight']}")

    svg_bytes = sanitize_svg(etree.tostring(root))

    # render svg to png bytes with white background
    png_bytes = cairosvg.svg2png(
        bytestring=svg_bytes,
        output_width=width_px,
        background_color="white",
    )

    # flatten + margin + 1-bit
    gray = flatten_png_bytes_to_gray(png_bytes)
    out = add_bottom_margin(gray, bottom_margin_px)
    to_1bpp(out, threshold).save(out_png_path)
    return out_png_path
