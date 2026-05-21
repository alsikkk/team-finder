import hashlib
import io

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


AVATAR_SIZE = 128
BACKGROUND_COLORS = (
    "#5B7C99",
    "#6B8E7B",
    "#8B7E6A",
    "#7A6B8E",
    "#6A7A8E",
    "#7E8B6B",
    "#8E6B7A",
    "#6B7E8E",
)


def _pick_background(email):
    digest = hashlib.md5(email.encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(BACKGROUND_COLORS)
    return BACKGROUND_COLORS[index]


def build_avatar_file(name, email):
    letter = (name or email or "?")[0].upper()
    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), _pick_background(email))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = (
        (AVATAR_SIZE - text_width) // 2,
        (AVATAR_SIZE - text_height) // 2 - 4,
    )
    draw.text(position, letter, fill="#F5F7FA", font=font)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return ContentFile(buffer.read(), name=f"avatar_{email}.png")
