#!/usr/bin/env python
"""Generate a synthetic 3-page image-only PDF for the Study Kit demo.

Page 1 is course intro / instructor / contact (should be dropped by sanitize).
Pages 2-3 are knowledge pages. No internal content, no real people.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
OUT = Path(__file__).resolve().parent / "slides.pdf"


def font(size: int) -> ImageFont.FreeTypeFont:
    for name in ("arial.ttf", "segoeui.ttf", "calibri.ttf"):
        p = Path(r"C:\Windows\Fonts") / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def page(title: str, lines: list[str]) -> Image.Image:
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 90], fill=(30, 60, 120))
    d.text((40, 22), title, fill="white", font=font(38))
    y = 140
    for line in lines:
        d.text((60, y), line, fill=(20, 20, 20), font=font(30))
        y += 62
    return img


def main() -> None:
    pages = [
        page("Course Intro", [
            "Instructor: John Doe",
            "Contact: john@example.com",
            "Tonight 8:00 PM, Room 101",
            "This page is promo/personal info and must be dropped.",
        ]),
        page("Chapter 1: Gradient Descent", [
            "Loss = mean((y - y_hat)^2)",
            "w := w - eta * dLoss/dw",
            "Learning rate too large: divergence",
            "Learning rate too small: slow convergence",
        ]),
        page("Chapter 2: Self-Attention", [
            "Q = X W_Q, K = X W_K, V = X W_V",
            "score = Q K^T / sqrt(d_k)",
            "Attention = softmax(score) V",
            "Multi-head: concat(heads) W_O",
        ]),
    ]
    pages[0].save(OUT, "PDF", resolution=150.0, save_all=True, append_images=pages[1:])
    print(f"wrote {OUT} ({len(pages)} pages)")


if __name__ == "__main__":
    main()
