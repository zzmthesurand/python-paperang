from labels import simple_label_to_png, svg_to_png_label_cairo, PRINTER_WIDTH
from paperang_printer import Paperang_Printer  # your existing wrapper

printer = Paperang_Printer()

# SVG
svg_to_png_label_cairo(
    "food_template.svg",
    {"food": "Chicken Thighs", "weight": "1.605 kg", "expiry": "Aug 17, 2025", "frozen": "Aug 12, 2025"},
    "from_svg.png",
    width_px=500,
    bottom_margin_px=10,
    threshold=180,
)
printer.print_image_file("from_svg.png", rotation = 90)