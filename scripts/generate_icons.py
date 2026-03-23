"""
Generate PWA icons for TrendPulse:
  public/icons/icon-192.png
  public/icons/icon-512.png

Design: dark navy (#0f172a) background, indigo-to-purple gradient circle,
white "TP" text in the center.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

OUTPUT_DIR = Path(__file__).parent.parent / "public" / "icons"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def lerp_color(c1, c2, t):
    """Linear interpolation between two RGB tuples."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_gradient_circle(draw, cx, cy, radius, color_start, color_end):
    """Draw a filled circle with a radial gradient from center outward."""
    for r in range(radius, 0, -1):
        t = 1.0 - r / radius
        color = lerp_color(color_start, color_end, t)
        bbox = [cx - r, cy - r, cx + r, cy + r]
        draw.ellipse(bbox, fill=color)


def make_icon(size: int, output_path: Path):
    BG_COLOR = (15, 23, 42)          # #0f172a
    INDIGO    = (99, 102, 241)        # #6366f1
    PURPLE    = (168, 85, 247)        # #a855f7
    WHITE     = (255, 255, 255)

    img = Image.new("RGBA", (size, size), (*BG_COLOR, 255))
    draw = ImageDraw.Draw(img)

    # Rounded rect background (already filled above)
    # Draw gradient circle
    cx, cy = size // 2, size // 2
    circle_radius = int(size * 0.38)
    draw_gradient_circle(draw, cx, cy, circle_radius, INDIGO, PURPLE)

    # Draw "TP" text
    font_size = int(size * 0.28)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except OSError:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()

    text = "TP"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = cx - text_w // 2
    text_y = cy - text_h // 2 - bbox[1]

    # Subtle shadow
    draw.text((text_x + 2, text_y + 2), text, font=font, fill=(0, 0, 0, 120))
    draw.text((text_x, text_y), text, font=font, fill=WHITE)

    img.save(output_path, "PNG")
    print(f"Generated: {output_path} ({size}x{size})")


if __name__ == "__main__":
    make_icon(192, OUTPUT_DIR / "icon-192.png")
    make_icon(512, OUTPUT_DIR / "icon-512.png")
    print("Done.")
