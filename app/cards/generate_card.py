# app/cards/generate_card.py

from pathlib import Path
from weasyprint import HTML
from app.db.session import SessionLocal
from app.resources import resources
from app.templating import templates


def render_card_html(row, url_path, qr_path, label_field):
    template = templates.get_template(f"cards/{url_path}.html")
    label = getattr(row, label_field)
    return template.render(
        qr_path=qr_path,
        label=label,
        scientific_name=row.scientific_name,
        light_needs=row.light_needs,
        watering_frequency=row.watering_frequency,
    )


def generate_card_image(row, url_path, label_field="common_name"):
    qr_path = Path(f"cards/output/{url_path}") / f"{row.slug}.png"
    if not qr_path.exists():
        print(f"[SKIP] No QR code found for {url_path}/{row.slug}")
        return

    html_content = render_card_html(
        row, url_path, qr_path.resolve().as_uri(), label_field
    )

    output_dir = Path(f"cards/output_final/{url_path}")
    output_dir.mkdir(parents=True, exist_ok=True)

    HTML(string=html_content).write_pdf(str(output_dir / f"{row.slug}.pdf"))


def generate_all_cards():
    session = SessionLocal()
    try:
        for resource in resources:
            model = resource["model"]
            url_path = resource["url_path"]
            label_field = resource.get("label_field", "common_name")

            rows = session.query(model).all()
            for row in rows:
                generate_card_image(row, url_path, label_field)
    finally:
        session.close()


if __name__ == "__main__":
    generate_all_cards()
