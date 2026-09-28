"""Create a deterministic local image for the Audit Ledger frame upload demo."""
from pathlib import Path

from PIL import Image, ImageDraw


OUTPUT = Path(__file__).resolve().parents[1] / "data" / "sample_inference_frame.png"


def main() -> None:
    image = Image.new("RGB", (640, 360), (18, 35, 48))
    draw = ImageDraw.Draw(image)
    draw.rectangle((120, 95, 520, 280), outline=(65, 210, 170), width=5)
    draw.rectangle((180, 140, 300, 235), fill=(45, 75, 95), outline=(230, 180, 70), width=3)
    draw.text((20, 20), "VAJRA-CV / EDGE FRAME 001", fill=(190, 225, 235))
    draw.text((20, 330), "LOCAL TEST FIXTURE", fill=(110, 180, 190))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, format="PNG")
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()
