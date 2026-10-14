
import re
import html


def clean_text(text):
    """Normalize SMS text while retaining useful spam-related signals."""
    text = html.unescape(str(text))
    text = text.lower()

    # Replace URLs and email addresses with placeholders.
    text = re.sub(r"https?://\S+|www\.\S+", " URLTOKEN ", text)
    text = re.sub(
        r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b",
        " EMAILTOKEN ",
        text
    )

    # Normalize phone numbers and long digit sequences.
    text = re.sub(r"\b\d{5,}\b", " NUMBERTOKEN ", text)

    # Keep letters, digits, and the placeholders.
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text
