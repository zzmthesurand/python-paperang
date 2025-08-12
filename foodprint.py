from labels import simple_label_to_png, svg_to_png_label_cairo, PRINTER_WIDTH
from paperang_printer import Paperang_Printer  # your existing wrapper

printer = Paperang_Printer()

# Simple
simple_label_to_png(
    [
        "Food: Chicken Thighs",
        "Weight: 1.605 kg",
        "Expiry: Aug 17, 2025",
        "Frozen: Aug 12, 2025",
    ],
    "simple.png",
    width_px=PRINTER_WIDTH,
    bottom_margin_px=100,
    threshold=180,
)
#printer.print_image_file("simple.png")

# SVG
svg_to_png_label_cairo(
    "food_template.svg",
    {"food": "Chicken Thighs", "weight": "1.605 kg", "expiry": "Aug 17, 2025", "frozen": "Aug 12, 2025"},
    "from_svg.png",
    width_px=500,
    bottom_margin_px=10,
    threshold=180,
)
#printer.print_image_file("from_svg.png", rotation = 0)

#printer.print_image_file("from_svg.png", rotation = 45)
#printer.print_self_test()

print("Printing image now")

#printer.print_image_file("from_svg.png", padding=0, rotation = 90)
#printer.print_image_file("from_svg.png", padding=0, density=70, rotation = 90)
#printer.print_image_file("kumiko.jpg", padding=0, density=70, rotation = 90)
printer.print_dithered_image("jonluke.jpg") #, rotation=90)
