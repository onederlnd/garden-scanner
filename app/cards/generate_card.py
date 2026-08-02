# app/cards/generate_card.py

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from app.db.sessions import SessionLocal
from app.config import settings
from app.resources import resources

if __name__ == "__main__":
    session = SessionLocal()
    try:
        for resource in resources:
            model = resource["model"]
            url_path = resource["url_path"]

            rows = session.query(model).all()
            for row in rows:
                canvas = Image.new("RGB", settings.card_canvas_size, "white")

                qr_path = Path(f"cards/output/{url_path}") / f"{row.slug}.png"

                qr_code = Image.open(qr_path)
                resized_qr = qr_code.resize(settings.card_qr_size)

                x = (settings.card_canvas_size[0] - settings.card_qr_size[0]) // 2

                canvas.paste(resized_qr, (x, settings.card_qr_offset_y))

                draw = ImageDraw.Draw(canvas)
                draw.text(
                    (x, settings.card_qr_offset_y + settings.card_qr_size[1] + 20),
                    row.common_name,
                    fill="black",
                )

                output_dir = Path(f"cards/output_final/{url_path}")
                output_dir.mkdir(parents=True, exist_ok=True)

                canvas.save(output_dir / f"{row.slug}.png")

    finally:
        session.close()
