from pathlib import Path
from io import BytesIO
from PIL import Image, ImageFont
from lxml import etree
import base64
from io import BytesIO
from PIL import Image
import qrcode

PRINTER_WIDTH = 384  # set to your printer head width

# ████████████████████ FONTS ████████████████████
def load_font(path: str | None = None, size: int = 24) -> ImageFont.FreeTypeFont:
    if path and Path(path).exists():
        return ImageFont.truetype(path, size=size)
    for fp in (
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
    ):
        p = Path(fp)
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()

# ████████████████████ IMAGE HELPERS ████████████████████
def add_bottom_margin(gray_img: Image.Image, margin_px: int = 80) -> Image.Image:
    w, h = gray_img.size
    out = Image.new("L", (w, h + margin_px), 255)
    out.paste(gray_img, (0, 0))
    return out

def to_1bpp(img: Image.Image, threshold: int | None = 180) -> Image.Image:
    if threshold is None:
        return img.convert("1")  # Floyd–Steinberg dithering
    return img.point(lambda p: 0 if p < threshold else 255).convert("1")

def flatten_png_bytes_to_gray(png_bytes: bytes) -> Image.Image:
    rgba = Image.open(BytesIO(png_bytes)).convert("RGBA")
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    return Image.alpha_composite(white, rgba).convert("L")

# ████████████████████ SVG HELPERS ████████████████████
def sanitize_svg(svg_bytes: bytes) -> bytes:
    invalid = {"null", "none", "nan", ""}
    root = etree.fromstring(svg_bytes)
    for el in root.iter():
        for attr in ("stroke-opacity", "fill-opacity", "opacity"):
            v = el.get(attr)
            if v is not None and v.strip().lower() in invalid:
                if attr == "opacity":
                    el.attrib[attr] = "1"
                else:
                    del el.attrib[attr]
        style = el.get("style")
        if style:
            parts, changed = [], False
            for chunk in style.split(";"):
                if ":" not in chunk:
                    continue
                k, v = (s.strip() for s in chunk.split(":", 1))
                if k in ("stroke-opacity", "fill-opacity", "opacity") and v.lower() in invalid:
                    changed = True
                    continue
                parts.append(f"{k}:{v}")
            if changed:
                if parts:
                    el.set("style", ";".join(parts))
                else:
                    del el.attrib["style"]
    return etree.tostring(root)


# ████████████████████ QR CODE HELPERS ████████████████████
def _make_qr_png_bytes(data: str, size_px: int, border: int = 1) -> bytes:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,  # generate large, we’ll downscale with NEAREST
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("L")
    img = img.resize((size_px, size_px), Image.NEAREST)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def _embed_qr_png(root, element_id: str, data: str):
    # Find the placeholder element by id
    nodes = root.xpath(f"//*[@id='{element_id}']")
    if not nodes:
        return
    node = nodes[0]
    # Get placement + size from the placeholder
    w = int(float(node.get("width", "96")))
    h = int(float(node.get("height", str(w))))
    size = min(w, h)

    png = _make_qr_png_bytes(data, size_px=size)
    data_uri = "data:image/png;base64," + base64.b64encode(png).decode("ascii")

    # If it's already an <image>, set href; else replace with <image>
    SVG_NS = "http://www.w3.org/2000/svg"
    XLINK_NS = "http://www.w3.org/1999/xlink"
    if node.tag.endswith("image"):
        node.set("{%s}href" % XLINK_NS, data_uri)  # xlink:href
        node.set("href", data_uri)                 # SVG2 href
        node.set("width", str(size))
        node.set("height", str(size))
    else:
        from lxml import etree
        image_el = etree.Element("{%s}image" % SVG_NS)
        # carry over position attrs if present
        for attr in ("x", "y"):
            if node.get(attr) is not None:
                image_el.set(attr, node.get(attr))
        image_el.set("width", str(size))
        image_el.set("height", str(size))
        image_el.set("{%s}href" % XLINK_NS, data_uri)
        image_el.set("href", data_uri)
        node.getparent().replace(node, image_el)