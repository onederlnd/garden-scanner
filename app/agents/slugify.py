# app/agents/slugify.py
import re


def generate_slug(item_name):
    item = item_name.lower()
    item = item.replace("'", "")
    item = item.replace(" ", "-")

    slug = re.sub(r"[^a-z0-9-]", "", item)
    return slug
