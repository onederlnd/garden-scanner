# app/cards/generate_qr.py
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from pathlib import Path
from app.db.sessions import SessionLocal
from app.config import BASE_URL, settings
from app.resources import resources

BASE_URL = BASE_URL.rstrip("/")

if __name__ == "__main__":
    session = SessionLocal()
    try:
        for resource in resources:
            model = resource["model"]
            url_path = resource["url_path"]

            rows = session.query(model).all()
            for row in rows:
                url = f"{BASE_URL}/{url_path}/{row.slug}"

                qr_code = qrcode.QRCode(
                    box_size=settings.qr_box_size, error_correction=ERROR_CORRECT_H
                )
                qr_code.add_data(url)
                qr_code.make(fit=True)

                img = qr_code.make_image()

                output_dir = Path(f"cards/output/{url_path}")
                output_dir.mkdir(parents=True, exist_ok=True)

                img.save(output_dir / f"{row.slug}.png")

    finally:
        session.close()
