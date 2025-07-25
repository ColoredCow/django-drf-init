import os
import re
import unicodedata
import uuid


def clean_filename(filename):
    name, ext = os.path.splitext(filename)
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    name = re.sub(r"[^a-zA-Z0-9-_\.]", "-", name)
    name = re.sub(r"-{2,}", "-", name).strip("-").lower()
    return f"{name}{ext.lower()}"


def generate_storage_key(filename, prefix="uploads"):
    cleaned = clean_filename(filename)
    return f"{prefix}/{uuid.uuid4().hex}_{cleaned}"
